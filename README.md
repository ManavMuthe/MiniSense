# MiniSense — Multi-Agent Survey Analysis System

MiniSense is a survey analysis system that combines structured data analysis, semantic FAQ retrieval, period-over-period comparisons, and evidence-based answer generation. It helps businesses understand customer satisfaction, identify recurring feedback themes, compare performance across time periods, and retrieve relevant operational policies.

The project demonstrates a modular multi-agent architecture in which an orchestrator coordinates specialized agents and combines their results into a single response.

## 1. Key Features

- **Survey metrics:** Calculate response counts, Customer Satisfaction Score (CSAT), average ratings, and common feedback themes.
- **Semantic FAQ retrieval:** Search a local FAQ knowledge base using sentence embeddings and ChromaDB.
- **Period comparison:** Compare survey metrics between two periods and calculate changes.
- **Multi-agent orchestration:** Route business questions to specialized agents and combine their outputs.
- **Evidence-based answers:** Use retrieved FAQ content to answer supported policy questions.
- **Synthetic dataset:** Generate 50,000 survey responses covering May and June 2026.
- **Automated tests:** Validate metric calculations and agent behavior using pytest.

## 2. Architecture

The system uses four specialized agents coordinated by an orchestrator.

```text
                         Business Question
                                |
                                v
                       +------------------+
                       |   Orchestrator   |
                       +------------------+
                          |      |      |
               +----------+      |      +-----------+
               |                 |                  |
               v                 v                  v
        +-------------+  +---------------+  +-------------+
        | DataAgent   |  | ComparisonAgent|  |  RAGAgent   |
        +-------------+  +---------------+  +-------------+
               |                 |                  |
               v                 v                  v
        Survey Dataset     Period Metrics       FAQ Retrieval
               |                 |             ChromaDB +
               +-----------------+             Embeddings
                          |
                          v
                   +--------------+
                   | SummaryAgent |
                   +--------------+
                          |
                          v
                  Final Business Answer
```

### Agent Responsibilities

**Orchestrator**
- Receives the business question.
- Determines which analysis tasks to execute using rule-based routing.
- Passes structured task specifications to the appropriate agents.
- Collects their outputs and invokes the SummaryAgent.

**DataAgent**
- Loads survey responses from the dataset.
- Filters records by date and business when requested.
- Calculates response counts, CSAT, average ratings, and feedback themes.
- Uses reusable metric functions rather than embedding calculations directly into the agent.

**ComparisonAgent**
- Analyzes two periods independently using the DataAgent.
- Calculates absolute differences in response counts, CSAT, and average ratings.
- Returns structured comparison results for further interpretation.

**RAGAgent**
- Retrieves FAQ chunks relevant to a business question.
- Uses sentence-transformer embeddings and a persistent ChromaDB collection.
- Returns retrieved text, source metadata, chunk identifiers, and similarity distances.

**SummaryAgent**
- Produces a question-specific response from structured metrics and retrieved FAQ evidence.
- Uses deterministic rules to answer supported operational policy questions.
- Provides a general metric summary when no supported policy rule matches.

> **Implementation note:** The current SummaryAgent is deterministic and rule-based. It does not use an LLM to generate responses. The architecture can be extended to use an LLM for more flexible planning and answer synthesis.

## 3. Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application development |
| uv | Dependency and environment management |
| Pandas | Dataset analysis and processing |
| Pydantic | Structured task and result schemas |
| Sentence Transformers | Semantic text embeddings |
| ChromaDB | Persistent vector storage and retrieval |
| NumPy | Numerical operations |
| Pytest | Automated testing |

## 4. Project Structure

```text
minisense/
├── main.py
├── app/
│   ├── __init__.py
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── orchestrator.py
│   │   ├── data_agent.py
│   │   ├── rag_agent.py
│   │   ├── comparison_agent.py
│   │   └── summary_agent.py
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── ingestion.py
│   │   └── retrieval.py
│   ├── tools/
│   │   ├── __init__.py
│   │   └── metrics.py
│   └── schemas.py
├── data/
│   ├── survey_responses.json
│   ├── product_faq.txt
│   └── rag_evaluation_results.json
├── scripts/
│   ├── generate_data.py
│   ├── test_data_agent.py
│   ├── ingest_faq.py
│   ├── test_rag_agent.py
│   ├── test_comparison_agent.py
│   ├── test_orchestrator.py
│   └── evaluate_rag.py
├── tests/
│   ├── test_metrics.py
│   └── test_summary_agent.py
├── pyproject.toml
├── uv.lock
├── .gitignore
└── README.md
```

