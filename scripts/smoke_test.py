"""Lab 3 — smoke test the deployed or local serving endpoint with three known payloads.

    python scripts/smoke_test.py --endpoint itcs355-serve
    python scripts/smoke_test.py --target http://localhost:8080
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cloudlayer.factory import get_adapter
from src import config

PAYLOADS = [
    {
        "name": "Normal operation",
        "payload": {
            "temp_c": 78.4,
            "vibration_mm_s": 3.1,
            "pressure_kpa": 315.2,
            "hours_since_service": 4200.0,
            "load_pct": 68.0,
            "ambient_humidity": 55.0,
        },
    },
    {
        "name": "Elevated warning",
        "payload": {
            "temp_c": 95.0,
            "vibration_mm_s": 12.0,
            "pressure_kpa": 380.0,
            "hours_since_service": 8500.0,
            "load_pct": 88.0,
            "ambient_humidity": 65.0,
        },
    },
    {
        "name": "High risk",
        "payload": {
            "temp_c": 115.0,
            "vibration_mm_s": 25.0,
            "pressure_kpa": 450.0,
            "hours_since_service": 15000.0,
            "load_pct": 98.0,
            "ambient_humidity": 80.0,
        },
    },
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--endpoint", default="itcs355-serve", help="Endpoint name or resource")
    ap.add_argument("--target", default=None, help="HTTP URL (e.g. http://localhost:8080) overriding endpoint")
    args = ap.parse_args()

    cfg = config.load(strict=False)
    adapter = get_adapter(cfg)
    target = args.target or args.endpoint

    print(f"Running smoke test against: {target}\n")

    for i, item in enumerate(PAYLOADS, 1):
        print(f"[{i}/3] Testing payload: {item['name']}")
        try:
            res = adapter.invoke(target, item["payload"])
            print(f"     Result: {res}")
        except Exception as exc:
            print(f"     Failed: {exc}")
            return 1

    print("\nPASS  all 3 smoke payloads scored successfully")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
