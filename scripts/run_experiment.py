"""Lance une experience : ingestion -> index -> evaluation, tracee dans MLflow.

Exemples :
    python -m scripts.run_experiment --run-name chunk400
    python -m scripts.run_experiment --run-name chunk800 --chunk-size 800 --overlap 100
"""
import argparse
import json
import os
import subprocess  # nosec B404
from pathlib import Path

import mlflow
import yaml

from scripts.common import load_questions, make_pipeline, prepare
from src.config import ROOT, load_params
from src.evaluate import evaluate, failures


def git_commit():
    try:
        # appel local de git, sans aucune entree utilisateur
        cmd = ["git", "rev-parse", "--short", "HEAD"]
        out = subprocess.check_output(cmd, cwd=ROOT, text=True)  # nosec B603 B607
        return out.strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def dvc_data_hash():
    """Hash DVC du corpus (data/raw.dvc) : identifie la version exacte des donnees."""
    try:
        meta = yaml.safe_load((ROOT / "data" / "raw.dvc").read_text(encoding="utf-8"))
        return meta["outs"][0].get("md5", "unknown")
    except (OSError, KeyError, IndexError, TypeError):
        return "unknown"


def main(argv=None):
    p = load_params()
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-name", default="run")
    ap.add_argument("--chunk-size", type=int, default=p["chunking"]["chunk_size"])
    ap.add_argument("--overlap", type=int, default=p["chunking"]["chunk_overlap"])
    ap.add_argument("--embedding", default=p["embedding"]["model_name"])
    ap.add_argument("--provider", default=p["embedding"]["provider"])
    ap.add_argument("--top-k", type=int, default=p["retrieval"]["top_k"])
    ap.add_argument("--min-score", type=float, default=p["retrieval"]["min_score"])
    a = ap.parse_args(argv)

    p["chunking"].update(chunk_size=a.chunk_size, chunk_overlap=a.overlap)
    p["embedding"].update(model_name=a.embedding, provider=a.provider)
    p["retrieval"].update(top_k=a.top_k, min_score=a.min_score)

    mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "http://127.0.0.1:5000"))
    mlflow.set_experiment("rag-ecommerce")

    chunks, embedder, index_dir = prepare(p)
    pipeline = make_pipeline(p, embedder, index_dir)
    metrics, rows = evaluate(pipeline, load_questions(p), float(os.getenv("EVAL_DELAY", "0")))
    metrics["n_chunks"] = float(len(chunks))

    out = ROOT / "reports"
    out.mkdir(exist_ok=True)
    (out / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    (out / "details.json").write_text(
        json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (out / "failures.json").write_text(
        json.dumps(failures(rows), ensure_ascii=False, indent=2), encoding="utf-8"
    )

    llm_name = pipeline.llm.name
    with mlflow.start_run(run_name=a.run_name):
        mlflow.log_params({
            "chunk_size": a.chunk_size, "chunk_overlap": a.overlap,
            "embedding_provider": a.provider, "embedding_model": a.embedding,
            "top_k": a.top_k, "min_score": a.min_score,
            "llm_provider": llm_name, "llm_model": p["llm"]["model"],
            "temperature": p["llm"]["temperature"],
        })
        mlflow.set_tags({"git_commit": git_commit(), "dvc_data_hash": dvc_data_hash()})
        mlflow.log_metrics(metrics)
        for f in ("details.json", "failures.json", "metrics.json"):
            mlflow.log_artifact(str(out / f))
        for f in ("params.yaml", "prompts/rag_system.txt", p["data"]["questions"]):
            mlflow.log_artifact(str(Path(ROOT) / f))

    print(json.dumps(metrics, indent=2))
    return metrics


if __name__ == "__main__":
    main()
