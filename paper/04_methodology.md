# 3. Methodology

*[Target: 3–4 pages. This is the longest and most important section for a CS-journal submission.]*

## 3.1 Overall Architecture

The MDT-LLM framework (Figure 1) is organized around three components: a **multi-agent orchestration layer** that simulates the role structure of a clinical multidisciplinary team, a **retrieval-augmented generation pipeline** that grounds agent outputs in current clinical guidelines, and a **multi-judge evaluation layer** that scores outputs against gold-standard reference answers.

Formally, given an input clinical scenario $q$ consisting of a patient vignette and a treatment-planning question, the framework produces a final response $\hat{y}$ via:

$$
\hat{y} = M\left(q,\ \{A_i(q, R(q))\}_{i=1}^{N},\ R(q)\right)
$$

where $A_i$ denotes the $i$-th specialist agent, $R(q)$ is the retrieval function returning relevant guideline chunks, and $M$ is the moderator agent that synthesizes the $N=4$ specialist outputs into a single consensus. Under ablation conditions, either $\{A_i\}$ (single-agent baseline) or $R$ (zero-shot baseline) is removed.

## 3.2 Multi-Agent MDT Design

### 3.2.1 Role Selection

The four specialist roles were selected to match the minimum composition of a thoracic oncology MDT as specified in the **NCCN Clinical Practice Guidelines in Oncology: Non-Small Cell Lung Cancer** [NCCN-NSCLC] and institutional tumor-board practices at major cancer centers:

| Agent | Role | Primary Responsibility |
|-------|------|------------------------|
| $A_1$ | Medical Oncologist | Systemic therapy (cytotoxic, targeted, immunotherapy) |
| $A_2$ | Thoracic Surgeon | Surgical candidacy, operability, perioperative considerations |
| $A_3$ | Radiation Oncologist | Definitive, adjuvant, palliative, stereotactic radiotherapy |
| $A_4$ | Pathologist / Molecular Specialist | Histologic subtyping, molecular biomarker interpretation |

Each agent is instantiated by prompting the underlying LLM with a **role-specific system message** specifying credentialing (board certification), experience level (15 years in thoracic oncology), and a directive to analyze the case from that discipline's perspective. Complete prompt templates are provided in Appendix A.

### 3.2.2 Two-Phase Orchestration

**Phase 1: Independent Specialist Opinions.** The four agents receive the clinical scenario *in parallel* and produce independent analyses. Critically, specialists *cannot see each other's outputs* at this phase—this design choice mirrors the pre-meeting preparation in real-world MDT, where each specialist reviews the case independently before the meeting. It avoids premature consensus and preserves perspective diversity.

**Phase 2: Moderator Synthesis.** A fifth agent $M$, configured as the MDT coordinator, receives all four specialist opinions concatenated with the original clinical scenario. Its system prompt directs it to: (1) state the agreed treatment plan with specific drugs, doses, and schedules where applicable; (2) explicitly surface any points of disagreement among specialists and describe their resolution; (3) specify follow-up and monitoring recommendations; and (4) cite relevant guidelines.

### 3.2.3 Homogeneous vs. Heterogeneous Agents

In this study we use a **homogeneous multi-agent configuration**: all five agents are instantiated from the same underlying LLM, differentiated only by role-specific system prompts. This design isolates the effect of role-specialized prompting from the effect of model-level heterogeneity, and enables a fair factorial comparison against single-agent baselines (where the same underlying LLM is used in single-role configuration). Heterogeneous configurations in which different underlying LLMs serve different specialist roles are reserved as future work.

## 3.3 Retrieval-Augmented Generation Pipeline

### 3.3.1 Corpus

The retrieval corpus consists of the four NCCN clinical practice guideline documents most relevant to the benchmark scope:

1. **NCCN Guidelines for Non-Small Cell Lung Cancer**, version 5.2026 (NSCLC)
2. **NCCN Guidelines for Small Cell Lung Cancer**, version 2.2026 (SCLC)
3. **NCCN Guidelines for Lung Cancer Screening**, version 2.2026
4. **NCCN Guidelines for Management of Immune Checkpoint Inhibitor-Related Toxicities**, version 1.2026

