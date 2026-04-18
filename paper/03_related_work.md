# 2. Related Work

*[Target: ~1.5 pages. 4 subsections ending with explicit "gap" statements pointing to our contribution.]*

## 2.1 LLMs for Clinical Decision Support

The clinical application of LLMs has progressed rapidly over the past three years. **Med-PaLM** [Singhal2022] and **Med-PaLM 2** [Singhal2023] demonstrated expert-level performance on the MedQA-USMLE benchmark, with Med-PaLM 2 reaching 86.5% accuracy, approaching practicing-clinician performance. **GPT-4** and its successors extended these capabilities to a broader array of medical tasks, with **Nori et al.** [Nori2023] showing that GPT-4 exceeds the passing threshold on USMLE without domain-specific fine-tuning.

Subsequent work has applied LLMs to increasingly specialized tasks: diagnostic differential generation [McDuff2024], radiology report synthesis [Liu2023-Radiology], clinical summarization [VanVeen2024], and patient communication [Ayers2023]. In oncology specifically, LLMs have been evaluated on treatment recommendations for breast cancer [Sorin2024], general tumor-board questions [Schulte2023], and molecular-tumor-board decisions [Benary2023].

Three consistent findings emerge across these studies. First, LLM accuracy varies sharply with task complexity: models that score well on multiple-choice benchmarks degrade on open-ended treatment-planning questions. Second, LLMs frequently produce plausible but outdated or fabricated recommendations when asked about recent therapeutic advances—a phenomenon particularly dangerous in oncology where first-line therapy can change within a single year. Third, single-model evaluations consistently underperform multi-model ensembles, suggesting that architectural diversity matters as much as raw model capability.

**Gap.** Prior oncology-focused LLM studies have evaluated models almost exclusively as single agents answering isolated questions. The specific reasoning structure of a multidisciplinary tumor board—parallel specialist perspectives followed by explicit consensus synthesis—has not been systematically simulated or benchmarked.

## 2.2 Retrieval-Augmented Generation

Retrieval-Augmented Generation was introduced by **Lewis et al.** [Lewis2020] as a mechanism for grounding generative outputs in non-parametric, updateable knowledge stores. In the general NLP setting, RAG has become a de facto standard for reducing hallucination and incorporating out-of-distribution knowledge [Gao2024-RAG-Survey].

Medical RAG variants have evolved along three axes. **Almanac** [Zakka2024] grounds clinical queries in curated peer-reviewed sources and demonstrated reduced hallucination on factual queries in a randomized evaluation. **Clinfo.ai** [Lozano2023] integrates live PubMed retrieval into a clinician-facing interface. **Medical-specific embedding models** such as MedCPT [Jin2023] and **BMRetriever** [Xu2024] have been developed to improve the semantic fidelity of clinical document retrieval.

Yet several design choices remain under-examined. **(a)** Most medical RAG papers use simple top-k retrieval with dense embeddings; the sensitivity of downstream answer quality to chunk size, overlap, and retrieval depth is rarely ablated. **(b)** RAG evaluations typically compare RAG-augmented outputs against zero-shot baselines in a single-agent setting; the interaction between RAG and multi-agent reasoning has not been characterized. **(c)** The question of which authoritative corpora to retrieve from (primary literature vs. guidelines) is often decided pragmatically rather than empirically.

**Gap.** The interaction between retrieval augmentation and multi-agent architectural patterns is empirically unquantified on guideline-concordant treatment-planning tasks.

## 2.3 Multi-Agent LLM Systems

Multi-agent LLM frameworks use a single underlying LLM with multiple role-conditioned prompts (or, less commonly, multiple different underlying LLMs) to produce specialized outputs that are subsequently combined. Early influential systems include **CAMEL** [Li2023-CAMEL], **AutoGen** [Wu2024-AutoGen], and **MetaGPT** [Hong2024-MetaGPT], each demonstrating that role specialization improves performance on software-engineering and general reasoning benchmarks.

In medicine, **MedAgents** [Tang2023-MedAgents] organizes LLM agents as a panel of medical specialists for diagnostic question-answering, showing measurable improvements over single-LLM baselines on MedQA. **AgentClinic** [Schmidgall2024-AgentClinic] simulates patient-doctor dialogues with separate agents for patient, physician, and measurement modalities. **MedCo** [Wei2024-MedCo] explores consensus-building among diagnostic agents. **KG4Diagnosis** [Liu2024-KG4Diagnosis] integrates knowledge-graph retrieval with multi-agent diagnosis.

Existing work has several shared characteristics that limit direct applicability to the clinical MDT setting. Most systems focus on **diagnosis rather than treatment planning**—diagnostic reasoning is more amenable to pattern-matching over findings, while treatment planning requires integration of evolving evidence and multidisciplinary trade-offs. The **role specialization** tends to be artificial (e.g., "general medical expert 1/2/3") rather than mapped to real-world clinical specialties. The **synthesis mechanism** is often a simple majority vote or unweighted concatenation, rather than a dedicated moderator-style synthesis that reflects actual tumor-board practice.

**Gap.** A multi-agent LLM framework explicitly modeled on the role composition and synthesis structure of clinical MDT meetings, evaluated on treatment-planning tasks rather than diagnostic classification, has not been reported.

## 2.4 Evaluation Methodologies for Medical LLMs

Evaluating LLM outputs on open-ended clinical questions is methodologically challenging. Reference-based automatic metrics (BLEU, ROUGE) correlate poorly with clinical correctness [Liu2023-Evaluation]. **Human expert scoring** remains the gold standard but is expensive and low-throughput. **LLM-as-judge** protocols, popularized by **Zheng et al.** [Zheng2023-MTBench] and **Chiang et al.** [Chiang2024], scale evaluation by using a strong LLM to score open-ended responses against a rubric, with reported correlations to human expert scores of 0.6–0.85.

LLM-as-judge has been applied in clinical settings by **Lievin et al.** [Lievin2024] and others, generally with a single judge model. Two methodological concerns persist. **(a) Single-judge bias:** a judge drawn from the same model family as a candidate may exhibit preferential scoring. **(b) Reliability characterization:** the inter-judge agreement across different LLM judges on open-ended clinical responses has not been systematically quantified.

**Gap.** A two-judge (cross-provider) LLM-as-judge protocol with explicit inter-judge reliability reporting, tailored to open-ended clinical recommendation tasks, would enable more trustworthy and reproducible LLM evaluations at scale.

---

## Summary of Positioning

Our work is, to our knowledge, the first to jointly address all four gaps: **(i)** we simulate the specific role composition and synthesis structure of clinical MDT rather than generic multi-agent reasoning; **(ii)** we ablate the joint and marginal effects of multi-agent architecture and retrieval augmentation in a factorial design; **(iii)** we evaluate on treatment-planning questions with gold-standard guideline-concordant answers, not multiple-choice or diagnostic classification; **(iv)** we deploy a multi-judge cross-provider evaluation protocol and report inter-judge reliability as a first-class methodological contribution.
