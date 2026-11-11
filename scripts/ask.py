"""Demo : poser une question a l'assistant.

    python -m scripts.ask                       (mode interactif)
    python -m scripts.ask -q "Quel est le delai de retour ?"
"""
import argparse

from scripts.common import make_pipeline, prepare
from src.config import ROOT, load_params


def show(out):
    print("\n" + out["answer"])
    if out["sources"]:
        print("Sources :", " | ".join(out["sources"]))
    if out["refused"]:
        print(f"[refus : {out['reason']}]")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("-q", "--question")
    a = ap.parse_args(argv)
    params = load_params()
    index_dir = ROOT / "artifacts" / "index"
    _chunks, embedder, index_dir = prepare(params, index_dir)  # index toujours a jour
    pipe = make_pipeline(params, embedder, index_dir)
    if a.question:
        show(pipe.answer(a.question))
        return
    while True:
        q = input("\nQuestion (q pour quitter) > ").strip()
        if q.lower() in {"q", "quit", "exit"}:
            break
        if q:
            show(pipe.answer(q))


if __name__ == "__main__":
    main()
