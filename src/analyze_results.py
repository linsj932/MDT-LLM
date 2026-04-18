"""
Analysis & Visualization
==========================
Load evaluation scores, compute metrics, generate all figures/tables.
Run after expert evaluation is complete.
"""

import json, sys, os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import cohen_kappa_score
from scipy.stats import wilcoxon

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

plt.rcParams.update({
    "font.family": "DejaVu Sans",  # Arial may not be available; DejaVu is bundled
    "font.size": 11,
    "figure.dpi": 150,              # 150 is plenty for preview; 300 for publication
    "savefig.bbox": "tight",
    "savefig.dpi": 300,
})

DIMS = ["accuracy", "completeness", "safety", "concordance"]
MODELS_ORDER = ["gpt-4o-mini", "claude-sonnet", "deepseek-r1", "llama-3.3-70b"]
CONDS_ORDER = ["single_zeroshot", "single_rag", "mdt_zeroshot", "mdt_rag"]
COND_LABELS = {
    "single_zeroshot": "Single (Zero-shot)",
    "single_rag": "Single + RAG",
    "mdt_zeroshot": "MDT (Zero-shot)",
    "mdt_rag": "MDT + RAG",
}
DOMAIN_MAP = {
    "D1_Diagnosis_Screening": "Diagnosis",
    "D2_Staging_Molecular": "Staging",
    "D3_First_Line": "First-line Tx",
    "D4_Subsequent_Resistance": "Subsequent Tx",
    "D5_Adverse_Events": "Adverse Events",
    "D6_Follow_Up": "Follow-up",
}
OUTDIR = "outputs/figures/"


def load_eval_scores(path: str) -> pd.DataFrame:
    """
    Load LLM-judge evaluation scores.
    Expected CSV columns:
      question_id, domain, difficulty, model, condition, judge,
      accuracy, completeness, safety, concordance,
      hallucination (0/1), safety_violation (0/1), rationale
    """
    df = pd.read_csv(path)
    df["domain_short"] = df["domain"].map(DOMAIN_MAP)
    # Coerce numeric (judge outputs sometimes contain non-numeric strings)
    for dim in DIMS + ["hallucination", "safety_violation"]:
        df[dim] = pd.to_numeric(df[dim], errors="coerce")
    # Drop rows where judge failed to produce valid scores
    n0 = len(df)
    df = df.dropna(subset=DIMS)
    if len(df) < n0:
        print(f"  ⚠ Dropped {n0 - len(df)} rows with missing judge scores")
    return df


# ══════════════════════════════════════════════════════════════════
# INTER-JUDGE RELIABILITY (Cohen's Kappa or Fleiss')
# ══════════════════════════════════════════════════════════════════

def compute_irr(df: pd.DataFrame) -> pd.DataFrame:
    """Compute inter-judge Cohen's Kappa between the first two judges."""
    judges = sorted(df["judge"].unique())
    if len(judges) < 2:
        print(f"  Only {len(judges)} judge(s); skipping IRR")
        return pd.DataFrame([{"dimension": "N/A", "kappa": None}])

    j1, j2 = judges[0], judges[1]
    e1 = df[df["judge"] == j1].sort_values(["question_id", "model", "condition"])
    e2 = df[df["judge"] == j2].sort_values(["question_id", "model", "condition"])

    # Align by key (some judge runs may have failed)
    key = ["question_id", "model", "condition"]
    merged = e1[key + DIMS].merge(e2[key + DIMS], on=key, suffixes=("_j1", "_j2"))
    print(f"  IRR computed on {len(merged)} aligned pairs "
          f"(judges: {j1} vs {j2})")

    results = []
    for dim in DIMS:
        try:
            kappa = cohen_kappa_score(
                merged[f"{dim}_j1"].values,
                merged[f"{dim}_j2"].values,
                weights="quadratic",
            )
            results.append({"dimension": dim, "kappa": round(kappa, 3)})
        except Exception as e:
            results.append({"dimension": dim, "kappa": None})

    # Overall
    all_j1 = np.concatenate([merged[f"{d}_j1"].values for d in DIMS])
    all_j2 = np.concatenate([merged[f"{d}_j2"].values for d in DIMS])
    kappa_all = cohen_kappa_score(all_j1, all_j2, weights="quadratic")
    results.append({"dimension": "Overall", "kappa": round(kappa_all, 3)})

    return pd.DataFrame(results)


# ══════════════════════════════════════════════════════════════════
# TABLE 3: MAIN RESULTS
# ══════════════════════════════════════════════════════════════════

def main_results_table(df: pd.DataFrame) -> pd.DataFrame:
    """Average scores across judges → pivot by model × condition."""
    avg = (df.groupby(["model", "condition"])[DIMS + ["hallucination", "safety_violation"]]
             .mean().round(2).reset_index())
    avg["condition_label"] = avg["condition"].map(COND_LABELS)
    return avg


