"""Milestone 5 — Gradio UI for the Unofficial Guide RAG.

A question goes in; a grounded answer plus the sources it drew from come out.
The index is built once at startup (idempotent) so the first query is ready.
Run: python app.py  ->  http://localhost:7860
"""

import gradio as gr

from generate import generate
from retrieve import build_index


def handle_query(question):
    if not question.strip():
        return "", ""
    result = generate(question)
    if result["sources"]:
        sources = "\n".join(f"- {s}" for s in result["sources"])
    else:
        sources = "(no sources — the guide could not answer from its documents)"
    return result["answer"], sources


with gr.Blocks(title="The Unofficial Guide — GA (CS-6515)") as demo:
    gr.Markdown(
        "# The Unofficial Guide — GA (CS-6515)\n"
        "Ask about Georgia Tech's Intro to Graduate Algorithms. Answers come only "
        "from collected student reviews, Reddit threads, and blog posts."
    )
    question = gr.Textbox(label="Your question", placeholder="How hard is GA, really?")
    ask = gr.Button("Ask", variant="primary")
    answer = gr.Textbox(label="Answer", lines=8)
    sources = gr.Textbox(label="Sources", lines=4)

    ask.click(handle_query, inputs=question, outputs=[answer, sources])
    question.submit(handle_query, inputs=question, outputs=[answer, sources])


if __name__ == "__main__":
    build_index()  # idempotent: skips when the collection is already populated
    demo.launch()
