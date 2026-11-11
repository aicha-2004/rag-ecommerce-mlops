import pytest

from src.config import ROOT, load_params
from src.embedding import HashingEmbedder
from src.index import Retriever, build_index
from src.ingest import build_chunks


@pytest.fixture(scope="session")
def params():
    return load_params()


@pytest.fixture(scope="session")
def built_index(tmp_path_factory, params):
    """Index reel du corpus ShopMed, avec l'embedder 'hashing' (rapide, sans telechargement)."""
    cfg = params["chunking"]
    chunks = build_chunks(ROOT / params["data"]["raw_dir"], cfg["chunk_size"], cfg["chunk_overlap"])
    embedder = HashingEmbedder()
    index_dir = tmp_path_factory.mktemp("index")
    build_index(chunks, embedder, index_dir)
    return chunks, embedder, index_dir


@pytest.fixture
def retriever(built_index, params):
    _, embedder, index_dir = built_index
    return Retriever(index_dir, embedder, params["retrieval"]["top_k"])
