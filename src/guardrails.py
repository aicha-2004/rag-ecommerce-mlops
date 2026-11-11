"""Garde-fous simples contre les tentatives de prompt injection (regex, volontairement limites)."""
import re

from src.config import normalize

INJECTION_PATTERNS = [
    r"ignore (toutes )?(tes|vos|les) (instructions|consignes|regles)",
    r"oublie (tes|vos|toutes les|toutes tes) (instructions|consignes|regles)",
    r"(revele|affiche|montre|donne).{0,25}(prompt|consignes|instructions)",
    r"prompt syst[e]?me",
    r"system prompt",
    r"ignore (all )?(previous|prior) instructions",
    r"tu es maintenant",
    r"\bact as\b",
    r"jailbreak",
    r"sans (aucune )?restriction",
]


def is_prompt_injection(text: str) -> bool:
    t = normalize(text)
    return any(re.search(p, t) for p in INJECTION_PATTERNS)
