"""Phase 2 - Indexation : index vectoriel Chroma (similarite cosinus) + recherche."""
from pathlib import Path

import chromadb
from chromadb.config import Settings

COLLECTION = "shopmed"


def _client(index_dir):
    Path(index_dir).mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(
        path=str(index_dir), settings=Settings(anonymized_telemetry=False)
    )


def build_index(chunks, embedder, index_dir):
    client = _client(index_dir)
    names = [getattr(c, "name", c) for c in client.list_collections()]
    if COLLECTION in names:  # repart d'un index propre : pas de doublons ni de chunks perimes
        client.delete_collection(COLLECTION)
    col = client.create_collection(COLLECTION, metadata={"hnsw:space": "cosine"})
    vectors = embedder.encode([c["text"] for c in chunks])
    col.add(
        ids=[c["chunk_id"] for c in chunks],
        documents=[c["text"] for c in chunks],
        metadatas=[
            {"source": c["source"], "section": c["section"], "chunk_index": c["chunk_index"]}
            for c in chunks
        ],
        embeddings=vectors.tolist(),
    )
    return col.count()


class Retriever:
    def __init__(self, index_dir, embedder, top_k: int):
        self.col = _client(index_dir).get_collection(COLLECTION)
        self.embedder, self.top_k = embedder, top_k

    def search(self, query: str):
        vec = self.embedder.encode([query])
        k = min(self.top_k, self.col.count())
        res = self.col.query(query_embeddings=vec.tolist(), n_results=k)
        hits = []
        for cid, doc, meta, dist in zip(
            res["ids"][0], res["documents"][0], res["metadatas"][0], res["distances"][0]
        ):
            hits.append({
                "chunk_id": cid, "text": doc, "source": meta["source"],
                "section": meta.get("section", ""), "score": 1.0 - float(dist),
            })
        return hits
