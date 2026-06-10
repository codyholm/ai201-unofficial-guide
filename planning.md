# Project 1 Planning: The Unofficial Guide

## Domain

This unofficial guide covers student reviews, experiences, and recommendations for Introduction to Graduate Algorithms (CS-6515) at Georgia Tech, the course that arguably has the hardest reputation for the online Master of Science in Computer Science program. Georgia Tech's official course page contains topics, the syllabus, and recommended prerequisites, but lacks the perspectives of students. Things such as the actual difficulty, weekly workload needed, and how to study are not available through official channels but instead the knowledge is provided by students across various sources. This system brings the scattered knowledge together for easy access.

---

## Documents

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | omscentral | GA CS6515 student reviews | https://www.omscentral.com/courses/introduction-to-graduate-algorithms/reviews |
| 2 | reddit | Effectively studying for GA | https://www.reddit.com/r/OMSCS/comments/15kch4o/how_to_effectively_prestudy_for_graduate/ |
| 3 | reddit | Student experiences in GA | https://www.reddit.com/r/OMSCS/comments/1osa2qg/how_has_been_your_experience_in_grad_algorithms/ |
| 4 | reddit | GA It's true what they say | https://www.reddit.com/r/OMSCS/comments/vleq4h/cs6515_graduate_algorithms_its_true_what_they_say/ |
| 5 | omshub | GA CS6515 course reviews | https://www.omshub.org/course/CS-6515 |
| 6 | lowyx blog | CS6515 OMSCS - Graduate Algorithm | https://lowyx.com/posts/gt-ga/ |
| 7 | takp blog | Course Review: Intro to Graduate Algorithms @Georgia Tech | https://takp.me/posts/cs-6515-into-to-graduate-algorithms-at-georgia-tech/ |
| 8 | richard lee blog | Tips to get an A in GA (study/exam strategy) | https://rich-w-lee.medium.com/tips-to-get-an-a-in-omscs-graduate-algorithms-6bf0af13b4e1 |
| 9 | abhijithc blog | GA CS6515 review (May 2024) | https://abhijithc.com/blog/2024/05/04/ga-(cs6515)-an-omscs-review.html |
| 10 | etlq blog | GA review - proofs and theory focus | https://etlq.github.io/omscs/ga/ |

---

## Chunking Strategy

We will use two chunking strategies for our documents based on source type, one for the review aggregators (omscentral and omshub) and another for the blogs and reddit threads.

**Chunk size:**

The sizing of chunks will vary depending on source type. For reviews, we will add a delimiter so we can separate and have one review per chunk. The reviews are self contained and could be tainted if multiple reviews are included in one chunk, however if reviews are too long and broad it could reduce the effectiveness as well. So in addition to doing no more than one review per chunk, if a review is larger than 256 tokens it will split into multiple chunks.

For the blogs and reddit threads, we will instead split by paragraph while also adding a delimiter to separate different users and comments. This ensures we are effectively chunking the content while separating different comments and posts by their writers, so multiple perspectives are not given in one chunk. In addition the same 256 token cap will apply, so longer paragraphs can have multiple chunks. A short reddit post or comment becomes a single chunk, but longer comments or blog posts become several.

**Overlap:**

We will have one sentence overlapping between chunks for the paragraph splits on blogs and reddit threads, while still respecting the delimiter between individual comments so overlap is only present when chunks are from the same writer.

**Reasoning:**

Our documents consist of two main source types. First we have short student reviews from omshub and omscentral. These make sense as one review per chunk since they are self-contained units within the larger document, and most fit under the 256 token cap or can be split effectively. The other type is more free form paragraphs from comments and blog posts of varying length and styles from different writers. Splitting these by paragraph and holding comment boundaries keeps the chunks focused and relevant.

---

## Retrieval Approach

**Embedding model:**

We will be using all-MiniLM-L6-v2 for the embedding model, via sentence-transformers. This was chosen because it runs locally with no API keys required, runs fast, and reads up to 256 tokens per chunk which is large enough to perform well with our content type in documents.

**Top-k:**

