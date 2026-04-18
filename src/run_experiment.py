"""
Experiment Runner
==================
Runs all questions × models × conditions and saves results.
"""

import csv, json, time, os, sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import config
from src.rag_pipeline import build_index, retrieve
from src.multi_agent_mdt import single_llm_answer, mdt_discussion


def load_questions(path: str) -> list[dict]:
    """Load questions from CSV."""
    questions = []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            full_q = f"Vignette: {row['vignette']}\n\nQuestion: {row['question']}"
            row["full_question"] = full_q
            questions.append(row)
    print(f"Loaded {len(questions)} questions.")
    return questions


def _load_done_keys(path: Path) -> set:
    """Return set of (qid, model, condition) tuples already successfully written."""
    done = set()
    if not path.exists():
        return done
    with open(path) as f:
        for line in f:
            try:
                r = json.loads(line)
                # Only consider successful records (no error field)
                if "error" in r:
                    continue
                # Also exclude records where answer/consensus starts with [ERROR]
                content = r.get("answer") or r.get("consensus", "")
                if content.startswith("[ERROR]"):
                    continue
                done.add((r["question_id"], r["model"], r["condition"]))
            except Exception:
                continue
    return done


def run_experiment(
    models: list[str] = None,
    conditions: list[str] = None,
    question_ids: list[str] = None,
    resume_from: str = None,
    output: str = None,
):
    """
    Main experiment loop.
    - resume_from: read done-keys from this file (for skip detection across parallel runs)
    - output: write new records to this file (default: auto-timestamped). If omitted and
      resume_from is given, appends to resume_from (single-process safe only).
    """
    models = models or list(config.MODELS.keys())
    conditions = conditions or config.EXPERIMENT["conditions"]
    questions = load_questions(config.EXPERIMENT["questions_file"])

    if question_ids:
        questions = [q for q in questions if q["id"] in question_ids]

    # Build RAG index if needed
    vectorstore = None
    if any("rag" in c for c in conditions):
        print("\n[SETUP] Building RAG index ...")
        vectorstore = build_index()

    # Prepare output
    outdir = Path(config.EXPERIMENT["output_dir"])
    outdir.mkdir(parents=True, exist_ok=True)

    # Determine done-keys from resume file (if any) AND from output file (if different & exists)
    done_keys = set()
    if resume_from:
        done_keys |= _load_done_keys(Path(resume_from))
        print(f"\n[RESUME] {len(done_keys)} combinations already done in {resume_from}")

    if output:
        results_file = Path(output)
        if results_file.exists():
            own = _load_done_keys(results_file)
            done_keys |= own
            print(f"[RESUME] +{len(own)} more already done in own output {results_file}")
            mode = "a"
        else:
            mode = "w"
    elif resume_from:
        results_file = Path(resume_from)
        mode = "a"
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = outdir / f"results_{timestamp}.jsonl"
        mode = "w"

    total = len(questions) * len(models) * len(conditions)
    count = 0
    skipped = 0

    with open(results_file, mode) as fout:
        for q in questions:
            qid = q["id"]
            full_q = q["full_question"]

            # Get RAG context once per question (only if needed)
            rag_ctx = None
            need_rag = any(c in conditions for c in ("single_rag", "mdt_rag"))
            if need_rag and vectorstore:
                rag_ctx = retrieve(vectorstore, full_q)

            for model in models:
                for cond in conditions:
                    count += 1
                    key = (qid, model, cond)
                    if key in done_keys:
                        skipped += 1
                        continue

                    print(f"[{count}/{total}] (skip={skipped}) "
                          f"{qid} | {model} | {cond}", flush=True)

                    try:
                        if cond == "single_zeroshot":
                            result = single_llm_answer(model, full_q)
                        elif cond == "single_rag":
                            result = single_llm_answer(model, full_q, rag_ctx)
                        elif cond == "mdt_zeroshot":
                            result = mdt_discussion(model, full_q)
                        elif cond == "mdt_rag":
                            result = mdt_discussion(model, full_q, rag_ctx)
                        else:
                            continue
                    except Exception as e:
                        result = {"error": str(e)}

                    # Add metadata
                    record = {
                        "question_id": qid,
                        "domain": q["domain"],
                        "difficulty": q["difficulty"],
                        "model": model,
                        "condition": cond,
                        "gold_standard": q["gold_standard_answer"],
                        **result,
                    }

                    fout.write(json.dumps(record, ensure_ascii=False) + "\n")
                    fout.flush()

                    # Rate limiting
                    time.sleep(1)

    print(f"\n{'='*60}")
    print(f"Experiment complete. Results saved to: {results_file}")
    print(f"Processed: {count - skipped}  Skipped: {skipped}")
    return results_file


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--models", nargs="+", default=None,
                        help="Models to run (default: all)")
    parser.add_argument("--conditions", nargs="+", default=None,
                        help="Conditions to run (default: all)")
    parser.add_argument("--questions", nargs="+", default=None,
                        help="Question IDs to run (default: all)")
    parser.add_argument("--resume-from", default=None,
                        help="Path to existing JSONL file to read done-keys from (safe for parallel)")
    parser.add_argument("--output", default=None,
                        help="Output JSONL file (per-process). Safer than --resume-from alone for parallel runs.")
    args = parser.parse_args()

    run_experiment(args.models, args.conditions, args.questions,
                   resume_from=args.resume_from, output=args.output)
