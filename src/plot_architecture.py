"""Figure 1: MDT-LLM Architecture (publication-quality v3 — minimalist).

Design principles:
- Single vertical flow axis, minimal arrow crossings.
- Specialists collapsed inside ONE Phase-1 container (no 4 parallel arrows).
- RAG rendered as a sidecar module, attached by a single augmentation arrow.
- Evaluation layer as a single container with internal horizontal micro-flow.
- Total of 5 main arrows (vs. ~15 in v2).
"""

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
from matplotlib.lines import Line2D
import numpy as np

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 9,
    "axes.linewidth": 0.0,
    "figure.dpi": 200,
    "savefig.bbox": "tight",
    "savefig.dpi": 300,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
})

# ──────────────── Palette ────────────────
C = {
    # backgrounds
    "input":    ("#FEF3C7", "#D97706"),
    "phase1":   ("#EFF6FF", "#2563EB"),   # light blue container
    "agent":    ("#DBEAFE", "#1D4ED8"),   # individual agent card
    "rag":      ("#ECFDF5", "#059669"),   # RAG sidecar
    "phase2":   ("#EEF2FF", "#4338CA"),
    "moderator":("#C7D2FE", "#312E81"),
    "output":   ("#F5F3FF", "#6D28D9"),
    "evalbg":   ("#FDF2F8", "#BE185D"),
    "judge":    ("#FCE7F3", "#9D174D"),
    "gold":     ("#FEF9C3", "#A16207"),
    # arrows
    "a_main":   "#111827",
    "a_rag":    "#059669",
    "a_eval":   "#BE185D",
    # text
    "t_title":  "#0F172A",
    "t_dim":    "#475569",
}


# ──────────────── Canvas ────────────────
fig, ax = plt.subplots(figsize=(12, 12.5))
ax.set_xlim(0, 12)
ax.set_ylim(0, 13)
ax.set_aspect('equal')
ax.axis('off')


# ──────────────── Helpers ────────────────
def rbox(x, y, w, h, fc, ec, lw=1.2, alpha=1.0, r=0.14, zorder=2):
    p = FancyBboxPatch((x, y), w, h,
                       boxstyle=f"round,pad=0.02,rounding_size={r}",
                       linewidth=lw, edgecolor=ec, facecolor=fc,
                       alpha=alpha, zorder=zorder, joinstyle='round')
    ax.add_patch(p)


def stext(x, y, s, fs=9, fw='normal', color=None, ha='center', va='center',
          zorder=4, style='normal'):
    ax.text(x, y, s, fontsize=fs, fontweight=fw, fontstyle=style,
            color=color or C['t_title'], ha=ha, va=va, zorder=zorder)


def arrow(x1, y1, x2, y2, color, lw=1.6, ls='-', shrink=5, mutation=16):
    a = FancyArrowPatch((x1, y1), (x2, y2),
                        arrowstyle='-|>', mutation_scale=mutation,
                        color=color, linewidth=lw, linestyle=ls,
                        shrinkA=shrink, shrinkB=shrink,
                        zorder=3, capstyle='round', joinstyle='round')
    ax.add_patch(a)


# ──────────────── Title ────────────────
stext(6, 12.55, "MDT-LLM Architecture",
      fs=15, fw='bold', color=C['t_title'])


# ══════════════════════════════════════════════════════════════════
# 1)  INPUT  (top-center)
# ══════════════════════════════════════════════════════════════════
IN = (3.5, 11.1, 5.0, 0.95)
rbox(*IN, fc=C['input'][0], ec=C['input'][1], lw=1.4)
stext(IN[0] + IN[2]/2, IN[1] + IN[3] - 0.27,
      "Clinical Vignette + Question", fs=10.5, fw='bold')
stext(IN[0] + IN[2]/2, IN[1] + 0.30,
      "Stage IV NSCLC, EGFR exon 19 del, PD-L1 80%, first-line therapy?",
      fs=7.8, color=C['t_dim'])


