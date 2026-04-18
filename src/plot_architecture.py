"""Figure 1: MDT-LLM Architecture (publication-quality v2)."""

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
from matplotlib.lines import Line2D
from matplotlib.patheffects import withStroke
import numpy as np

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 9,
    "axes.linewidth": 0.0,
    "figure.dpi": 200,
    "savefig.bbox": "tight",
    "savefig.dpi": 300,
    "pdf.fonttype": 42,   # Embed fonts (Type-1) for Elsevier compliance
    "ps.fonttype": 42,
})

# ──────────────── Design tokens (consistent palette) ────────────────
COLOR = {
    "input_fill":   "#FEF3C7", "input_edge":   "#D97706",
    "rag_fill":     "#DCFCE7", "rag_edge":     "#047857", "rag_text": "#065F46",
    "spec_fill":    "#DBEAFE", "spec_edge":    "#1D4ED8", "spec_text": "#1E3A8A",
    "mod_fill":     "#BFDBFE", "mod_edge":     "#1D4ED8", "mod_text":  "#1E3A8A",
    "out_fill":     "#E0E7FF", "out_edge":     "#4338CA",
    "eval_fill":    "#FCE7F3", "eval_edge":    "#BE185D", "eval_text": "#9D174D",
    "gold_fill":    "#FEF9C3", "gold_edge":    "#CA8A04",
    "zone_fill":    "#F8FAFC", "zone_edge":    "#CBD5E1",
    "arrow_main":   "#1F2937",
    "arrow_rag":    "#047857",
    "arrow_eval":   "#BE185D",
    "title":        "#0F172A",
}

FS_TITLE   = 14
FS_HEADER  = 9.5
FS_BOX     = 8.5
FS_SMALL   = 7.5


# ──────────────── Canvas ────────────────
fig, ax = plt.subplots(figsize=(16, 9.5))
ax.set_xlim(0, 18)
ax.set_ylim(0, 11)
ax.set_aspect('equal')
ax.axis('off')


# ──────────────── Helpers ────────────────
def rounded(x, y, w, h, fc, ec, lw=1.1, alpha=1.0, rounding=0.15):
    p = FancyBboxPatch((x, y), w, h,
                       boxstyle=f"round,pad=0.03,rounding_size={rounding}",
                       linewidth=lw, edgecolor=ec, facecolor=fc, alpha=alpha,
                       joinstyle='round')
    ax.add_patch(p)
    return p


def text_in(x, y, w, h, title, body, color_title=None, color_body='#1F2937',
            fs_title=FS_HEADER, fs_body=FS_SMALL):
    cx, cy = x + w/2, y + h/2
    color_title = color_title or '#0F172A'
    if title and body:
        ax.text(cx, cy + 0.18, title, ha='center', va='center',
                fontsize=fs_title, fontweight='bold', color=color_title)
        ax.text(cx, cy - 0.25, body, ha='center', va='center',
                fontsize=fs_body, color=color_body, linespacing=1.25)
    elif title:
        ax.text(cx, cy, title, ha='center', va='center',
                fontsize=fs_title, fontweight='bold', color=color_title)
    else:
        ax.text(cx, cy, body, ha='center', va='center',
                fontsize=fs_body, color=color_body, linespacing=1.25)


def arrow(x1, y1, x2, y2, color, lw=1.4, ls='-', shrink=6,
          style='-|>', mutation=14):
    a = FancyArrowPatch((x1, y1), (x2, y2),
                        arrowstyle=style, mutation_scale=mutation,
                        color=color, linewidth=lw, linestyle=ls,
                        shrinkA=shrink, shrinkB=shrink,
                        zorder=3,
                        capstyle='round', joinstyle='round')
    ax.add_patch(a)