Starting at k=5. The questions this guide answers are mostly consensus questions, for things such as difficulty or weekly workload the useful answers are the ones the most students agree on. Too few chunks we might only get one outlier review and not see what most students think, or not take into account a contradicting claim. If there are too many though we could receive chunks that are unrelated or broaden the scope of what we're asking. 5 should be a good starting number for testing, will tune during evaluation stage.

**Production tradeoff reflection:**

If this were a real production deployment with no cost constraints, the first thing to look at would be context length. The 256 token limit forces us to split long reviews and blog sections, even if all of the context is relevant and we wanted it larger. This results in the possibility that a chunk does not contain a complete argument or all the desired detail for later retrieval. A longer context model could hold a full review and longer sections of blog posts in one chunk. Also I'd test a larger or newer model for domain accuracy on the technical language and on the opinion text, MiniLM is a small general-purpose model but bigger models not run locally could retrieve more accurately.

---

## Evaluation Plan

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | How many hours per week do students usually spend on GA? | Around 20-30+ hours depending on student's algorithms background |
| 2 | What do students recommend to do in preparation for GA before starting? | Review the course's textbooks, understand math and dsa fundamentals. |
| 3 | Is GA as hard as people say? | Mixed reports. Many call it brutal and stressful, others say it is manageable and fair if you keep up with homework and practice problems |
| 4 | Should I practice LeetCode to prepare for GA? | No, LeetCode is more about implementing to solve specific puzzles, and GA is about theory and proof-writing. |
| 5 | What is the most difficult subject or topic in GA? | Often the proofs and max-flow/NP material, but all of it can be difficult if not studied and practiced. |

---

## Anticipated Challenges

1. Conflicting reviews and opinions. Students can disagree substantially on things such as difficulty and time needed. Retrieval might pull chunks from only one side, producing a biased answer. This system is better used to gather a consensus and various perspectives, not providing a single factual answer.

2. Course information that has changed or is outdated. The GA course has seen updates in recent years, including the grading structure and how much exams make up final grade. Although our documents tend to be newer, there are some things that are inconsistent based on when the course was taken.

---

## Architecture

```
Document Ingestion       ->  Python script (load 10 .txt, clean)
         |
         v
Chunking                 ->  two-mode chunker (review / paragraph)
         |
         v
Embedding + Vector Store ->  all-MiniLM-L6-v2  ->  ChromaDB
         |
         v
Retrieval                ->  semantic top-k search (k=5)
         |
         v
Generation               ->  Groq llama-3.3-70b-versatile  ->  Gradio UI
```

## AI Tool Plan

**Milestone 3 — Ingestion and chunking:**

I will use Claude Opus for implementation and Gpt 5.5 to do reviews. First I'll give Claude the Domain, Documents, and Chunking Strategy sections from planning.md as context and have it summarize to make sure we're aligned. Then have it write implementation plan for writing load_documents() and chunk_text(). This includes the cleaning and normalizing of characters as well as cleaning up various web page elements. And then for the text chunking, implementing the two different methods based off source type. Review the plan and if it meets requirements have Claude implement.

**Milestone 4 — Embedding and retrieval:**

In new session with Claude Opus, provide the retrieval approach section and the architecture diagram as context. Ask it to embed the chunks with all-MiniLM-L6-v2 and load them into ChromaDB with metadata. Then have them write function retrieve(query, k), which should return relevant chunks plus sources and distances. Verify by running evaluation questions, check distances are low and the chunks are relevant. If needed adjust k and compare results. In new session with GPT 5.5, have them review the implementations from milestone 3 and 4. They should verify code is correct, check for edge cases, and that the full process runs. Request they come up with additional questions to test out in addition to evaluation questions.

**Milestone 5 — Generation and interface:**

In new session with Claude Opus, give Claude the architecture diagram and retrieval approach as context again, as well as having it check the implementation for milestone 3 and 4. Then in plan mode have it write out implementation plan for the generation and interface. For Generation they should write generate(query) which calls the groq model with a grounding prompt, having it answer only from the retrieved chunks with sources included, and returning an appropriate message when not enough information. For the interface we are doing a Gradio UI, which takes the question and returns answer with sources. Review the plan and if it meets requirements have Claude implement. After verify end to end with eval questions, confirm sources show in the output, and that questions not answerable from sources are refused. Once verified, have GPT 5.5 code review final implementation, checking for potential edge cases or runtime issues.
