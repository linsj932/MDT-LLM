# MDT-LLM Paper Outline

**Target Journal:** Journal of King Saud University - Computer and Information Sciences (JKSUCIS)
**IF:** 6.9 (JCR Q1) | Elsevier Open Access | Word limit: ~8000-10000 words

---

## Title

**MDT-LLM: A Multi-Agent Large Language Model Framework with Retrieval-Augmented Generation for Lung Cancer Multidisciplinary Decision Support**

Shorter variant for running head: *MDT-LLM: Multi-Agent LLM for Clinical Decision Support*

---

## Authors (TBD)

- [Your name], [Institution] — first author
- [Dr. Hao], [Institution] — clinical co-author / corresponding
- [Advisor], [Institution] — senior author

---

## Abstract (≤250 words, structured)

**Background.** Large Language Models (LLMs) have shown promise in medical question answering, yet single-agent deployments suffer from hallucination, narrow reasoning perspectives, and limited adherence to evolving clinical guidelines. In high-stakes domains such as oncology, a single LLM cannot replicate the collaborative reasoning of a multidisciplinary clinical team.

**Methods.** We propose **MDT-LLM**, a multi-agent framework that simulates a clinical multidisciplinary team (MDT) using four role-conditioned specialist agents (medical oncologist, thoracic surgeon, radiation oncologist, pathologist) and a moderator agent that synthesizes a consensus recommendation. The framework integrates a retrieval-augmented generation (RAG) pipeline over the current NCCN clinical guidelines, built with FAISS and dense embeddings. We benchmark MDT-LLM against single-agent baselines across four frontier LLMs (GPT-4o-mini, Claude Sonnet 4.5, DeepSeek-R1, Llama-3.3-70B) on a curated benchmark of 100 lung cancer clinical scenarios (LungMDT-Bench-100) spanning six clinical domains and three difficulty levels. We further introduce a multi-judge LLM-as-judge evaluation protocol (n=2 judges, with inter-judge reliability analysis) scoring responses on four dimensions.

**Results.** Unexpectedly, retrieval augmentation significantly *reduced* score in strong LLMs (Claude Δ=−0.29, DeepSeek Δ=−0.32, both Bonferroni-corrected p<0.002, medium effect) — a finding robust across retrieval depths k ∈ {1, 3, 5, 10}. Multi-agent MDT produced modest non-significant gains overall, with significant benefit for Claude on Easy questions (Δ=+0.23, p=0.023, medium effect). A heterogeneous MDT, assigning four different LLMs to four specialty roles, achieved parity with the best homogeneous configuration (4.73 vs 4.76) at approximately 32% lower cost. Inter-judge reliability was substantial on factual dimensions (accuracy κ=0.70, concordance κ=0.68) but poor on safety judgment (κ=0.21). Error analysis identified recommending immunotherapy when an actionable driver mutation is present in 8.5% of low-scoring outputs.

**Conclusion.** MDT-LLM demonstrates that multi-agent orchestration combined with guideline-grounded retrieval yields substantial and reproducible gains over single-agent LLMs in complex clinical reasoning. We release the framework and benchmark to support future research.

**Keywords:** Large Language Models · Multi-Agent Systems · Retrieval-Augmented Generation · Clinical Decision Support · Multidisciplinary Team · Lung Cancer · Benchmark

---

## 1. Introduction

### 1.1 Motivation
- LLMs are increasingly applied to clinical decision support, but generalist LLMs have documented weaknesses: factual hallucination, outdated training knowledge, single-perspective reasoning.
- Clinical reasoning is inherently multidisciplinary: complex cancer cases require input from medical oncology, surgery, radiation oncology, and pathology. A single LLM "specialist" cannot replicate this reasoning structure.
- Two parallel research directions have emerged: **(i)** Retrieval-Augmented Generation (RAG) to ground LLM outputs in authoritative knowledge sources, and **(ii)** Multi-agent LLM systems to simulate collaborative reasoning. Their combination remains under-explored in high-stakes clinical settings.

### 1.2 Research Questions
- **RQ1:** Does a multi-agent MDT framework improve clinical decision quality over single-agent LLM baselines?
- **RQ2:** What is the marginal contribution of retrieval augmentation over parametric knowledge?
- **RQ3:** Are the benefits consistent across LLMs of varying capability, across clinical domains, and across difficulty levels?
- **RQ4:** Is LLM-as-judge evaluation reliable for such complex open-ended tasks?

