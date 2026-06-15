# The Unofficial Guide — Project 1

---

## Domain

This unofficial guide covers student reviews, experiences, and recommendations for Introduction to Graduate Algorithms (CS-6515) at Georgia Tech, the course that arguably has the hardest reputation for the online Master of Science in Computer Science program. Georgia Tech's official course page contains topics, the syllabus, and recommended prerequisites, but lacks the perspectives of students. Things such as the actual difficulty, weekly workload needed, and how to study are not available through official channels but instead the knowledge is provided by students across various sources. This system brings the scattered knowledge together for easy access.

---

## Document Sources

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | omscentral | Review aggregator | https://www.omscentral.com/courses/introduction-to-graduate-algorithms/reviews |
| 2 | reddit (prestudy) | Reddit thread | https://www.reddit.com/r/OMSCS/comments/15kch4o/how_to_effectively_prestudy_for_graduate/ |
| 3 | reddit (experience) | Reddit thread | https://www.reddit.com/r/OMSCS/comments/1osa2qg/how_has_been_your_experience_in_grad_algorithms/ |
| 4 | reddit (reputation) | Reddit thread | https://www.reddit.com/r/OMSCS/comments/vleq4h/cs6515_graduate_algorithms_its_true_what_they_say/ |
| 5 | omshub | Review aggregator | https://www.omshub.org/course/CS-6515 |
| 6 | lowyx blog | Blog | https://lowyx.com/posts/gt-ga/ |
| 7 | takp blog | Blog | https://takp.me/posts/cs-6515-into-to-graduate-algorithms-at-georgia-tech/ |
| 8 | richard lee blog | Blog | https://rich-w-lee.medium.com/tips-to-get-an-a-in-omscs-graduate-algorithms-6bf0af13b4e1 |
| 9 | abhijithc blog | Blog | https://abhijithc.com/blog/2024/05/04/ga-(cs6515)-an-omscs-review.html |
| 10 | etlq blog | Blog | https://etlq.github.io/omscs/ga/ |

---

## Chunking Strategy

**Chunk size:**

There are two chunking strategies depending on source type. omscentral and omshub are review aggregators, so each student review becomes its own chunk. A delimiter in the source files marks where one review ends and the next starts.

The blogs and reddit threads are split by paragraph, with a delimiter between different writers and comments so one chunk never mixes two people. Both modes cap at 256 tokens, which is the limit all-MiniLM-L6-v2 will embed. Anything longer is packed into multiple chunks. A short review or comment stays one chunk, while a long review or blog post becomes several.

**Overlap:**

We have one sentence overlapping between chunks for the paragraph splits on blogs and reddit threads, while still respecting the delimiter between individual comments so overlap is only present when chunks are from the same writer.

**Why these choices fit your documents:**

Our documents consist of two main source types. First we have short student reviews from omshub and omscentral. These make sense as one review per chunk since they are self-contained units within the larger document, and most fit under the 256 token cap or can be split effectively. The other type is more free form paragraphs from comments and blog posts of varying length and styles from different writers. Splitting these by paragraph and holding comment boundaries keeps the chunks focused and relevant.

**Final chunk count:**

1048 chunks across the 10 documents. There are roughly 784 for omscentral, 55 for omshub, 174 for the reddit threads, and 35 for the blogs.

### Sample Chunks

1. **omscentral review** (id omscentral-0001-c0)
   > TL/DR: This course has a reputation of graduation gatekeeping, and while it can be difficult, it is very doable if you are diligent and detail oriented when following course expectations. People will be unkind this course, but I enjoyed it and have some thoughts...

2. **omshub review** (id omshub-0002-c0)
   > While this course isn't perfect, I really enjoyed it. Unfortunately, its shortcomings are amplified by administrative issues. If GA wasn't required for most specializations and wasn't so impacted, I think it would have much better reviews...

3. **reddit-experience comment** (id reddit-experience-0001-c0)
   > I have a bachelors in math and cs I think this format seems pretty easy compared to the expectations I have been given coming into the course. Granted, I am having to take a makeup exam for exam 1...

4. **blog-etlq** (id blog-etlq-0000-c0)
   > My Review of GA (CS6515) Graduate Algorithms Grade: B Difficulty: 10/10 Rating: 8/10 Time commitment: 20 hours/week ------------------------------- Overall It's arguably the hardest course in the program. Not impossible but definitely needs serious time commitment. It's really a theory course...

5. **omscentral course_facts** (id omscentral-0000-c0)
   > Introduction to Graduate Algorithms 3.28 / 5 rating 4.05 / 5 difficulty 19.13 hrs / week Name Introduction to Graduate Algorithms Listed As CS-6515 Credit Hours 3 Available to CS students Description Design and analysis of algorithms on a graduate level, including dynamic programming, divide and conquer, FFT, graph and...

