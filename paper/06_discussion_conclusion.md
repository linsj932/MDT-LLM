# 6. Discussion

*[Draft template — specific numerical claims will be added after results are finalized. ~2 pages.]*

## 6.1 Principal Findings

This study provides, to our knowledge, the first systematic benchmarking of multi-agent LLM orchestration combined with retrieval-augmented generation for oncology treatment-planning decisions. Three findings stand out.

**First, and most unexpectedly: retrieval-augmented generation *reduced* the clinical answer quality of the two strongest LLMs in our study** (Claude Sonnet 4.5: Δ=−0.29, p=0.001 Bonferroni-corrected, Cliff's δ=−0.28; DeepSeek R1: Δ=−0.32, p=0.002, Cliff's δ=−0.36, medium effect). The effect was robust to retrieval depth: k=1, k=3, k=5, and k=10 all produced scores below the zero-shot baseline, with the harm manifesting fully at k=1. This rules out a naive "too-much-context" explanation and implicates the mechanism of guideline injection itself: forcing a well-pretrained LLM to quote from retrieved chunks appears to shift its output from integrated clinical reasoning toward verbatim guideline recital, which is penalized by judges comparing against the more narratively-phrased gold-standard.

**Second, multi-agent MDT orchestration produced modest but non-significant overall gains**, with suggestive benefits concentrated in Easy-to-Medium questions for the strongest model (Claude: Δ=+0.23 on Easy questions, p=0.023, medium effect size). Notably, `mdt_zeroshot` was the top-scoring condition for both Claude and DeepSeek — the multi-agent benefit exists but is partially masked when RAG is included.

**Third, DeepSeek R1 matched or exceeded Claude Sonnet 4.5 on this benchmark at approximately 1/5 the API cost**, and open-weight Llama-3.3-70B under MDT+RAG approached GPT-4o-mini in single zero-shot. The practical implication: the architectural choice (MDT vs. single, RAG vs. zero-shot) has a larger impact on Pareto-efficient deployment than does flagship-model selection, a finding with direct relevance to health systems constrained by data-residency or budget considerations.

## 6.2 Interpretation of Architectural Effects

### 6.2.1 Why Multi-Agent Helps

The observed MDT advantage aligns with the theoretical case for role-specialized reasoning. By conditioning each specialist on a role-specific prompt that biases their attention toward a subset of the case, the framework effectively implements a **decomposition-and-synthesis** strategy analogous to mixture-of-experts or chain-of-thought specialization. Crucially, the *parallel* (rather than sequential) specialist phase avoids anchoring bias: each specialist reasons from first principles rather than being led by a preceding agent's conclusions. This is consistent with findings in [Liu2024-KG4Diagnosis] and aligns with cognitive-psychology evidence that diverse independent judgments outperform deliberative groups on quantitative estimation tasks.

### 6.2.2 Why RAG *Hurts* Strong LLMs

Contrary to the prevailing assumption that RAG universally benefits LLM deployments, our strongest empirical finding is that RAG *reduced* performance for Claude Sonnet 4.5 and DeepSeek R1. Our k-sensitivity ablation (§5.9) shows the harm is present even at k=1, arguing against a "context overwhelm" explanation. Three mechanisms are consistent with this pattern:

**(i) Phrasing distortion.** Strong LLMs, absent retrieval, produce integrated clinical narratives ("for this patient with EGFR exon 19 deletion and PD-L1 80%, first-line therapy should be osimertinib, *because* driver-mutation targeting takes priority over immunotherapy in NSCLC"). When retrieved NCCN chunks are injected, the model tends to quote them ("per NSCL-J page 2, osimertinib is a Category 1 recommendation..."), and the judges — scoring against a narrative gold-standard — penalize the quote-style output even when it is factually equivalent.

**(ii) Parametric knowledge adequacy.** NCCN guidelines are heavily represented in frontier LLM training corpora. A well-aligned LLM already "knows" osimertinib is first-line for EGFR exon 19 deletion; appending a retrieved chunk adds no new signal while displacing attention from the clinical reasoning the judge values.

**(iii) Judge bias.** The LLM-as-judge protocol rewards responses that resemble the gold-standard in both content and form. Our gold-standards are expert clinician narratives, not verbatim guideline text. A RAG-augmented output that is faithful to the guideline but diverges stylistically from the gold-standard is scored down. This would be a judge-methodology artifact rather than a true quality degradation.

