"""Figure 1: MDT-LLM Architecture (matplotlib, publication-quality)."""

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
from matplotlib.lines import Line2D
import numpy as np

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 9,
    "figure.dpi": 150,
    "savefig.bbox": "tight",
    "savefig.dpi": 300,
})

fig, ax = plt.subplots(figsize=(14, 9))
ax.set_xlim(0, 16)
ax.set_ylim(0, 11)
ax.axis('off')


def box(x, y, w, h, text, fc, ec='black', fs=9, bold=False):
    patch = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.04,rounding_size=0.15",
        linewidth=1.2, edgecolor=ec, facecolor=fc
    )
    ax.add_patch(patch)
    weight = 'bold' if bold else 'normal'
    ax.text(x + w/2, y + h/2, text, ha='center', va='center',
            fontsize=fs, fontweight=weight, wrap=True)


def arrow(x1, y1, x2, y2, style='-|>', color='black', lw=1.5, ls='-'):
    a = FancyArrowPatch(
        (x1, y1), (x2, y2),
        arrowstyle=style, mutation_scale=15,
        color=color, linewidth=lw, linestyle=ls,
    )
    ax.add_patch(a)


# =========================
# TITLE
# =========================
ax.text(8, 10.6, "MDT-LLM Architecture",
        fontsize=14, fontweight='bold', ha='center')

# =========================
# INPUT (top-left)
# =========================
box(0.3, 8.7, 3.5, 1.3,
    "Clinical Vignette + Question\n"
    "(e.g., EGFR mutation +, PD-L1 80%,\n"
    "first-line therapy?)",
    fc='#FEF3C7', bold=True, fs=9)

# =========================
# RAG PIPELINE (top-right block)
# =========================
# Background rectangle
rag_bg = FancyBboxPatch((8.5, 7.2), 7.2, 3.3,
                        boxstyle="round,pad=0.08,rounding_size=0.15",
                        linewidth=1, edgecolor='#047857',
                        facecolor='#ECFDF5', alpha=0.5)
ax.add_patch(rag_bg)
ax.text(12.1, 10.2, "Retrieval-Augmented Generation Pipeline",
        fontsize=10, fontweight='bold', ha='center', color='#047857')

box(8.8, 8.3, 1.9, 1.0, "NCCN\nGuidelines\n(618 pages)",
    fc='#D1FAE5', fs=8)
box(10.9, 8.3, 1.5, 1.0, "Chunks\n(n=6,252)\n512+128",
    fc='#D1FAE5', fs=8)
box(12.6, 8.3, 1.5, 1.0, "Embeddings\ntext-embed-3\n3,072-d",
    fc='#D1FAE5', fs=8)
box(14.3, 8.3, 1.3, 1.0, "FAISS\nIndex", fc='#D1FAE5', fs=8)

box(11.5, 7.3, 2.5, 0.7, "Retrieval (top-k=5)",
    fc='#A7F3D0', bold=True, fs=9)

# Arrows in RAG
arrow(10.7, 8.8, 10.9, 8.8, color='#047857')
arrow(12.4, 8.8, 12.6, 8.8, color='#047857')
arrow(14.1, 8.8, 14.3, 8.8, color='#047857')
arrow(14.9, 8.3, 14, 7.7, color='#047857')

# =========================
# PHASE 1: Specialists (middle row)
# =========================
ax.text(8, 6.4, "Phase 1: Independent Specialist Opinions (parallel)",
        fontsize=10, fontweight='bold', ha='center', color='#1E40AF')

specialists = [
    (0.3, "Medical\nOncologist", "Systemic tx:\nchemo/IO/targeted"),
    (4.1, "Thoracic\nSurgeon", "Surgical candidacy\nPerioperative"),
    (7.9, "Radiation\nOncologist", "RT role\n(SBRT/CRT/palliative)"),
    (11.7, "Pathologist /\nMolecular", "Histology +\nbiomarker interp."),
]

spec_positions = []
for x, role, desc in specialists:
    box(x, 4.4, 3.5, 1.6, f"{role}\n\n{desc}",
        fc='#DBEAFE', bold=True, fs=9)
    spec_positions.append((x + 1.75, 6.0))

# =========================
# PHASE 2: Moderator
# =========================
ax.text(8, 3.2, "Phase 2: Moderator Synthesis",
        fontsize=10, fontweight='bold', ha='center', color='#1E40AF')

box(5.5, 1.7, 5, 1.3,
    "MDT Coordinator\n"
    "(1) Treatment plan (drug/dose)\n"
    "(2) Resolve disagreements\n"
    "(3) Follow-up & monitoring",
    fc='#BFDBFE', bold=True, fs=9)

# =========================
# OUTPUT + EVALUATION
# =========================
box(0.3, 0.15, 5, 1.1,
    "Final MDT Recommendation\n(Consensus output)",
    fc='#E0E7FF', ec='#4F46E5', bold=True, fs=10)

# Evaluation block (right)
eval_bg = FancyBboxPatch((10.7, 0.05), 5.1, 1.3,
                         boxstyle="round,pad=0.05,rounding_size=0.12",
                         linewidth=1, edgecolor='#BE185D',
                         facecolor='#FCE7F3', alpha=0.5)
ax.add_patch(eval_bg)
ax.text(13.25, 1.1, "LLM-as-Judge Evaluation",
        fontsize=9, fontweight='bold', ha='center', color='#BE185D')
box(10.9, 0.2, 2.2, 0.7, "Judge 1:\nGPT-4o-mini", fc='#FBCFE8', fs=8)
box(13.4, 0.2, 2.2, 0.7, "Judge 2:\nClaude Sonnet", fc='#FBCFE8', fs=8)

# =========================
# ARROWS / EDGES
# =========================
# Question → each specialist
for x_center, _ in spec_positions:
    arrow(2.0, 8.7, x_center, 6.05, color='black', lw=1.2)

# RAG context → each specialist (dashed)
for x_center, _ in spec_positions:
    arrow(13, 7.25, x_center, 6.05, color='#047857', lw=1.0, ls='--')
# RAG → moderator (dashed)
arrow(13, 7.25, 9.5, 3.0, color='#047857', lw=1.0, ls='--')

# Specialists → moderator
for x_center, _ in spec_positions:
    arrow(x_center, 4.4, 8.0, 3.0, color='#1E40AF', lw=1.2)

# Moderator → output
arrow(6.5, 1.7, 3.5, 1.25, color='black', lw=1.5)

# Output → judges
arrow(5, 0.7, 10.9, 0.55, color='#BE185D', lw=1.2)

# =========================
# Legend
# =========================
legend_elements = [
    Line2D([0], [0], color='black', lw=1.5, label='Always-active flow'),
    Line2D([0], [0], color='#047857', lw=1.5, linestyle='--',
           label='RAG context (RAG conditions only)'),
]
ax.legend(handles=legend_elements, loc='upper left',
          bbox_to_anchor=(0.02, 0.45), fontsize=8, frameon=True)

plt.savefig("outputs/figures/fig1_architecture.png", dpi=300, bbox_inches='tight')
plt.savefig("paper/latex/figures/fig1_architecture.png", dpi=300, bbox_inches='tight')
# Also export as PDF for LaTeX inclusion (vector)
plt.savefig("paper/latex/figures/fig1_architecture.pdf", bbox_inches='tight')
print("Saved fig1_architecture (PNG + PDF)")