def zone(x, y, w, h, label, color='#64748B'):
    """Light background zone with a label ABOVE the zone (no overlap with contents)."""
    p = Rectangle((x, y), w, h,
                  facecolor=COLOR['zone_fill'], edgecolor=COLOR['zone_edge'],
                  linewidth=0.6, linestyle=(0, (4, 3)), alpha=0.6, zorder=0)
    ax.add_patch(p)
    # Label placed as a "tab" on top of the zone
    tab_width = min(len(label) * 0.11 + 0.4, w - 0.4)
    tab = Rectangle((x + 0.2, y + h - 0.02), tab_width, 0.34,
                    facecolor='white', edgecolor=color,
                    linewidth=0.8, zorder=2)
    ax.add_patch(tab)
    ax.text(x + 0.2 + tab_width/2, y + h + 0.15, label, ha='center', va='center',
            fontsize=8.5, color=color, fontweight='bold', zorder=3)


# ──────────────── Title ────────────────
ax.text(9, 10.55, "MDT-LLM Architecture",
        ha='center', va='center', fontsize=FS_TITLE,
        fontweight='bold', color=COLOR['title'])


# ══════════════════════════════════════════════════════════════════
#  Row 0: INPUT  (top, centered)
# ══════════════════════════════════════════════════════════════════
INPUT = (5.5, 9.15, 7.0, 0.9)
rounded(*INPUT, fc=COLOR['input_fill'], ec=COLOR['input_edge'], lw=1.3)
text_in(*INPUT,
        title="Clinical Vignette + Question",
        body="(e.g., stage IV NSCLC, EGFR exon 19 deletion, PD-L1 TPS 80%; first-line therapy?)",
        fs_title=10.5, fs_body=8)


# ══════════════════════════════════════════════════════════════════
#  Left column: RAG Pipeline (vertical zone)
# ══════════════════════════════════════════════════════════════════
zone(0.25, 2.65, 3.7, 5.75, "RAG Pipeline", color=COLOR['rag_text'])

RAG_BOXES = [
    (0.55, 7.35, 3.1, 0.85, "NCCN Guidelines",   "4 PDFs · 618 pages"),
    (0.55, 6.25, 3.1, 0.85, "Chunking",           "size=512, overlap=128\n|C| = 6,252"),
    (0.55, 5.15, 3.1, 0.85, "Dense Embedding",    "text-embedding-3-large\nd = 3,072"),
    (0.55, 4.05, 3.1, 0.85, "FAISS Index",        "IndexFlatIP"),
    (0.55, 2.95, 3.1, 0.85, "Top-k Retrieval",    "k = 5"),
]
for (x, y, w, h, t, b) in RAG_BOXES:
    rounded(x, y, w, h, fc=COLOR['rag_fill'], ec=COLOR['rag_edge'],
            lw=1.0, alpha=0.95)
    text_in(x, y, w, h, title=t, body=b,
            color_title=COLOR['rag_text'], fs_title=9.2, fs_body=7.4)

# Vertical arrows inside RAG pipeline
for i in range(len(RAG_BOXES) - 1):
    x_top, y_top = RAG_BOXES[i][0] + RAG_BOXES[i][2]/2, RAG_BOXES[i][1]
    x_bot, y_bot = RAG_BOXES[i+1][0] + RAG_BOXES[i+1][2]/2, RAG_BOXES[i+1][1] + RAG_BOXES[i+1][3]
    arrow(x_top, y_top, x_bot, y_bot, color=COLOR['arrow_rag'], lw=1.0)


# ══════════════════════════════════════════════════════════════════
#  Center: PHASE 1 — 4 specialist agents (parallel)
# ══════════════════════════════════════════════════════════════════
zone(4.4, 5.55, 13.3, 2.7, "Phase 1 — Specialists (parallel, independent)",
     color=COLOR['spec_text'])

# 4 specialist boxes — spread wider, no overlap
SPEC_Y = 5.95
SPEC_WIDTH, SPEC_HEIGHT = 2.85, 1.85
SPEC_STARTS_X = [4.7, 7.9, 11.1, 14.3]
SPEC = [
    (SPEC_STARTS_X[0], "Medical Oncologist",   "Systemic therapy\nChemo · Targeted · IO"),
    (SPEC_STARTS_X[1], "Thoracic Surgeon",     "Surgical candidacy\nPerioperative"),
    (SPEC_STARTS_X[2], "Radiation Oncologist", "RT role\nSBRT · CRT · Palliative"),
    (SPEC_STARTS_X[3], "Pathologist / Molecular",  "Histology\nBiomarker interpretation"),
]
for (x, role, desc) in SPEC:
    rounded(x, SPEC_Y, SPEC_WIDTH, SPEC_HEIGHT,
            fc=COLOR['spec_fill'], ec=COLOR['spec_edge'], lw=1.2)
    text_in(x, SPEC_Y, SPEC_WIDTH, SPEC_HEIGHT, title=role, body=desc,
            color_title=COLOR['spec_text'], fs_title=9.4, fs_body=7.7)


