"""Exporte les runs MLflow en tableau (Markdown/CSV) et en graphique pour le rapport."""
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mlflow

from src.config import ROOT

COLS = {
    "tags.mlflow.runName": "run", "params.chunk_strategy": "strategie", "params.chunk_size": "chunk_size",
    "params.embedding_model": "embedding", "params.top_k": "top_k",
    "params.min_score": "min_score", "metrics.recall_at_k": "recall@k",
    "metrics.answer_accuracy": "accuracy", "metrics.faithfulness": "faithfulness",
    "metrics.refusal_rate_oos": "refus_oos", "metrics.false_refusal_rate": "faux_refus",
}


def main():
    mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "http://127.0.0.1:5000"))
    df = mlflow.search_runs(experiment_names=["rag-ecommerce"], order_by=["start_time ASC"])
    df = df[[c for c in COLS if c in df.columns]].rename(columns=COLS)
    out = ROOT / "reports"
    out.mkdir(exist_ok=True)
    df.to_csv(out / "experiments.csv", index=False)
    (out / "experiments.md").write_text(df.round(3).to_markdown(index=False), encoding="utf-8")
    metrics = [m for m in ("recall@k", "accuracy", "faithfulness", "refus_oos") if m in df]
    ax = df.set_index("run")[metrics].plot.bar(figsize=(8, 4), ylim=(0, 1.05), rot=30)
    ax.set_ylabel("score")
    ax.set_title("Comparaison des experiences")
    plt.tight_layout()
    plt.savefig(out / "experiments.png", dpi=150)
    print(df.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
