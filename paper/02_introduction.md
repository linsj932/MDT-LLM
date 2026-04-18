# 1. Introduction

*[Target: ~1.5 pages, ~900 words. JKSUCIS style: motivation → gap → contribution list.]*

## 1.1 Background and Motivation

Large Language Models (LLMs) have rapidly advanced medical question-answering capabilities, with recent models such as GPT-4 [Nori2023], Med-PaLM 2 [Singhal2023], and open-weight alternatives reaching or surpassing human-expert performance on standardized medical examinations. These successes have prompted a growing interest in deploying LLMs as clinical decision-support tools, particularly for complex specialties such as oncology, where treatment decisions depend on the integration of pathology, molecular diagnostics, imaging, and rapidly evolving evidence-based guidelines.

However, the direct translation of benchmark-level performance to real-world clinical reasoning is far from straightforward. Single-agent LLMs exhibit three well-documented limitations that compromise their safety and reliability in high-stakes decision-making. **First**, they are prone to *hallucination*—producing confident yet factually incorrect statements, including fabricated drug doses, nonexistent clinical trials, and outdated treatment recommendations [Ji2023, Omiye2023]. **Second**, they operate from a *single epistemic perspective*, unable to spontaneously foreground the competing considerations that different medical specialties would bring to the same case. **Third**, their parametric knowledge is *temporally stale*; oncology guidelines are revised multiple times per year, and critical updates (e.g., new FDA-approved agents, shifted first-line preferences) may not be reflected in a model's weights for months or years.

Real clinical oncology practice mitigates these same risks through the **Multidisciplinary Team (MDT) meeting**, in which medical oncologists, surgeons, radiation oncologists, and pathologists jointly review each case and negotiate an evidence-grounded consensus [NCCN-MDT, ESMO-MDT]. MDT meetings are associated with measurable improvements in guideline-concordant care and patient outcomes across multiple cancer types [Pillay2016]. The structural features that make MDT effective—*role specialization*, *parallel independent reasoning*, *explicit synthesis*, and *traceable grounding in guidelines*—are precisely those missing from single-agent LLM deployments.

## 1.2 Research Gap

Two parallel lines of research have attempted to address subsets of these limitations. **Retrieval-Augmented Generation (RAG)** [Lewis2020] grounds LLM output in authoritative external documents, and recent medical variants [Zakka2024, Jeong2024] have shown reduced hallucination on factual queries. **Multi-agent LLM systems** [Hong2024, Wu2024] use role-conditioned prompts to simulate collaborative reasoning, with promising early results in medical diagnosis [Tang2023-MedAgents, Schmidgall2024-AgentClinic].

Yet three gaps persist:

1. **Limited integration.** Most existing medical LLM studies evaluate RAG *or* multi-agent reasoning in isolation. The joint effect—and the extent to which these two mechanisms are complementary or redundant—remains empirically unquantified on complex clinical decision tasks.
2. **Benchmark scope.** Public medical LLM benchmarks (MedQA, MedMCQA, USMLE) are dominated by single-best-answer multiple-choice items. They do not capture the open-ended, multidisciplinary treatment-planning reasoning that defines actual oncology MDT practice.
3. **Evaluation reliability.** Expert human scoring is the gold standard but is costly and does not scale. LLM-as-judge protocols [Zheng2023, Chiang2024] offer scalability, yet *inter-judge reliability* and robustness to judge model choice have not been systematically characterized for open-ended clinical recommendations.

## 1.3 Contributions

This work addresses these three gaps through the following contributions:

1. **MDT-LLM framework.** We propose a multi-agent LLM architecture that simulates a clinical MDT using four role-conditioned specialist agents—medical oncologist, thoracic surgeon, radiation oncologist, and pathologist/molecular specialist—whose opinions are synthesized by a dedicated moderator agent into a single consensus recommendation. The framework is integrated with a retrieval pipeline over the current NCCN clinical guidelines, enabling any combination of {single-agent, multi-agent} × {zero-shot, retrieval-augmented} to be evaluated under a unified experimental design.

2. **LungMDT-Bench-100.** We release a new benchmark of 100 expert-annotated lung cancer clinical scenarios, structured across six clinical domains (screening/diagnosis, staging/molecular, first-line therapy, subsequent/resistance, adverse events, follow-up) and three difficulty levels (easy/medium/hard). Each scenario is accompanied by a gold-standard, guideline-concordant reference answer with explicit NCCN section citations.

3. **Multi-judge evaluation protocol.** We design and deploy a two-judge LLM-as-judge protocol using judges from *different providers* (GPT-4o-mini and Claude Sonnet 4.5) to minimize single-vendor bias. We report per-dimension Cohen's weighted κ as an inter-judge reliability check, providing a reusable methodological template for future open-ended clinical LLM evaluation.

4. **Large-scale factorial study.** We evaluate four frontier LLMs spanning proprietary-commercial (GPT-4o-mini, Claude Sonnet 4.5), reasoning-specialized (DeepSeek-R1), and open-weight (Llama-3.3-70B) under a 2×2 factorial design (single/MDT × zero-shot/RAG), yielding 1,600 model responses evaluated on six scoring dimensions. We provide the first comprehensive empirical characterization of how multi-agent orchestration and retrieval augmentation interact to affect accuracy, completeness, safety, guideline concordance, and hallucination rates in complex oncology decision-making.

## 1.4 Paper Organization

Section 2 situates our work within prior research on medical LLMs, RAG, and multi-agent systems. Section 3 details the MDT-LLM architecture, benchmark construction, and LLM-as-judge evaluation protocol. Section 4 specifies the experimental setup. Section 5 reports quantitative results across models, conditions, domains, and difficulty levels. Section 6 discusses practical implications, limitations, and threats to validity. Section 7 concludes.
