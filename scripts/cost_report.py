"""Lab 5 — cost report scaffold.

    python scripts/cost_report.py --estimate 120 --actual 187 --rps 42 --instance ml.m5.large

Produces reports/lab5-cost.md with all six required sections. It fills in what it can
compute and leaves the parts requiring your judgement clearly marked. The gap between
estimate and actual is the interesting part — explaining it scores, hiding it does not.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src import config, costs


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--estimate", type=float, required=True, help="THB, predicted in advance")
    ap.add_argument("--actual", type=float, required=True, help="THB, from billing, by tag")
    ap.add_argument("--rps", type=float, required=True, help="throughput from your Lab 3 load test")
    ap.add_argument("--instance", required=True)
    ap.add_argument("--spot", action="store_true")
    ap.add_argument("--out", type=Path, default=Path("reports/lab5-cost.md"))
    args = ap.parse_args()

    cfg = config.load(strict=False)
    rate = costs.hourly_rate(cfg.provider, args.instance, spot=args.spot)
    gap = args.actual - args.estimate
    gap_pct = (gap / args.estimate * 100) if args.estimate else float("nan")

    rows = [
        f"| {int(u * 100)}% | {costs.cost_per_1k_predictions(rate, args.rps, u):.4f} |"
        for u in costs.DEFAULT_UTILISATIONS
    ]
    breakeven = costs.batch_breakeven_rps(rate, batch_job_thb=rate * 0.5)

    content = f"""# Lab 5 — Cost report

Provider `{cfg.provider}` · instance `{args.instance}`{" (spot)" if args.spot else ""} · {rate:.2f} THB/hour

## 1. Estimate, made before running
{args.estimate:.2f} THB

## 2. Actual, from billing filtered by tag
{args.actual:.2f} THB

## 3. The gap
{gap:+.2f} THB ({gap_pct:+.1f}%)

TODO(Lab 5): explain it. There is always a gap. The usual causes: the meter ran while you
debugged a broken job; storage and egress were left out of the estimate; the endpoint
stayed warm overnight; the instance was larger than planned. Name yours.

## 4. Breakdown by component
| Component | THB | Notes |
|---|---|---|
| Training | | |
| Storage | | |
| Serving | | |
| Pipeline | | |
| Monitoring | | |

TODO(Lab 5): fill from billing, split by tag.

## 5. Cost per 1,000 predictions
Measured throughput: {args.rps:.1f} req/s

| Utilisation | THB per 1,000 |
|---|---|
{chr(10).join(rows)}

Utilisation is the most fragile number here, which is why three are reported rather than
one. State which you believe and why.

Below roughly **{breakeven:.4f} req/s**, scheduled batch inference is cheaper than keeping
this endpoint warm. TODO(Lab 5): check that against your actual request rate. The answer
is usually lower than students expect.

## 6. One optimisation you applied
| | Before | After |
|---|---|---|
| Configuration | | |
| THB per 1,000 | | |
| Latency p95 | | |

TODO(Lab 5): candidates — right-size the instance, move to a scale-to-zero service, batch
where latency allows, cache repeated inputs, use spot for training, shorten log retention.
Report the latency cost as well as the money saved. An optimisation that halves cost and
triples p99 is a trade, not a win.
"""
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(content)
    print(f"wrote {args.out}")
    print(f"gap {gap:+.2f} THB ({gap_pct:+.1f}%)")
    if abs(gap_pct) > 20:
        print("Gap exceeds 20% — the lab requires your figure to match billing within 20%. "
              "Either the estimate needs work or there is spend you have not accounted for.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
