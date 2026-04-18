"""
Ablation 3: RAG top-k Sensitivity
==================================
Tests whether the observed "RAG hurts" finding is robust to retrieval depth.
Runs single_rag on 100 questions × 2 strong models × k ∈ {1, 3, 10}
(we already have k=5 data from the main experiment).
"""

import os
import sys
import json
import time
import csv
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import config
from src.multi_agent_mdt import single_llm_answer
from src.rag_pipeline import build_index, retrieve

MODELS = ["claude-sonnet", "deepseek-r1"]
K_VALUES = [1, 3, 10]  # baseline k=5 is already in main experiment
OUTPUT = "outputs/ablation_rag_topk.jsonl"


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
                if "error" not in r and not r.get("answer", "").startswith("[ERROR]"):
                    done.add((r["question_id"], r["model"], r["condition"]))
            except Exception:
                continue
    return done


def main():
    questions = load_questions(config.EXPERIMENT["questions_file"])
    Path(OUTPUT).parent.mkdir(parents=True, exist_ok=True)
    done = load_done_keys(OUTPUT)

    conditions = [f"single_rag_k{k}" for k in K_VALUES]
    total = len(questions) * len(MODELS) * len(conditions)
    print(f"Total combos: {total}. Already done: {len(done)}. "
          f"Remaining: {total - len(done)}")

    print("Building RAG index...")
    vs = build_index()

    mode = "a" if done else "w"
    with open(OUTPUT, mode) as fout:
        count = 0
        for q in questions:
            qid = q["id"]
            full_q = f"Vignette: {q['vignette']}\n\nQuestion: {q['question']}"

            # Retrieve once per k value (saves time)
            rag_ctx_by_k = {k: retrieve(vs, full_q, top_k=k) for k in K_VALUES}

            for model in MODELS:
                for k in K_VALUES:
                    cond = f"single_rag_k{k}"
                    count += 1
                    if (qid, model, cond) in done:
                        continue
                    print(f"[{count}/{total}] {qid} | {model} | {cond}", flush=True)

                    try:
                        result = single_llm_answer(
                            model, full_q, rag_context=rag_ctx_by_k[k]
                        )
                    except Exception as e:
                        result = {"error": str(e), "answer": ""}

                    rec = {
                        "question_id": qid,
                        "domain": q["domain"],
                        "difficulty": q["difficulty"],
                        "model": model,
                        "condition": cond,
                        "top_k": k,
                        "gold_standard": q["gold_standard_answer"],
                        **{k_: v_ for k_, v_ in result.items() if k_ != "mode"},
                    }
                    fout.write(json.dumps(rec, ensure_ascii=False) + "\n")
                    fout.flush()
                    time.sleep(0.3)

    print(f"\n✅ Complete: {OUTPUT}")


if __name__ == "__main__":
    main()