### 1.3 Contributions
1. **MDT-LLM framework** — an open-source multi-agent architecture simulating clinical MDT with 4 specialist roles + a moderator, combined with a RAG pipeline over clinical guidelines.
2. **LungMDT-Bench-100** — a new benchmark of 100 expert-curated lung cancer clinical scenarios annotated with gold-standard guideline-concordant answers (6 clinical domains × 3 difficulty levels).
3. **Multi-judge LLM evaluation protocol** — scoring 4 frontier LLMs across 4 conditions (2×2: single/MDT × zero-shot/RAG) with 2 LLM judges and inter-judge reliability analysis.
4. **Empirical insights** — [will fill after experiments]

### 1.4 Paper Organization
...

---

## 2. Related Work

### 2.1 LLMs for Clinical Decision Support
- Med-PaLM / Med-PaLM 2 (Singhal 2022, 2023)
- GPT-4 in medical licensing (Nori 2023)
- Clinical decision support studies (2024–2025)
- **Gap:** most prior work evaluates LLMs as single agents on QA-style benchmarks (MedQA, MedMCQA), not complex case-level multidisciplinary decisions.

### 2.2 Retrieval-Augmented Generation
- RAG origins (Lewis 2020)
- Medical RAG: Almanac (Zakka 2024), Clinfo.ai, PubMed-RAG variants
- **Gap:** few papers systematically ablate RAG contribution in combination with multi-agent architectures.

### 2.3 Multi-Agent LLM Systems
- Role-playing agents: CAMEL, AutoGen, ChatDev
- Medical multi-agent: MedAgents (Tang 2023), AgentClinic
- **Gap:** existing medical multi-agent systems focus on diagnosis; systematic benchmarking on guideline-concordant treatment decisions is missing.

### 2.4 Evaluation of Medical LLMs
- Human expert scoring (gold standard but expensive)
- LLM-as-judge paradigm (Zheng 2023, Chiang 2024)
- **Gap:** inter-judge reliability in clinical open-ended answers under-studied.

---

## 3. Methodology

### 3.1 Overall Architecture
[Figure 1: System architecture diagram — show data flow from question → 4 parallel specialist agents → moderator → final consensus; show RAG pipeline feeding into each agent]

### 3.2 MDT Agent Design
- **Four specialists** with role-conditioned system prompts: medical oncologist, thoracic surgeon, radiation oncologist, pathologist.
- **Moderator agent** receives all four opinions and synthesizes a consensus (treatment plan + disagreement resolution + follow-up).
- **Design rationale**: these four disciplines match real-world tumor board composition (cite: NCCN MDT guidelines, JNCCN).

### 3.3 Retrieval-Augmented Generation Pipeline
- Corpus: NCCN Clinical Practice Guidelines (NSCLC v5.2026, SCLC, Lung Cancer Screening, ICI Toxicities) — 618 pages.
- Chunking: RecursiveCharacterTextSplitter, chunk_size=512, overlap=128 → 6,252 chunks.
- Embedding: OpenAI `text-embedding-3-large` (3072-d dense vectors).
- Index: FAISS flat IP index.
- Retrieval: top-k=5 at inference time, per-question.

### 3.4 LungMDT-Bench-100: Benchmark Construction
- **Design:** 100 clinical scenarios (vignette + question + gold standard + guideline citation).
- **Taxonomy (Table 1):** 6 clinical domains × 3 difficulty levels.
  - D1 Diagnosis/Screening (n=17)
  - D2 Staging/Molecular (n=15)
  - D3 First-line Therapy (n=20)
  - D4 Subsequent/Resistance (n=16)
  - D5 Adverse Events (n=17)
  - D6 Follow-up (n=15)
- **Annotation:** expert-curated by [Dr. Hao, thoracic oncology specialist], each question mapped to specific NCCN section.
- **Quality control:** all gold-standards verified against current NCCN v5.2026 at the time of benchmark freezing.

### 3.5 Experimental Conditions
- 2×2 factorial design: {Single, MDT} × {Zero-shot, RAG} = 4 conditions.
- For MDT + RAG: each specialist agent sees the retrieved context.

### 3.6 LLM-as-Judge Evaluation
- **Judges:** GPT-4o-mini and Claude Sonnet 4.5 (diverse providers to reduce single-vendor bias).
- **Rubric:** 4 dimensions (accuracy, completeness, safety, concordance) on 1–5 Likert scale, plus 2 binary flags (hallucination, safety violation).
- **Reliability:** Cohen's weighted κ computed across judge pairs per dimension.
- **Ensemble score:** mean across judges.

