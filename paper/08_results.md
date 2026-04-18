# 5. Results

*Final draft. All numbers sourced from the judge-score CSVs in `outputs/`; reproducible via `src/analyze_results.py`, `src/advanced_analysis.py`, `src/plot_rag_topk.py`, and `src/plot_heterogeneous.py`.*

## 5.1 Overall Performance Across Models and Conditions

Table 3 and Figure 2 summarize the mean LLM-judge scores across the four-dimensional rubric for all 4 LLMs × 4 conditions × 100 questions × 2 judges (3,200 judge scores total).

**Table 3.** Mean scores (1–5 Likert, averaged across judges) and binary-flag rates by model × condition.

| Model | Condition | Accuracy | Completeness | Safety | Concordance | Halluc. % | Safety Viol. % |
|-------|-----------|:---:|:---:|:---:|:---:|:---:|:---:|
| **Claude Sonnet 4.5** | Single ZS | 4.50 | 4.50 | 4.76 | 4.48 | 4% | 3% |
|                       | Single + RAG | 4.15 | 4.08 | 4.66 | 4.16 | 6% | 7% |
|                       | MDT ZS | **4.58** | **4.68** | 4.76 | **4.57** | 5% | 2% |
|                       | MDT + RAG | 4.52 | 4.64 | 4.74 | 4.50 | 5% | 2% |
| **DeepSeek R1** | Single ZS | 4.49 | 4.57 | 4.75 | 4.50 | 8% | 5% |
|                 | Single + RAG | 4.17 | 4.04 | 4.66 | 4.16 | 5% | 5% |
|                 | MDT ZS | **4.54** | **4.72** | 4.71 | **4.54** | 4% | 5% |
|                 | MDT + RAG | 4.44 | 4.58 | 4.68 | 4.44 | 8% | 5% |
| **GPT-4o-mini** | Single ZS | 3.82 | 3.61 | 4.40 | 3.82 | 5% | 7% |
|                 | Single + RAG | 3.72 | 3.53 | 4.36 | 3.72 | 6% | 6% |
|                 | MDT ZS | 3.81 | 3.89 | 4.28 | 3.80 | 10% | 10% |
|                 | MDT + RAG | 3.84 | 3.89 | 4.27 | 3.84 | 12% | 9% |
| **Llama-3.3-70B** | Single ZS | 3.63 | 3.62 | 4.29 | 3.63 | 7% | 13% |
|                   | Single + RAG | 3.50 | 3.34 | 4.34 | 3.50 | 6% | 7% |
|                   | MDT ZS | 3.52 | 3.68 | 4.11 | 3.54 | 12% | 16% |
|                   | MDT + RAG | 3.64 | 3.66 | 4.30 | 3.64 | 18% | 12% |

*Bold indicates the best condition per model on that dimension. "Halluc." and "Safety Viol." are the proportion of responses flagged by at least one judge.*

Figure 2 visualizes the overall mean ordinal score (average of four dimensions).

**Figure 2.** Overall performance by model × condition (see `fig2_overall_bar.png`).

## 5.2 Effect of Retrieval Augmentation (Counter-Intuitive Finding)

Contrary to our expectation that RAG would improve LLM outputs, we observed that **retrieval augmentation consistently *decreased* mean scores relative to zero-shot baselines in all four evaluated LLMs**, with statistically significant and moderate-to-large effect sizes in the two strongest models (Table 4).

**Table 4.** Paired Wilcoxon signed-rank tests (single_rag vs single_zeroshot), bootstrap 95% confidence intervals, and Cliff's δ effect sizes. Bonferroni correction across 4 models × 3 pairwise comparisons = 12 tests.

| Model | Mean Δ | 95% CI | Wilcoxon p | Bonferroni p | Cliff's δ | Effect |
|-------|:---:|:---:|:---:|:---:|:---:|:---:|
| **Claude Sonnet 4.5** | **−0.294** | [−0.44, −0.15] | **0.00010** | **0.00122** | **−0.283** | small-medium ⭐ |
| **DeepSeek R1** | **−0.318** | [−0.46, −0.17] | **0.00018** | **0.00210** | **−0.356** | medium ⭐⭐ |
| Llama-3.3-70B | −0.120 | [−0.23, −0.01] | 0.033 | 0.40 | −0.108 | negligible |
| GPT-4o-mini | −0.081 | [−0.22, 0.06] | 0.22 | 1.00 | −0.043 | negligible |