# ══════════════════════════════════════════════════════════════════
# FIGURES
# ══════════════════════════════════════════════════════════════════

def fig2_overall_bar(df: pd.DataFrame):
    """Fig 2: Grouped bar chart – overall performance by model × condition."""
    avg = df.groupby(["model", "condition"])[DIMS].mean().reset_index()
    avg["mean_score"] = avg[DIMS].mean(axis=1)
    avg["condition_label"] = avg["condition"].map(COND_LABELS)

    fig, ax = plt.subplots(figsize=(10, 5))
    x = np.arange(len(MODELS_ORDER))
    width = 0.18
    colors = ["#C0C0C0", "#6BAED6", "#FDB863", "#E6550D"]

    for i, cond in enumerate(CONDS_ORDER):
        subset = avg[avg["condition"] == cond].set_index("model").loc[MODELS_ORDER]
        ax.bar(x + i * width, subset["mean_score"], width,
               label=COND_LABELS[cond], color=colors[i], edgecolor="white")

    ax.set_xticks(x + 1.5 * width)
    ax.set_xticklabels(MODELS_ORDER, fontsize=10)
    ax.set_ylabel("Mean Score (1–5)")
    ax.set_ylim(1, 5.2)
    ax.legend(loc="upper right", fontsize=9)
    ax.set_title("Overall Performance by Model and Condition")
    ax.spines[["top", "right"]].set_visible(False)

    os.makedirs(OUTDIR, exist_ok=True)
    fig.savefig(f"{OUTDIR}/fig2_overall_bar.png")
    plt.close()
    print("  Saved fig2_overall_bar.png")


def fig3_domain_heatmap(df: pd.DataFrame):
    """Fig 3: Heatmap – accuracy by model × domain (MDT+RAG condition)."""
    sub = df[df["condition"] == "mdt_rag"]
    pivot = (sub.groupby(["model", "domain_short"])["accuracy"]
                .mean().reset_index()
                .pivot(index="model", columns="domain_short", values="accuracy"))
    pivot = pivot.loc[MODELS_ORDER]

    fig, ax = plt.subplots(figsize=(8, 4))
    sns.heatmap(pivot, annot=True, fmt=".2f", cmap="YlGnBu",
                vmin=1, vmax=5, ax=ax, linewidths=0.5)
    ax.set_title("Accuracy by Model × Domain (MDT + RAG)")
    ax.set_ylabel("")
    fig.savefig(f"{OUTDIR}/fig3_domain_heatmap.png")
    plt.close()
    print("  Saved fig3_domain_heatmap.png")


def fig4_improvement_bar(df: pd.DataFrame):
    """Fig 4: RAG/MDT improvement delta over single zero-shot baseline."""
    avg = df.groupby(["model", "condition"])["accuracy"].mean().reset_index()
    baseline = avg[avg["condition"] == "single_zeroshot"].set_index("model")["accuracy"]

    fig, ax = plt.subplots(figsize=(8, 5))
    x = np.arange(len(MODELS_ORDER))
    width = 0.25
    colors = ["#6BAED6", "#FDB863", "#E6550D"]

    for i, cond in enumerate(["single_rag", "mdt_zeroshot", "mdt_rag"]):
        vals = avg[avg["condition"] == cond].set_index("model")["accuracy"]
        deltas = (vals - baseline).loc[MODELS_ORDER]
        ax.bar(x + i * width, deltas, width,
               label=COND_LABELS[cond], color=colors[i], edgecolor="white")

    ax.set_xticks(x + width)
    ax.set_xticklabels(MODELS_ORDER, fontsize=10)
    ax.set_ylabel("Accuracy Improvement (Δ)")
    ax.axhline(0, color="grey", linewidth=0.5)
    ax.legend(fontsize=9)
    ax.set_title("Improvement Over Single Zero-Shot Baseline")
    ax.spines[["top", "right"]].set_visible(False)

    fig.savefig(f"{OUTDIR}/fig4_improvement.png")
    plt.close()
    print("  Saved fig4_improvement.png")


def fig5_hallucination(df: pd.DataFrame):
    """Fig 5: Hallucination rate by model × condition."""
    hall = (df.groupby(["model", "condition"])["hallucination"]
              .mean().reset_index())
    hall["condition_label"] = hall["condition"].map(COND_LABELS)

    fig, ax = plt.subplots(figsize=(8, 5))
    x = np.arange(len(MODELS_ORDER))
    width = 0.18
    colors = ["#C0C0C0", "#6BAED6", "#FDB863", "#E6550D"]

    for i, cond in enumerate(CONDS_ORDER):
        subset = hall[hall["condition"] == cond].set_index("model").loc[MODELS_ORDER]
        ax.bar(x + i * width, subset["hallucination"] * 100, width,
               label=COND_LABELS[cond], color=colors[i], edgecolor="white")

    ax.set_xticks(x + 1.5 * width)
    ax.set_xticklabels(MODELS_ORDER, fontsize=10)
    ax.set_ylabel("Hallucination Rate (%)")
    ax.legend(fontsize=9)
    ax.set_title("Hallucination Rate by Model and Condition")
    ax.spines[["top", "right"]].set_visible(False)

    fig.savefig(f"{OUTDIR}/fig5_hallucination.png")
    plt.close()
    print("  Saved fig5_hallucination.png")