---

## Embedding Model

**Model used:**

We use all-MiniLM-L6-v2 for the embedding model, via sentence-transformers. This was chosen because it runs locally with no API keys required, runs fast, and reads up to 256 tokens per chunk which is large enough to perform well with our content type in documents.

**Production tradeoff reflection:**

If this were a real production deployment with no cost constraints, the first thing to look at would be context length. The 256 token limit forces us to split long reviews and blog sections, even if all of the context is relevant and we wanted it larger. This results in the possibility that a chunk does not contain a complete argument or all the desired detail for later retrieval. A longer context model could hold a full review and longer sections of blog posts in one chunk. Also I'd test a larger or newer model for domain accuracy on the technical language and on the opinion text, MiniLM is a small general-purpose model but bigger models not run locally could retrieve more accurately.

### Retrieval Test Results

Three queries with their top retrieved chunks. The number before each chunk is the cosine distance, lower is a closer match.

**Query: What do students recommend to do in preparation for GA before starting?**

- [1] 0.358 reddit-reputation comment: "I've been preparing for GA for last 2 months and I was really getting worked up if I'd be able to clear this one. Your comments helped me to calm myself down and enter the course with a positive mindset."
- [2] 0.379 reddit-experience comment: "For GA, you can't do that. You need to know beforehand that you should ALWAYS just learn the material, not bump your way through the class."
- [3] 0.379 blog-etlq: "How to prepare for this course (CS 6515)? Be comfortable writing proof. There is a lot of content so start watching the lecture videos to get a sense of what they teach. The best way to prepare for GA is to take GA."

**Query: Is GA as hard as people say?**

- [1] 0.392 reddit-experience comment: "I think GA is a little far along the curve where even understanding it you can really screw yourself with small mistakes."
- [2] 0.405 reddit-reputation comment: "highly unlikely you will get into GA for your first class."
- [3] 0.406 omscentral review: "It is a hard class, but not as hard as many said. I put 8 hours or less on average a week, and ended up with an A."

These are relevant because these are students' opinions on the difficulty of the course, and will vary. Chunk 3 calls it hard but doable with moderate hours, while chunk 1 says it's far along the curve and can really screw yourself with small mistakes. The varied opinions are what this question should pull, since we are looking for the consensus between students not just one factual answer.

**Query: Should I practice LeetCode to prepare for GA?**

- [1] 0.383 omscentral review: "LeetCode problems, even many of the hard ones, feel significantly more manageable after taking this class. I also improved a lot with dynamic programming and graph/tree algorithms."
- [2] 0.413 reddit-prestudy comment: "You only write pseudocode for homework and exams for the first exam material (dynamic programming), so practicing Leetcode style problems only makes sense for dynamic programming."
- [3] 0.423 omscentral review: "If you are a working professional whose background or skill-set does not align much with GA's topics, you WILL need the time to study and prepare adequately for assignments."

These are relevant because chunk 1 directly discusses the benefits/shared topics between Leetcode and GA. Chunk 2 is also directly about LeetCode, noting it only really makes sense for the dynamic programming material since the rest is pseudocode and proofs. Chunk 3 isn't about LeetCode directly, but it talks about preparation methods and being ready for the course which is still relevant to the question asked.

---

## Grounded Generation

**System prompt grounding instruction:**

The model is told to only use the numbered student sources passed in with each request, and not to rely on any training data for any facts or information. The full instructions:

> You are The Unofficial Guide to Georgia Tech's CS-6515 (Introduction to Graduate Algorithms). You answer questions using only the numbered student sources provided in each request.
>
> Rules:
>
> - Use only the information in the provided sources. Do not use any outside or prior knowledge.
> - The sources are student reviews, comments, and blog posts; when they disagree, reflect the range of views instead of inventing a single fact.
> - If the sources do not contain enough information to answer the question, reply with exactly this sentence and nothing else: I don't have enough information on that.
> - Do not guess or fill gaps from general knowledge.

In addition there are two structural choices that help with grounding. First, the chunks go in as a numbered, labeled block so the model only sees what was already retrieved and bases its output on that. Second, providing a specific sentence to fall back on when the sources don't cover the question gives the model an explicit out. Models are trained to be helpful, and might still try to answer without sources if they think that is what the user wants. Providing the exact alternative path encourages them not to answer beyond the retrieved documents.

**How source attribution is surfaced in the response:**

