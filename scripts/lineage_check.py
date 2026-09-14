"""Lab 2 — Check the 8 lineage fields on a registered model version.

    python scripts/lineage_check.py [--name <model_name>] [--version <version>]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import mlflow
from mlflow.tracking import MlflowClient
from src import config

REQUIRED_FIELDS = [
    "git_commit",
    "data_version",
    "mlflow_run_id",
    "training_job_id",
    "image_digest",
    "seed",
    "metric_val",
    "metric_test",
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", default=None, help="registered model name")
    ap.add_argument("--version", default="1", help="model version (default: 1)")
    args = ap.parse_args()

    cfg = config.load(strict=False)
    mlflow.set_tracking_uri(cfg.mlflow_tracking_uri)
    client = MlflowClient()

    name = args.name or cfg.model_registry_name
    try:
        mv = client.get_model_version(name, args.version)
    except Exception as e:
        print(f"Error fetching model '{name}' version '{args.version}': {e}")
        return 1

    print(f"Registered Model : {mv.name}")
    print(f"Version          : {mv.version}")
    print(f"Stage            : {mv.current_stage}")
    print(f"Aliases          : {mv.aliases}\n")
    print("Lineage Fields (8 required for Lab 2):")

    all_passed = True
    for field in REQUIRED_FIELDS:
        val = mv.tags.get(field)
        if val is not None:
            print(f"  [PASS] {field:<16} = {val}")
        else:
            print(f"  [FAIL] {field:<16} = MISSING")
            all_passed = False

    print()
    if all_passed:
        print(f"PASS: All 8 lineage fields are present on {mv.name} v{mv.version}!")
        return 0
    else:
        print("FAIL: Some required lineage fields are missing.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