These mechanisms have different implications: (i) and (ii) suggest that RAG's marginal value is domain-dependent and vanishes where parametric knowledge is already strong; (iii) suggests the RAG-harm finding would not replicate under expert-clinician scoring, which would score factual correctness and would not penalize guideline-consistent phrasing. **Distinguishing these mechanisms requires human expert validation on a subset of responses, which we identify as a priority for future work.** Regardless of which mechanism dominates, the practical implication is clear: naive retrieval augmentation is not a guaranteed win for strong LLMs, and deployments should A/B test against zero-shot baselines rather than assume RAG's benefit.

### 6.2.3 MDT × RAG Interaction

The overall MDT benefit is modest (Δ~+0.05 in accuracy score) but consistent in direction across the strongest models. More interestingly, the MDT × RAG interaction is *negative*: adding RAG to an MDT configuration tends to reduce scores relative to MDT alone (e.g., Claude: MDT_ZS=4.58 vs MDT_RAG=4.52; DeepSeek: 4.54 vs 4.44). This is consistent with the §6.2.2 interpretation — if RAG induces phrasing distortion, injecting it into four specialist agents *plus* a moderator amplifies the distortion rather than correcting it. It motivates future MDT frameworks that use retrieval more selectively — e.g., the adaptive-retrieval option in our enhanced framework (§3 Appendix A.2), where specialists issue their own follow-up queries only when needed.

## 6.3 Evaluation Methodology Insights

The two-judge protocol yielded inter-judge Cohen's weighted κ of **0.70** on accuracy, **0.40** on completeness, **0.21** on safety, and **0.68** on concordance, with lowest agreement on **safety**. The pattern is striking: judges agreed substantially (κ ≥ 0.60, considered "substantial" in the κ literature) on dimensions tied to verifiable factual content (accuracy, guideline concordance) but agreed only moderately on completeness (κ=0.40) and *poorly* on safety (κ=0.21). This gradient is consistent with construct complexity: factual accuracy is close to a lookup task for an LLM judge, while "safety" requires the kind of holistic clinical appropriateness judgment that is inherently subjective even among human clinicians.

Two implications follow. First, **reporting ensemble means across judges is not a substitute for reporting the underlying κ** — it masks the degree to which subjective dimensions are under-constrained. Future LLM-as-judge protocols for clinical recommendations should report per-dimension κ routinely. Second, the safety-κ finding motivates **methodological reformulation**: rather than 1–5 Likert safety scales, binary "safety violation" flags accompanied by explicit triggering criteria (e.g., "recommended a drug contraindicated by the patient's comorbidity list") may be more reproducible across judges. Our binary `safety_violation` flag showed inter-judge agreement consistent with its more objective formulation.

Judges from different providers (OpenAI's GPT-4o-mini and Anthropic's Claude Sonnet 4.5) produced **systematically offset but directionally consistent** scores: Claude tended to be stricter (lower mean) than GPT-4o-mini on completeness, but the *ranking* of conditions within each model was nearly identical between judges. This pattern supports using multi-vendor LLM judges as a robustness check rather than a replacement for each other, and argues against single-vendor-judge evaluations being fully reliable for high-stakes benchmarking.

## 6.4 Comparison with Prior Work

Our MDT-LLM framework extends MedAgents [Tang2023-MedAgents] in three ways: (i) we target treatment planning rather than diagnostic classification; (ii) our role composition maps to real-world tumor-board specialties rather than generic "expert panel"; (iii) we explicitly combine multi-agent with RAG in a unified design. Our LungMDT-Bench-100 complements MedQA [Jin2020-MedQA] by providing open-ended, case-level, multidisciplinary scenarios rather than isolated multiple-choice items.

Relative to the general medical-RAG literature (Almanac [Zakka2024], Clinfo.ai [Lozano2023]), our work is the first to ablate RAG specifically in the context of multi-agent orchestration on guideline-concordant treatment planning.

## 6.5 Practical Deployment Implications

For institutions considering deploying LLM-based decision support, our findings suggest the following hierarchy of intervention value (subject to the cost-accuracy trade-off shown in Figure 7):

1. **RAG over institutional guidelines** provides the largest single-intervention benefit and should be considered a baseline requirement.
2. **Multi-agent MDT orchestration** adds a further increment, particularly for complex cases (Hard difficulty, multi-organ / resistance scenarios).
3. **Frontier LLM selection** matters less than architectural choice: a well-orchestrated cost-efficient model can match a frontier model used naively.

Cost and latency considerations are non-trivial: MDT + RAG uses **5×** the API calls of single zero-shot. For high-volume deployments, this may motivate a **tiered triage** approach—routing routine cases to single-agent inference and escalating complex cases to MDT.

## 6.6 Limitations

**Single-model multi-agent.** All five agents in the MDT configuration are instantiated from the same underlying LLM. While this isolates the effect of role-specialization, it may *underestimate* the benefit of a true multi-agent system where different underlying models bring genuine knowledge diversity. Heterogeneous agent configurations are a natural extension.