Total corpus: **618 pages** of PDF content, loaded and parsed using PyMuPDF [Artifex-PyMuPDF].

### 3.3.2 Preprocessing and Chunking

Documents are segmented using the `RecursiveCharacterTextSplitter` algorithm, which recursively splits on a hierarchy of separators (`\n\n`, `\n`, `. `, ` `, ``) to preserve semantic boundaries:

- **Chunk size:** 512 characters
- **Chunk overlap:** 128 characters
- **Total chunks produced:** 6,252

Chunk size was selected as a balance between retrieval precision (favoring smaller chunks) and context coherence (favoring larger chunks), based on pilot experiments and prior findings [Gao2024-RAG-Survey].

### 3.3.3 Embedding and Indexing

Each chunk is embedded using **OpenAI `text-embedding-3-large`** (3,072-dimensional dense vectors). The embedding choice reflects two considerations: (1) `text-embedding-3-large` has demonstrated strong performance on the MTEB medical subset [MTEB], and (2) its context window (8,192 tokens) exceeds our chunk size by an order of magnitude, avoiding truncation.

Chunks are indexed using **FAISS** [Johnson2019-FAISS] with a flat inner-product index (`IndexFlatIP`). Given the moderate corpus size (6,252 vectors × 3,072 dim = ~77 MB), exact search is preferred over approximate variants.

### 3.3.4 Retrieval at Inference Time

At query time, the input scenario $q$ is embedded using the same embedding model and the top-$k$ most similar chunks are retrieved, where $k=5$. The retrieved chunks are concatenated with explicit source attribution (filename and page number) and injected into the agent's user message under an "retrieved guideline excerpts" header. The concatenated retrieval context is shared across all four specialist agents and the moderator in RAG conditions.

## 3.4 LungMDT-Bench-100: Benchmark Construction

### 3.4.1 Design Principles

LungMDT-Bench-100 was constructed to satisfy four design criteria:

1. **Clinical realism.** Every scenario is phrased as a realistic patient presentation a clinician might encounter, not an abstract factual query.
2. **Guideline groundedness.** Every gold-standard answer is traceable to a specific NCCN section, enabling reviewers to verify correctness independently.
3. **Taxonomic coverage.** Scenarios span the full clinical pathway from screening through terminal-line management and survivorship.
4. **Difficulty stratification.** Each scenario is rated Easy, Medium, or Hard based on the complexity of reasoning required and the level of expert knowledge involved.

### 3.4.2 Composition

The benchmark contains **100 scenarios** structured across 6 clinical domains × 3 difficulty levels (Table 1):

**Table 1.** Composition of LungMDT-Bench-100 (domain × difficulty).

| Domain | Easy | Medium | Hard | Total |
|--------|-----:|-------:|-----:|------:|
| D1: Diagnosis / Screening | 5 | 6 | 6 | 17 |
| D2: Staging / Molecular | 4 | 6 | 5 | 15 |
| D3: First-line Therapy | 4 | 8 | 8 | 20 |
| D4: Subsequent / Resistance | 3 | 8 | 5 | 16 |
| D5: Adverse Events | 5 | 7 | 5 | 17 |
| D6: Follow-up | 4 | 6 | 5 | 15 |
| **Total** | **25** | **41** | **34** | **100** |

### 3.4.3 Annotation Protocol

Each scenario was drafted and annotated by a board-certified thoracic oncology specialist [author initials to be added], following a four-step process:

