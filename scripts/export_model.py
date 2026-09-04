"""Export a trained model to a local file, for the CI integration test.

Real deployments load a registered version from the registry. This exists only so CI can
start the service without a registry, and it is not acceptable in a submitted Lab 3.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import joblib
from sklearn.ensemble import RandomForestClassifier

from src import config, data, seeds


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=Path("reports/model.joblib"))
    ap.add_argument("--seed", type=int, default=seeds.DEFAULT_SEED)
    args = ap.parse_args()

    cfg = config.load(strict=False)
    seed = seeds.set_all(args.seed)
    df = data.load_raw(cfg.raw_path)
    train_df, _, _ = data.split(df, seed=seed)

    model = RandomForestClassifier(n_estimators=200, max_depth=8, min_samples_leaf=5,
                                   random_state=seed, n_jobs=-1)
    model.fit(train_df[data.FEATURES], train_df[data.TARGET])
    args.out.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, args.out)
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
