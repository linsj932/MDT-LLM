# MDT-LLM: A Multidisciplinary Team-Based Multi-Agent LLM Framework with RAG for Clinical Decision Support

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/)
[![Paper](https://img.shields.io/badge/paper-JKSUCIS-red)](#)

Open-source framework and benchmark accompanying our paper
**"MDT-LLM: A Multidisciplinary Team-Based Multi-Agent Large Language
Model Framework with Retrieval-Augmented Generation for Evidence-Based
Clinical Decision Support"**, submitted to *Journal of King Saud
University - Computer and Information Sciences* (JKSUCIS).

---

## 🔑 Key findings

Across 4 frontier LLMs × 4 conditions × 100 expert-annotated lung
cancer scenarios (1,600 model responses, 3,200 LLM-judge scores):

1. **Naive RAG *reduces* strong-LLM quality** (Claude Sonnet 4.5
   Δ=−0.29, DeepSeek R1 Δ=−0.32, both Bonferroni-corrected *p<0.002*,
   medium effect size). The effect is **robust across retrieval depths
   k ∈ {1,3,5,10}** — it's not a "too much context" problem.
2. **Heterogeneous multi-agent MDT** (four different LLMs in four
   specialty roles) **matches the best homogeneous MDT at ~32% lower
   cost**. Role specialization partially compensates for individual
   model weakness.
3. **Inter-judge reliability is poor on safety** (κ=0.21) but
   substantial on accuracy (κ=0.70), motivating binary safety-flag
   rubrics for future medical LLM evaluations.
4. **8.5% of low-scoring outputs recommend immunotherapy when a driver
   mutation is actionable** — a clinically critical error type.

## 🧩 What's in this repo

```
lung_mdt_project/
├── config.py                 # Model + RAG + MDT agent configuration
├── requirements.txt
├── all_100_questions.csv     # LungMDT-Bench-100 (THE BENCHMARK)
├── .env.example              # Template for API keys
├── src/
│   ├── multi_agent_mdt.py      # Baseline MDT (4 specialists + moderator)
│   ├── enhanced_mdt.py         # Enhanced MDT: debate + confidence + hetero
│   ├── rag_pipeline.py         # FAISS-based NCCN-guideline retrieval
│   ├── run_experiment.py       # Main runner (resumable, per-model parallel)
│   ├── llm_judge.py            # Multi-judge LLM-as-judge pipeline
│   ├── merge_judge_scores.py   # Aggregate judges across models
│   ├── analyze_results.py      # Core figures 2–6 + Table 3/5
│   ├── advanced_analysis.py    # Subgroup, bootstrap CI, forest, cost–acc
│   ├── ablation_heterogeneous.py  # Heterogeneous-agent ablation
│   ├── ablation_rag_topk.py       # RAG top-k sensitivity ablation
│   ├── ablation_enhanced.py       # Enhanced-MDT ablation (optional)
│   ├── case_study_analysis.py     # Case studies + error taxonomy
│   ├── plot_architecture.py       # Generates Figure 1
│   ├── plot_rag_topk.py           # Generates Figure 11
│   └── plot_heterogeneous.py      # Generates Figure 12
├── data/
│   └── guidelines/           # Put NCCN PDFs here (not redistributed)
├── paper/                    # LaTeX source, figures, BibTeX
│   └── latex/                # Overleaf-ready folder
└── outputs/figures/          # Generated figures + summary CSV tables
```

## 📊 The benchmark: LungMDT-Bench-100

**100 expert-annotated clinical scenarios** across 6 domains × 3 difficulty levels:

| Domain | Easy | Medium | Hard | Total |
|--------|------|--------|------|-------|
| D1: Diagnosis / Screening    | 5 | 6 | 6 | 17 |
| D2: Staging / Molecular      | 4 | 6 | 5 | 15 |
| D3: First-line Therapy       | 4 | 8 | 8 | 20 |
| D4: Subsequent / Resistance  | 3 | 8 | 5 | 16 |
| D5: Adverse Events           | 5 | 7 | 5 | 17 |
| D6: Follow-up                | 4 | 6 | 5 | 15 |

Each scenario includes a patient vignette, focused clinical question,
gold-standard answer, and explicit NCCN section citation.

See `all_100_questions.csv`.

## ⚙️ Quick start

### 1. Install

```bash
git clone https://github.com/deepdoctor/MDT-LLM.git
cd MDT-LLM
pip install -r requirements.txt
```

### 2. Configure API keys

```bash
cp .env.example .env.local
# Edit .env.local and fill in your 4 keys (OpenAI, Anthropic, DeepSeek, Together)
source .env.local
```

### 3. Download NCCN guidelines (required for RAG)

For copyright reasons we do not redistribute NCCN PDFs. Register a
free account at <https://www.nccn.org/> and download:

- NCCN NSCLC v5.2026 (or latest)
- NCCN SCLC v2.2026 (or latest)
- NCCN Lung Cancer Screening v2.2026 (or latest)
- NCCN Immune Checkpoint Inhibitor-Related Toxicities v1.2026 (or latest)

Place the PDFs in `data/guidelines/`.

### 4. Build the RAG index

```bash
python src/rag_pipeline.py
```

This chunks the PDFs and builds the FAISS index (~36s for 618 pages).

### 5. Run the main experiment

```bash
# Full 2×2 factorial study (4 models × 4 conditions × 100 questions)
python src/run_experiment.py

# Or run one model at a time (recommended — easier to parallelize):
python src/run_experiment.py --models gpt-4o-mini --output outputs/run_gpt4omini.jsonl
python src/run_experiment.py --models claude-sonnet --output outputs/run_claude.jsonl
python src/run_experiment.py --models deepseek-r1 --output outputs/run_deepseek.jsonl
python src/run_experiment.py --models llama-3.3-70b --output outputs/run_llama.jsonl
```

Each run is resumable via `--resume-from <file>.jsonl`.

### 6. Score responses with LLM judges

```bash
for f in outputs/run_*.jsonl; do
  python src/llm_judge.py "$f" --output "outputs/judge_$(basename $f .jsonl).csv"
done
python src/merge_judge_scores.py    # → outputs/all_judge_scores.csv
```

### 7. Generate figures

```bash
python src/analyze_results.py outputs/all_judge_scores.csv
python src/advanced_analysis.py     # subgroup, bootstrap, forest, cost–acc
python src/case_study_analysis.py   # case studies + error taxonomy
python src/plot_architecture.py     # Figure 1 (architecture)
```

Outputs land in `outputs/figures/` (12 PNGs + 7 CSV tables).

## 🧪 Running ablations

```bash
# RAG top-k sensitivity  (Claude + DeepSeek × k ∈ {1,3,10})
python src/ablation_rag_topk.py
python src/llm_judge.py outputs/ablation_rag_topk.jsonl \
    --output outputs/judge_rag_topk.csv --judges gpt-4o-mini

# Heterogeneous-agent MDT (4 different LLMs across 4 specialist roles)
python src/ablation_heterogeneous.py
python src/llm_judge.py outputs/ablation_heterogeneous.jsonl \
    --output outputs/judge_heterogeneous.csv --judges gpt-4o-mini

# Enhanced MDT with debate + confidence-weighted moderator (optional, expensive)
python src/ablation_enhanced.py
```

## 📦 Reproducing paper figures

All figures in the paper can be reproduced in a single pass after you
have `outputs/all_judge_scores.csv`:

```bash
python src/analyze_results.py outputs/all_judge_scores.csv
python src/advanced_analysis.py
python src/plot_rag_topk.py
python src/plot_heterogeneous.py
python src/plot_architecture.py
```

Figures are written to `outputs/figures/*.png`.

## 📐 Methodology at a glance

- **MDT framework** (Eq. 1–2 in paper): 4 role-conditioned specialist
  agents run in parallel, outputs concatenated and synthesized by a
  moderator agent. Homogeneous (single LLM for all roles) or
  heterogeneous (different LLMs per role).
- **RAG pipeline** (Eq. 3–5): Recursive character chunking
  (size=512, overlap=128) → OpenAI `text-embedding-3-large` (3,072-d)
  → FAISS flat inner-product index → top-k dense retrieval.
- **LLM-as-judge** (Eq. 6–9): 2 judges (GPT-4o-mini, Claude Sonnet 4.5)
  scoring 4 ordinal dimensions (1–5 Likert) + 2 binary flags; ensemble
  via mean; inter-judge Cohen's weighted κ reported.
- **Statistics** (Eq. 10–15): Paired Wilcoxon signed-rank tests with
  Bonferroni (main) or Benjamini-Hochberg (subgroup) correction;
  Cliff's δ effect sizes; bootstrap 95% CIs at the question level.

## 💰 Approximate API cost

For a full run (1,600 main responses + 3,200 judge scorings +
ablations) the aggregate spend is approximately **USD 39**:

| Provider | Usage | Approximate cost |
|----------|-------|-----------------:|
| OpenAI (GPT-4o-mini + embeddings + judge) | ~4,000 calls | ~$3 |
| Anthropic (Claude Sonnet + judge) | ~2,800 calls | ~$18 |
| DeepSeek (R1) | ~1,200 calls | ~$13 |
| Together AI (Llama-3.3-70B) | ~1,000 calls | ~$3 |
| OpenAI text-embedding-3-large (index build) | ~6,250 chunks | ~$1 |

## 📚 Citation

```bibtex
@article{MDTLLM2026,
  title   = {MDT-LLM: A Multidisciplinary Team-Based Multi-Agent
             Large Language Model Framework with Retrieval-Augmented
             Generation for Evidence-Based Clinical Decision Support},
  author  = {First Author and Second Author and Senior Author},
  journal = {Journal of King Saud University - Computer and
             Information Sciences},
  year    = {2026},
  note    = {Under review},
}
```

## ⚠️ Disclaimer

This software is a **research prototype** for LLM benchmarking. It is
**not a medical device** and is **not intended for direct clinical
use**. All clinical decisions must be made by qualified healthcare
professionals.

## 📄 License

- **Code and benchmark**: MIT License (see `LICENSE`).
- **NCCN guideline PDFs**: © NCCN, not redistributed. Users must
  obtain their own copies from <https://www.nccn.org/>.

## 🙏 Acknowledgments

We thank NCCN for maintaining the clinical guidelines that make
evidence-based oncology benchmarks like this possible, and the
open-source AI community for the tools (LangChain, FAISS, HuggingFace,
Anthropic SDK, OpenAI SDK) upon which this work builds.

## 🤝 Contact / issues

Open a GitHub issue for bugs or questions. For substantive research
discussion, please reference the paper correspondence address.
