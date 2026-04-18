"""
Advanced Statistical Analysis and Visualization
================================================
Runs subgroup analyses, advanced figures, and rigorous statistical tests
on the merged judge score data.

Produces:
  - Subgroup Wilcoxon tests (domain × condition, difficulty × condition)
  - Bonferroni and FDR corrected p-values
  - Cliff's delta effect sizes
  - Bootstrap 95% CIs
  - Cost-accuracy trade-off figure
  - Forest plot of MDT benefit per model/subgroup
  - Judge disagreement pattern analysis
"""

import os
import sys
import json
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from scipy.stats import wilcoxon, rankdata
from scipy.stats import bootstrap
from statsmodels.stats.multitest import multipletests

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 10,
    "figure.dpi": 150,
    "savefig.bbox": "tight",
    "savefig.dpi": 300,
})

DIMS = ["accuracy", "completeness", "safety", "concordance"]
MODELS = ["gpt-4o-mini", "claude-sonnet", "deepseek-r1", "llama-3.3-70b"]
CONDS = ["single_zeroshot", "single_rag", "mdt_zeroshot", "mdt_rag"]
COND_LABEL = {
    "single_zeroshot": "Single (ZS)",
    "single_rag": "Single + RAG",
    "mdt_zeroshot": "MDT (ZS)",
    "mdt_rag": "MDT + RAG",
}
DOMAIN_SHORT = {
    "D1_Diagnosis_Screening": "Dx",
    "D2_Staging_Molecular": "Stage",
    "D3_First_Line": "1L Rx",
    "D4_Subsequent_Resistance": "2L/Res",
    "D5_Adverse_Events": "irAE",
    "D6_Follow_Up": "F/U",
}
OUT = Path("outputs/figures")
OUT.mkdir(parents=True, exist_ok=True)


# =======================================================
# Data load
# =======================================================
def load(path="outputs/all_judge_scores.csv"):
    df = pd.read_csv(path)
    for dim in DIMS + ["hallucination", "safety_violation"]:
        df[dim] = pd.to_numeric(df[dim], errors="coerce")
    df = df.dropna(subset=DIMS)
    df["mean_score"] = df[DIMS].mean(axis=1)
    df["domain_short"] = df["domain"].map(DOMAIN_SHORT)
    # Average scores across judges → one value per (q, model, cond)
    agg = (df.groupby(["question_id", "domain", "domain_short",
                       "difficulty", "model", "condition"])
             [DIMS + ["mean_score", "hallucination", "safety_violation"]]
             .mean().reset_index())
    return df, agg


# =======================================================
# Cliff's delta
# =======================================================
def cliffs_delta(x, y):
    x = np.asarray(x)
    y = np.asarray(y)
    nx, ny = len(x), len(y)
    if nx == 0 or ny == 0:
        return np.nan
    # Vectorized
    diff = x[:, None] - y[None, :]
    pos = (diff > 0).sum()
    neg = (diff < 0).sum()
    return (pos - neg) / (nx * ny)


def effect_label(d):
    a = abs(d)
    if a < 0.147: return "negligible"
    if a < 0.33: return "small"
    if a < 0.474: return "medium"
    return "large"


# =======================================================
# 1. Per-model paired tests with effect sizes
# =======================================================
def paired_tests(agg: pd.DataFrame):
    """Pairwise comparisons single_zs vs each other condition, per model."""
    rows = []
    pivot = (agg.pivot_table(index=["question_id", "model"],
                             columns="condition", values="mean_score")
                .reset_index())

    for model in MODELS:
        sub = pivot[pivot["model"] == model]
        base = sub["single_zeroshot"].values
        for cond in CONDS:
            if cond == "single_zeroshot":
                continue
            target = sub[cond].values
            # drop nan pairs
            mask = ~(np.isnan(base) | np.isnan(target))
            a, b = base[mask], target[mask]
            stat, p = wilcoxon(a, b, alternative="two-sided",
                               zero_method="wilcox")
            delta = cliffs_delta(b, a)
            rows.append({
                "model": model,
                "comparison": f"{cond} vs single_zeroshot",
                "n": int(mask.sum()),
                "median_diff": float(np.median(b - a)),
                "mean_diff": float(np.mean(b - a)),
                "wilcoxon_stat": float(stat),
                "p_value": float(p),
                "cliffs_delta": float(delta),
                "effect_size": effect_label(delta),
            })

    tests = pd.DataFrame(rows)
    # Multiple comparisons correction
    tests["p_bonferroni"] = multipletests(tests["p_value"],
                                          method="bonferroni")[1]
    tests["p_fdr_bh"] = multipletests(tests["p_value"], method="fdr_bh")[1]
    tests["sig_bonf"] = tests["p_bonferroni"] < 0.05
    return tests


