"""Construction du pipeline a partir de params.yaml (partage par les scripts)."""
import yaml
from dotenv import load_dotenv

from src.config import ROOT
from src.embedding import get_embedder
from src.index import Retriever, build_index
from src.ingest import build_chunks
from src.llm import get_llm
from src.rag import RAGPipeline


def prepare(params, index_dir=None):
    """Ingestion + indexation. Retourne (chunks, embedder, index_dir)."""
    load_dotenv()
    index_dir = index_dir or ROOT / "artifacts" / "index"
    cfg = params["chunking"]
    chunks = build_chunks(ROOT / params["data"]["raw_dir"], cfg["chunk_size"], cfg["chunk_overlap"])
    embedder = get_embedder(params)
    build_index(chunks, embedder, index_dir)
    return chunks, embedder, index_dir


def make_pipeline(params, embedder, index_dir):
    retriever = Retriever(index_dir, embedder, params["retrieval"]["top_k"])
    return RAGPipeline(retriever, get_llm(params), params["retrieval"]["min_score"])


def load_questions(params):
    path = ROOT / params["data"]["questions"]
    return yaml.safe_load(path.read_text(encoding="utf-8"))
