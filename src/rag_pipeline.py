"""
RAG Pipeline: Build and query a FAISS-based retrieval system
over lung cancer clinical guidelines (NCCN / ESMO).
"""

import os, json, pickle
from pathlib import Path

from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

import config


def load_guidelines(guidelines_dir: str) -> list:
    """Load all PDF files from the guidelines directory."""
    docs = []
    gdir = Path(guidelines_dir)
    for pdf in gdir.glob("*.pdf"):
        print(f"  Loading {pdf.name} ...")
        loader = PyMuPDFLoader(str(pdf))
        docs.extend(loader.load())
    print(f"  Total pages loaded: {len(docs)}")
    return docs


def build_index(force_rebuild: bool = False):
    """Chunk guidelines, embed, and build FAISS index."""
    index_path = Path(config.RAG_CONFIG["faiss_index_path"])

    if index_path.exists() and not force_rebuild:
        print("[RAG] Loading existing FAISS index ...")
        embeddings = OpenAIEmbeddings(
            model=config.RAG_CONFIG["embedding_model"],
            openai_api_key=config.OPENAI_API_KEY,
        )
        vectorstore = FAISS.load_local(
            str(index_path), embeddings, allow_dangerous_deserialization=True
        )
        return vectorstore

    print("[RAG] Building new FAISS index ...")
    docs = load_guidelines(config.RAG_CONFIG["guidelines_dir"])

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.RAG_CONFIG["chunk_size"],
        chunk_overlap=config.RAG_CONFIG["chunk_overlap"],
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(docs)
    print(f"  Total chunks: {len(chunks)}")

    embeddings = OpenAIEmbeddings(
        model=config.RAG_CONFIG["embedding_model"],
        openai_api_key=config.OPENAI_API_KEY,
    )
    vectorstore = FAISS.from_documents(chunks, embeddings)

    index_path.mkdir(parents=True, exist_ok=True)
    vectorstore.save_local(str(index_path))
    print(f"  Index saved to {index_path}")
    return vectorstore


def retrieve(vectorstore, query: str, top_k: int = None) -> str:
    """Retrieve top-k relevant chunks and return concatenated context."""
    k = top_k or config.RAG_CONFIG["top_k"]
    results = vectorstore.similarity_search(query, k=k)
    context = "\n\n---\n\n".join(
        [f"[Source: {r.metadata.get('source', 'unknown')}, "
         f"Page {r.metadata.get('page', '?')}]\n{r.page_content}"
         for r in results]
    )
    return context


if __name__ == "__main__":
    # Quick test
    vs = build_index()
    ctx = retrieve(vs, "first-line treatment EGFR exon 19 deletion NSCLC")
    print("\n=== Retrieved Context (preview) ===")
    print(ctx[:1000])
