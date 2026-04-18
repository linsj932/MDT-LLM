"""
Enhanced MDT Agent Framework v2
================================
Upgrades over the baseline MDT:
  1. **Debate rounds**: after independent opinions, specialists see each
     other's views and can revise (2-turn Delphi-style consensus).
  2. **Confidence reporting**: each specialist outputs an explicit
     confidence score (1-5) along with their recommendation.
  3. **Adaptive retrieval**: specialists can issue their own follow-up
     retrieval queries after their initial draft.
  4. **Heterogeneous mode**: different LLMs can play different roles.
  5. **Uncertainty-aware moderator**: weights specialist opinions by
     their reported confidence when synthesizing.
"""

import os
import sys
import json
import re
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import config
from src.multi_agent_mdt import _call_llm
from src.rag_pipeline import retrieve


# =======================================================
# Prompt templates
# =======================================================
SPECIALIST_CONFIDENCE_SUFFIX = """

---
FORMAT YOUR RESPONSE AS JSON:
{
  "analysis": "<your clinical analysis from the perspective of your role>",
  "recommendation": "<your specific recommendation>",
  "confidence": <integer 1-5, where 1=very uncertain, 5=highly confident>,
  "key_concerns": "<any safety flags or caveats>",
  "follow_up_query": "<a guideline retrieval query you'd like to issue, or 'none'>"
}

Return ONLY the JSON object, no other text.
"""

DEBATE_PROMPT = """\
In phase 1 you gave the following analysis:

=== YOUR PRIOR ANALYSIS ===
{prior_opinion}

=== OTHER SPECIALISTS' ANALYSES ===
{other_opinions}

Now, having seen your colleagues' input, you may optionally REVISE your
analysis. Only revise if the other specialists raise a clinical point you
missed or had weighed incorrectly. If your original view stands, say so briefly.

Respond in JSON:
{{
  "revised_analysis": "<revised or confirmed analysis>",
  "revised_recommendation": "<revised or confirmed recommendation>",
  "revised_confidence": <integer 1-5>,
  "changed_mind": <true|false>,
  "what_changed": "<if changed_mind is true, explain briefly>"
}}

Return ONLY the JSON object.
"""

UNCERTAINTY_MODERATOR_PROMPT = """\
You are the MDT coordinator chairing a multidisciplinary tumor board for
lung cancer. You have received FINAL opinions from four specialists, each
with a self-reported confidence score (1-5).

When specialists DISAGREE, weight higher-confidence opinions more heavily.
When confidence is uniformly low, explicitly acknowledge the clinical
uncertainty and recommend additional workup or expert consultation.

Synthesize a unified consensus. State:
(1) the agreed treatment plan with specific drugs/doses/schedules;
(2) any lingering points of disagreement AND how you resolved them (citing
    confidence scores if relevant);
(3) overall team-level confidence in the recommendation (1-5);
(4) recommended follow-up and monitoring;
(5) any clinical flags that warrant escalation.

Cite relevant NCCN/ESMO guidelines inline where possible.
"""


# =======================================================
# Helpers
# =======================================================
def _parse_json(raw: str) -> dict:
    """Extract and parse JSON from possibly messy LLM output."""
    if not raw or raw.startswith("[ERROR]"):
        return {"_error": raw}
    m = re.search(r"\{[\s\S]*\}", raw)
    if not m:
        return {"_error": f"no JSON in: {raw[:150]}"}
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError as e:
        return {"_error": f"parse: {e}; raw={raw[:150]}"}


def _format_opinions(opinions: dict) -> str:
    parts = []
    for role, info in opinions.items():
        a = info.get("analysis", "")
        rec = info.get("recommendation", "")
        conf = info.get("confidence", "?")
        parts.append(f"=== {role} (confidence={conf}/5) ===\n"
                     f"Analysis: {a}\nRecommendation: {rec}")
    return "\n\n".join(parts)


