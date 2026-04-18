"""
Case Study & Error Analysis
============================
Produces two artifacts:
  1. outputs/case_studies.md — 3 representative cases showing
     qualitative differences across conditions (for paper Appendix E).
  2. outputs/error_taxonomy.csv — failure-mode classification by scanning
     low-scoring responses across all 1600 records.
"""

import os, sys, json, csv, re
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import pandas as pd

# ---------- Paths ----------
JSONL_FILES = [
    "outputs/results_20260416_122622.jsonl",
    "outputs/run_gpt4omini.jsonl",
    "outputs/run_claude.jsonl",
    "outputs/run_deepseek.jsonl",
    "outputs/run_llama.jsonl",
]
SCORES_FILE = "outputs/all_judge_scores.csv"
QUESTIONS_FILE = "all_100_questions.csv"


# ---------- Helpers ----------
def load_all_responses():
    records = {}  # (qid, model, cond) -> record
    for path in JSONL_FILES:
        if not Path(path).exists():
            continue
        with open(path) as f:
            for line in f:
                try:
                    r = json.loads(line)
                    key = (r["question_id"], r["model"], r["condition"])
                    records[key] = r
                except Exception:
                    pass
    return records


def load_questions():
    qmap = {}
    with open(QUESTIONS_FILE) as f:
        for row in csv.DictReader(f):
            qmap[row["id"]] = row
    return qmap


