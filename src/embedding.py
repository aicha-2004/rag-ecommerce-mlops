"""Modeles d'embeddings : reel (sentence-transformers) ou 'hashing' (tests rapides)."""
import hashlib
import re

import numpy as np

from src.config import normalize

_STOP = {
    "les", "des", "une", "est", "que", "qui", "quoi", "dans", "pour", "par", "sur", "avec",
    "pas", "vous", "nous", "mon", "ma", "mes", "son", "sa", "ses", "aux", "ont", "sont",
    "puis", "peut", "quel", "quelle", "quels", "quelles", "comment", "combien", "faire",
    "dois", "avez", "etre", "tout", "tous", "plus", "donne", "moi", "elle", "il", "ce", "cette",
}


class HashingEmbedder:
    """Sac de mots hache et normalise : deterministe, sans telechargement.

    Sert aux tests unitaires et a verifier la logique du pipeline. Ce n'est PAS un modele
    semantique : les vrais resultats se mesurent avec sentence-transformers.
    """

    def __init__(self, dim: int = 2048):
        self.dim = dim

    def encode(self, texts):
        mat = np.zeros((len(texts), self.dim), dtype="float32")
        for row, text in enumerate(texts):
            for tok in re.findall(r"\w+", normalize(text)):
                if len(tok) <= 2 or tok in _STOP:
                    continue
                h = int(hashlib.sha1(tok.encode(), usedforsecurity=False).hexdigest(), 16)
                mat[row, h % self.dim] += 1.0
        norms = np.linalg.norm(mat, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        return mat / norms


class SentenceTransformerEmbedder:
    def __init__(self, model_name: str):
        from sentence_transformers import SentenceTransformer  # import tardif (lourd)

        self.model = SentenceTransformer(model_name)

    def encode(self, texts):
        return np.asarray(
            self.model.encode(list(texts), normalize_embeddings=True, show_progress_bar=False),
            dtype="float32",
        )


def get_embedder(params):
    cfg = params["embedding"]
    if cfg["provider"] == "hashing":
        return HashingEmbedder()
    return SentenceTransformerEmbedder(cfg["model_name"])
