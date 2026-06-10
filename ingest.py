"""Milestone 3 — document ingestion and chunking for the Unofficial Guide RAG.

load_documents() reads and cleans the 10 source files; chunk_text() splits them into
embedding-ready chunks (one dict per chunk: id + text + metadata) and appends new ones
to chunks.jsonl. Two chunking modes: review aggregators (omscentral, omshub) get one
review per chunk; reddit threads and blogs get paragraph/sentence packing. Both cap at
256 tokens (the all-MiniLM-L6-v2 limit) with one-sentence overlap on same-unit splits.
"""

import json
import re
import unicodedata
from collections import Counter
from functools import lru_cache
from pathlib import Path

from transformers import AutoTokenizer

EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
MAX_TOKENS = 256
OVERLAP_RESERVE = 32  # pack to MAX_TOKENS - this so the carried overlap sentence still fits
DOCS_DIR = "documents"
OUT_PATH = "data/chunks.jsonl"  # data/ also holds the persistent Chroma index (M4)


# --- tokenizer (the real cap is what MiniLM will embed) ---------------------

@lru_cache(maxsize=1)
def _tokenizer():
    return AutoTokenizer.from_pretrained(EMBED_MODEL)


def _token_count(text):
    return len(_tokenizer().encode(text, add_special_tokens=False))


# --- shared text helpers ----------------------------------------------------

_SMART = {
    "‘": "'", "’": "'", "“": '"', "”": '"',
    "–": "-", "—": "-", "…": "...", " ": " ",
}

_SENT_SPLIT = re.compile(r"(?<=[.!?])\s+")


def _normalize(text):
    text = unicodedata.normalize("NFKC", text)
    for a, b in _SMART.items():
        text = text.replace(a, b)
    text = "\n".join(ln.rstrip() for ln in text.split("\n"))
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _sentences(text):
    flat = re.sub(r"\s+", " ", text).strip()
    return [s for s in _SENT_SPLIT.split(flat) if s]


def _first_line(text):
    for ln in text.split("\n"):
        if ln.strip():
            return ln.strip()
    return ""


def _hard_split(text, max_tokens):
    """Last-resort split for a single sentence longer than the cap."""
    tok = _tokenizer()
    ids = tok.encode(text, add_special_tokens=False)
    return [tok.decode(ids[i:i + max_tokens]) for i in range(0, len(ids), max_tokens)]


def _split_unit(text, max_tokens):
    """One chunk if the unit fits; otherwise pack sentences with a one-sentence overlap
    between consecutive chunks (same unit only). Packs to a reduced cap so the carried
    overlap sentence leaves the chunk under max_tokens; the hard cap is never exceeded."""
    text = text.strip()
    if not text:
        return []
    if _token_count(text) <= max_tokens:
        return [text]

    cap = max_tokens - OVERLAP_RESERVE  # headroom for the carried overlap sentence
    pieces = []
    for s in _sentences(text):
        pieces.extend(_hard_split(s, cap) if _token_count(s) > cap else [s])

    chunks, cur, i = [], [], 0
    while i < len(pieces):
        piece = pieces[i]
        if not cur:
            cur, i = [piece], i + 1
        elif _token_count(" ".join(cur + [piece])) <= cap:
            cur.append(piece)
            i += 1
        elif len(cur) == 1 and _token_count(" ".join(cur + [piece])) <= max_tokens:
            cur.append(piece)  # overlap-only chunk may use the reserve up to the hard cap
            i += 1
        else:
            chunks.append(" ".join(cur))
            overlap = cur[-1]  # always carry the last sentence into the next chunk
            cur = [overlap] if _token_count(overlap + " " + piece) <= max_tokens else []
    if cur:
        chunks.append(" ".join(cur))
    return chunks


def _mk_chunks(slug, unit_index, text, metadata, max_tokens):
    out = []
    for sub_i, ctext in enumerate(_split_unit(text, max_tokens)):
        out.append({
            "id": f"{slug}-{unit_index:04d}-c{sub_i}",
            "text": ctext,
            "metadata": dict(metadata),
        })
    return out


# --- load_documents ---------------------------------------------------------

def _source_type(slug):
    if slug.startswith("reddit"):
        return "reddit"
    if slug.startswith("blog-"):
        return "blog"
    if slug in ("omscentral", "omshub"):
        return slug
    raise ValueError(f"unknown source slug: {slug}")


_TS = re.compile(r"\d+\s*[a-zA-Z]+\s+ago")  # relative reddit timestamp, e.g. "3y ago"


