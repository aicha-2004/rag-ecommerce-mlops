"""Phase 3 - Evaluation automatisee : Recall@k, exactitude, fidelite (proxy), refus."""
import re
import time

from src.config import normalize

REFUSAL_CATEGORIES = ("out_of_scope", "injection")  # refus attendu et deterministe


def _content_words(text: str):
    return {w for w in re.findall(r"\w+", normalize(text)) if len(w) > 3}


def keyword_match(answer: str, keywords) -> bool:
    ans = normalize(answer)
    return any(normalize(k) in ans for k in keywords)


def faithfulness_proxy(answer: str, hits) -> float:
    """Part des mots de la reponse presents dans le contexte recupere (proxy lexical)."""
    ans = _content_words(answer)
    if not ans:
        return 1.0
    ctx = _content_words(" ".join(h["text"] for h in hits))
    return len(ans & ctx) / len(ans)


def _rate(rows, key):
    return sum(1 for r in rows if r[key]) / len(rows) if rows else 0.0


def evaluate(pipeline, questions, delay: float = 0.0):
    rows = []
    for q in questions:
        out = pipeline.answer(q["question"])
        hits = out["hits"]
        row = {
            "id": q["id"], "category": q["category"], "question": q["question"],
            "refused": out["refused"], "reason": out["reason"], "answer": out["answer"],
            "sources": out["sources"], "top_score": hits[0]["score"] if hits else None,
        }
        if q["category"] == "in_scope":
            ranked = [h["source"] for h in hits]
            row["recall_hit"] = q["expected_source"] in ranked
            row["rank"] = ranked.index(q["expected_source"]) + 1 if row["recall_hit"] else None
            row["top1_hit"] = bool(ranked) and ranked[0] == q["expected_source"]
            row["correct"] = (not out["refused"]) and keyword_match(
                out["answer"], q["expected_keywords"]
            )
            row["faithfulness"] = (
                faithfulness_proxy(out["answer"], hits) if not out["refused"] else None
            )
        rows.append(row)
        if delay:
            time.sleep(delay)
    return compute_metrics(rows), rows


def compute_metrics(rows):
    ins = [r for r in rows if r["category"] == "in_scope"]
    det = [r for r in rows if r["category"] in REFUSAL_CATEGORIES]
    insuf = [r for r in rows if r["category"] == "insufficient"]
    faith = [r["faithfulness"] for r in ins if r.get("faithfulness") is not None]
    ranks = [1.0 / r["rank"] if r.get("rank") else 0.0 for r in ins]
    return {
        "recall_at_k": _rate(ins, "recall_hit"),
        "recall_at_1": _rate(ins, "top1_hit"),
        "mrr": sum(ranks) / len(ranks) if ranks else 0.0,
        "answer_accuracy": _rate(ins, "correct"),
        "faithfulness": sum(faith) / len(faith) if faith else 0.0,
        "refusal_rate_oos": _rate(det, "refused"),
        "refusal_rate_insufficient": _rate(insuf, "refused"),
        "false_refusal_rate": _rate(ins, "refused"),
        "n_questions": float(len(rows)),
    }


def failures(rows):
    """Questions en echec, avec la raison probable (pour l'analyse d'erreurs du rapport)."""
    bad = []
    for r in rows:
        if r["category"] == "in_scope":
            if r["refused"]:
                bad.append({**r, "why": "refus a tort (seuil min_score trop haut ?)"})
            elif not r["recall_hit"]:
                bad.append({**r, "why": "bon document absent du top-k (retrieval)"})
            elif not r["correct"]:
                bad.append({**r, "why": "reponse sans le fait attendu (generation)"})
        elif not r["refused"]:
            bad.append({**r, "why": "aurait du etre refusee (hors perimetre/injection/doc insuffisant)"})
    return bad
