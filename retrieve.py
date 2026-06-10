"""Milestone 4 — embedding and retrieval for the Unofficial Guide RAG.

build_index() embeds every chunk in data/chunks.jsonl with all-MiniLM-L6-v2 and
loads the vectors (plus text and metadata) into a persistent ChromaDB collection.
retrieve(query, k) embeds a question with the same model and returns the k nearest
chunks by cosine distance, each with its source and distance. Consumes the M3
output; it does not import ingest.py.
"""

import json
import re
from functools import lru_cache
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"  # same model string as ingest.py
CHUNKS_PATH = "data/chunks.jsonl"
CHROMA_PATH = "data/chroma"
COLLECTION = "ga_reviews"
TOP_K = 5


# --- lazy singletons (load the model / open the DB once) --------------------

@lru_cache(maxsize=1)
def _model():
    return SentenceTransformer(EMBED_MODEL)


@lru_cache(maxsize=1)
def _client():
    return chromadb.PersistentClient(path=CHROMA_PATH)


@lru_cache(maxsize=1)
def _collection():
    # cosine overrides Chroma's L2 default; our vectors are normalized at encode time
    return _client().get_or_create_collection(
        COLLECTION, metadata={"hnsw:space": "cosine"}
    )


def _embed(texts):
    """Encode to normalized vectors. Returns a list of lists (Chroma-friendly)."""
    vecs = _model().encode(texts, normalize_embeddings=True, batch_size=64)
    return vecs.tolist()


# --- build_index ------------------------------------------------------------

_POS = re.compile(r"^(.+)-(\d{4})-c(\d+)$")  # id shape: <slug>-<unit:04d>-c<sub>


def _position(chunk_id):
    """Pull (unit_index, chunk_index) out of an id like 'omscentral-0077-c0'.
    unit_index is the review/comment/section's position within its document;
    chunk_index is the sub-chunk within that unit (0 unless a long unit was split)."""
    m = _POS.match(chunk_id)
    if not m:
        raise ValueError(f"unexpected chunk id format: {chunk_id}")
    return int(m.group(2)), int(m.group(3))


def _load_chunks(path=CHUNKS_PATH):
    ids, texts, metadatas = [], [], []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        c = json.loads(line)
        unit_index, chunk_index = _position(c["id"])
        meta = dict(c["metadata"])  # already scalar-only, Chroma-safe
        meta["unit_index"] = unit_index    # position of the source unit in its document
        meta["chunk_index"] = chunk_index  # sub-chunk within that unit
        ids.append(c["id"])
        texts.append(c["text"])
        metadatas.append(meta)
    return ids, texts, metadatas


def build_index(rebuild=False):
    """Embed every chunk and load it into the persistent collection.

    Idempotent: skips the work when the collection already holds every chunk.
    rebuild=True drops the collection and re-embeds from scratch.
    """
    ids, texts, metadatas = _load_chunks()

    if rebuild:
        try:
            _client().delete_collection(COLLECTION)
        except Exception:
            pass  # nothing to drop on a clean run
        _collection.cache_clear()

    collection = _collection()
    if collection.count() == len(ids) and not rebuild:
        print(f"index already built ({collection.count()} chunks)")
        return collection

    print(f"embedding {len(ids)} chunks with {EMBED_MODEL} ...")
    embeddings = _embed(texts)
    collection.add(ids=ids, embeddings=embeddings, documents=texts, metadatas=metadatas)
    print(f"index built ({collection.count()} chunks) at {CHROMA_PATH}")
    return collection


# --- retrieve ---------------------------------------------------------------

def retrieve(query, k=TOP_K):
    """Return the k chunks nearest to query, nearest first.

    Each result: {text, source, kind, distance, metadata}. distance is cosine
    distance (0 = identical meaning, up to 2); lower means more relevant.
    """
    collection = _collection()
    if collection.count() == 0:
        raise RuntimeError(
            "index is empty — run build_index() or `python retrieve.py` first"
        )

    res = collection.query(
        query_embeddings=_embed([query]),
        n_results=k,
        include=["documents", "metadatas", "distances"],
    )
    out = []
    for text, meta, dist in zip(
        res["documents"][0], res["metadatas"][0], res["distances"][0]
    ):
        out.append({
            "text": text,
            "source": meta.get("source"),
            "kind": meta.get("kind"),
            "distance": dist,
            "metadata": meta,
        })
    return out


# --- verification driver ----------------------------------------------------

EVAL_QUESTIONS = [
    "How many hours per week do students usually spend on GA?",
    "What do students recommend to do in preparation for GA before starting?",
    "Is GA as hard as people say?",
    "Should I practice LeetCode to prepare for GA?",
    "What is the most difficult subject or topic in GA?",
]


if __name__ == "__main__":
    build_index()

    for q in EVAL_QUESTIONS:
        print(f"\n{'=' * 80}\nQ: {q}")
        for i, r in enumerate(retrieve(q), 1):
            snippet = " ".join(r["text"].split())[:200]
            print(f"\n  [{i}] dist={r['distance']:.3f}  {r['source']} ({r['kind']})")
            print(f"      {snippet}")
