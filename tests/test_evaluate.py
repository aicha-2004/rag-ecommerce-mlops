from src.evaluate import compute_metrics, faithfulness_proxy, keyword_match


def test_keyword_match_ignores_case_accents_and_nbsp():
    assert keyword_match("Le remboursement prend 7\u00a0jours ouvrés.", ["7 jours"])
    assert keyword_match("A LA CHARGE DU CLIENT", ["à la charge du client"])
    assert not keyword_match("Réponse sans rapport", ["14 jours"])


def test_faithfulness_proxy():
    hits = [{"text": "Le remboursement est effectue sous 7 jours ouvres"}]
    assert faithfulness_proxy("remboursement effectue sous 7 jours", hits) == 1.0
    assert faithfulness_proxy("ordinateur portable gratuit", hits) < 0.5


def _row(cat, refused, **kw):
    base = {"category": cat, "refused": refused}
    base.update(kw)
    return base


def test_compute_metrics_on_toy_rows():
    rows = [
        _row("in_scope", False, recall_hit=True, rank=1, top1_hit=True, correct=True,
             faithfulness=1.0),
        _row("in_scope", False, recall_hit=True, rank=2, top1_hit=False, correct=False,
             faithfulness=0.5),
        _row("in_scope", True, recall_hit=False, rank=None, top1_hit=False, correct=False,
             faithfulness=None),
        _row("out_of_scope", True),
        _row("injection", False),
        _row("insufficient", True),
    ]
    m = compute_metrics(rows)
    assert m["recall_at_k"] == 2 / 3
    assert m["recall_at_1"] == 1 / 3
    assert round(m["mrr"], 3) == round((1 + 0.5 + 0) / 3, 3)
    assert m["answer_accuracy"] == 1 / 3
    assert m["refusal_rate_oos"] == 0.5
    assert m["false_refusal_rate"] == 1 / 3
    assert m["refusal_rate_insufficient"] == 1.0
