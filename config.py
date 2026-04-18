"""
Configuration for Lung Cancer MDT Multi-Agent LLM Benchmark
============================================================
Fill in your API keys before running.
Supports: OpenAI, Anthropic (Claude), DeepSeek, Together AI.
"""

import os

# ── API Keys ─────────────────────────────────────────────────────
# Keys read from environment variables. To set them:
#   1) Copy .env.example to .env.local and fill in your keys
#   2) Run:  source .env.local
# OR export them directly:  export OPENAI_API_KEY="sk-..."
OPENAI_API_KEY    = os.environ.get("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
DEEPSEEK_API_KEY  = os.environ.get("DEEPSEEK_API_KEY", "")
TOGETHER_API_KEY  = os.environ.get("TOGETHER_API_KEY", "")

# Friendly error if something is missing at runtime
def _check_keys(required: list[str]):
    missing = [k for k in required if not globals().get(k)]
    if missing:
        raise RuntimeError(
            f"Missing API keys: {missing}. "
            f"Set them as environment variables (see .env.example)."
        )

# ── Model Definitions ─────────────────────────────────────────────
MODELS = {
    "gpt-4o-mini": {
        "provider": "openai",
        "model_id": "gpt-4o-mini-2024-07-18",
        "api_key_var": "OPENAI_API_KEY",
        "base_url": "https://api.openai.com/v1",
    },
    "claude-sonnet": {
        "provider": "anthropic",          # uses Anthropic SDK, NOT OpenAI-compatible
        "model_id": "claude-sonnet-4-5-20250929",
        "api_key_var": "ANTHROPIC_API_KEY",
        "base_url": None,                 # Anthropic SDK uses default endpoint
    },
    "deepseek-r1": {
        "provider": "openai",             # deepseek uses openai-compatible API
        "model_id": "deepseek-reasoner",
        "api_key_var": "DEEPSEEK_API_KEY",
        "base_url": "https://api.deepseek.com/v1",
    },
    "llama-3.3-70b": {
        "provider": "openai",
        "model_id": "meta-llama/Llama-3.3-70B-Instruct-Turbo",
        "api_key_var": "TOGETHER_API_KEY",
        "base_url": "https://api.together.xyz/v1",
    },
}

# ── RAG Settings ──────────────────────────────────────────────────
RAG_CONFIG = {
    "chunk_size": 512,
    "chunk_overlap": 128,
    "top_k": 5,
    "embedding_model": "text-embedding-3-large",  # or "BAAI/bge-large-en-v1.5" for free
    "guidelines_dir": "data/guidelines/",          # put NCCN/ESMO PDFs here
    "faiss_index_path": "data/faiss_index/",
}

# ── MDT Agent Roles ───────────────────────────────────────────────
MDT_AGENTS = {
    "medical_oncologist": {
        "role": "Medical Oncologist",
        "system_prompt": (
            "You are a board-certified medical oncologist specializing in thoracic "
            "oncology with 15 years of clinical experience. You focus on systemic "
            "therapy decisions including chemotherapy, targeted therapy, and "
            "immunotherapy. Analyze the case from a medical oncology perspective. "
            "Provide evidence-based treatment recommendations citing specific "
            "clinical trials and guideline references."
        ),
    },
    "thoracic_surgeon": {
        "role": "Thoracic Surgeon",
        "system_prompt": (
            "You are a board-certified thoracic surgeon specializing in lung cancer "
            "surgery. You evaluate surgical candidacy, operability, and the role of "
            "neoadjuvant/adjuvant approaches. Analyze the case from a surgical "
            "perspective: Is the patient a surgical candidate? What procedure is "
            "appropriate? What are the perioperative considerations?"
        ),
    },
    "radiation_oncologist": {
        "role": "Radiation Oncologist",
        "system_prompt": (
            "You are a board-certified radiation oncologist with expertise in "
            "thoracic radiation therapy. You evaluate the role of radiation "
            "(definitive, adjuvant, palliative, stereotactic) in the treatment plan. "
            "Consider radiation dose, fractionation, technique, and toxicity. "
            "Address the role of concurrent chemoradiation when applicable."
        ),
    },
    "pathologist": {
        "role": "Pathologist / Molecular Specialist",
        "system_prompt": (
            "You are a board-certified pathologist with subspecialty training in "
            "molecular pathology and thoracic cytopathology. You focus on histologic "
            "subtyping, molecular biomarker interpretation, and the clinical "
            "implications of genomic findings. Evaluate the adequacy of tissue "
            "sampling and molecular testing in the case."
        ),
    },
}

MDT_MODERATOR_PROMPT = (
    "You are the MDT coordinator chairing a multidisciplinary tumor board for "
    "lung cancer. You have received opinions from four specialists: a medical "
    "oncologist, a thoracic surgeon, a radiation oncologist, and a pathologist. "
    "Synthesize their inputs into a unified, consensus-based treatment recommendation. "
    "Clearly state: (1) the agreed treatment plan with specific drugs/doses/schedules "
    "where applicable; (2) any points of disagreement and how they were resolved; "
    "(3) recommended follow-up and monitoring. Cite relevant guidelines."
)

# ── Experiment Settings ───────────────────────────────────────────
EXPERIMENT = {
    "temperature": 0,
    "max_tokens": 1024,
    "questions_file": "all_100_questions.csv",
    "output_dir": "outputs/",
    "conditions": [
        "single_zeroshot",    # single LLM, no RAG
        "single_rag",         # single LLM + RAG
        "mdt_zeroshot",       # multi-agent MDT, no RAG
        "mdt_rag",            # multi-agent MDT + RAG
    ],
}