def load_scores():
    df = pd.read_csv(SCORES_FILE)
    for c in ["accuracy", "completeness", "safety", "concordance",
              "hallucination", "safety_violation"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["mean_score"] = df[["accuracy", "completeness", "safety", "concordance"]].mean(axis=1)
    return df


# =======================================================
# PART 1: Case Studies
# =======================================================
def select_case_studies(scores_df, responses, qmap):
    """
    Pick 3 representative cases:
      A. Large MDT benefit (one where mdt_rag >> single_zs)
      B. RAG harm case (single_rag << single_zs)
      C. Judge disagreement case (high variance across judges)
    """
    # A: biggest MDT+RAG improvement over single_zs
    pivot = scores_df.pivot_table(
        index=["question_id", "model"],
        columns="condition", values="mean_score", aggfunc="mean",
    ).reset_index()

    # filter Claude (strongest model) for interpretable cases
    pivot_c = pivot[pivot["model"] == "claude-sonnet"].copy()
    pivot_c["mdt_rag_gain"] = pivot_c["mdt_rag"] - pivot_c["single_zeroshot"]
    pivot_c["rag_harm"] = pivot_c["single_zeroshot"] - pivot_c["single_rag"]

    # Judge disagreement: compute per-question judge variance on mean_score
    jvar = (scores_df.groupby(["question_id", "model", "condition"])["mean_score"]
                    .std().reset_index(name="judge_std"))
    jvar_c = jvar[jvar["model"] == "claude-sonnet"]

    # Pick case A
    case_a_qid = pivot_c.sort_values("mdt_rag_gain", ascending=False).iloc[0]["question_id"]
    # Pick case B
    case_b_qid = pivot_c.sort_values("rag_harm", ascending=False).iloc[0]["question_id"]
    # Pick case C
    case_c_qid = jvar_c.sort_values("judge_std", ascending=False).iloc[0]["question_id"]

    return case_a_qid, case_b_qid, case_c_qid


def format_case_study(qid, responses, qmap, scores_df, title):
    q = qmap[qid]
    lines = [f"## Case {title}: {qid} ({q['domain']}, {q['difficulty']})\n"]
    lines.append(f"### Vignette")
    lines.append(f"> {q['vignette']}\n")
    lines.append(f"### Question")
    lines.append(f"> {q['question']}\n")
    lines.append(f"### Gold-standard answer")
    lines.append(f"> {q['gold_standard_answer']}\n")
    lines.append(f"### Model responses (Claude Sonnet across 4 conditions)\n")

    # Show Claude's responses under each condition
    model = "claude-sonnet"
    for cond in ["single_zeroshot", "single_rag", "mdt_zeroshot", "mdt_rag"]:
        rec = responses.get((qid, model, cond))
        if not rec:
            continue
        ans = rec.get("consensus") or rec.get("answer", "")
        # Score summary
        sub = scores_df[(scores_df.question_id == qid) &
                        (scores_df.model == model) &
                        (scores_df.condition == cond)]
        if len(sub):
            score_avg = sub["mean_score"].mean()
            halluc = sub["hallucination"].max()
            lines.append(f"#### {cond.replace('_', ' ').title()} "
                         f"— mean score **{score_avg:.2f}/5**, hallucination={int(halluc)}")
        else:
            lines.append(f"#### {cond}")
        # Truncate long responses
        preview = ans[:1500] + ("\n\n[... truncated ...]" if len(ans) > 1500 else "")
        lines.append(f"```\n{preview}\n```\n")

    return "\n".join(lines)


# =======================================================
# PART 2: Error taxonomy
# =======================================================
# Keyword heuristics for common failure modes
ERROR_PATTERNS = {
    "missing_driver_mutation_priority": [
        r"pembrolizumab.*first.line|first.line.*pembrolizumab|"
        r"immunotherapy first|atezolizumab first",
    ],
    "vague_dosing": [
        r"standard dose|appropriate dose|usual dose",
    ],
    "no_guideline_citation": None,  # computed separately
    "fabricated_trial": [
        r"(LUNG|STAR|TRIAL)-\d{3,4}|NCT\d{8}",  # heuristic; need manual review
    ],
    "missing_molecular_testing": [
        r"no molecular|molecular testing not",
    ],
    "outdated_regimen": [
        r"gefitinib\s+(first.line|is recommended)|erlotinib\s+monotherapy\s+is\s+standard",
    ],
}


def classify_errors(text):
    """Return list of error flags based on heuristic pattern matches."""
    flags = []
    for flag, patterns in ERROR_PATTERNS.items():
        if patterns is None:
            continue
        for pat in patterns:
            if re.search(pat, text, re.IGNORECASE):
                flags.append(flag)
                break
    # No-guideline-citation
    if not re.search(r"NCCN|ESMO|ASCO|FDA|category\s+[12]", text, re.IGNORECASE):
        flags.append("no_guideline_citation")
    return flags


def error_analysis(scores_df, responses):
    """Scan low-scoring responses for error patterns."""
    # Low-scoring = mean_score < 3.5
    low = scores_df[scores_df["mean_score"] < 3.5]
    # Get unique (qid, model, cond) tuples that scored low
    low_keys = set(zip(low["question_id"], low["model"], low["condition"]))

    tally = Counter()
    examples = defaultdict(list)

    for key in low_keys:
        rec = responses.get(key)
        if not rec:
            continue
        text = rec.get("consensus") or rec.get("answer", "")
        flags = classify_errors(text)
        for fl in flags:
            tally[fl] += 1
            if len(examples[fl]) < 3:
                examples[fl].append({
                    "qid": key[0], "model": key[1], "condition": key[2],
                    "text_excerpt": text[:200],
                })

    rows = []
    for flag, count in tally.most_common():
        rows.append({
            "error_type": flag,
            "count": count,
            "pct_of_low_scoring": round(100 * count / max(1, len(low_keys)), 1),
            "example_qid": examples[flag][0]["qid"] if examples[flag] else "",
            "example_excerpt": examples[flag][0]["text_excerpt"] if examples[flag] else "",
        })
    return pd.DataFrame(rows), tally, examples


# =======================================================
# Main
# =======================================================
def main():
    print("Loading data...")
    responses = load_all_responses()
    qmap = load_questions()
    scores_df = load_scores()
    print(f"  {len(responses)} response records")
    print(f"  {len(qmap)} questions")
    print(f"  {len(scores_df)} judge scores")

    print("\n=== PART 1: Selecting case studies ===")
    a, b, c = select_case_studies(scores_df, responses, qmap)
    print(f"  Case A (MDT benefit): {a}")
    print(f"  Case B (RAG harm):    {b}")
    print(f"  Case C (judge disagreement): {c}")

    md = ["# Appendix E: Case Studies\n",
          "Three illustrative cases chosen to highlight qualitative differences "
          "across conditions. All responses are from Claude Sonnet 4.5.\n"]
    md.append(format_case_study(a, responses, qmap, scores_df,
                                "A — Largest MDT+RAG benefit"))
    md.append(format_case_study(b, responses, qmap, scores_df,
                                "B — Clearest RAG harm"))
    md.append(format_case_study(c, responses, qmap, scores_df,
                                "C — Highest judge disagreement"))

    out_md = Path("paper/09_case_studies.md")
    out_md.write_text("\n\n".join(md))
    print(f"  Saved: {out_md}")

    print("\n=== PART 2: Error taxonomy ===")
    df_err, tally, examples = error_analysis(scores_df, responses)
    out_csv = Path("outputs/figures/table_error_taxonomy.csv")
    df_err.to_csv(out_csv, index=False)
    print(df_err.to_string(index=False))
    print(f"\n  Saved: {out_csv}")


if __name__ == "__main__":
    main()
