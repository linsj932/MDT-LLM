"""
Ablation 2: Enhanced MDT with Debate + Confidence
==================================================
Runs enhanced_mdt_discussion on 100 questions × 2 strong models
(Claude, DeepSeek-R1) to test whether debate & confidence weighting
provides meaningful gains over the baseline MDT.
"""

import os
import sys
import json
import time
import csv
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import config
from src.enhanced_mdt import enhanced_mdt_discussion
from src.rag_pipeline import build_index, retrieve

MODELS = ["claude-sonnet", "deepseek-r1"]  # strong-model subset
OUTPUT = "outputs/ablation_enhanced.jsonl"


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
                if "error" not in r and r.get("consensus"):
                    done.add((r["question_id"], r["model"], r["condition"]))
            except Exception:
                continue
    return done


def main():
    questions = load_questions(config.EXPERIMENT["questions_file"])
    Path(OUTPUT).parent.mkdir(parents=True, exist_ok=True)
    done = load_done_keys(OUTPUT)

    conditions = [
        "enhanced_mdt_zeroshot",  # with debate + confidence weighting, no RAG
        "enhanced_mdt_rag",       # with debate + confidence weighting + RAG
    ]
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
            rag_ctx = retrieve(vs, full_q)

            for model in MODELS:
                for cond in conditions:
                    count += 1
                    if (qid, model, cond) in done:
                        continue
                    print(f"[{count}/{total}] {qid} | {model} | {cond}", flush=True)

                    try:
                        result = enhanced_mdt_discussion(
                            full_q,
                            primary_model=model,
                            rag_context=rag_ctx if "rag" in cond else None,
                            enable_debate=True,
                            use_confidence_weighting=True,
                        )
                    except Exception as e:
                        result = {"error": str(e), "consensus": ""}

                    rec = {
                        "question_id": qid,
                        "domain": q["domain"],
                        "difficulty": q["difficulty"],
                        "model": model,
                        "condition": cond,
                        "gold_standard": q["gold_standard_answer"],
                        "phase1_opinions": result.get("phase1_opinions"),
                        "phase2_revisions": result.get("phase2_revisions"),
                        "consensus": result.get("consensus", ""),
                    }
                    fout.write(json.dumps(rec, ensure_ascii=False) + "\n")
                    fout.flush()
                    time.sleep(0.5)

    print(f"\n✅ Complete: {OUTPUT}")


if __name__ == "__main__":
    main()
