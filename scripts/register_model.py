"""Lab 2 — Register the chosen model from tracking with lineage tags and promote to Staging.

    python scripts/register_model.py [--run-id <run_id>] [--name <model_name>]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import mlflow
from cloudlayer.factory import get_adapter
from src import config


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", default=None, help="MLflow run ID to register (default: top run by val_roc_auc)")
    ap.add_argument("--experiment", default="itcs355-lab2", help="experiment name")
    ap.add_argument("--name", default=None, help="registered model name (default: cfg.model_registry_name)")
    args = ap.parse_args()

    cfg = config.load(strict=False)
    mlflow.set_tracking_uri(cfg.mlflow_tracking_uri)

    run_id = args.run_id
    if not run_id:
        exp = mlflow.get_experiment_by_name(args.experiment)
        if not exp:
            print(f"Error: Experiment '{args.experiment}' not found.")
            return 1
        runs = mlflow.search_runs(
            experiment_ids=[exp.experiment_id],
            order_by=["metrics.val_roc_auc DESC"],
            max_results=1,
        )
        if runs.empty:
            print(f"Error: No runs found in experiment '{args.experiment}'.")
            return 1
        run_id = runs.iloc[0]["run_id"]
        print(f"Selected top run {run_id} (val_roc_auc={runs.iloc[0]['metrics.val_roc_auc']:.4f})")

    model_name = args.name or cfg.model_registry_name
    model_uri = f"runs:/{run_id}/model"
    print(f"Registering model from {model_uri} as '{model_name}'...")

    adapter = get_adapter(cfg)
    version = adapter.register_model(model_uri, model_name)

    client = mlflow.tracking.MlflowClient()
    mv = client.get_model_version(model_name, version)
    print(f"\nModel registered successfully!")
    print(f"  Name:    {mv.name}")
    print(f"  Version: {mv.version}")
    print(f"  Stage:   {mv.current_stage}")
    print(f"  Aliases: {mv.aliases}")
    print("  Lineage tags:")
    for k, v in mv.tags.items():
        print(f"    - {k} = {v}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
