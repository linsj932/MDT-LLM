"""
Generate Blinded Evaluation Sheet
===================================
Reads experiment results (JSONL) and produces a randomized,
blinded CSV for expert evaluation.
"""

import json, random, csv, sys, os
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


def generate_eval_sheet(results_jsonl: str, output_csv: str, seed: int = 42):
    """Convert raw results to blinded evaluation CSV."""
    records = []
    with open(results_jsonl) as f:
        for line in f:
            r = json.loads(line)
            # For MDT conditions, use the consensus answer
            answer = r.get("consensus") or r.get("answer", "")
            records.append({
                "question_id": r["question_id"],
                "domain": r["domain"],
                "difficulty": r["difficulty"],
                "gold_standard": r["gold_standard"],
                "question": r.get("full_question", ""),
                "model": r["model"],
                "condition": r["condition"],
                "response": answer,
            })

    # Shuffle for blinding
    random.seed(seed)
    random.shuffle(records)

    # Assign blinded IDs
    for i, rec in enumerate(records):
        rec["eval_id"] = f"EVAL_{i+1:04d}"

    # Write evaluation CSV (blinded: model/condition columns hidden for evaluator)
    fieldnames = [
        "eval_id", "question_id", "domain", "difficulty",
        "gold_standard", "response",
        "accuracy", "completeness", "safety", "concordance",
        "hallucination", "safety_violation", "notes",
        # Hidden columns (for analysis, not shown to evaluator)
        "_model", "_condition",
    ]

    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for rec in records:
            writer.writerow({
                "eval_id": rec["eval_id"],
                "question_id": rec["question_id"],
                "domain": rec["domain"],
                "difficulty": rec["difficulty"],
                "gold_standard": rec["gold_standard"],
                "response": rec["response"],
                "accuracy": "",
                "completeness": "",
                "safety": "",
                "concordance": "",
                "hallucination": "",
                "safety_violation": "",
                "notes": "",
                "_model": rec["model"],
                "_condition": rec["condition"],
            })

    print(f"Generated blinded evaluation sheet: {output_csv}")
    print(f"Total responses to evaluate: {len(records)}")
    print("Instruction: Hide _model and _condition columns before sharing.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_eval_sheet.py <results.jsonl> [output.csv]")
        sys.exit(1)
    results = sys.argv[1]
    output = sys.argv[2] if len(sys.argv) > 2 else "outputs/eval_sheet_blinded.csv"
    generate_eval_sheet(results, output)