# ══════════════════════════════════════════════════════════════════
#  Center: PHASE 2 — Moderator
# ══════════════════════════════════════════════════════════════════
zone(4.4, 3.2, 13.3, 1.95, "Phase 2 — Moderator Synthesis",
     color=COLOR['mod_text'])

MOD = (8.2, 3.45, 5.7, 1.45)
rounded(*MOD, fc=COLOR['mod_fill'], ec=COLOR['mod_edge'], lw=1.4)
ax.text(MOD[0] + MOD[2]/2, MOD[1] + MOD[3] - 0.29,
        "MDT Coordinator", ha='center', va='center',
        fontsize=10.5, fontweight='bold', color=COLOR['mod_text'])
ax.text(MOD[0] + MOD[2]/2, MOD[1] + 0.46,
        "(1) Consensus treatment plan (drug · dose · schedule)\n"
        "(2) Resolve inter-specialist disagreement\n"
        "(3) Follow-up & monitoring",
        ha='center', va='center', fontsize=8, color='#1F2937',
        linespacing=1.4)


# ══════════════════════════════════════════════════════════════════
#  Bottom-left: OUTPUT
# ══════════════════════════════════════════════════════════════════
OUT = (4.4, 1.35, 4.8, 1.1)
rounded(*OUT, fc=COLOR['out_fill'], ec=COLOR['out_edge'], lw=1.5)
text_in(*OUT, title="Final MDT Recommendation",
        body="Consensus output to evaluator",
        color_title='#312E81', fs_title=10, fs_body=7.8)


# ══════════════════════════════════════════════════════════════════
#  Bottom-right: EVALUATION (2 judges + gold)
# ══════════════════════════════════════════════════════════════════
zone(9.55, 0.45, 8.15, 2.3, "LLM-as-Judge Evaluation",
     color=COLOR['eval_text'])

# Gold standard
GOLD = (9.85, 1.55, 2.2, 0.95)
rounded(*GOLD, fc=COLOR['gold_fill'], ec=COLOR['gold_edge'], lw=1.1)
text_in(*GOLD, title="Gold Standard",
        body="Expert-annotated\n(NCCN-grounded)",
        color_title='#713F12', fs_title=9, fs_body=7.5)

# Judge 1
J1 = (12.35, 1.55, 2.35, 0.95)
rounded(*J1, fc=COLOR['eval_fill'], ec=COLOR['eval_edge'], lw=1.1)
text_in(*J1, title="Judge J\u2081",
        body="GPT-4o-mini",
        color_title=COLOR['eval_text'], fs_title=9, fs_body=7.5)

# Judge 2
J2 = (15.0, 1.55, 2.4, 0.95)
rounded(*J2, fc=COLOR['eval_fill'], ec=COLOR['eval_edge'], lw=1.1)
text_in(*J2, title="Judge J\u2082",
        body="Claude Sonnet 4.5",
        color_title=COLOR['eval_text'], fs_title=9, fs_body=7.5)

# Score dimensions
SCORES = (9.85, 0.6, 7.55, 0.85)
rounded(*SCORES, fc="white", ec=COLOR['eval_edge'], lw=0.9, alpha=0.95)
ax.text(SCORES[0] + SCORES[2]/2, SCORES[1] + SCORES[3]/2,
        "Scoring rubric: Accuracy · Completeness · Safety · Concordance (1–5)  |  "
        "Hallucination · Safety-violation (0/1)",
        ha='center', va='center', fontsize=7.8, color=COLOR['eval_text'])