Attribution is built in the Python code from the retrieved chunks' metadata, not written by the model in its response. After the model answers, generate() walks the same chunks that went into the prompt, dedupes them by source and position, and returns a Sources list with entries like omscentral review (Fall 2020) and reddit-experience comment. When the model refuses a question it can't answer from the sources, that list is dropped, so an unanswerable question shows the plain refusal instead of a misleading set of unrelated sources.

The list comes from the retrieval pipeline and not the model, so the sources are always pulled from the real document metadata instead of relying on the model to transcribe each source it used. This helps models of any size. It lets them focus on generating an answer grounded in the sources, instead of spending extra tokens tracking which sources went into their reasoning and trying to reliably list them all in the output.

### Example Responses

**Example 1**

> **Question:** Is GA as hard as people say?
>
> **Answer:** According to the sources, opinions on the difficulty of GA vary. One reviewer from omscentral (Fall 2020) states that it's "a hard class, but not as hard as many said" and was able to achieve an A with relatively less effort compared to other classes. In contrast, another omscentral review (Spring 2024) advises not to underestimate the course and warns that it can be tough, especially for those without a relevant background. Reddit comments also reflect this range of views, with one comment (7mo ago) suggesting that GA requires a deeper understanding of the material to pass, while another comment (4y ago) implies that it's a challenging class by stating it's "highly unlikely" to be taken as a first class. Overall, the sources indicate that GA can be a difficult course, but the level of difficulty may vary depending on individual backgrounds and preparation.
>
> **Sources:**
> - reddit-experience comment (era 7mo ago)
> - reddit-reputation comment (era 4y ago)
> - omscentral review (Fall 2020)
> - omscentral review (Spring 2024)

**Example 2**

> **Question:** Should I practice LeetCode to prepare for GA?
>
> **Answer:** According to the sources, practicing LeetCode can be helpful, especially for dynamic programming. Source [1] mentions that LeetCode problems feel more manageable after taking the class, and source [2] suggests that practicing LeetCode style problems makes sense for dynamic programming. However, source [2] also notes that you only write pseudocode for homework and exams for the first exam material, so LeetCode practice may not be as relevant for other topics. Overall, it seems that LeetCode practice can be beneficial, but it's not the only way to prepare for GA, and other study methods, such as watching lectures and taking notes, may also be effective.
>
> **Sources:**
> - omscentral review (Spring 2026)
> - reddit-prestudy comment (era 3y ago)
> - omscentral review (Spring 2024)
> - reddit-reputation comment (era 4y ago)
> - omscentral review (Fall 2020)

**Out-of-scope refusal**

> **Question:** Which dining hall at Georgia Tech has the best food?
>
> **Answer:** I don't have enough information on that.

The dining question only pulls far matches, around 0.62 to 0.68, and the system declines instead of guessing.

---

## Query Interface

The interface is a Gradio web app in app.py. Run it with `python app.py` and open http://localhost:7860.

There is one input and two outputs. The input is a text box for the question, with an Ask button to submit, and pressing Enter in the box does the same thing. The first output is the answer from the model. The second is the list of sources the answer drew from, built from the retrieved chunks. On a refusal that box shows a short note instead of a source list.

Sample interaction:

> **Your question:** How many hours per week do students usually spend on GA?
>
> **Answer:** According to the sources, the number of hours per week students spend on GA varies. One student reported spending 8 hours or less per week and ended up with an A [1]. Another source suggests that 10-15 hours per week is required, but it can go up to 20-25 hours per week for those not familiar with the concepts [2]. A third student spent 30 hours a week, which they considered overkill, and suggested that 15-20 hours is sufficient for a B [4].
>
> **Sources:**
> - omscentral review (Fall 2020)
> - blog-abhijithc blog
> - reddit-experience comment (era 7mo ago)
> - reddit-prestudy comment (era 3y ago)

---

## Evaluation Report