The structure above describes the expected project layout. Files such as `main.py`, `.env.example`, or `uv.lock` should be included only if they actually exist in your working directory.

## 5. Setup

### Prerequisites

- Python 3.11 or newer
- uv package manager
- Internet access for the initial download of the sentence-transformer model

### Install Dependencies

From the project root, run:

```cmd
uv sync
```

This installs the dependencies defined in `pyproject.toml`.

### Generate the Synthetic Dataset

If you need to regenerate the survey dataset, run:

```cmd
uv run python -m scripts.generate_data
```

The dataset generator creates synthetic survey responses across two months. The generated data is intended for development and evaluation, not as a representation of actual customer behavior.

### Ingest the FAQ

Build or update the local FAQ vector collection:

```cmd
uv run python -m scripts.ingest_faq
```

This process reads the FAQ, splits it into overlapping text chunks, generates embeddings, and stores the results in ChromaDB.

The initial execution downloads the configured embedding model if it is not already available locally.

### Run the RAG Evaluation

```cmd
uv run python -m scripts.evaluate_rag
```

The evaluation runs three sample questions, prints the retrieved FAQ chunks and final answers, and saves the results to:

```text
data/rag_evaluation_results.json
```

### Run Individual Agent Tests

```cmd
uv run python -m scripts.test_data_agent
uv run python -m scripts.test_rag_agent
uv run python -m scripts.test_comparison_agent
uv run python -m scripts.test_orchestrator
```

### Run Automated Tests

```cmd
uv run python -m pytest -v
```

## 6. Survey Metrics

### Response Count

Counts the valid survey responses in the selected dataset after filtering.

### CSAT

Customer Satisfaction Score is calculated as the percentage of valid ratings that are 4 or 5 on a five-point scale.

**Formula:**

CSAT (%) = (Number of ratings >= 4 / Number of valid ratings) × 100

### Average Rating

Calculates the arithmetic mean of valid ratings on the five-point scale.

### Feedback Themes

The current baseline theme detector uses keywords in free-text responses to identify themes such as food quality, waiting time, staff behavior, cleanliness, pricing, and order accuracy.

This method is intentionally simple and interpretable. It can miss synonyms, context, negation, and subtle sentiment. Theme counts should therefore be treated as approximate indicators rather than definitive classifications.

## 7. RAG Design and Evaluation

The retrieval pipeline uses the `sentence-transformers/all-MiniLM-L6-v2` embedding model and ChromaDB with cosine-distance-based retrieval.

The FAQ is split into overlapping character-based chunks. Each chunk is embedded and stored with source metadata. For an incoming question, the system embeds the question and retrieves up to three relevant chunks.

### Sample Evaluation Questions

| Question | Expected policy information |
|---|---|
| How quickly must a customer complaint be escalated? | Escalation within 15 minutes |
| What waiting times should customers expect during busy periods? | Approximately 15–20 minutes during peak periods |
| What CSAT score triggers a root-cause review? | Scores below 4.0 trigger a review; the business target is 4.5 or higher |

The evaluation script records the retrieved text and the final answer for each question. This allows retrieval quality to be examined separately from answer quality.

### Strengths

- Retrieval is performed locally using a persistent vector database.
- Semantic embeddings can retrieve relevant content even when the question differs from the FAQ wording.
- The final answer rules can extract important policy details from retrieved evidence.
- Saved evaluation results make manual inspection repeatable.

### Limitations

- Only three manually selected questions are currently evaluated.
- Character-based chunking can split sentences or related information across chunks.
- A low cosine distance indicates embedding similarity, not guaranteed factual correctness.
- The current evaluation does not calculate formal retrieval precision, recall, or answer-grounding scores.
- The SummaryAgent uses fixed rules and does not generalize to arbitrary questions in the way a capable language model might.

