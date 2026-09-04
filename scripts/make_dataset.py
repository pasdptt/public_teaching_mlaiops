"""Generate the default dataset for Lab 1.

Deterministic: the same seed always produces a byte-identical file, so the data
fingerprint is stable across machines. Swap this out if you bring your own problem —
the rest of the repo does not care where data/raw/sensors.csv came from.

Machines have persistent characteristics, which is exactly why the split must be
grouped by machine_id. See src/data.split.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

N_MACHINES = 240
READINGS_PER_MACHINE = 25


def build(seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows = []
    reading_id = 0
    for machine in range(N_MACHINES):
        # Persistent per-machine traits. A row-wise split would let a model memorise these.
        base_temp = rng.normal(72, 9)
        wear = rng.gamma(2.0, 1.4)
        duty = rng.uniform(0.3, 1.0)
        for _ in range(READINGS_PER_MACHINE):
            hours = float(rng.uniform(0, 9000))
            temp = base_temp + 0.0016 * hours + rng.normal(0, 2.2)
            vib = 1.4 + 0.55 * wear + 0.00035 * hours + rng.normal(0, 0.45)
            pressure = 320 - 0.7 * wear + rng.normal(0, 14)
            load = float(np.clip(100 * duty + rng.normal(0, 6), 0, 100))
            humidity = float(np.clip(rng.normal(58, 12), 0, 100))

            logit = (
                -6.1
                + 0.052 * (temp - 72)
                + 0.71 * (vib - 2.2)
                + 0.00021 * hours
                + 0.019 * (load - 60)
                - 0.004 * (pressure - 320)
            )
            p = 1.0 / (1.0 + np.exp(-logit))
            rows.append({
                "reading_id": reading_id,
                "machine_id": machine,
                "temp_c": round(float(temp), 3),
                "vibration_mm_s": round(float(vib), 3),
                "pressure_kpa": round(float(pressure), 3),
                "hours_since_service": round(hours, 3),
                "load_pct": round(load, 3),
                "ambient_humidity": round(humidity, 3),
                "failed_within_7d": int(rng.random() < p),
            })
            reading_id += 1
    return pd.DataFrame(rows)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=20260101)
    ap.add_argument("--out", type=Path, default=Path("data/raw/sensors.csv"))
    args = ap.parse_args()

    df = build(args.seed)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.out, index=False, lineterminator="\n")
    rate = df["failed_within_7d"].mean()
    print(f"wrote {args.out}  rows={len(df)}  machines={df.machine_id.nunique()}  positive_rate={rate:.3f}")


if __name__ == "__main__":
    main()