# =======================================================
# 2. Subgroup analysis: domain and difficulty
# =======================================================
def subgroup_tests(agg: pd.DataFrame, by: str):
    """Test MDT_RAG vs single_zs separately within each subgroup."""
    rows = []
    pivot = (agg.pivot_table(index=["question_id", "model", by],
                             columns="condition", values="mean_score")
                .reset_index())

    for model in MODELS:
        for grp in pivot[by].unique():
            sub = pivot[(pivot["model"] == model) & (pivot[by] == grp)]
            if len(sub) < 3:
                continue
            base = sub["single_zeroshot"].values
            target = sub["mdt_rag"].values
            mask = ~(np.isnan(base) | np.isnan(target))
            if mask.sum() < 3:
                continue
            a, b = base[mask], target[mask]
            try:
                stat, p = wilcoxon(a, b, alternative="two-sided",
                                   zero_method="wilcox")
            except Exception:
                continue
            delta = cliffs_delta(b, a)
            rows.append({
                "model": model, by: grp, "n": int(mask.sum()),
                "mean_single": float(a.mean()), "mean_mdt_rag": float(b.mean()),
                "diff": float(b.mean() - a.mean()),
                "p": float(p), "cliffs_delta": float(delta),
                "effect": effect_label(delta),
            })
    out = pd.DataFrame(rows)
    if len(out):
        out["p_fdr"] = multipletests(out["p"], method="fdr_bh")[1]
        out["sig_fdr"] = out["p_fdr"] < 0.05
    return out


# =======================================================
# 3. Bootstrap 95% CIs for mean scores per (model, condition)
# =======================================================
def bootstrap_ci(agg: pd.DataFrame, n_boot=1000, seed=42):
    rng = np.random.default_rng(seed)
    rows = []
    for model in MODELS:
        for cond in CONDS:
            vals = agg[(agg["model"] == model) & (agg["condition"] == cond)]["mean_score"].values
            if len(vals) == 0:
                continue
            # Simple percentile bootstrap at question level
            boot_means = []
            for _ in range(n_boot):
                sample = rng.choice(vals, size=len(vals), replace=True)
                boot_means.append(sample.mean())
            lo, hi = np.percentile(boot_means, [2.5, 97.5])
            rows.append({
                "model": model, "condition": cond,
                "mean": float(vals.mean()),
                "ci_lo": float(lo), "ci_hi": float(hi),
                "n": len(vals),
            })
    return pd.DataFrame(rows)


# =======================================================
# 4. Figure: forest plot of MDT+RAG benefit
# =======================================================
def fig_forest(subgroup_domain: pd.DataFrame, subgroup_diff: pd.DataFrame):
    fig, axes = plt.subplots(1, 2, figsize=(14, 7),
                             gridspec_kw={"width_ratios": [1.3, 1]})

    # Left: by domain
    ax = axes[0]
    ax.set_title("Forest plot: MDT + RAG vs Single Zero-shot (by clinical domain)")
    ax.axvline(0, color="grey", lw=0.7)

    model_colors = dict(zip(MODELS, ["#2563eb", "#dc2626", "#16a34a", "#ea580c"]))
    y = 0
    ticks = []
    labels = []
    for domain in sorted(subgroup_domain["domain_short"].unique()):
        for model in MODELS:
            sub = subgroup_domain[(subgroup_domain["domain_short"] == domain) &
                                  (subgroup_domain["model"] == model)]
            if sub.empty:
                y += 1; continue
            diff = sub["diff"].iloc[0]
            p = sub["p"].iloc[0]
            sig = "*" if p < 0.05 else ""
            ax.plot(diff, y, "o", color=model_colors[model], markersize=8)
            ax.text(diff, y, f"  {sig}", va="center", fontsize=11)
            ticks.append(y)
            labels.append(f"{domain} / {model.split('-')[0]}")
            y += 1
        y += 0.5

    ax.set_yticks(ticks)
    ax.set_yticklabels(labels, fontsize=7)
    ax.set_xlabel("Δ Mean Score (MDT+RAG − Single Zero-shot)")
    ax.spines[["top", "right"]].set_visible(False)
    # Legend
    for m, c in model_colors.items():
        ax.plot([], [], "o", color=c, label=m, markersize=8)
    ax.legend(fontsize=8, loc="lower right")

    # Right: by difficulty
    ax = axes[1]
    ax.set_title("By difficulty")
    ax.axvline(0, color="grey", lw=0.7)
    y = 0; ticks = []; labels = []
    for diff_level in ["Easy", "Medium", "Hard"]:
        for model in MODELS:
            sub = subgroup_diff[(subgroup_diff["difficulty"] == diff_level) &
                                (subgroup_diff["model"] == model)]
            if sub.empty:
                y += 1; continue
            d = sub["diff"].iloc[0]
            p = sub["p"].iloc[0]
            sig = "*" if p < 0.05 else ""
            ax.plot(d, y, "o", color=model_colors[model], markersize=8)
            ax.text(d, y, f"  {sig}", va="center", fontsize=11)
            ticks.append(y); labels.append(f"{diff_level} / {model.split('-')[0]}")
            y += 1
        y += 0.5
    ax.set_yticks(ticks); ax.set_yticklabels(labels, fontsize=7)
    ax.set_xlabel("Δ Mean Score")
    ax.spines[["top", "right"]].set_visible(False)

    plt.savefig(OUT / "fig7_forest_subgroup.png")
    plt.close()
    print("  Saved fig7_forest_subgroup.png")


