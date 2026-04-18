"""Figure 12: Heterogeneous MDT vs homogeneous MDT."""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 11,
    "figure.dpi": 150, "savefig.bbox": "tight", "savefig.dpi": 300,
})

het = pd.read_csv("outputs/judge_heterogeneous.csv")
main = pd.read_csv("outputs/all_judge_scores.csv")

for d in [het, main]:
    for c in ['accuracy','completeness','safety','concordance']:
        d[c] = pd.to_numeric(d[c], errors='coerce')
    d['mean'] = d[['accuracy','completeness','safety','concordance']].mean(axis=1)

main_j = main[main['judge']=='gpt-4o-mini']

# Build comparison table
configs = [
    ('Llama-3.3-70B\n(homo)', main_j[(main_j['model']=='llama-3.3-70b') & (main_j['condition']=='mdt_zeroshot')]['mean'].mean(), 0.02, '#ea580c'),
    ('GPT-4o-mini\n(homo)', main_j[(main_j['model']=='gpt-4o-mini') & (main_j['condition']=='mdt_zeroshot')]['mean'].mean(), 0.005, '#2563eb'),
    ('Claude-Sonnet\n(homo)', main_j[(main_j['model']=='claude-sonnet') & (main_j['condition']=='mdt_zeroshot')]['mean'].mean(), 0.25, '#dc2626'),
    ('DeepSeek-R1\n(homo)', main_j[(main_j['model']=='deepseek-r1') & (main_j['condition']=='mdt_zeroshot')]['mean'].mean(), 0.05, '#16a34a'),
    ('HETERO\n(all 4 mixed)', het[het['condition']=='mdt_zeroshot_hetero']['mean'].mean(), 0.17, '#7c3aed'),
]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

# LEFT: mean scores
labels = [c[0] for c in configs]
means = [c[1] for c in configs]
colors = [c[3] for c in configs]
bars = ax1.bar(labels, means, color=colors, edgecolor='black', linewidth=1)
ax1.set_ylabel('Mean Judge Score (1–5)')
ax1.set_title('MDT Zero-shot: Heterogeneous vs Homogeneous Configurations')
ax1.set_ylim(3.8, 4.85)
for b, v in zip(bars, means):
    ax1.text(b.get_x() + b.get_width()/2, v + 0.015, f"{v:.3f}",
             ha='center', fontsize=10, fontweight='bold')
# Highlight hetero
bars[-1].set_edgecolor('gold')
bars[-1].set_linewidth(3)
ax1.axhline(max(means[:-1]), color='gray', linestyle='--', alpha=0.5, label='Best homogeneous')
ax1.legend(loc='lower right', fontsize=9)
ax1.spines[['top','right']].set_visible(False)

# RIGHT: cost-quality scatter
costs = [c[2] for c in configs]
ax2.scatter(costs, means, s=300, c=colors, edgecolor='black', linewidth=1.5, alpha=0.9)
for lbl, c, m in zip(labels, costs, means):
    ax2.annotate(lbl.replace('\n', ' '), (c, m), textcoords="offset points",
                 xytext=(10, 6), fontsize=8)
# Highlight hetero
hetero_idx = 4
ax2.scatter(costs[hetero_idx], means[hetero_idx], s=400, facecolors='none',
            edgecolor='gold', linewidth=3)
ax2.set_xscale('log')
ax2.set_xlabel('Estimated Cost per Question (USD, log scale)')
ax2.set_ylabel('Mean Judge Score (1–5)')
ax2.set_title('Cost-Quality Frontier (Heterogeneous highlighted in gold)')
ax2.grid(alpha=0.3)
ax2.spines[['top','right']].set_visible(False)

plt.tight_layout()
fig.savefig("outputs/figures/fig12_heterogeneous.png")
print("Saved fig12_heterogeneous.png")

# Save data table
pd.DataFrame({
    'config': labels,
    'mean_score': means,
    'cost_per_q': costs
}).to_csv("outputs/figures/table7_heterogeneous.csv", index=False)
print("Saved table7_heterogeneous.csv")
