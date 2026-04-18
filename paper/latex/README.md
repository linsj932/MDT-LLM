# Overleaf Submission Package — MDT-LLM → JKSUCIS

This directory is ready to upload to **Overleaf**.

## Directory contents

```
latex/
├── main.tex                  ← the paper (Elsevier elsarticle, ~30 pages single-col)
├── references.bib            ← ~45 BibTeX entries (Elsevier numeric style)
├── cover_letter.tex          ← separate submission cover letter
├── figures/
│   ├── fig1_architecture.pdf       ← system architecture (vector)
│   ├── fig1_architecture.png
│   ├── fig2_overall_bar.png        ← overall performance
│   ├── fig3_domain_heatmap.png     ← accuracy by model×domain
│   ├── fig4_improvement.png        ← improvement Δ vs baseline
│   ├── fig5_hallucination.png      ← hallucination rates
│   ├── fig6_difficulty.png         ← performance by difficulty
│   ├── fig7_forest_subgroup.png    ← subgroup forest plot
│   ├── fig8_cost_accuracy.png      ← cost–accuracy tradeoff
│   ├── fig9_judge_disagreement.png ← judge agreement heatmap
│   ├── fig10_mdt_rag_interaction.png ← 2×2 CI plot
│   ├── fig11_rag_topk.png          ← RAG top-k sensitivity
│   └── fig12_heterogeneous.png     ← heterogeneous MDT comparison
└── README.md                 ← this file
```

## How to upload to Overleaf

### Option 1: create new Overleaf project

1. Go to https://www.overleaf.com → **New Project** → **Upload Project**.
2. Zip the entire `latex/` directory:
   ```bash
   cd paper
   zip -r mdt-llm-jksucis.zip latex/
   ```
3. Upload the zip; Overleaf will auto-detect `main.tex`.
4. In Overleaf menu → Settings → Compiler: choose **pdfLaTeX**.
5. Click **Recompile**.

### Option 2: local compile

```bash
cd paper/latex
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

## Before submission checklist

- [ ] Fill in author names and affiliations in `main.tex` (lines 44–53).
- [ ] Fill in corresponding author email (line 46).
- [ ] Fill in `[org]` placeholder in Data and code availability section
      with the real GitHub URL.
- [ ] Replace `[reviewers / funding sources]` in Acknowledgments.
- [ ] Check the "Suggested reviewers" in `cover_letter.tex`.
- [ ] (Optional) Switch from `3p` (single-column) to `5p` (two-column
      Elsevier layout) in the `\documentclass` options if the journal
      prefers double-column.
- [ ] Remove the `\linenumbers` comment/uncomment line before submission.
- [ ] Upload supplementary files:
  - `outputs/all_judge_scores.csv` (3,200 judge scores)
  - `outputs/judge_rag_topk.csv` (RAG top-k ablation scores)
  - `outputs/judge_heterogeneous.csv` (heterogeneous ablation scores)
  - `all_100_questions.csv` (the benchmark)
- [ ] Write a 250-word abstract **highlights** (bulleted, required by
      Elsevier).

## Journal formatting notes

**JKSUCIS** uses Elsevier's standard `elsarticle` document class.

- Classes: `1p` (single-column preprint), `3p` (single-col final),
  `5p` (two-col final). Check the *Guide for Authors* at:
  https://www.elsevier.com/journals/journal-of-king-saud-university-computer-and-information-sciences/1319-1578/guide-for-authors

- Bibliography: `elsarticle-num` (numeric) — already set in `main.tex`.

- Figures: accept PDF (preferred, vector) or high-res PNG (≥ 300 dpi).
  All figures here are PNG at 300 dpi; Figure 1 also provided as PDF.

- Highlights: 3–5 bullet points, each 85 characters max — see template
  on Elsevier website.

- Open Access APC (as of 2026): approximately USD 2000 (check journal
  website for current fee).

## Generated highlights (for Elsevier submission form)

Paste the following into the "Highlights" field when submitting:

```
• MDT-LLM: multi-agent framework simulating clinical tumor boards with RAG
• New benchmark LungMDT-Bench-100: 100 expert-annotated oncology scenarios
• Naive RAG significantly reduces strong LLM quality (Bonferroni p<0.002)
• Heterogeneous multi-agent MDT matches best homogeneous MDT at 32% lower cost
• Inter-judge κ poor on safety (0.21) — motivates binary safety-flag rubrics
```

## Post-acceptance

If accepted, JKSUCIS will request:
- High-resolution source figures (included: `figures/`)
- Source LaTeX (included: `main.tex` + `references.bib`)
- Supplementary material (CSVs + scripts — provide separate zip)
- Graphical abstract (optional; can be `fig1_architecture.png`
  cropped to highlight the Phase 1 + Phase 2 flow)

Good luck!