# =======================================================
# 5. Figure: cost–accuracy trade-off
# =======================================================
# Approximate per-call prices (USD/1M tokens): input × 1 + output × 1
# Per MDT call we use 5 API calls; per single_rag we add retrieval context
MODEL_PRICING = {  # ($/1M input, $/1M output)
    "gpt-4o-mini": (0.15, 0.60),
    "claude-sonnet": (3.00, 15.00),
    "deepseek-r1": (0.55, 2.19),
    "llama-3.3-70b": (0.88, 0.88),
}
# Rough per-condition tokens (input_tok, output_tok) per single call
# MDT = 5× (specialists use ~2000 input, 1000 output; moderator ~5000 input, 1500 output)
COND_TOKENS = {
    "single_zeroshot": (400, 800),
    "single_rag": (2000, 800),
    "mdt_zeroshot": (5 * 1500, 5 * 1000),  # 4 specialists + moderator
    "mdt_rag": (5 * 3000, 5 * 1000),
}


def estimate_cost(model, cond):
    in_tok, out_tok = COND_TOKENS[cond]
    in_price, out_price = MODEL_PRICING[model]
    return (in_tok * in_price + out_tok * out_price) / 1e6


def fig_cost_accuracy(agg: pd.DataFrame, ci: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(9, 6))
    markers = {"single_zeroshot": "o", "single_rag": "s",
               "mdt_zeroshot": "^", "mdt_rag": "D"}
    colors = {"gpt-4o-mini": "#2563eb", "claude-sonnet": "#dc2626",
              "deepseek-r1": "#16a34a", "llama-3.3-70b": "#ea580c"}

    for _, row in ci.iterrows():
        cost = estimate_cost(row["model"], row["condition"])
        yerr = [[row["mean"] - row["ci_lo"]], [row["ci_hi"] - row["mean"]]]
        ax.errorbar(cost, row["mean"],
                    yerr=yerr,
                    fmt=markers[row["condition"]],
                    color=colors[row["model"]],
                    markersize=10, capsize=3,
                    label=f"{row['model']} / {COND_LABEL[row['condition']]}")

    ax.set_xscale("log")
    ax.set_xlabel("Estimated Cost per Question (USD, log scale)")
    ax.set_ylabel("Mean Score (1-5, ±95% CI bootstrap)")
    ax.set_title("Cost-Accuracy Trade-off Across Models and Conditions")
    ax.grid(True, alpha=0.3)

    # Create custom legend — model legend on left, condition legend on right
    from matplotlib.patches import Patch
    from matplotlib.lines import Line2D
    mlegend = [Line2D([], [], marker="o", color=c, linestyle="",
                       markersize=10, label=m) for m, c in colors.items()]
    clegend = [Line2D([], [], marker=markers[k], color="black", linestyle="",
                       markersize=10, label=COND_LABEL[k]) for k in CONDS]
    leg1 = ax.legend(handles=mlegend, title="Model", loc="upper left",
                     fontsize=8, title_fontsize=9)
    ax.add_artist(leg1)
    ax.legend(handles=clegend, title="Condition", loc="lower right",
              fontsize=8, title_fontsize=9)

    plt.savefig(OUT / "fig8_cost_accuracy.png")
    plt.close()
    print("  Saved fig8_cost_accuracy.png")