# =======================================================
# Enhanced MDT
# =======================================================
def enhanced_mdt_discussion(
    question: str,
    primary_model: str = "claude-sonnet",
    role_models: Optional[dict] = None,
    rag_vectorstore=None,
    rag_context: Optional[str] = None,
    enable_debate: bool = True,
    enable_adaptive_retrieval: bool = False,
    use_confidence_weighting: bool = True,
) -> dict:
    """
    Run an enhanced MDT discussion.

    Parameters
    ----------
    primary_model : str
        Default model for all roles (homogeneous MDT).
    role_models : dict or None
        If given, maps role_key -> model name (heterogeneous MDT).
        Example: {"medical_oncologist": "claude-sonnet",
                  "thoracic_surgeon": "deepseek-r1", ...,
                  "_moderator": "gpt-4o-mini"}
    rag_vectorstore : FAISS or None
        If provided with enable_adaptive_retrieval, specialists can issue
        follow-up queries.
    rag_context : str or None
        Static RAG context injected into all prompts.
    enable_debate : bool
        If True, run a phase-2 revision round where specialists can revise
        after seeing each other's views.
    use_confidence_weighting : bool
        If True, the moderator is instructed to weight by confidence.
    """
    # --- Resolve which model plays each role ---
    role_models = role_models or {}
    get_model = lambda role: role_models.get(role, primary_model)

    result = {
        "question": question,
        "mode": "enhanced_mdt",
        "phase1_opinions": {},
        "phase2_revisions": {},
        "consensus": None,
        "meta": {
            "primary_model": primary_model,
            "role_models": role_models,
            "enable_debate": enable_debate,
            "use_confidence_weighting": use_confidence_weighting,
        },
    }

    # --- PHASE 1: Independent specialists with confidence ---
    phase1 = {}
    for role_key, role_cfg in config.MDT_AGENTS.items():
        role = role_cfg["role"]
        system = role_cfg["system_prompt"] + "\n\nWhen responding, include a confidence score."
        ctx_block = f"\n\nRETRIEVED GUIDELINES:\n{rag_context}\n" if rag_context else ""
        user = (f"Please analyze this case from your perspective as {role}."
                f"{ctx_block}\n\nCASE:\n{question}"
                + SPECIALIST_CONFIDENCE_SUFFIX)

        raw = _call_llm(get_model(role_key), system, user)
        parsed = _parse_json(raw)
        phase1[role] = parsed

    result["phase1_opinions"] = phase1

    # --- Optional PHASE 1.5: Adaptive retrieval ---
    if enable_adaptive_retrieval and rag_vectorstore is not None:
        adaptive_context = []
        for role, info in phase1.items():
            q = info.get("follow_up_query")
            if q and q.lower() not in ("none", "n/a", ""):
                ctx = retrieve(rag_vectorstore, q, top_k=3)
                adaptive_context.append(f"[{role} asked: {q}]\n{ctx}")
        adaptive_ctx_text = "\n\n---\n\n".join(adaptive_context)
        result["adaptive_retrieval_context"] = adaptive_ctx_text
    else:
        adaptive_ctx_text = ""

    # --- PHASE 2: Debate / revision ---
    phase2 = {}
    if enable_debate:
        for role_key, role_cfg in config.MDT_AGENTS.items():
            role = role_cfg["role"]
            my_prior = phase1.get(role, {})
            others = {r: op for r, op in phase1.items() if r != role}

            system = role_cfg["system_prompt"]
            prior_text = json.dumps(my_prior, indent=2, ensure_ascii=False)
            others_text = _format_opinions(others)

            user = DEBATE_PROMPT.format(
                prior_opinion=prior_text,
                other_opinions=others_text,
            )
            if adaptive_ctx_text:
                user = (f"ADDITIONAL RETRIEVED CONTEXT:\n{adaptive_ctx_text}\n\n"
                        + user)

            raw = _call_llm(get_model(role_key), system, user)
            parsed = _parse_json(raw)
            phase2[role] = parsed

    result["phase2_revisions"] = phase2

    # --- PHASE 3: Uncertainty-aware moderator synthesis ---
    # Use phase-2 revisions if debate was run, else phase-1
    final_opinions = phase2 if enable_debate else phase1

    def summarize_for_moderator(role, op):
        if enable_debate:
            return (f"=== {role} ===\n"
                    f"Analysis: {op.get('revised_analysis','')}\n"
                    f"Recommendation: {op.get('revised_recommendation','')}\n"
                    f"Confidence: {op.get('revised_confidence','?')}/5\n"
                    f"Changed mind: {op.get('changed_mind', False)}")
        else:
            return (f"=== {role} (confidence={op.get('confidence','?')}/5) ===\n"
                    f"Analysis: {op.get('analysis','')}\n"
                    f"Recommendation: {op.get('recommendation','')}")

    opinions_block = "\n\n".join(
        summarize_for_moderator(r, op) for r, op in final_opinions.items()
    )

    moderator_system = UNCERTAINTY_MODERATOR_PROMPT if use_confidence_weighting \
        else config.MDT_MODERATOR_PROMPT

    moderator_user = (
        f"FINAL SPECIALIST OPINIONS:\n\n{opinions_block}\n\n"
        f"---\n\nORIGINAL CASE:\n{question}\n\n"
        "Please synthesize the consensus MDT recommendation."
    )
    if rag_context or adaptive_ctx_text:
        extra = adaptive_ctx_text or rag_context or ""
        moderator_user = f"GUIDELINE CONTEXT:\n{extra}\n\n" + moderator_user

    consensus = _call_llm(
        get_model("_moderator"),
        moderator_system,
        moderator_user,
    )
    result["consensus"] = consensus

    return result


# =======================================================
# Quick demo
# =======================================================
if __name__ == "__main__":
    q = ("Vignette: A 62-year-old male with newly diagnosed stage IV lung "
         "adenocarcinoma, EGFR exon 19 deletion positive, PD-L1 TPS 80%, "
         "ECOG PS 1, no brain metastases.\n\n"
         "Question: What is the recommended first-line systemic therapy?")

    print("=== Enhanced MDT (homogeneous, Claude, with debate) ===\n")
    r = enhanced_mdt_discussion(
        q,
        primary_model="claude-sonnet",
        enable_debate=True,
        use_confidence_weighting=True,
    )
    print("\nPhase 1 confidences:")
    for role, op in r["phase1_opinions"].items():
        print(f"  {role}: confidence={op.get('confidence', '?')}")
    print("\nPhase 2 changes:")
    for role, op in r["phase2_revisions"].items():
        changed = op.get("changed_mind")
        new_conf = op.get("revised_confidence")
        print(f"  {role}: changed_mind={changed}, new_confidence={new_conf}")
    print(f"\nConsensus preview ({len(r['consensus'])} chars):")
    print(r['consensus'][:800])