# ══════════════════════════════════════════════════════════════════
# 2)  PHASE 1 — Specialists container (center)
# ══════════════════════════════════════════════════════════════════
P1 = (2.0, 8.0, 8.0, 2.55)
rbox(*P1, fc=C['phase1'][0], ec=C['phase1'][1], lw=1.6, r=0.18, zorder=1)

# Header inside phase-1
stext(P1[0] + 0.25, P1[1] + P1[3] - 0.22,
      "Phase 1 — Specialist Agents (parallel, independent)",
      fs=9.2, fw='bold', color=C['phase1'][1], ha='left')

# 4 agent cards (compact)
AGENT_Y, AGENT_H, AGENT_W = 8.25, 1.75, 1.75
AGENT_X = [2.22, 4.17, 6.12, 8.07]
AGENT_LABELS = [
    ("Medical\nOncologist", "Chemo · Targeted · IO"),
    ("Thoracic\nSurgeon",   "Surgical candidacy"),
    ("Radiation\nOncologist","SBRT · CRT"),
    ("Pathologist /\nMolecular", "Biomarker interp."),
]
for (x, (title, sub)) in zip(AGENT_X, AGENT_LABELS):
    rbox(x, AGENT_Y, AGENT_W, AGENT_H,
         fc=C['agent'][0], ec=C['agent'][1], lw=1.0, r=0.10)
    stext(x + AGENT_W/2, AGENT_Y + 1.15, title,
          fs=8.8, fw='bold', color=C['phase1'][1])
    stext(x + AGENT_W/2, AGENT_Y + 0.35, sub,
          fs=7.3, color=C['t_dim'])


# ══════════════════════════════════════════════════════════════════
# 3)  RAG SIDECAR (left of Phase 1)
# ══════════════════════════════════════════════════════════════════
RAG = (0.12, 8.25, 1.72, 2.3)
rbox(*RAG, fc=C['rag'][0], ec=C['rag'][1], lw=1.4, r=0.14)
stext(RAG[0] + RAG[2]/2, RAG[1] + RAG[3] - 0.22,
      "RAG Sidecar", fs=9.5, fw='bold', color=C['rag'][1])

# RAG internal micro-components (small pills)
rag_items = [
    "NCCN · 618 pp",
    "6,252 chunks",
    "FAISS index",
    "top-k = 5",
]
pill_top_y = RAG[1] + RAG[3] - 0.60
pill_w = RAG[2] - 0.24
pill_h = 0.34
pill_gap = 0.10
for i, label in enumerate(rag_items):
    pill_x = RAG[0] + 0.12
    pill_y = pill_top_y - i * (pill_h + pill_gap) - pill_h
    rbox(pill_x, pill_y, pill_w, pill_h,
         fc='white', ec=C['rag'][1], lw=0.7, r=0.10)
    stext(pill_x + pill_w/2, pill_y + pill_h/2, label,
          fs=7.2, color=C['rag'][1])

# RAG → Phase 1 (single augmentation arrow, dashed)
arrow(RAG[0] + RAG[2], RAG[1] + RAG[3]/2,
      P1[0] + 0.02, P1[1] + P1[3]/2,
      color=C['a_rag'], lw=1.8, ls='--', mutation=20, shrink=2)


# ══════════════════════════════════════════════════════════════════
# 4)  PHASE 2 — Moderator
# ══════════════════════════════════════════════════════════════════
P2 = (2.8, 5.45, 6.4, 1.95)
rbox(*P2, fc=C['phase2'][0], ec=C['phase2'][1], lw=1.5, r=0.16)
stext(P2[0] + 0.25, P2[1] + P2[3] - 0.22,
      "Phase 2 — Moderator Synthesis",
      fs=9.2, fw='bold', color=C['phase2'][1], ha='left')

MOD = (3.3, 5.70, 5.4, 1.35)
rbox(*MOD, fc=C['moderator'][0], ec=C['moderator'][1], lw=1.4, r=0.12)
stext(MOD[0] + MOD[2]/2, MOD[1] + MOD[3] - 0.30,
      "MDT Coordinator", fs=10.5, fw='bold', color=C['phase2'][1])
