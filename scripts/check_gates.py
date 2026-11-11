"""Quality gates : echoue (code 1) si une metrique ne respecte pas son seuil (params.yaml)."""
import json
import sys

from src.config import ROOT, load_params


def check(metrics, gates):
    rules = [
        ("recall_at_k", ">=", gates["min_recall_at_k"]),
        ("refusal_rate_oos", ">=", gates["min_refusal_rate_oos"]),
        ("answer_accuracy", ">=", gates["min_answer_accuracy"]),
        ("false_refusal_rate", "<=", gates["max_false_refusal_rate"]),
    ]
    results = []
    for name, op, thr in rules:
        val = metrics[name]
        ok = val >= thr if op == ">=" else val <= thr
        results.append((name, op, thr, val, ok))
    return results


def main():
    metrics = json.loads((ROOT / "reports" / "metrics.json").read_text(encoding="utf-8"))
    results = check(metrics, load_params()["quality_gate"])
    for name, op, thr, val, ok in results:
        print(f"{'OK    ' if ok else 'ECHEC '} {name} = {val:.2f} (exige {op} {thr})")
    if not all(r[-1] for r in results):
        print("QUALITY GATE ECHOUEE : deploiement bloque.")
        sys.exit(1)
    print("Quality gates OK.")


if __name__ == "__main__":
    main()