def fig6_difficulty(df: pd.DataFrame):
    """Fig 6: Performance by difficulty level (MDT+RAG)."""
    sub = df[df["condition"] == "mdt_rag"]
    avg = sub.groupby(["model", "difficulty"])["accuracy"].mean().reset_index()

    diff_order = ["Easy", "Medium", "Hard"]
    fig, ax = plt.subplots(figsize=(7, 5))
    for model in MODELS_ORDER:
        m = avg[avg["model"] == model].set_index("difficulty").loc[diff_order]
        ax.plot(diff_order, m["accuracy"], marker="o", label=model, linewidth=2)

    ax.set_ylabel("Accuracy Score")
    ax.set_ylim(1, 5.2)
    ax.legend(fontsize=9)
    ax.set_title("Performance by Difficulty (MDT + RAG)")
    ax.spines[["top", "right"]].set_visible(False)

    fig.savefig(f"{OUTDIR}/fig6_difficulty.png")
    plt.close()
    print("  Saved fig6_difficulty.png")


def statistical_tests(df: pd.DataFrame):
    """Wilcoxon signed-rank tests for paired comparisons."""
    print("\n=== Statistical Tests (Wilcoxon signed-rank) ===")
    avg = df.groupby(["question_id", "model", "condition"])["accuracy"].mean()

    for model in MODELS_ORDER:
        # single_zeroshot vs mdt_rag
        a = avg.xs((model, "single_zeroshot"), level=("model", "condition"))
        b = avg.xs((model, "mdt_rag"), level=("model", "condition"))
        common = a.index.intersection(b.index)
        if len(common) > 5:
            stat, p = wilcoxon(a[common], b[common])
            print(f"  {model}: single_zs vs mdt_rag  p={p:.4f}")


# ══════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════

def describe_coverage(df: pd.DataFrame) -> None:
    """Print coverage diagnostic so you know which cells are populated."""
    print("\n=== Coverage Diagnostic ===")
    cov = (df.groupby(["model", "condition"]).size().unstack(fill_value=0))
    print(cov)
    # Expected per cell = n_questions × n_judges
    n_q = df["question_id"].nunique()
    n_j = df["judge"].nunique()
    expected = n_q * n_j
    print(f"  Expected per cell: {n_q} questions × {n_j} judges = {expected}")
    incomplete = (cov < expected).any().any()
    if incomplete:
        print("  ⚠ Some cells are incomplete (partial data)")


def generate_all(eval_csv: str):
    """Generate all figures and tables from evaluation CSV."""
    os.makedirs(OUTDIR, exist_ok=True)

    print(f"Loading evaluation data from {eval_csv} ...")
    df = load_eval_scores(eval_csv)
    print(f"  Loaded {len(df)} rows")
    print(f"  Unique: {df['question_id'].nunique()} questions, "
          f"{df['model'].nunique()} models, "
          f"{df['condition'].nunique()} conditions, "
          f"{df['judge'].nunique()} judges")
    describe_coverage(df)

    print("\n=== Inter-Judge Reliability (Cohen's κ) ===")
    irr = compute_irr(df)
    print(irr.to_string(index=False))
    irr.to_csv(f"{OUTDIR}/table5_irr.csv", index=False)

    print("\n=== Main Results Table ===")
    main = main_results_table(df)
    print(main.to_string(index=False))
    main.to_csv(f"{OUTDIR}/table3_main_results.csv", index=False)

    print("\n=== Generating Figures ===")
    try: fig2_overall_bar(df)
    except Exception as e: print(f"  ❌ fig2 failed: {e}")
    try: fig3_domain_heatmap(df)
    except Exception as e: print(f"  ❌ fig3 failed: {e}")
    try: fig4_improvement_bar(df)
    except Exception as e: print(f"  ❌ fig4 failed: {e}")
    try: fig5_hallucination(df)
    except Exception as e: print(f"  ❌ fig5 failed: {e}")
    try: fig6_difficulty(df)
    except Exception as e: print(f"  ❌ fig6 failed: {e}")

    statistical_tests(df)
    print(f"\n✅ Done! All outputs in: {OUTDIR}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("eval_csv", help="Path to evaluation scores CSV")
    args = parser.parse_args()
    generate_all(args.eval_csv)