def _clean_reddit(text):
    """Strip per-comment chrome that is not the delimiter, capture thread era, and
    reorder the original post so its username precedes its timestamp (matching the
    comment shape) so chunk_text can split every unit uniformly."""
    era = None
    kept = []
    for ln in text.split("\n"):
        t = ln.strip()
        if _TS.fullmatch(t) and era is None:
            era = t
        if t in ("•", "·", "OP", "Comments Section", "Continue this thread"):
            continue  # "OP" is the original-poster badge shown between username and timestamp
        if re.fullmatch(r"u/\S+ avatar", t):
            continue
        if re.fullmatch(r"r/\S+", t):
            continue
        if re.fullmatch(r"\d+ more repl(?:y|ies)", t):
            continue
        if re.match(r"Comment (deleted|removed)", t, re.I):
            continue
        if re.fullmatch(r"\d+", t):  # standalone vote / score / comment count
            continue
        kept.append(ln)

    # After dropping subreddit + bullet, the OP block leads with timestamp then
    # username; swap them so it reads username -> timestamp like every comment.
    first = next((i for i, l in enumerate(kept) if l.strip()), None)
    if first is not None and _TS.fullmatch(kept[first].strip()):
        nxt = next((k for k in range(first + 1, len(kept)) if kept[k].strip()), None)
        if nxt is not None:
            kept[first], kept[nxt] = kept[nxt], kept[first]

    return _normalize("\n".join(kept)), era


def load_documents(docs_dir=DOCS_DIR):
    docs = []
    for path in sorted(Path(docs_dir).glob("*.txt")):
        slug = path.stem
        stype = _source_type(slug)
        text = _normalize(path.read_text(encoding="utf-8"))
        era = None
        if stype == "reddit":
            text, era = _clean_reddit(text)
        docs.append({"source": slug, "source_type": stype, "text": text, "era": era})
    return docs


# --- chunk_text: review mode ------------------------------------------------

_DATE_LONG = re.compile(r"[A-Z][a-z]+ \d{1,2}, \d{4}")          # "May 15, 2026"
_SEM_LONG = re.compile(r"(Spring|Summer|Fall|Winter) \d{4}")    # "Spring 2026"
_SEM_CAPS = re.compile(r"(SPRING|SUMMER|FALL|WINTER)\s+\d{4}")  # "SUMMER 2024"
_DATE_NUM = re.compile(r"\d{1,2}/\d{1,2}/\d{4}")                # "8/10/2024"


def _chunk_omscentral(doc):
    slug = doc["source"]
    lines = doc["text"].split("\n")
    starts = [
        i for i in range(len(lines) - 1)
        if _DATE_LONG.fullmatch(lines[i].strip()) and _SEM_LONG.fullmatch(lines[i + 1].strip())
    ]
    chunks = []
    header = "\n".join(lines[:starts[0]]) if starts else doc["text"]
    chunks += _mk_chunks(slug, 0, header,
                         {"source": slug, "source_type": "omscentral", "kind": "course_facts"},
                         MAX_TOKENS)

    for j, s in enumerate(starts):
        e = starts[j + 1] if j + 1 < len(starts) else len(lines)
        block = lines[s:e]
        date, semester = block[0].strip(), block[1].strip()
        rating = difficulty = workload = None
        body = []
        for bl in block[2:]:
            t = bl.strip()
            if (m := re.match(r"Rating:\s*(\d+)", t)):
                rating = int(m.group(1))
            elif (m := re.match(r"Difficulty:\s*(\d+)", t)):
                difficulty = int(m.group(1))
            elif (m := re.match(r"Workload:\s*(.+)", t)):
                workload = m.group(1).strip()
            elif t == "Georgia Tech Student":
                continue  # reviewer-affiliation label, not review content
            else:
                body.append(bl)
        meta = {"source": slug, "source_type": "omscentral", "kind": "review",
                "semester": semester, "date": date}
        if rating is not None:
            meta["rating"] = rating
        if difficulty is not None:
            meta["difficulty"] = difficulty
        if workload is not None:
            meta["workload"] = workload
        chunks += _mk_chunks(slug, j + 1, "\n".join(body), meta, MAX_TOKENS)
    return chunks