stext(MOD[0] + MOD[2]/2, MOD[1] + 0.42,
      "(1) Consensus plan  ·  (2) Resolve disagreement  ·  (3) Follow-up",
      fs=7.7, color='#1F2937')


# ══════════════════════════════════════════════════════════════════
# 5)  OUTPUT
# ══════════════════════════════════════════════════════════════════
OUT = (3.5, 3.55, 5.0, 1.0)
rbox(*OUT, fc=C['output'][0], ec=C['output'][1], lw=1.5, r=0.14)
stext(OUT[0] + OUT[2]/2, OUT[1] + OUT[3] - 0.28,
      "Final MDT Recommendation", fs=10.5, fw='bold', color=C['output'][1])
stext(OUT[0] + OUT[2]/2, OUT[1] + 0.32,
      "Consensus output for evaluation",
      fs=7.8, color=C['t_dim'])


# ══════════════════════════════════════════════════════════════════
# 6)  EVALUATION container (bottom)
# ══════════════════════════════════════════════════════════════════
EV = (1.2, 0.35, 9.6, 2.55)
rbox(*EV, fc=C['evalbg'][0], ec=C['evalbg'][1], lw=1.5, r=0.16)
stext(EV[0] + 0.25, EV[1] + EV[3] - 0.22,
      "LLM-as-Judge Evaluation",
      fs=9.2, fw='bold', color=C['evalbg'][1], ha='left')

# Gold standard (left)
GOLD = (1.55, 1.1, 2.05, 1.15)
rbox(*GOLD, fc=C['gold'][0], ec=C['gold'][1], lw=1.2, r=0.12)
stext(GOLD[0] + GOLD[2]/2, GOLD[1] + GOLD[3] - 0.30,
      "Gold Standard", fs=9.2, fw='bold', color=C['gold'][1])
stext(GOLD[0] + GOLD[2]/2, GOLD[1] + 0.35,
      "Expert-annotated\nNCCN-grounded",
      fs=7.4, color=C['t_dim'])

# Judge 1
J1 = (4.25, 1.1, 2.05, 1.15)
rbox(*J1, fc=C['judge'][0], ec=C['judge'][1], lw=1.2, r=0.12)
stext(J1[0] + J1[2]/2, J1[1] + J1[3] - 0.30,
      "Judge  J\u2081", fs=9.2, fw='bold', color=C['judge'][1])
stext(J1[0] + J1[2]/2, J1[1] + 0.35,
      "GPT-4o-mini\n(OpenAI)", fs=7.4, color=C['t_dim'])

# Judge 2
J2 = (6.95, 1.1, 2.05, 1.15)
rbox(*J2, fc=C['judge'][0], ec=C['judge'][1], lw=1.2, r=0.12)
stext(J2[0] + J2[2]/2, J2[1] + J2[3] - 0.30,
      "Judge  J\u2082", fs=9.2, fw='bold', color=C['judge'][1])
stext(J2[0] + J2[2]/2, J2[1] + 0.35,
      "Claude Sonnet 4.5\n(Anthropic)", fs=7.4, color=C['t_dim'])

# Scores output (right)
SCORE = (9.55, 1.1, 1.15, 1.15)
rbox(*SCORE, fc='white', ec=C['evalbg'][1], lw=1.2, r=0.12)
stext(SCORE[0] + SCORE[2]/2, SCORE[1] + SCORE[3] - 0.30,
      "Scores", fs=9.2, fw='bold', color=C['evalbg'][1])
stext(SCORE[0] + SCORE[2]/2, SCORE[1] + 0.40,
      "4×(1-5)\n+ 2×(0/1)",
      fs=7.2, color=C['evalbg'][1])

# Internal arrows in evaluation: Gold → Judges, Judges → Scores
arrow(GOLD[0] + GOLD[2], GOLD[1] + GOLD[3]/2,
      J1[0], J1[1] + J1[3]/2, color=C['a_eval'], lw=1.0, ls=':',
      mutation=12)
