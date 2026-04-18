"""
Merge all judge score CSVs into a single unified file.

Inputs:
  - outputs/validation_judge_scores.csv   (pilot: all 4 models, Q001-Q018 partial)
  - outputs/judge_gpt4omini.csv           (GPT-4o-mini, Q011-Q100)
  - outputs/judge_claude.csv              (Claude Sonnet, Q011-Q100)
  - outputs/judge_deepseek.csv            (DeepSeek R1, Q011-Q100)
  - outputs/judge_llama.csv               (Llama 3.3-70B, Q011-Q100)

Output:
  - outputs/all_judge_scores.csv          (full merged, deduplicated)

Deduplication key: (question_id, model, condition, judge)
If a tuple appears in multiple files, keep the first occurrence.
"""

import csv
import os
from pathlib import Path

INPUT_FILES = [
    "outputs/validation_judge_scores.csv",
    "outputs/judge_gpt4omini.csv",
    "outputs/judge_claude.csv",
    "outputs/judge_deepseek.csv",
    "outputs/judge_llama.csv",
]
OUTPUT_FILE = "outputs/all_judge_scores.csv"


def merge_csvs(inputs, output):
    seen = set()
    all_rows = []
    fieldnames = None

    for path in inputs:
        if not Path(path).exists():
            print(f"  ⚠ Missing: {path}")
            continue
        with open(path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if fieldnames is None:
                fieldnames = reader.fieldnames
            n_added = 0
            n_dup = 0
            for row in reader:
                key = (row["question_id"], row["model"],
                       row["condition"], row["judge"])
                if key in seen:
                    n_dup += 1
                    continue
                seen.add(key)
                all_rows.append(row)
                n_added += 1
            print(f"  {os.path.basename(path):<32} +{n_added:>4} rows "
                  f"({n_dup} dups skipped)")

    Path(output).parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"\n  Total unique: {len(all_rows)} rows")
    print(f"  Written: {output}")

    # Coverage check
    from collections import Counter
    by_mc = Counter((r["model"], r["condition"]) for r in all_rows)
    print("\n  Coverage matrix (expect 200 per cell = 100 Q × 2 judges):")
    models = sorted(set(r["model"] for r in all_rows))
    conds = sorted(set(r["condition"] for r in all_rows))
    print(f"  {'Model':<18}", *[f"{c[:12]:>13}" for c in conds])
    for m in models:
        cells = [by_mc.get((m, c), 0) for c in conds]
        marks = ["✅" if v >= 200 else "⚠" if v >= 100 else "❌" for v in cells]
        print(f"  {m:<18}", *[f"{v:>10} {mk}" for v, mk in zip(cells, marks)])


if __name__ == "__main__":
    print("Merging judge score files ...\n")
    merge_csvs(INPUT_FILES, OUTPUT_FILE)
