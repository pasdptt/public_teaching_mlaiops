"""Lab 2 — budgeted hyperparameter study.

Run:  python -m src.tune --trials 12 --budget-thb 150

The budget is enforced, not advisory. The study stops when projected spend would exceed
it, and reports what it did not get to. This is the habit the lab is teaching: compute is
a resource you spend deliberately, and a trial that is 0.3% better and four times the cost
is not better.

Every trial logs its estimated cost alongside its metric, so `scripts/compare_runs.py` can
rank by cost per point rather than by metric alone.
"""
from __future__ import annotations

import argparse
import itertools
import json
import time
from pathlib import Path

import mlflow
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import average_precision_score, roc_auc_score

from src import config, costs, data, seeds
from src.train import git_commit

# TODO(Lab 2): widen this. Three hyperparameters minimum, and vary something that
# actually changes model behaviour rather than three variants of the same idea.
SEARCH_SPACE: dict[str, list] = {
    "n_estimators": [100, 300],
    "max_depth": [4, 8, 12],
    "min_samples_leaf": [1, 5],
}


def grid(space: dict[str, list]) -> list[dict]:
    keys = list(space)
    return [dict(zip(keys, values)) for values in itertools.product(*(space[k] for k in keys))]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="ITCS355 Lab 2 — budgeted study")
    p.add_argument("--trials", type=int, default=12, help="minimum 12 for the lab")
    p.add_argument("--budget-thb", type=float, default=150.0)
    p.add_argument("--instance", default="local", help="key into src/costs.py PRICE_TABLE")
    p.add_argument("--seed", type=int, default=seeds.DEFAULT_SEED)
    p.add_argument("--experiment", default="itcs355-lab2")
    p.add_argument("--checkpoint", type=Path, default=Path("reports/tune_checkpoint.json"),
                   help="Resume file. Spot interruption should cost minutes, not the run.")
    return p.parse_args()


def load_checkpoint(path: Path) -> dict:
    if path.exists():
        return json.loads(path.read_text())
    return {"completed": [], "spent_thb": 0.0}


def save_checkpoint(path: Path, state: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2))


def main() -> None:
    args = parse_args()
    cfg = config.load(strict=False)
    seed = seeds.set_all(args.seed)

    df = data.load_raw(cfg.raw_path)
    fingerprint = data.data_fingerprint(cfg.raw_path)
    train_df, val_df, test_df = data.split(df, seed=seed)

    mlflow.set_tracking_uri(cfg.mlflow_tracking_uri)
    mlflow.set_experiment(args.experiment)

    state = load_checkpoint(args.checkpoint)
    candidates = grid(SEARCH_SPACE)[: args.trials]
    rate = costs.hourly_rate(cfg.provider, args.instance)

    skipped: list[dict] = []
    for i, params in enumerate(candidates):
        key = json.dumps(params, sort_keys=True)
        if key in state["completed"]:
            print(f"trial {i}: already done, skipping (resumed from checkpoint)")
            continue

        if state["spent_thb"] >= args.budget_thb:
            skipped.append(params)
            continue

        started = time.perf_counter()
        with mlflow.start_run(run_name=f"trial-{i:02d}"):
            model = RandomForestClassifier(random_state=seed, n_jobs=-1, **params)
            model.fit(train_df[data.FEATURES], train_df[data.TARGET])

            metrics = {}
            for name, part in (("val", val_df), ("test", test_df)):
                proba = model.predict_proba(part[data.FEATURES])[:, 1]
                metrics[f"{name}_roc_auc"] = float(roc_auc_score(part[data.TARGET], proba))
                metrics[f"{name}_pr_auc"] = float(average_precision_score(part[data.TARGET], proba))

            elapsed_h = (time.perf_counter() - started) / 3600.0
            trial_cost = elapsed_h * rate
            state["spent_thb"] += trial_cost

            mlflow.log_params({**params, "seed": seed, "instance": args.instance})
            mlflow.log_metrics({
                **metrics,
                "duration_s": round(elapsed_h * 3600, 3),
                "cost_thb": round(trial_cost, 4),
            })
            mlflow.set_tags({
                "git_commit": git_commit(),
                "data_fingerprint": fingerprint,
                "lab": "2",
            })
            mlflow.sklearn.log_model(model, name="model")

        state["completed"].append(key)
        save_checkpoint(args.checkpoint, state)
        print(f"trial {i}: {params} -> val_roc_auc={metrics['val_roc_auc']:.4f} "
              f"cost={trial_cost:.4f} THB  cumulative={state['spent_thb']:.4f}")

    print(f"\nspent {state['spent_thb']:.4f} of {args.budget_thb} THB")
    if skipped:
        print(f"BUDGET EXHAUSTED — {len(skipped)} configurations not run:")
        for s in skipped:
            print(f"  {s}")
        print("Report this in your README. Which trials you could not afford is a finding, "
              "not an embarrassment.")


if __name__ == "__main__":
    main()