1. **Scenario drafting:** patient vignette (age, sex, smoking history, relevant comorbidities, molecular/pathologic findings, performance status) followed by a single focused clinical question.
2. **Gold-standard drafting:** reference answer grounded in the current NCCN section, citing specific trial data and category of recommendation.
3. **Cross-verification:** each gold-standard answer was independently verified against NCCN v5.2026 PDFs at the time of benchmark freezing (April 2026).
4. **Difficulty rating:** assigned based on a three-level rubric: *Easy* = single guideline lookup; *Medium* = integration of multiple guideline facts or clinical parameters; *Hard* = multi-step reasoning involving conflicting considerations, emerging evidence, or frailty/special populations.

Each item in the benchmark is stored with the following fields: `id`, `domain`, `difficulty`, `vignette`, `question`, `gold_standard_answer`, `guideline_reference`.

## 3.5 LLM-as-Judge Evaluation Protocol

### 3.5.1 Judge Selection

Two judges from distinct providers are used to reduce single-vendor bias:

| Judge | Model | Provider | Rationale |
|-------|-------|----------|-----------|
| $J_1$ | GPT-4o-mini (2024-07-18) | OpenAI | Cost-efficient proprietary model |
| $J_2$ | Claude Sonnet 4.5 (2025-09-29) | Anthropic | Frontier proprietary model from different provider |

Both judges receive identical prompts (Appendix C).

### 3.5.2 Scoring Rubric

Each candidate response is scored on **four ordinal dimensions** (1–5 Likert scale) and **two binary flags**:

- **Accuracy** (1–5): Factual correctness of recommendations vs. gold standard.
- **Completeness** (1–5): Coverage of key clinical points in the gold standard.
- **Safety** (1–5): Absence of potentially harmful recommendations.
- **Concordance** (1–5): Alignment with current NCCN/ESMO/ASCO guidelines.
- **Hallucination** (0/1): Presence of any fabricated facts (trial names, doses, mechanisms).
- **Safety Violation** (0/1): Presence of any recommendation that could directly cause patient harm.

Anchor descriptions for each scale point are provided in the judge prompt (Appendix C). Judges are explicitly instructed to avoid being influenced by response length or formatting, focusing on clinical correctness and safety.

### 3.5.3 Output Format and Parsing

Judges output a single JSON object with the six scores plus a one- to two-sentence free-text `rationale` explaining key scoring decisions. Responses are parsed via regex-anchored JSON extraction, with automatic retry and schema validation.

### 3.5.4 Inter-Judge Reliability

For each scoring dimension, we compute **Cohen's weighted κ** [Cohen1968] between the two judges across all model-condition-question combinations, with quadratic weights reflecting the ordinal nature of the 1–5 scale. An overall κ is also computed by concatenating all ordinal dimensions. Values of κ ≥ 0.60 are considered substantial agreement; ≥ 0.80 almost perfect.

### 3.5.5 Ensemble Scoring

For all downstream analyses, we report the **mean across judges** as the effective score per (question, model, condition) triple, with 95% confidence intervals computed via bootstrap resampling ($n = 1{,}000$ resamples at the question level).

## 3.6 Implementation Details

### 3.6.1 Software Stack

- **Language:** Python 3.13
- **LLM clients:** `openai` (v2.32), `anthropic` (v0.95)
- **Retrieval:** `langchain_community`, `langchain_text_splitters`, `faiss-cpu` (v1.13)
- **PDF parsing:** `pymupdf` (v1.27)
- **Analysis:** `pandas`, `scikit-learn` (for κ computation), `scipy.stats` (for Wilcoxon), `matplotlib`, `seaborn`

### 3.6.2 Hyperparameters

| Parameter | Value |
|-----------|-------|
| Temperature (all LLM calls) | 0 |
| Max tokens per call | 1024 |
| RAG top-$k$ | 5 |
| Chunk size (characters) | 512 |
| Chunk overlap | 128 |
| Judge count | 2 |

### 3.6.3 Reproducibility

All API calls use temperature 0 for maximal determinism. The benchmark CSV, agent system prompts, judge prompt, and FAISS index (with embedding cache) are released as supplementary materials. Given the stochastic remainders of LLM decoding at temperature 0, we report results from a single pass; small fluctuations (< 2% on main metrics) are expected across re-runs.
