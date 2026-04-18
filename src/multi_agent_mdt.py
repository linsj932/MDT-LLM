"""
Multi-Agent MDT (Multidisciplinary Tumor Board) System
=======================================================
Simulates a lung cancer MDT with four specialist agents
who each analyze a case, followed by a moderator who
synthesizes a consensus recommendation.

Supports both OpenAI-compatible APIs and Anthropic Claude API.
"""

from openai import OpenAI
import anthropic
import config


# ── Client cache (avoid re-creating per call) ────────────────────
_clients = {}


def _get_client(model_name: str):
    """Return (client, provider) for the given model, cached."""
    if model_name in _clients:
        return _clients[model_name]

    mcfg = config.MODELS[model_name]
    api_key = getattr(config, mcfg["api_key_var"])
    provider = mcfg["provider"]

    if provider == "anthropic":
        client = anthropic.Anthropic(api_key=api_key)
    else:  # openai-compatible
        client = OpenAI(api_key=api_key, base_url=mcfg["base_url"])

    _clients[model_name] = (client, provider)
    return client, provider


def _call_llm(model_name: str, system: str, user: str) -> str:
    """
    Single LLM call with error handling.
    Dispatches to OpenAI or Anthropic SDK based on provider config.
    """
    mcfg = config.MODELS[model_name]
    client, provider = _get_client(model_name)

    try:
        if provider == "anthropic":
            resp = client.messages.create(
                model=mcfg["model_id"],
                max_tokens=config.EXPERIMENT["max_tokens"],
                temperature=config.EXPERIMENT["temperature"],
                system=system,
                messages=[
                    {"role": "user", "content": user},
                ],
            )
            return resp.content[0].text.strip()
        else:
            # OpenAI-compatible (GPT-4o, DeepSeek, Together/Llama, etc.)
            resp = client.chat.completions.create(
                model=mcfg["model_id"],
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                temperature=config.EXPERIMENT["temperature"],
                max_tokens=config.EXPERIMENT["max_tokens"],
            )
            return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"[ERROR] {e}"


def single_llm_answer(
    model_name: str,
    question: str,
    rag_context: str = None,
) -> dict:
    """Get answer from a single LLM (zero-shot or RAG)."""
    system = (
        "You are a board-certified oncologist specializing in lung cancer. "
        "Answer the following clinical question based on current evidence-based "
        "guidelines. Provide a clear recommendation with reasoning."
    )

    if rag_context:
        user = (
            f"Based on the following clinical guideline excerpts:\n\n"
            f"{rag_context}\n\n"
            f"---\n\nClinical Question:\n{question}"
        )
    else:
        user = f"Clinical Question:\n{question}"

    answer = _call_llm(model_name, system, user)
    return {
        "model": model_name,
        "mode": "single_rag" if rag_context else "single_zeroshot",
        "answer": answer,
    }


def mdt_discussion(
    model_name: str,
    question: str,
    rag_context: str = None,
) -> dict:
    """Run full MDT discussion: 4 specialists → moderator consensus."""

    # ── Phase 1: Individual specialist opinions ───────────────────
    specialist_opinions = {}
    for agent_key, agent_cfg in config.MDT_AGENTS.items():
        if rag_context:
            user_msg = (
                f"The following clinical guideline excerpts are available for "
                f"reference:\n\n{rag_context}\n\n---\n\n"
                f"Please analyze this case from your perspective as a "
                f"{agent_cfg['role']}:\n\n{question}"
            )
        else:
            user_msg = (
                f"Please analyze this case from your perspective as a "
                f"{agent_cfg['role']}:\n\n{question}"
            )

        opinion = _call_llm(
            model_name, agent_cfg["system_prompt"], user_msg
        )
        specialist_opinions[agent_key] = {
            "role": agent_cfg["role"],
            "opinion": opinion,
        }

    # ── Phase 2: Moderator synthesis ──────────────────────────────
    opinions_text = "\n\n".join(
        [f"=== {v['role']} ===\n{v['opinion']}"
         for v in specialist_opinions.values()]
    )

    moderator_input = (
        f"The following specialist opinions have been provided for this case:\n\n"
        f"{opinions_text}\n\n"
        f"---\n\nOriginal clinical question:\n{question}\n\n"
        f"Please synthesize a consensus MDT recommendation."
    )

    consensus = _call_llm(
        model_name,
        config.MDT_MODERATOR_PROMPT,
        moderator_input,
    )

    return {
        "model": model_name,
        "mode": "mdt_rag" if rag_context else "mdt_zeroshot",
        "specialist_opinions": specialist_opinions,
        "consensus": consensus,
    }


if __name__ == "__main__":
    # Quick test with one question
    test_q = (
        "Vignette: A 62-year-old male with newly diagnosed stage IV lung "
        "adenocarcinoma, EGFR exon 19 deletion positive, PD-L1 TPS 80%, "
        "ECOG PS 1, no brain metastases.\n\n"
        "Question: What is the recommended first-line systemic therapy?"
    )

    # Test each available model
    for model_name in config.MODELS:
        api_key = getattr(config, config.MODELS[model_name]["api_key_var"])
        if not api_key or api_key.startswith("sk-...") or api_key.startswith("sk-ant-..."):
            print(f"\n⏭ Skipping {model_name} (no API key)")
            continue
        print(f"\n=== Testing {model_name} (single, zero-shot) ===")
        result = single_llm_answer(model_name, test_q)
        print(result["answer"][:500])