## 8. Example Period Comparison

The synthetic dataset was generated for May and June 2026. An observed run produced the following comparison:

| Metric | May 2026 | June 2026 | Change |
|---|---:|---:|---:|
| Responses | 25,246 | 24,754 | -492 |
| CSAT | 51.48% | 50.32% | -1.16 percentage points |
| Average rating | 3.34 | 3.30 | -0.04 |

These values are from the current synthetic dataset and should be reproducible when the dataset and calculation logic remain unchanged.

The results show a modest decline in satisfaction metrics between the two periods. They do not establish the cause of that decline. Further investigation should examine feedback themes, business-level differences, response channels, and operational context.

## 9. Proposed Fine-Tuning Strategy

The current implementation does not train or fine-tune a language model. The following is a proposed approach for a future version that needs more reliable classification, routing, and evidence-grounded answer generation.

### Dataset Strategy

Create a curated dataset from historical survey comments, business questions, verified operational policies, and human-reviewed responses. Remove personal information and sensitive customer details before training. Include examples covering positive and negative sentiment, mixed feedback, ambiguous requests, common complaint themes, policy questions, and cases where the available evidence is insufficient.

Begin with approximately 3,000–5,000 carefully labeled examples for a pilot. Expand to 10,000–20,000 or more examples if evaluation results indicate that additional training data improves performance. Split the dataset into training, validation, and test sets, ensuring that near-duplicate examples do not leak across splits.

### Model and Fine-Tuning Approach

Start with a capable open-weight instruction model suitable for the available hardware and deployment constraints. Establish a baseline using prompt engineering and retrieval-augmented generation before fine-tuning. For the initial experiment, use LoRA (Low-Rank Adaptation) to train a small number of additional parameters while keeping the base model frozen. If GPU memory is limited, consider QLoRA, which uses a quantized base model to reduce memory requirements. Full fine-tuning can be evaluated later if parameter-efficient approaches do not meet quality targets.

### Training Pipeline and Evaluation

Use Hugging Face Transformers and PEFT to prepare the model, configure adapters, and run supervised fine-tuning. Version the datasets, prompts, model configurations, and evaluation results so experiments remain reproducible.

Evaluate the model on a held-out dataset using classification F1 scores, routing accuracy, answer relevance, factual consistency with retrieved evidence, and correct abstention when evidence is insufficient. Compare every fine-tuned version against the original model and the current rule-based implementation. Include human review of a representative sample of generated answers. Do not deploy a model solely because its training loss decreases.

### Serving and Future Maintenance

Deploy the selected model with its adapter in a versioned inference service. Keep retrieval, deterministic metric calculations, and business policy validation separate from model generation. This separation reduces the risk of a language model inventing numerical results or operational policies. Re-evaluate performance whenever the FAQ, dataset, base model, or adapter changes.

## 10. Future Improvements

- Replace keyword-based orchestration with an LLM planner that emits validated task specifications.
- Add more robust theme classification, including sentiment, negation, and multi-label evaluation.
- Support user-defined comparison periods instead of fixed May–June dates.
- Improve chunking and evaluate retrieval using precision@k, recall@k, and manually verified relevance labels.
- Add answer-grounding checks and explicit abstention when retrieved evidence is insufficient.
- Expose the analysis pipeline through a documented API and add input validation, logging, and error handling.
- Expand automated tests to cover retrieval failures, invalid questions, missing data, and unexpected agent outputs.

## 11. Design Principles

MiniSense separates deterministic calculations from semantic retrieval and answer synthesis. Metric functions provide reproducible numerical results, Pydantic schemas help validate structured data, and the RAG pipeline supplies operational context from the FAQ. The orchestrator coordinates these components without requiring every task to use a language model.

The current implementation is a prototype built around synthetic survey data. Its reported metrics demonstrate the pipeline's behavior on that dataset and should not be interpreted as real business findings. The fine-tuning strategy describes future work; no model has been fine-tuned as part of the current implementation.