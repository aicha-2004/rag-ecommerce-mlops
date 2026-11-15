"""Balaye `min_score` : pour chaque seuil, faux refus et refus hors perimetre (sans appeler le LLM)."""
from scripts.common import load_questions, prepare
from src.config import load_params
from src.index import Retriever


def main():
    p = load_params()
    _chunks, embedder, index_dir = prepare(p)
    retriever = Retriever(index_dir, embedder, p["retrieval"]["top_k"])
    valid, oos = [], []
    for q in load_questions(p):
        if q["category"] not in ("in_scope", "out_of_scope"):
            continue  # injections : refusees avant la recherche ; "insufficient" : role du LLM
        hits = retriever.search(q["question"])
        score = hits[0]["score"] if hits else 0.0
        (valid if q["category"] == "in_scope" else oos).append((score, q["question"]))

    print("Questions valides, du score le plus bas au plus haut (les 6 premieres) :")
    for s, text in sorted(valid)[:6]:
        print(f"  {s:.2f}  {text}")
    print("Questions hors perimetre, du score le plus haut au plus bas :")
    for s, text in sorted(oos, reverse=True):
        print(f"  {s:.2f}  {text}")

    print("\nmin_score | faux refus (valides) | refus hors perimetre")
    for i in range(13):
        t = round(0.20 + 0.025 * i, 3)
        fr = sum(s < t for s, _ in valid) / len(valid)
        ro = sum(s < t for s, _ in oos) / len(oos)
        print(f"  {t:.3f}   |        {fr:.2f}          |        {ro:.2f}")


if __name__ == "__main__":
    main()