arrow(J1[0] + J1[2], J1[1] + J1[3]/2,
      J2[0], J2[1] + J2[3]/2, color=C['a_eval'], lw=1.0, ls=':',
      mutation=12)
arrow(J2[0] + J2[2], J2[1] + J2[3]/2,
      SCORE[0], SCORE[1] + SCORE[3]/2, color=C['a_eval'], lw=1.0, ls=':',
      mutation=12)

# Rubric line at the bottom of Eval container
stext(EV[0] + EV[2]/2, EV[1] + 0.62,
      "Dimensions:  Accuracy · Completeness · Safety · Concordance"
      "  |  Flags:  Hallucination · Safety-violation",
      fs=7.4, color=C['evalbg'][1], fw='normal')


# ══════════════════════════════════════════════════════════════════
#  MAIN SPINE ARROWS (only 4!)
# ══════════════════════════════════════════════════════════════════
# Input → Phase 1
arrow(IN[0] + IN[2]/2, IN[1],
      P1[0] + P1[2]/2, P1[1] + P1[3],
      color=C['a_main'], lw=2.0, mutation=20)
stext(IN[0] + IN[2]/2 + 0.15, (IN[1] + P1[1] + P1[3])/2 + 0.05,
      "broadcast",
      fs=7.2, color=C['t_dim'], style='italic', ha='left')

# Phase 1 → Phase 2
arrow(P1[0] + P1[2]/2, P1[1],
      P2[0] + P2[2]/2, P2[1] + P2[3],
      color=C['a_main'], lw=2.0, mutation=20)
stext(P1[0] + P1[2]/2 + 0.15, (P1[1] + P2[1] + P2[3])/2 + 0.03,
      "4 opinions",
      fs=7.2, color=C['t_dim'], style='italic', ha='left')

# Phase 2 → Output
arrow(P2[0] + P2[2]/2, P2[1],
      OUT[0] + OUT[2]/2, OUT[1] + OUT[3],
      color=C['a_main'], lw=2.0, mutation=20)
stext(P2[0] + P2[2]/2 + 0.15, (P2[1] + OUT[1] + OUT[3])/2 + 0.03,
      "consensus",
      fs=7.2, color=C['t_dim'], style='italic', ha='left')

# Output → Evaluation
arrow(OUT[0] + OUT[2]/2, OUT[1],
      OUT[0] + OUT[2]/2, EV[1] + EV[3],
      color=C['a_main'], lw=2.0, mutation=20)
stext(OUT[0] + OUT[2]/2 + 0.15, (OUT[1] + EV[1] + EV[3])/2 + 0.03,
      "evaluate",
      fs=7.2, color=C['t_dim'], style='italic', ha='left')


# ══════════════════════════════════════════════════════════════════
#  LEGEND (bottom-right corner, compact)
# ══════════════════════════════════════════════════════════════════
legend_elements = [
    Line2D([0], [0], color=C['a_main'], lw=2.0, label='Main flow'),
    Line2D([0], [0], color=C['a_rag'],  lw=1.5, linestyle='--',
           label='RAG augmentation'),
    Line2D([0], [0], color=C['a_eval'], lw=1.2, linestyle=':',
           label='Evaluation'),
]
leg = ax.legend(handles=legend_elements,
                loc='upper right', bbox_to_anchor=(0.98, 0.96),
                fontsize=8.5, frameon=True, framealpha=0.95,
                edgecolor='#CBD5E1', ncol=1, handlelength=2.3,
                borderpad=0.55, title="Edge semantics",
                title_fontsize=9)
leg.get_frame().set_linewidth(0.6)


# ──────────────── Save ────────────────
for out in ["outputs/figures/fig1_architecture.png",
            "outputs/figures/fig1_architecture.pdf",
            "paper/latex/figures/fig1_architecture.png",
            "paper/latex/figures/fig1_architecture.pdf"]:
    plt.savefig(out)
print("Saved fig1_architecture v3 (minimalist, single-axis flow)")
