"""Plot RAG top-k sensitivity as a line chart (Figure 11)."""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 11,
    "figure.dpi": 150, "savefig.bbox": "tight", "savefig.dpi": 300,
})

# Load RAG top-k scores (gpt-4o-mini judge only)
df = pd.read_csv("outputs/judge_rag_topk.csv")
main = pd.read_csv("outputs/all_judge_scores.csv")

for d in [df, main]:
    for c in ['accuracy','completeness','safety','concordance']:
        d[c] = pd.to_numeric(d[c], errors='coerce')
    d['mean'] = d[['accuracy','completeness','safety','concordance']].mean(axis=1)

# Filter to gpt-4o-mini judge for fair comparison
main_j = main[main['judge'] == 'gpt-4o-mini']

# Compute per-model per-k means
results = {}
for model in ['claude-sonnet', 'deepseek-r1']:
    baseline = main_j[(main_j['model']==model) & (main_j['condition']=='single_zeroshot')]['mean'].mean()
    k5 = main_j[(main_j['model']==model) & (main_j['condition']=='single_rag')]['mean'].mean()
    row = {0: baseline, 5: k5}
    for k in [1, 3, 10]:
        sub = df[(df['model']==model) & (df['condition']==f'single_rag_k{k}')]
        row[k] = sub['mean'].mean()
    results[model] = row

# Plot
fig, ax = plt.subplots(figsize=(8, 5))
colors = {'claude-sonnet': '#dc2626', 'deepseek-r1': '#16a34a'}
markers = {'claude-sonnet': 'o', 'deepseek-r1': 's'}

k_vals = [1, 3, 5, 10]
for model, vals in results.items():
    xs = [0] + k_vals
    ys = [vals[k] for k in xs]
    ax.plot(xs, ys, marker=markers[model], markersize=9,
            linewidth=2, color=colors[model], label=model)
    # Annotate baseline
    ax.axhline(vals[0], color=colors[model], linestyle='--', alpha=0.3)
    ax.text(11, vals[0], f"  ZS baseline", color=colors[model],
            fontsize=8, va='center')

ax.set_xlabel("RAG top-k (0 = zero-shot)")
ax.set_ylabel("Mean Judge Score (1–5)")
ax.set_title("RAG Retrieval Depth Sensitivity\n(Every k ≥ 1 harms performance; effect is k-insensitive)")
ax.set_xticks([0, 1, 3, 5, 10])
ax.set_xticklabels(['ZS (k=0)', 'k=1', 'k=3', 'k=5', 'k=10'])
ax.grid(alpha=0.3)
ax.legend(fontsize=10, loc='lower left')
ax.spines[['top','right']].set_visible(False)

fig.savefig("outputs/figures/fig11_rag_topk.png")
print("Saved outputs/figures/fig11_rag_topk.png")

# Also save the data table
pd.DataFrame(results).T.to_csv("outputs/figures/table6_rag_topk.csv")
print("Saved outputs/figures/table6_rag_topk.csv")
