"""Compare the metric just produced against the claim in README.md.

This is what `make verify` runs, and it is a close cousin of what the grader runs.
Run it yourself before submitting: if it fails for you, it will fail for them.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
METRICS = ROOT / "reports" / "metrics.json"
README = ROOT / "README.md"

CLAIM = re.compile(
    r"expected\s+test_roc_auc\s*[:=]\s*(?P<value>[0-9.]+)\s*(?:±|\+/-)\s*(?P<tol>[0-9.]+)",
    re.IGNORECASE,
)


def main() -> int:
    if not METRICS.exists():
        print("FAIL  reports/metrics.json missing — run `make reproduce` first")
        return 1
    match = CLAIM.search(README.read_text())
    if not match:
        print("FAIL  README.md has no claim line.\n"
              "      Add one, exactly in this form:\n"
              "        expected test_roc_auc: 0.848 ± 0.010")
        return 1

    claimed = float(match.group("value"))
    tol = float(match.group("tol"))
    actual = json.loads(METRICS.read_text())["test_roc_auc"]
    delta = abs(actual - claimed)

    print(f"claimed  {claimed:.4f} ± {tol:.4f}")
    print(f"actual   {actual:.4f}")
    print(f"delta    {delta:.4f}")

    if delta <= tol:
        print("\nPASS  reproduced within tolerance")
        return 0
    print("\nFAIL  outside tolerance.\n"
          "      Either your run is not deterministic, or the claim is stale.\n"
          "      Widening the tolerance to hide non-determinism is visible to the grader.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