Ran with k=5 against Groq llama-3.3-70b-versatile. I judged retrieval from the cosine distances and whether the top chunks were actually on topic.

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | How many hours per week do students usually spend on GA? | Around 20-30+ hours depending on student's algorithms background | Gives a range: one student under 8 hrs for an A, others 10-15 up to 20-25, another 15-20 for a B and 30 personally | Relevant (0.45-0.47) | Accurate. Reflects the real spread in the corpus rather than a single number |
| 2 | What do students recommend to do in preparation for GA before starting? | Review the course's textbooks, understand math and dsa fundamentals. | Be comfortable with proofs, watch lectures early, review an undergrad algorithms course, commit real time during the term | Relevant (0.36-0.39, closest of the set) | Accurate |
| 3 | Is GA as hard as people say? | Mixed reports. Many call it brutal and stressful, others say it is manageable and fair if you keep up with homework and practice problems | Opinions vary: some say not as hard as claimed, others warn not to underestimate it | Relevant (0.39-0.45) | Accurate |
| 4 | Should I practice LeetCode to prepare for GA? | No, LeetCode is more about implementing to solve specific puzzles, and GA is about theory and proof-writing. | Says LeetCode can help for dynamic programming, but homework and exams are pseudocode and proofs, so it is not the main prep | Relevant (0.38-0.45) | Partially accurate, softer than the expected flat no and leans toward helps for DP |
| 5 | What is the most difficult subject or topic in GA? | Often the proofs and max-flow/NP material, but all of it can be difficult if not studied and practiced. | Refused, returned the set message I don't have enough information on that. | Off-target (0.49-0.50, general-difficulty reviews, none topic-specific) | Inaccurate by omission, an honest refusal but no answer (see Failure Case) |

**Retrieval quality:** Relevant for Q1-Q4, Off-target for Q5
**Response accuracy:** Accurate for Q1-Q3, Partially accurate for Q4, refusal for Q5

---

## Failure Case Analysis

**Question that failed:**

What is the most difficult subject or topic in GA?

**What the system returned:**

I don't have enough information on that. (refusal).

**Root cause (tied to a specific pipeline stage):**

This is a retrieval failure. The five retrieved chunks are general difficulty reviews, lines like "It's a tough course" or "do not underestimate this course", sitting at cosine distance 0.49 to 0.50. That is close to where matches start getting weak, and none of them name a specific hardest topic. The question embeds near broad "GA is difficult" language, not near the scattered mentions of max-flow, NP, or proofs that show up across many separate reviews. Because we chunk one review per chunk, those topic opinions are spread thin, so no single chunk says "the hardest topic is X". With nothing in the retrieved set to ground an answer, the model refused instead of making one up. So the refusal is the grounding doing its job, and the miss is in retrieval, not generation.

**What you would change to fix it:**

Raise k so more chunks get a chance to surface a topic-specific mention, or add a keyword (BM25) pass over terms like max flow, NP, and proofs to pull the topic sentences that semantic search watered down. Hybrid search like that is one of the listed stretch features. Rewording the question toward a concrete topic helps too, but the real fix is on the retrieval side.

---

## Spec Reflection

**One way the spec helped you during implementation:**

The two-mode chunking decision in planning.md shaped the whole ingestion script. I had already split the self-contained reviews from the looser blog and reddit text in the spec, so going into the code I knew the shape I was building. One review per chunk for the aggregators, and paragraph splitting with a one sentence overlap for the blogs and reddit, all under the 256 token cap. Because that was settled up front, I built ingest.py straight to that plan instead of writing something generic and reworking it once I saw bad retrieval.

**One way your implementation diverged from the spec, and why:**

The spec said the answer should include its sources but never said how to produce them. The natural reading was that the model would write the sources into its response along with the answer. The build went a different way. Instead of trusting the model to list what it used, the code builds the source list itself from the retrieval metadata, so the sources are always the real chunks behind the answer and a citation can't be made up. I went this way because a model writing its own citations can invent one or drop a source it actually used, and the whole point of this system is that the answer stays grounded and traceable.

---

## AI Usage

### Instance 1

- *What I gave the AI:*
  The Domain, Documents, and Chunking Strategy sections of planning.md plus the architecture diagram, and asked it to implement load_documents() and chunk_text() with the two-mode strategy and 256-token cap.
- *What it produced:*
  ingest.py with the loader, per-source delimiters, and the sentence-packing chunker.
- *What I changed or overrode:*
  I directed the two-mode chunking instead of one splitter, one review per chunk for omscentral and omshub and paragraph splitting for the blogs and reddit. I set the per-source delimiters myself (date plus semester for omscentral, the SEMESTER line for omshub, username and timestamp for reddit), had it defer the reddit per-comment cleanup to the script instead of me stripping it by hand, and required scalar-only metadata so ChromaDB would accept it.

### Instance 2

- *What I gave the AI:*
  planning.md, the architecture diagram, and the existing M3/M4 code, and asked it in plan mode to implement generate() with a grounding prompt and a Gradio UI.
- *What it produced:*
  A plan that surfaced four design choices (file split, grounding method, attribution format, UI scope), then generate.py and app.py once I chose.
- *What I changed or overrode:*
  I chose prompt-only grounding with no distance gate, specifically so weakly retrieved questions still get a shot at an answer instead of being silently refused by a threshold. I also chose the programmatic Sources-list attribution, built in Python from the retrieval metadata, over having the model write inline citations, so the sources can't be hallucinated.