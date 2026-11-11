"""Chargement de params.yaml et utilitaires de texte communs."""
import re
import unicodedata
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def load_params(path=None):
    path = Path(path) if path else ROOT / "params.yaml"
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def normalize(text: str) -> str:
    """Minuscules, sans accents, espaces insecables et apostrophes typographiques unifies.

    Evite les faux echecs de comparaison (cf. TP3 : « 80 % » avec une espace insecable).
    """
    text = unicodedata.normalize("NFKC", text)
    text = text.replace("\u00a0", " ").replace("\u202f", " ").replace("\u2019", "'")
    text = unicodedata.normalize("NFD", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    return re.sub(r"\s+", " ", text.lower()).strip()
