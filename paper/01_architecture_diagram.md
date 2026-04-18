# Figure 1: MDT-LLM Architecture

## Primary architecture diagram (Mermaid)

```mermaid
flowchart TB
    %% ==================== INPUT ====================
    Q["<b>Clinical Vignette + Question</b><br/>e.g., 62yo male, stage IV NSCLC,<br/>EGFR exon 19 del, PD-L1 80%"]

    %% ==================== RAG PIPELINE ====================
    subgraph RAG["📚 Retrieval-Augmented Generation Pipeline"]
        direction LR
        GL["<b>NCCN Clinical Guidelines</b><br/>• NSCLC v5.2026<br/>• SCLC<br/>• Lung Cancer Screening<br/>• ICI Toxicities<br/><i>618 pages</i>"]
        CHUNK["Chunking<br/>(size=512, overlap=128)"]
        EMB["Dense Embeddings<br/>text-embedding-3-large<br/>(3072-d)"]
        FAISS["FAISS Index<br/>6,252 chunks"]
        RETR["Top-k Retrieval<br/>(k=5)"]
        GL --> CHUNK --> EMB --> FAISS --> RETR
    end

    %% ==================== PHASE 1: SPECIALISTS ====================
    subgraph PHASE1["🧑‍⚕️ Phase 1: Specialist Agents (Parallel)"]
        direction LR
        A1["<b>Medical Oncologist</b><br/>Systemic therapy<br/>Targeted/IO/Chemo"]
        A2["<b>Thoracic Surgeon</b><br/>Surgical candidacy<br/>Perioperative"]
        A3["<b>Radiation Oncologist</b><br/>RT role & dosing<br/>CRT, SBRT"]
        A4["<b>Pathologist</b><br/>Histology & molecular<br/>Biomarker interpretation"]
    end

    %% ==================== PHASE 2: MODERATOR ====================
    MOD["<b>🎯 Moderator Agent</b><br/>Synthesize consensus<br/>Resolve disagreements<br/>Cite guidelines"]

    %% ==================== OUTPUT ====================
    OUT["<b>📋 Final MDT Recommendation</b><br/>• Treatment plan (drug, dose, schedule)<br/>• Disagreement resolution<br/>• Follow-up & monitoring"]

    %% ==================== EVALUATION ====================
    subgraph EVAL["⚖️ LLM-as-Judge Evaluation"]
        direction LR
        J1["<b>Judge 1</b><br/>GPT-4o-mini"]
        J2["<b>Judge 2</b><br/>Claude Sonnet 4.5"]
        SCORES["<b>Scores</b><br/>Accuracy · Completeness<br/>Safety · Concordance<br/>Hallucination · Safety Violation<br/>(1–5 + binary)"]
        J1 --> SCORES
        J2 --> SCORES
    end

    GOLD["<b>Gold Standard</b><br/>NCCN-grounded<br/>expert-annotated answer"]

    %% ==================== EDGES ====================
    Q --> A1
    Q --> A2
    Q --> A3
    Q --> A4
    RETR -.->|"retrieved context<br/>(in RAG conditions)"| A1
    RETR -.-> A2
    RETR -.-> A3
    RETR -.-> A4
    RETR -.-> MOD

    A1 --> MOD
    A2 --> MOD
    A3 --> MOD
    A4 --> MOD

    MOD --> OUT

    OUT --> J1
    OUT --> J2
    GOLD --> J1
    GOLD --> J2

    %% ==================== STYLING ====================
    classDef inputNode fill:#FEF3C7,stroke:#F59E0B,stroke-width:2px,color:#000
    classDef agentNode fill:#DBEAFE,stroke:#3B82F6,stroke-width:2px,color:#000
    classDef ragNode fill:#D1FAE5,stroke:#10B981,stroke-width:2px,color:#000
    classDef evalNode fill:#FCE7F3,stroke:#EC4899,stroke-width:2px,color:#000
    classDef outputNode fill:#E0E7FF,stroke:#6366F1,stroke-width:3px,color:#000

    class Q inputNode
    class A1,A2,A3,A4,MOD agentNode
    class GL,CHUNK,EMB,FAISS,RETR ragNode
    class J1,J2,SCORES,GOLD evalNode
    class OUT outputNode
```

---

## Alternative simpler version (for publication)

```mermaid
flowchart LR
    Q[Clinical<br/>Question] --> S1[Specialist 1<br/>Med. Onc.]
    Q --> S2[Specialist 2<br/>Surgeon]
    Q --> S3[Specialist 3<br/>Rad. Onc.]
    Q --> S4[Specialist 4<br/>Pathologist]
    
    RAG[(NCCN<br/>Guidelines<br/>FAISS)] -.retrieved chunks.-> S1
    RAG -.-> S2
    RAG -.-> S3
    RAG -.-> S4
    RAG -.-> MOD
    
    S1 --> MOD[Moderator<br/>Synthesizer]
    S2 --> MOD
    S3 --> MOD
    S4 --> MOD
    
    MOD --> OUT[Consensus<br/>Recommendation]
```

---

## How to render for the paper

### Option 1: Export high-res PNG/SVG from Mermaid Live Editor
1. Go to https://mermaid.live
2. Paste the Mermaid code above
3. Click "Actions" → "Download as SVG" (or PNG for 2x)
4. For JKSUCIS submission, export as **SVG** (vector, lossless)

### Option 2: Rebuild in draw.io / Figma for publication quality
- Import the Mermaid SVG, clean up arrows and typography
- Keep the layout but use JKSUCIS-compatible fonts (Times / Helvetica)

### Option 3: TikZ (LaTeX-native)
```latex
\usepackage{tikz}
\usetikzlibrary{shapes,arrows,positioning,fit}
% ... (can provide TikZ code on request)
```

---

## Caption for Figure 1

> **Figure 1.** Architecture of the MDT-LLM framework. A clinical vignette and question are presented in parallel to four role-conditioned specialist agents (medical oncologist, thoracic surgeon, radiation oncologist, pathologist), each instantiated with a distinct system prompt. Their individual opinions are synthesized by a moderator agent into a consensus recommendation. When retrieval-augmented generation (RAG) is enabled, relevant chunks from the NCCN clinical guidelines (indexed in FAISS) are retrieved via dense embeddings and injected into the context of each agent. The final output is evaluated by two independent LLM judges (GPT-4o-mini, Claude Sonnet 4.5) against a gold-standard, expert-annotated answer across four scoring dimensions.

---

## Data-flow legend (for reader clarity)

| Arrow style | Meaning |
|-------------|---------|
| Solid arrow → | Always-active data flow |
| Dashed arrow -.-> | Active only when RAG condition enabled |
| Thick outline | Final output |
