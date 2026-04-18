"""
Ablation 1: Heterogeneous MDT
==============================
Different LLMs play different specialist roles.
Runs on all 100 questions × 1 config × RAG on/off.

Role assignment reflects plausible strengths:
- Medical Oncologist:   Claude Sonnet (best at nuanced therapy reasoning)
- Thoracic Surgeon:     GPT-4o-mini  (cost-efficient workhorse)
- Radiation Oncologist: Llama-3.3-70B (open-weight baseline)
- Pathologist/Molec:    DeepSeek-R1  (strong at multi-step reasoning)
- Moderator:            Claude Sonnet (synthesis needs high capability)
"""

import os
import sys
import json
import time
import csv
from pathlib import Path
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import config
from src.multi_agent_mdt import _call_llm
from src.rag_pipeline import build_index, retrieve

ROLE_MODELS = {
    "medical_oncologist": "claude-sonnet",
    "thoracic_surgeon": "gpt-4o-mini",
    "radiation_oncologist": "llama-3.3-70b",
    "pathologist": "deepseek-r1",
    "_moderator": "claude-sonnet",
}

OUTPUT = "outputs/ablation_heterogeneous.jsonl"


def heterogeneous_mdt(question: str, rag_context: str = None) -> dict:
    """Run MDT with each role played by a different model."""
    specialist_opinions = {}

    for agent_key, agent_cfg in config.MDT_AGENTS.items():
        model = ROLE_MODELS.get(agent_key, "claude-sonnet")
        ctx = (f"RETRIEVED GUIDELINES:\n{rag_context}\n\n---\n\n"
               if rag_context else "")
        user_msg = (f"{ctx}Please analyze this case from your perspective as a "
                    f"{agent_cfg['role']}:\n\n{question}")

        opinion = _call_llm(model, agent_cfg["system_prompt"], user_msg)
        specialist_opinions[agent_key] = {
            "role": agent_cfg["role"],
            "opinion": opinion,
            "model_played_by": model,
        }

    # Moderator synthesis
    opinions_text = "\n\n".join(
        f"=== {v['role']} (by {v['model_played_by']}) ===\n{v['opinion']}"
        for v in specialist_opinions.values()
    )
    mod_input = (f"SPECIALIST OPINIONS:\n\n{opinions_text}\n\n---\n\n"
                 f"CASE:\n{question}\n\n"
                 "Please synthesize a consensus MDT recommendation.")
    if rag_context:
        mod_input = f"GUIDELINES:\n{rag_context}\n\n" + mod_input

    consensus = _call_llm(
        ROLE_MODELS["_moderator"],
        config.MDT_MODERATOR_PROMPT,
        mod_input,
    )

    return {
        "specialist_opinions": specialist_opinions,
        "consensus": consensus,
        "role_models": ROLE_MODELS,
    }


def load_questions(path):
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_done_keys(path):
    done = set()
    if not Path(path).exists():
        return done
    with open(path) as f:
        for line in f:
            try:
                r = json.loads(line)
                if "error" not in r and not r.get("consensus", "").startswith("[ERROR]"):
                    done.add((r["question_id"], r["condition"]))
            except Exception:
                continue
    return done


def main():
    questions = load_questions(config.EXPERIMENT["questions_file"])
    Path(OUTPUT).parent.mkdir(parents=True, exist_ok=True)
    done = load_done_keys(OUTPUT)
    print(f"Resume: {len(done)} done, {len(questions)*2 - len(done)} remaining")

    print("Building RAG index...")
    vs = build_index()

    conditions = ["mdt_zeroshot_hetero", "mdt_rag_hetero"]
    mode = "a" if done else "w"

    with open(OUTPUT, mode) as fout:
        n = len(questions) * len(conditions)
        count = 0
        for q in questions:
            qid = q["id"]
            full_q = f"Vignette: {q['vignette']}\n\nQuestion: {q['question']}"
            rag_ctx = retrieve(vs, full_q)

            for cond in conditions:
                count += 1
                if (qid, cond) in done:
                    continue
                print(f"[{count}/{n}] {qid} | {cond}", flush=True)

                try:
                    use_rag = "rag" in cond
                    result = heterogeneous_mdt(
                        full_q,
                        rag_context=rag_ctx if use_rag else None,
                    )
                except Exception as e:
                    result = {"error": str(e)}

                rec = {
                    "question_id": qid,
                    "domain": q["domain"],
                    "difficulty": q["difficulty"],
                    "model": "heterogeneous",
                    "condition": cond,
                    "gold_standard": q["gold_standard_answer"],
                    **result,
                }
                fout.write(json.dumps(rec, ensure_ascii=False) + "\n")
                fout.flush()
                time.sleep(0.5)

    print(f"\n✅ Complete: {OUTPUT}")


if __name__ == "__main__":
    main()