# ══════════════════════════════════════════════════════════════════
#  ARROWS (no overlap, clear semantic grouping)
# ══════════════════════════════════════════════════════════════════
# 1) INPUT → each specialist (main solid)
input_cx, input_by = INPUT[0] + INPUT[2]/2, INPUT[1]
for (x, _, _) in SPEC:
    arrow(input_cx, input_by,
          x + SPEC_WIDTH/2, SPEC_Y + SPEC_HEIGHT + 0.02,
          color=COLOR['arrow_main'], lw=1.15)

# 2) RAG retrieval → each specialist (dashed green)
rag_out_x = RAG_BOXES[-1][0] + RAG_BOXES[-1][2]
rag_out_y = RAG_BOXES[-1][1] + RAG_BOXES[-1][3]/2
for (x, _, _) in SPEC:
    arrow(rag_out_x, rag_out_y,
          x + 0.12, SPEC_Y + SPEC_HEIGHT/2,
          color=COLOR['arrow_rag'], lw=1.0, ls='--')
# RAG → Moderator (dashed green)
arrow(rag_out_x, rag_out_y,
      MOD[0] + 0.12, MOD[1] + MOD[3]/2,
      color=COLOR['arrow_rag'], lw=1.0, ls='--')

# 3) Each specialist → moderator (solid blue funnel)
mod_top_cx = MOD[0] + MOD[2]/2
mod_top_y  = MOD[1] + MOD[3]
for (x, _, _) in SPEC:
    arrow(x + SPEC_WIDTH/2, SPEC_Y,
          mod_top_cx, mod_top_y,
          color=COLOR['arrow_main'], lw=1.1)

# 4) Moderator → Output (short diagonal from mod bottom-left to output top-right)
arrow(MOD[0] + 0.5, MOD[1],
      OUT[0] + OUT[2] - 0.3, OUT[1] + OUT[3],
      color=COLOR['arrow_main'], lw=1.5)

# 5) Output → Judges (dotted magenta)
out_r_x, out_r_y = OUT[0] + OUT[2], OUT[1] + OUT[3]/2
arrow(out_r_x, out_r_y,
      J1[0], J1[1] + J1[3]/2,
      color=COLOR['arrow_eval'], lw=1.1, ls=':')
arrow(out_r_x, out_r_y,
      J2[0], J2[1] + J2[3]/2,
      color=COLOR['arrow_eval'], lw=1.1, ls=':')

# 6) Gold standard → Judges (dotted)
g_r_x, g_r_y = GOLD[0] + GOLD[2], GOLD[1] + GOLD[3]/2
arrow(g_r_x, g_r_y, J1[0], J1[1] + J1[3]/2,
      color=COLOR['arrow_eval'], lw=0.8, ls=':')
arrow(g_r_x, g_r_y, J2[0], J2[1] + J2[3]/2,
      color=COLOR['arrow_eval'], lw=0.8, ls=':')


# ══════════════════════════════════════════════════════════════════
#  LEGEND (bottom-center, clean)
# ══════════════════════════════════════════════════════════════════
legend_elements = [
    Line2D([0], [0], color=COLOR['arrow_main'], lw=1.6, label='Main flow'),
    Line2D([0], [0], color=COLOR['arrow_rag'],  lw=1.4, linestyle='--',
           label='RAG context (RAG conditions only)'),
    Line2D([0], [0], color=COLOR['arrow_eval'], lw=1.2, linestyle=':',
           label='Evaluation'),
]
leg = ax.legend(handles=legend_elements,
                loc='lower left', bbox_to_anchor=(0.005, 0.01),
                fontsize=8.5, frameon=True, framealpha=0.95,
                edgecolor='#CBD5E1', ncol=1,
                handlelength=2.2, borderpad=0.5)
leg.get_frame().set_linewidth(0.6)


# ──────────────── Save ────────────────
for out in ["outputs/figures/fig1_architecture.png",
            "outputs/figures/fig1_architecture.pdf",
            "paper/latex/figures/fig1_architecture.png",
            "paper/latex/figures/fig1_architecture.pdf"]:
    plt.savefig(out)
print("Saved fig1_architecture (PNG + PDF, v2 redesign)")