# =======================================================
# 6. Judge disagreement heatmap
# =======================================================
def fig_judge_disagreement(df: pd.DataFrame):
    j1 = df[df["judge"] == sorted(df["judge"].unique())[0]]
    j2 = df[df["judge"] == sorted(df["judge"].unique())[1]]
    key = ["question_id", "model", "condition"]
    merged = j1[key + DIMS].merge(j2[key + DIMS], on=key, suffixes=("_j1", "_j2"))

    fig, axes = plt.subplots(2, 2, figsize=(10, 9))
    for ax, dim in zip(axes.flat, DIMS):
        # 2D histogram of J1 vs J2 scores
        cnt = (merged.groupby([f"{dim}_j1", f"{dim}_j2"]).size()
                     .unstack(fill_value=0))
        sns.heatmap(cnt, annot=True, fmt="d", cmap="Blues", ax=ax, cbar=False)
        ax.set_title(f"{dim.title()} (j1=claude-sonnet vs j2=gpt-4o-mini)")
        ax.set_xlabel("GPT-4o-mini judge"); ax.set_ylabel("Claude judge")

    plt.tight_layout()
    plt.savefig(OUT / "fig9_judge_disagreement.png")
    plt.close()
    print("  Saved fig9_judge_disagreement.png")


# =======================================================
# 7. MDT × RAG interaction figure (2×2 cell plot with CIs)
# =======================================================
def fig_interaction(ci: pd.DataFrame):
    fig, axes = plt.subplots(1, 4, figsize=(16, 4), sharey=True)
    for ax, model in zip(axes, MODELS):
        sub = ci[ci["model"] == model].set_index("condition").loc[CONDS]
        x = ["Single\nZS", "Single\n+RAG", "MDT\nZS", "MDT\n+RAG"]
        y = sub["mean"].values
        yerr = [sub["mean"] - sub["ci_lo"], sub["ci_hi"] - sub["mean"]]
        colors = ["#9CA3AF", "#6BAED6", "#FDB863", "#E6550D"]
        bars = ax.bar(x, y, yerr=yerr, color=colors, capsize=4, edgecolor="black")
        ax.set_title(model, fontsize=10)
        ax.set_ylim(1, 5.1)
        ax.grid(axis="y", alpha=0.3)
        for b, v in zip(bars, y):
            ax.text(b.get_x() + b.get_width() / 2, v + 0.05,
                    f"{v:.2f}", ha="center", fontsize=8)

    axes[0].set_ylabel("Mean Score (1–5, ±95% CI)")
    fig.suptitle("MDT × RAG: Mean Score per Condition (Bootstrap 95% CI)", fontsize=12)
    plt.tight_layout()
    plt.savefig(OUT / "fig10_mdt_rag_interaction.png")
    plt.close()
    print("  Saved fig10_mdt_rag_interaction.png")


# =======================================================
# 8. Summary tables
# =======================================================
def save_summary_tables(tests, subgroup_domain, subgroup_diff, ci):
    tests.to_csv(OUT / "table_paired_tests.csv", index=False)
    subgroup_domain.to_csv(OUT / "table_subgroup_domain.csv", index=False)
    subgroup_diff.to_csv(OUT / "table_subgroup_difficulty.csv", index=False)
    ci.to_csv(OUT / "table_bootstrap_ci.csv", index=False)
    print("  Saved 4 summary tables")


# =======================================================
# MAIN
# =======================================================
def main():
    df, agg = load()
    print(f"Loaded {len(df)} judge rows → {len(agg)} question-model-condition triples")

    print("\n=== Paired tests with effect sizes ===")
    tests = paired_tests(agg)
    print(tests.to_string(index=False))

    print("\n=== Subgroup: by DOMAIN (MDT+RAG vs single_zs) ===")
    sg_d = subgroup_tests(agg, "domain_short")
    sig_d = sg_d[sg_d["p"] < 0.05]
    print(f"  {len(sig_d)} / {len(sg_d)} subgroups p<0.05 (uncorrected)")
    if len(sg_d):
        sig_fdr = sg_d[sg_d["sig_fdr"]]
        print(f"  {len(sig_fdr)} remain significant after FDR correction")
        if len(sig_fdr):
            print(sig_fdr.to_string(index=False))

    print("\n=== Subgroup: by DIFFICULTY (MDT+RAG vs single_zs) ===")
    sg_diff = subgroup_tests(agg, "difficulty")
    print(sg_diff.to_string(index=False))

    print("\n=== Bootstrap 95% CIs ===")
    ci = bootstrap_ci(agg)
    print(ci.to_string(index=False))

    print("\n=== Generating advanced figures ===")
    fig_forest(sg_d, sg_diff)
    fig_cost_accuracy(agg, ci)
    fig_judge_disagreement(df)
    fig_interaction(ci)

    save_summary_tables(tests, sg_d, sg_diff, ci)
    print(f"\n✅ All advanced outputs in: {OUT}")


if __name__ == "__main__":
    main()
