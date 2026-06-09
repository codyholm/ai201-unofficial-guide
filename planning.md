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

Our documents consist of two main source types. First we have short student reviews from omshub and omscentral. These make sense as one review per chunk since they are self-contained unit withen the larger document, and most fit under the 256 token cap or can be split effectively. The other type is more free form paragraphs from comments and blog posts of varying length and styles from different writers. Splitting these by paragraph and holding comment boundaries keeps the chunks focused and relevant.

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:**

**Top-k:**

**Production tradeoff reflection:**

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | | |
| 2 | | |
| 3 | | |
| 4 | | |
| 5 | | |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1.

2.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:**

**Milestone 4 — Embedding and retrieval:**

**Milestone 5 — Generation and interface:**
