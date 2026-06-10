"""Milestone 5 — grounded generation for the Unofficial Guide RAG.

generate(query, k) retrieves the k nearest chunks (via retrieve.py), hands them
to Groq's llama-3.3-70b-versatile as the only allowed context, and returns a
grounded answer. The system prompt forbids outside knowledge and forces a set
refusal when the context doesn't cover the question. Source attribution is built
in Python from the retrieved metadata, not left to the model.
"""

import os
from functools import lru_cache

from dotenv import load_dotenv
from groq import Groq

from retrieve import build_index, retrieve

load_dotenv()

GEN_MODEL = "llama-3.3-70b-versatile"
TEMPERATURE = 0.2  # low: grounded answers should be consistent, not creative
REFUSAL = "I don't have enough information on that."

SYSTEM_PROMPT = (
    "You are The Unofficial Guide to Georgia Tech's CS-6515 (Introduction to "
    "Graduate Algorithms). You answer questions using only the numbered student "
    "sources provided in each request.\n\n"
    "Rules:\n"
    "- Use only the information in the provided sources. Do not use any outside "
    "or prior knowledge.\n"
    "- The sources are student reviews, comments, and blog posts; when they "
    "disagree, reflect the range of views instead of inventing a single fact.\n"
    "- If the sources do not contain enough information to answer the question, "
    f"reply with exactly this sentence and nothing else: {REFUSAL}\n"
    "- Do not guess or fill gaps from general knowledge."
)


# --- lazy singleton (open the Groq client once) -----------------------------

@lru_cache(maxsize=1)
def _client():
    key = os.environ.get("GROQ_API_KEY")
    if not key:
        raise RuntimeError("GROQ_API_KEY is not set — copy .env.example to .env")
    return Groq(api_key=key)


# --- source attribution (built from metadata, not the model) ----------------

def _descriptor(meta):
    """A human-readable label for one chunk's source, from its metadata."""
    source = meta.get("source", "unknown")
    kind = meta.get("kind", "")
    if kind == "review":
        semester = meta.get("semester")
        return f"{source} review ({semester})" if semester else f"{source} review"
    if kind in ("comment", "post"):
        era = meta.get("era")
        return f"{source} {kind} (era {era})" if era else f"{source} {kind}"
    if kind == "blog":
        return f"{source} blog"
    if kind == "course_facts":
        return f"{source} course facts"
    return f"{source} {kind}".strip()


def _format_context(results):
    """Number each retrieved chunk and label it with its source descriptor.
    This labeled block is the only context the model is allowed to use."""
    blocks = []
    for i, r in enumerate(results, 1):
        label = _descriptor(r["metadata"])
        blocks.append(f"[{i}] {label}\n{r['text']}")
    return "\n\n".join(blocks)


def _source_list(results):
    """Deduped, first-appearance-ordered list of source descriptors.

    Dedupe by (source, unit_index) so multiple chunks from the same review or
    comment collapse to one line. This is the programmatic attribution the guide
    requires — the model never produces it."""
    seen = set()
    sources = []
    for r in results:
        meta = r["metadata"]
        key = (meta.get("source"), meta.get("unit_index"))
        if key in seen:
            continue
        seen.add(key)
        sources.append(_descriptor(meta))
    return sources


# --- generation -------------------------------------------------------------

def generate(query, k=5):
    """Answer query from retrieved context only.

    Returns {answer, sources, refused}. On refusal, sources is empty so an
    out-of-scope question shows a clean refusal, not a misleading source list.
    """
    results = retrieve(query, k)
    context = _format_context(results)

    response = _client().chat.completions.create(
        model=GEN_MODEL,
        temperature=TEMPERATURE,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Sources:\n{context}\n\nQuestion: {query}"},
        ],
    )
    answer = response.choices[0].message.content.strip()

    refused = REFUSAL.lower() in answer.lower()
    sources = [] if refused else _source_list(results)
    return {"answer": answer, "sources": sources, "refused": refused}


# --- verification driver ----------------------------------------------------

EVAL_QUESTIONS = [
    "How many hours per week do students usually spend on GA?",
    "What do students recommend to do in preparation for GA before starting?",
    "Is GA as hard as people say?",
    "Should I practice LeetCode to prepare for GA?",
    "What is the most difficult subject or topic in GA?",
]

# deliberately outside the corpus (no dining content) — should refuse
OUT_OF_SCOPE = "Which dining hall at Georgia Tech has the best food?"


if __name__ == "__main__":
    build_index()

    for q in EVAL_QUESTIONS + [OUT_OF_SCOPE]:
        result = generate(q)
        print(f"\n{'=' * 80}\nQ: {q}\n")
        print(result["answer"])
        if result["sources"]:
            print("\nSources:")
            for s in result["sources"]:
                print(f"  - {s}")
        else:
            print("\n(no sources — refused)")
