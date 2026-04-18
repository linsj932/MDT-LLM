# 4. Experimental Setup

## 4.1 Models Evaluated

We evaluate four LLMs spanning three categories of the current LLM landscape (Table 2). Selection aimed to cover: (i) cost-efficient proprietary commercial models, (ii) frontier proprietary models from distinct vendors, (iii) reasoning-specialized models, and (iv) open-weight alternatives deployable in institutional settings where data residency is a concern.

**Table 2.** LLMs evaluated in this study.

| Label | Model ID | Provider | Category | Price (USD / 1M tokens, in / out) |
|-------|----------|----------|----------|------------------------------------|
| GPT-4o-mini | `gpt-4o-mini-2024-07-18` | OpenAI | Proprietary, cost-efficient | 0.15 / 0.60 |
| Claude Sonnet 4.5 | `claude-sonnet-4-5-20250929` | Anthropic | Proprietary, frontier | 3.00 / 15.00 |
| DeepSeek-R1 | `deepseek-reasoner` | DeepSeek | Reasoning-specialized | 0.55 / 2.19 |
| Llama-3.3-70B | `meta-llama/Llama-3.3-70B-Instruct-Turbo` | Meta (via Together AI) | Open-weight | 0.88 / 0.88 |

All models are accessed via their respective providers' production APIs at inference-time defaults except for temperature and max_tokens, which are fixed as specified in Section 3.6.2.

## 4.2 Experimental Conditions

Each of the 100 questions is evaluated under a 2×2 factorial design:

| Condition | Multi-agent? | Retrieval? | Total API calls per question |
|-----------|:---:|:---:|:---:|
| `single_zeroshot` | No | No | 1 |
| `single_rag` | No | Yes | 1 |
| `mdt_zeroshot` | Yes | No | 5 (4 specialists + moderator) |
| `mdt_rag` | Yes | Yes | 5 (4 specialists + moderator) |

This yields **4 conditions × 4 models × 100 questions = 1,600 independent model responses** for the main study. Including the two-judge scoring layer, a total of **3,200 judge calls** are executed for evaluation.

## 4.3 Primary Metrics

For each (question, model, condition, judge) tuple, we record the six scores defined in Section 3.5.2. Primary downstream metrics are computed as follows:

- **Mean ordinal score:** arithmetic mean of {accuracy, completeness, safety, concordance}, per (question, model, condition), averaged across judges.
- **Hallucination rate:** proportion of (question, model, condition) tuples flagged by *either* judge as containing hallucination. (The OR operator is chosen conservatively: if either judge detects a hallucination, it counts.)
- **Safety violation rate:** defined analogously.

## 4.4 Statistical Analysis

### 4.4.1 Paired Condition Comparisons

For each model, we test whether MDT + RAG yields statistically significantly higher scores than single zero-shot, using a **two-sided Wilcoxon signed-rank test** [Wilcoxon1945] paired at the question level. We apply a **Bonferroni correction** across the $4$ models × $3$ paired comparisons (single_rag vs baseline, mdt_zs vs baseline, mdt_rag vs baseline) = $12$ tests, giving corrected $\alpha = 0.05 / 12 \approx 0.0042$.

### 4.4.2 Effect Size

We report **Cliff's δ** [Cliff1993] as a non-parametric effect size. Conventional thresholds: $|\delta| < 0.147$ negligible; $0.147 \leq |\delta| < 0.330$ small; $0.330 \leq |\delta| < 0.474$ medium; $|\delta| \geq 0.474$ large.

### 4.4.3 Bootstrap Confidence Intervals

95% CIs for all reported means are computed via non-parametric bootstrap with $n = 1{,}000$ resamples at the question level (BCa method).

### 4.4.4 Stratified Analyses

We repeat the main comparison stratified by (a) clinical domain ($6$ levels) and (b) question difficulty ($3$ levels) to test whether architectural benefits are homogeneous or concentrated in specific subsets.

## 4.5 Computational Resources

All experiments were conducted on a single workstation (Apple M-series, 32 GB RAM) using cloud-hosted LLM APIs. Total end-to-end wall-clock time was approximately **12 hours** (main experiment: 1,600 model responses in ~7 hours under 4-way per-model parallelism; main judge: 3,200 judgments in ~1 hour; ablations: ~3 hours total). Aggregate API spend was approximately **USD 39** across all experiments and judge scorings (breakdown: OpenAI GPT-4o-mini ~$2; Anthropic Claude Sonnet 4.5 ~$18; DeepSeek R1 via DeepSeek API ~$13; Together AI Llama-3.3-70B ~$3; OpenAI text-embedding-3-large for RAG index ~$1; Anthropic/OpenAI judges ~$2).
