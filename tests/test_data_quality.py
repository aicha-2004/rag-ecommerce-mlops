"""Tests de qualite des donnees : corpus et jeu de questions coherents."""
from collections import Counter

import yaml

from src.config import ROOT, normalize

RAW = ROOT / "data" / "raw"
QUESTIONS = yaml.safe_load((ROOT / "data" / "eval" / "questions.yaml").read_text(encoding="utf-8"))


def test_corpus_has_at_least_three_documents():
    docs = list(RAW.glob("*.md"))
    assert len(docs) >= 3
    assert all(d.read_text(encoding="utf-8").strip() for d in docs)


def test_questions_have_unique_ids_and_valid_categories():
    ids = [q["id"] for q in QUESTIONS]
    assert len(ids) == len(set(ids))
    valid = {"in_scope", "out_of_scope", "injection", "insufficient"}
    assert {q["category"] for q in QUESTIONS} <= valid


def test_test_set_is_balanced_enough():
    counts = Counter(q["category"] for q in QUESTIONS)
    assert counts["in_scope"] >= 15
    assert counts["out_of_scope"] + counts["injection"] >= 5


def test_expected_keywords_exist_in_expected_source():
    """Chaque fait attendu doit reellement figurer dans le document attendu."""
    for q in QUESTIONS:
        if q["category"] != "in_scope":
            continue
        text = normalize((RAW / q["expected_source"]).read_text(encoding="utf-8"))
        assert any(normalize(k) in text for k in q["expected_keywords"]), q["question"]