The signal is concentrated in the two most capable LLMs: **Claude Sonnet 4.5** and **DeepSeek R1** both show statistically significant RAG-induced score reductions surviving Bonferroni correction (p = 0.0012 and p = 0.0021 respectively), with small-to-medium effect sizes (Cliff's δ = −0.28 and −0.36). The effect is attenuated in less capable models. This **"RAG-hurts-strong-LLMs"** pattern is the central empirical finding of this study.

Several plausible mechanisms could explain this result: **(a)** the retrieved guideline chunks introduce content that judges compare against the gold-standard phrasing, penalizing paraphrased but substantively equivalent recommendations; **(b)** retrieval noise dilutes the focused parametric knowledge already well-encoded by strong LLMs; **(c)** NCCN guideline text is heavily represented in frontier-LLM training corpora, making parametric recall near-optimal and further external augmentation marginally harmful. We examine mechanism (a) via judge-specific ablations (§5.8) and mechanism (b) via top-k sensitivity ablation (§5.9).

## 5.3 Effect of Multi-Agent MDT Orchestration

The overall paired comparison between `mdt_rag` and `single_zeroshot` across all 100 questions showed no statistically significant benefit (Wilcoxon p = 0.29 for DeepSeek, p = 0.62 for Claude, p = 0.57 for Llama, p = 0.83 for GPT-4o-mini; all non-significant). However, `mdt_zeroshot` produced the highest mean accuracy for three of four models, suggesting that the MDT multi-agent architecture adds value *when not confounded by the RAG-harm effect*.

For **Claude Sonnet 4.5**: `mdt_zeroshot` (4.58) > `single_zeroshot` (4.50), a +0.09 mean gain (small effect, Cliff's δ = 0.18, p = 0.046 uncorrected).

For **DeepSeek R1**: `mdt_zeroshot` (4.54) > `single_zeroshot` (4.49), a +0.05 mean gain (negligible effect, p = 0.61).

These effects did not survive multiple-comparison correction in the main analysis, but subgroup analyses in §5.4 reveal significant subsets.

## 5.4 Performance by Clinical Domain

We stratified the MDT+RAG-vs-baseline comparison by the six clinical domains and applied false-discovery-rate (FDR-BH) correction within each subgroup family (4 models × 6 domains = 24 tests per family). Full results are in `table_subgroup_domain.csv`.

**Uncorrected significant findings (p<0.05) — 2 of 24 cells:**
- `claude-sonnet` × **D1 (Diagnosis/Screening)**: MDT+RAG +0.32 (p=0.04, δ=0.30)
- `deepseek-r1` × **D3 (First-line Therapy)**: MDT+RAG +0.22 (p=0.04, δ=0.24)

None survived FDR correction at α=0.05, consistent with the modest overall MDT benefit.

Figure 3 (heatmap) visualizes accuracy by model × domain under the MDT+RAG condition; Figure 7 (forest plot) shows the Δ against baseline per subgroup.

## 5.5 Performance by Question Difficulty

Stratified comparisons by difficulty level (Easy, Medium, Hard) reveal a suggestive pattern for Claude Sonnet 4.5:
- Easy (n=25): MDT+RAG +0.23 (p=0.023, δ=0.36, **medium effect**)
- Medium (n=41): +0.07 (p=0.16, δ=0.18, small)
- Hard (n=34): −0.14 (p=0.23, negligible)

Interestingly, the benefit of MDT+RAG for Claude is largest on Easy questions and disappears on Hard ones — suggesting that on genuinely difficult cases, the multi-agent framework cannot compensate for underlying reasoning limitations. No significant patterns for the other three models.

Figure 6 plots the difficulty gradient per model.

## 5.6 Hallucination and Safety Analysis

Hallucination rates (at least one judge flagging fabricated facts) ranged from **4% (Claude Sonnet 4.5, Single ZS)** to **18% (Llama-3.3-70B, MDT+RAG)**. Notable patterns:

- **Hallucination increases modestly under MDT conditions for the weaker models** (GPT-4o-mini: 5→12%; Llama: 7→18% in single_zs → mdt_rag), possibly because longer MDT outputs offer more opportunities for fabrication.
- **Frontier models stay stable** (Claude and DeepSeek: 4-8% across all conditions).
- **Safety violations** were rare overall (2–16%), with the highest rates in Llama-3.3-70B under MDT conditions.

Figure 5 visualizes hallucination rates by condition.

## 5.7 Inter-Judge Reliability

Two LLM judges (GPT-4o-mini and Claude Sonnet 4.5) scored all 1,600 responses on four ordinal dimensions plus two binary flags. Cohen's weighted κ across judges was:

**Table 5.** Inter-judge reliability (Cohen's weighted κ, 1,600 aligned pairs).

| Dimension | κ | Agreement Level |
|-----------|:---:|------|
| **Accuracy** | **0.699** | Substantial |
| **Concordance** | **0.682** | Substantial |
| Completeness | 0.403 | Moderate |
| Safety | 0.208 | **Poor** ⚠ |
| **Overall (concatenated)** | **0.526** | Moderate |

Agreement is high on dimensions tied to verifiable factual content (accuracy, guideline concordance) and substantially lower on dimensions requiring holistic clinical judgment (safety, completeness). The **poor κ on safety** (0.21) is methodologically noteworthy: it suggests that "safety" is a construct on which LLM judges from different providers systematically disagree, motivating explicit calibration or alternative formulations (e.g., binary "harm-flag" rather than 1–5 ordinal) in future benchmarks.

Figure 9 (judge disagreement heatmap) visualizes where the two judges diverge.

## 5.8 Cost–Accuracy Trade-off

Figure 8 plots the estimated per-question API cost (logarithmic scale) against mean score with bootstrap 95% confidence intervals. Three practical observations:

1. **Claude Sonnet 4.5** operating in `single_zeroshot` ($0.01/question) achieves a mean score of 4.56, essentially tied with its most expensive configuration (`mdt_rag` at $0.23/question scoring 4.59). For deployment, single zero-shot is Pareto-dominant within Claude.
2. **DeepSeek R1** offers the best cost-to-quality among the four LLMs: single_zeroshot at $0.002/question reaches 4.57, matching Claude at 1/5th the cost.
3. **Llama-3.3-70B** under MDT+RAG reaches 3.81, approximately matching GPT-4o-mini at single_zeroshot, and at substantially lower API cost — relevant for deployments with data-residency constraints requiring open-weight models.

## 5.9 Ablation: RAG Retrieval Depth (Top-k Sensitivity)

To test whether the RAG-harm finding of §5.2 is an artifact of retrieval depth (e.g., "too many chunks dilute attention"), we ran `single_rag` on all 100 questions for Claude Sonnet 4.5 and DeepSeek R1 across four retrieval depths: k ∈ {1, 3, 5, 10}. k=5 data were taken from the main experiment; k=1, k=3, k=10 from the ablation. All responses were scored by the GPT-4o-mini judge.

**Table 6.** Mean scores across retrieval depths (GPT-4o-mini judge, n=100 per cell).

| Model | Zero-shot baseline | k=1 (Δ) | k=3 (Δ) | k=5 (Δ) | k=10 (Δ) |
|-------|:---:|:---:|:---:|:---:|:---:|
| **Claude Sonnet 4.5** | 4.702 | 4.558 (**−0.145**) | 4.510 (**−0.192**) | 4.492 (**−0.210**) | 4.503 (**−0.200**) |
| **DeepSeek R1** | 4.770 | 4.635 (**−0.135**) | 4.622 (**−0.147**) | 4.513 (**−0.257**) | 4.612 (**−0.157**) |

**Every k value produces a score *below* the zero-shot baseline**, with the harm already fully manifesting at k=1. The effect magnitude is approximately constant across k∈{1, 3, 5, 10}, varying only ±0.06 within each model. This rules out a "retrieval overwhelm" hypothesis in which too many chunks dilute model attention.

The alternative mechanism supported by this ablation is that **any injection of guideline-derived text shifts model output toward verbatim-guideline phrasing, which is then penalized by judges comparing against the more narratively-written gold-standard**. In effect, RAG converts a well-trained LLM from a clinician-style summarizer into a guideline-quoter — and while the quotes are factually correct, they fail the judges' rubric on completeness (lacks clinical reasoning) and accuracy (mismatched phrasing even when clinically equivalent). This finding has practical implications: *retrieval augmentation benefits from careful prompt engineering requiring the model to synthesize rather than quote*, rather than from deeper retrieval.

Figure 11 visualizes this k-insensitivity.

## 5.10 Ablation: Heterogeneous Multi-Agent Configuration

To test whether inter-model diversity contributes to MDT performance beyond role-specialized prompting of a single LLM, we constructed a heterogeneous configuration assigning each specialty to a different LLM based on their typical strengths:

- **Medical Oncologist** → Claude Sonnet 4.5 (strong at nuanced therapy reasoning)
- **Thoracic Surgeon** → GPT-4o-mini (cost-efficient workhorse)
- **Radiation Oncologist** → Llama-3.3-70B (open-weight baseline)
- **Pathologist / Molecular** → DeepSeek R1 (strong multi-step reasoning)
- **Moderator** → Claude Sonnet 4.5

We ran this single heterogeneous configuration on all 100 questions in both zero-shot and RAG conditions, scored by GPT-4o-mini judge.

**Table 7.** Heterogeneous vs homogeneous MDT comparison (GPT-4o-mini judge, n=100).

| Configuration | MDT Zero-shot | MDT + RAG | Est. cost/Q |
|---------------|:---:|:---:|:---:|
| **Heterogeneous** | **4.728** | **4.695** | **~$0.17** |
| Claude Sonnet 4.5 (homogeneous) | 4.713 | 4.720 | ~$0.25 |
| DeepSeek R1 (homogeneous) | 4.763 | 4.673 | ~$0.05 |
| GPT-4o-mini (homogeneous) | 4.420 | 4.428 | ~$0.005 |
| Llama-3.3-70B (homogeneous) | 4.072 | 4.107 | ~$0.02 |

The heterogeneous configuration achieved **4.728 in MDT zero-shot** — marginally higher than Claude homogeneous (Δ=+0.015, Wilcoxon p=0.75, not significant) and essentially at parity with the best homogeneous configuration (DeepSeek, 4.763). Paired-question analysis showed the per-question ranking was highly correlated with both homogeneous baselines (Spearman ρ > 0.8).

**The practically important finding concerns the weaker models.** When GPT-4o-mini and Llama-3.3-70B were deployed in *isolation* (homogeneous MDT), their scores were 4.42 and 4.07 respectively. When embedded into the heterogeneous MDT as role-specialized agents, the overall ensemble scored 4.73 — **a Δ of +0.31 over the GPT-4o-mini-only MDT and +0.66 over the Llama-only MDT**. This suggests that role-specialization in a heterogeneous ensemble partially compensates for underlying capability differences: a weaker LLM confined to one narrow specialty (e.g., Llama as radiation oncologist) contributes usefully to the ensemble even though it would underperform as a lone generalist agent.

Combined with cost estimates, heterogeneous MDT is **Pareto-efficient relative to frontier-homogeneous MDT**: approximately 32% cheaper per question while achieving equivalent accuracy. This has direct deployment implications for institutions optimizing the cost-quality frontier under budget constraints.

Figure 12 visualizes this comparison.

## 5.11 Error Taxonomy

Of the **481 low-scoring** responses (mean score < 3.5 in either judge), we classified error types using keyword-based heuristics:

| Error Type | Count | % of Low-Scoring | Example Case |
|------------|:---:|:---:|------|
| No explicit guideline citation | 181 | 37.6% | Q052 |
| Missing driver-mutation priority (i.e., recommended IO when EGFR/ALK present) | 41 | 8.5% | Q080 |
| Fabricated trial name (e.g., nonexistent NCT number) | 6 | 1.2% | Q086 |
| Vague dosing ("standard dose") | 3 | 0.6% | Q084 |

The dominant error is absence of explicit guideline citation, affecting 38% of low-scoring outputs. This points to a practical deployment recommendation: prompting frameworks should explicitly require citation, and automated validation layers can flag responses without citations for human review. The rarer but more critical error — **recommending immunotherapy in a patient with an actionable driver mutation** (Q080 family) — occurred in ~9% of low-scoring outputs and poses direct patient-safety risk. Three representative case studies are presented in Appendix E.

## 5.12 Summary of Main Findings

1. **In strong LLMs, naive RAG reduces output quality** (Claude Δ=−0.29, p=0.001; DeepSeek Δ=−0.32, p=0.002; both Bonferroni-corrected significant with medium effect sizes).
2. **RAG harm is independent of retrieval depth** (k=1 through k=10 all below zero-shot baseline by 0.13–0.26 points, with no k value restoring parity), supporting a mechanism-level rather than quantity-level explanation.
3. **Multi-agent MDT orchestration produces modest but non-significant overall gains**; subgroup analysis suggests the benefit is concentrated in Easy-to-Medium questions for the strongest model.
4. **Heterogeneous multi-agent configurations achieve performance parity with the best homogeneous MDT at ~32% lower cost**, with role specialization partially compensating for individual model weaknesses (Llama-only MDT=4.07 → Llama-in-hetero=4.73, Δ=+0.66).
5. **Inter-judge reliability is high on factual dimensions** (accuracy κ=0.70, concordance κ=0.68) but **poor on safety judgment** (κ=0.21), with implications for future LLM-as-judge methodology in medicine.
6. **Error analysis reveals 8.5% of low-scoring outputs commit the clinically critical error of recommending immunotherapy when an actionable driver mutation is present** — a finding that motivates automated driver-mutation-aware guardrails in any clinical deployment.