---

## 4. Experimental Setup

### 4.1 Models Evaluated
| Model | Version | Provider | Role |
|-------|---------|----------|------|
| GPT-4o-mini | gpt-4o-mini-2024-07-18 | OpenAI | Proprietary commercial (cost-efficient) |
| Claude Sonnet 4.5 | claude-sonnet-4-5-20250929 | Anthropic | Proprietary commercial (frontier) |
| DeepSeek-R1 | deepseek-reasoner | DeepSeek | Proprietary reasoning-specialized |
| Llama-3.3-70B | Llama-3.3-70B-Instruct-Turbo | Meta (via Together AI) | Open-weight |

### 4.2 Hyperparameters
- Temperature: 0 (deterministic)
- Max tokens: 1024
- RAG top-k: 5

### 4.3 Statistical Analysis
- Wilcoxon signed-rank tests (paired, per question) for condition comparisons.
- Bonferroni correction for multiple comparisons.
- Effect size: Cliff's δ.

---

## 5. Results

[Populated after experiments complete. Expected structure:]

### 5.1 Overall Performance by Model × Condition (Table 3, Fig 2)

### 5.2 Effect of RAG Augmentation (Fig 4a)

### 5.3 Effect of Multi-Agent MDT Architecture (Fig 4b)

### 5.4 Combined MDT + RAG (Fig 4c)

### 5.5 Performance Across Clinical Domains (Fig 3 heatmap)

### 5.6 Performance by Question Difficulty (Fig 6)

### 5.7 Hallucination and Safety Analysis (Fig 5)

### 5.8 Inter-Judge Reliability (Table 5)

---

## 6. Discussion

### 6.1 Key Findings
- MDT consistently outperforms single-agent, particularly on Hard questions
- RAG has largest effect on molecular/pharmacology domains
- Open-weight Llama-3.3 is competitive with proprietary models when given MDT+RAG
- Judge reliability (κ) is high for clear-cut clinical facts, lower for nuanced recommendations

### 6.2 Architectural Insights
- Specialist role diversity matters
- Moderator quality is the bottleneck for overall consensus quality
- Token cost trade-off: MDT+RAG is 5× more expensive than single zero-shot but [X%] more accurate

### 6.3 Limitations
- Single-model MDT (same LLM plays all roles) — future work: heterogeneous agents
- English-only; NCCN-centric; US-practice-centric
- LLM-as-judge may share biases with models being evaluated
- 100 questions is modest; generalization to other tumor types untested
- No prospective clinical validation

### 6.4 Ethical Considerations
- Not a medical device; intended as research tool
- Risk of automation bias if deployed naively

---

## 7. Conclusion
Concise restatement of contributions + forward-looking statement.

---

## Acknowledgments
Clinical collaborators, funding sources.

## Data & Code Availability
- Benchmark: `github.com/.../LungMDT-Bench-100`
- Framework: `github.com/.../MDT-LLM`
- Judge scores: as CSV appendix.

## References
(Elsevier numeric style)

---

## Appendices / Supplementary

- **Appendix A:** Full prompt templates for all 5 agents and 2 judges
- **Appendix B:** Benchmark question examples (one per domain × difficulty)
- **Appendix C:** Judge rubric definition with anchor examples
- **Appendix D:** Per-model detailed results table
- **Appendix E:** Case study (qualitative comparison of single vs MDT on 3 representative cases)

---

## Target Figures & Tables Inventory

| # | Name | Purpose |
|---|------|---------|
| Fig 1 | Architecture diagram | Show MDT-LLM system design |
| Fig 2 | Overall bar chart | Model × Condition main comparison |
| Fig 3 | Domain heatmap | Accuracy by model × clinical domain |
| Fig 4 | Improvement Δ chart | RAG / MDT / MDT+RAG vs baseline |
| Fig 5 | Hallucination rates | Safety analysis |
| Fig 6 | Difficulty gradient | Performance by Easy/Medium/Hard |
| Fig 7 (new) | Cost-accuracy trade-off | Practical deployment guidance |
| Tab 1 | Benchmark statistics | Domain × difficulty composition |
| Tab 2 | Model specifications | Models used + hyperparameters |
| Tab 3 | Main results matrix | Scores across all cells |
| Tab 4 | Wilcoxon test results | Statistical comparisons |
| Tab 5 | Inter-judge reliability | Cohen's κ |