def _chunk_omshub(doc):
    slug = doc["source"]
    lines = doc["text"].split("\n")
    starts = [i for i, l in enumerate(lines) if _SEM_CAPS.fullmatch(l.strip())]
    chunks = []
    header = "\n".join(lines[:starts[0]]) if starts else doc["text"]
    chunks += _mk_chunks(slug, 0, header,
                         {"source": slug, "source_type": "omshub", "kind": "course_facts"},
                         MAX_TOKENS)

    for j, s in enumerate(starts):
        e = starts[j + 1] if j + 1 < len(starts) else len(lines)
        block = lines[s:e]
        semester = block[0].strip()
        date = workload = difficulty = overall = None
        meta_idx = {0}
        bi = 1
        while bi < len(block):
            t = block[bi].strip()
            if _DATE_NUM.fullmatch(t):
                date = t
                meta_idx.add(bi)
            elif t in ("VERIFIED",) or t.startswith("CS-6515") or t.startswith("Video version:"):
                meta_idx.add(bi)
            elif t in ("WORKLOAD", "DIFFICULTY", "OVERALL"):
                val = block[bi + 1].strip() if bi + 1 < len(block) else ""
                num = re.match(r"(\d+)", val)
                if num and t == "WORKLOAD":
                    workload = int(num.group(1))
                elif num and t == "DIFFICULTY":
                    difficulty = int(num.group(1))
                elif num and t == "OVERALL":
                    overall = int(num.group(1))
                meta_idx.update({bi, bi + 1, bi + 2})  # keyword, value, unit/label
            bi += 1
        body = "\n".join(block[i] for i in range(len(block)) if i not in meta_idx)
        meta = {"source": slug, "source_type": "omshub", "kind": "review", "semester": semester}
        if date is not None:
            meta["date"] = date
        if workload is not None:
            meta["workload"] = workload
        if difficulty is not None:
            meta["difficulty"] = difficulty
        if overall is not None:
            meta["overall"] = overall
        chunks += _mk_chunks(slug, j + 1, body, meta, MAX_TOKENS)
    return chunks


# --- chunk_text: paragraph mode ---------------------------------------------

def _reddit_units(text):
    """Split cleaned reddit text into writer units. Every unit reads
    username -> timestamp -> body, so the timestamp lines are the boundaries."""
    lines = text.split("\n")
    ts = [i for i, l in enumerate(lines) if _TS.fullmatch(l.strip())]
    units = []
    for k, i in enumerate(ts):
        end = ts[k + 1] if k + 1 < len(ts) else len(lines)
        body = lines[i + 1:end]
        if k + 1 < len(ts):  # drop trailing blank(s) + the next unit's username line
            while body and not body[-1].strip():
                body.pop()
            if body:
                body.pop()
        body = "\n".join(body).strip()
        if body:
            units.append(body)
    return units


def _chunk_reddit(doc):
    slug = doc["source"]
    units = _reddit_units(doc["text"])
    thread_title = _first_line(units[0]) if units else ""
    chunks = []
    for u_i, unit in enumerate(units):
        meta = {"source": slug, "source_type": "reddit",
                "kind": "post" if u_i == 0 else "comment",
                "era": doc["era"] or "", "thread_title": thread_title}
        chunks += _mk_chunks(slug, u_i, unit, meta, MAX_TOKENS)
    return chunks


def _chunk_blog(doc):
    slug = doc["source"]
    meta = {"source": slug, "source_type": "blog", "kind": "blog",
            "title": _first_line(doc["text"])}
    return _mk_chunks(slug, 0, doc["text"], meta, MAX_TOKENS)


# --- chunk_text: dispatch + incremental persistence -------------------------

_DISPATCH = {
    "omscentral": _chunk_omscentral,
    "omshub": _chunk_omshub,
    "reddit": _chunk_reddit,
    "blog": _chunk_blog,
}


def _existing_sources(out_path):
    p = Path(out_path)
    if not p.exists():
        return set()
    return {
        json.loads(line)["metadata"]["source"]
        for line in p.read_text(encoding="utf-8").splitlines() if line.strip()
    }


def chunk_text(docs, max_tokens=MAX_TOKENS, out_path=OUT_PATH):
    done = _existing_sources(out_path)
    new_chunks = []
    for doc in docs:
        if doc["source"] in done:
            continue
        new_chunks.extend(_DISPATCH[doc["source_type"]](doc))
    if new_chunks:
        Path(out_path).parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "a", encoding="utf-8") as f:
            for c in new_chunks:
                f.write(json.dumps(c, ensure_ascii=False) + "\n")
    return new_chunks


# --- verification driver ----------------------------------------------------

if __name__ == "__main__":
    docs = load_documents()
    chunks = chunk_text(docs)

    print(f"new chunks: {len(chunks)}")
    for src, n in sorted(Counter(c["metadata"]["source"] for c in chunks).items()):
        print(f"  {src}: {n}")

    if chunks:
        lengths = [_token_count(c["text"]) for c in chunks]
        print(f"\ntokens  min={min(lengths)}  max={max(lengths)}  mean={sum(lengths) // len(lengths)}")
        over = [c["id"] for c, t in zip(chunks, lengths) if t > MAX_TOKENS]
        print(f"over {MAX_TOKENS}: {len(over)} {over[:5]}")
        cf = [c["id"] for c in chunks if c["metadata"].get("kind") == "course_facts"]
        print(f"course_facts chunks: {cf}")

        print("\n--- samples ---")
        seen = set()
        for c in chunks:
            key = (c["metadata"]["source_type"], c["metadata"].get("kind"))
            if key in seen:
                continue
            seen.add(key)
            print(f"\n[{c['id']}] {c['metadata']}")
            print(c["text"][:300])
