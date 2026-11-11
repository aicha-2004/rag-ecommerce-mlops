"""Aide au choix de min_score : compare les scores des questions valides et hors perimetre."""
import json

from scripts.common import load_questions, prepare
from src.config import ROOT, load_params
from src.index import Retriever


def main():
    p = load_params()
    _chunks, embedder, index_dir = prepare(p)
    retr = Retriever(index_dir, embedder, p["retrieval"]["top_k"])
    scores = {"in_scope": [], "other": []}
    for q in load_questions(p):
        hits = retr.search(q["question"])
        top = hits[0]["score"] if hits else 0.0
        key = "in_scope" if q["category"] == "in_scope" else "other"
        scores[key].append((top, q["category"], q["question"]))
    low_in = min(s for s, _, _ in scores["in_scope"])
    high_out = max(s for s, c, _ in scores["other"] if c == "out_of_scope")
    print(f"Score le plus bas (questions valides)        : {low_in:.2f}")
    print(f"Score le plus haut (questions hors perimetre) : {high_out:.2f}")
    if low_in > high_out:
        print(f"-> seuil conseille : {(low_in + high_out) / 2:.2f} (zone de separation)")
    else:
        print("-> les scores se chevauchent : changez de modele d'embeddings ou de chunking.")
    detail = {k: [(round(s, 3), c, q) for s, c, q in v] for k, v in scores.items()}
    (ROOT / "reports" / "calibration.json").write_text(
        json.dumps(detail, ensure_ascii=False, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