**English-only and NCCN-centric.** The benchmark and guideline corpus are in English and follow U.S.-practice (NCCN) conventions. Generalization to ESMO-practice regions, other languages, or low-resource settings remains to be tested.

**Temporal scope.** Guidelines are frozen at a single timepoint (April 2026). A longitudinal study tracking performance degradation as guidelines evolve—and the effectiveness of incremental RAG corpus updates—would be valuable.

**LLM-as-judge limitations.** Despite the multi-judge protocol, LLM judges may share systematic biases with the models being evaluated (e.g., shared training data, similar alignment approaches). Comparison against expert human scoring on a subset of responses, for calibration, remains desirable and is an ongoing effort in our group.

**Treatment-planning scope.** We evaluate on *treatment planning* questions. Other MDT functions (consent discussions, patient-facing communication, prognostic counseling) are not tested.

**No prospective deployment.** Our evaluation is retrospective and synthetic; the framework has not been integrated into live clinical workflows. Clinical deployment would require additional validation including prospective case comparison, clinician trust studies, and regulatory review.

## 6.7 Threats to Validity

**Construct validity:** Does our benchmark capture the full spectrum of clinical reasoning? Partly—our 100 scenarios span the major clinical pathway milestones but cannot be exhaustive. We have prioritized breadth (6 domains) over within-domain depth.

**Internal validity:** Are observed differences attributable to our manipulations? The factorial design controls for scenario-level variance. Temperature 0 reduces stochastic variance but eliminates neither LLM nor judge noise; we report bootstrap CIs to quantify remaining uncertainty.

**External validity:** Do findings generalize beyond this benchmark? We believe the *direction* of findings (MDT > single, RAG > zero-shot) is robust, but absolute magnitudes may vary with scenario distribution.

## 6.8 Future Work

- **Heterogeneous multi-agent configurations** (different LLMs for different specialties).
- **Dynamic retrieval**—allowing agents to issue follow-up retrieval queries based on initial analysis.
- **Longitudinal cases**—multi-turn scenarios with evolving patient information.
- **Extension to other tumor types** (breast, colorectal, gastric) using the same framework.
- **Prospective clinical validation** with deployment in a supervised-use pilot study.
- **Judge calibration**—comparing LLM-judge scores to board-certified expert panels.

---

# 7. Conclusion

*[~0.5 pages]*

We presented MDT-LLM, a multi-agent large language model framework for evidence-based clinical decision support that models the role composition and synthesis structure of clinical multidisciplinary team meetings. Our systematic 2×2 factorial evaluation across 4 frontier LLMs and 100 expert-annotated lung-cancer clinical scenarios produced three primary findings that refine the prevailing enthusiasm for RAG-and-multi-agent clinical LLM deployments: (i) naive retrieval augmentation *reduces* output quality in strong LLMs (Bonferroni-corrected significant for Claude Sonnet 4.5 and DeepSeek R1, medium effect size, k-insensitive); (ii) multi-agent MDT orchestration provides modest non-significant overall gains but shows promise on easy-to-medium-difficulty cases for the strongest model; (iii) heterogeneous multi-agent configurations match the best homogeneous MDT at ~32% lower cost, suggesting role specialization partially substitutes for model capability. These findings question the assumption that "more augmentation is always better" and motivate careful, empirically-grounded evaluation of each architectural component before clinical deployment.

We release LungMDT-Bench-100 and the MDT-LLM implementation as open resources to support future research, and we introduce a multi-judge LLM-as-judge evaluation protocol with explicit inter-judge reliability reporting as a methodological template for open-ended clinical LLM benchmarking.

Taken together, these results suggest that architectural choices—role specialization, parallel reasoning, explicit synthesis, guideline grounding—are at least as important as raw model capability for safe and reliable clinical decision support. Future work will extend the framework to heterogeneous agents, longitudinal cases, and prospective clinical validation.

## Author Contributions

[YC]: conceptualization, software implementation, experiments, writing (draft).
[HY]: clinical case authoring, gold-standard annotation, clinical validation, writing (methodology).
[Senior author]: supervision, writing (review and editing).
All authors read and approved the final manuscript.

## Declaration of Competing Interest

The authors declare no competing interests.

## Data and Code Availability

- Benchmark: `https://github.com/[org]/LungMDT-Bench-100`
- Framework implementation: `https://github.com/[org]/MDT-LLM`
- Judge scoring outputs (full CSV): Supplementary File S1.

## Funding

[To be added.]

## Acknowledgments

[To be added.]
