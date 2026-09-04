"""Resolve the eight capability slots and report PASS/FAIL for each.

Run this before every lab. Post the output in the course channel before Session 1.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src import config

CLI_FOR = {"aws": "aws", "azure": "az", "gcp": "gcloud", "local": None}
IDENTITY_CMD = {
    "aws": ["aws", "sts", "get-caller-identity"],
    "azure": ["az", "account", "show"],
    "gcp": ["gcloud", "auth", "list"],
}


def line(name: str, ok: bool, detail: str = "") -> bool:
    print(f"  [{'PASS' if ok else 'FAIL'}] {name:<22} {detail}")
    return ok


def main() -> int:
    print("ITCS355 cloud check\n")
    results = []

    provider = os.environ.get("CLOUD_PROVIDER", "").lower()
    results.append(line("CLOUD_PROVIDER", provider in CLI_FOR,
                        provider or "unset — expected aws | azure | gcp | local"))

    for slot in config.CAPABILITY_SLOTS:
        if slot == "CLOUD_PROVIDER":
            continue
        value = os.environ.get(slot, "")
        shown = value if len(value) < 46 else value[:43] + "..."
        results.append(line(slot, bool(value), shown or "unset"))

    print()
    cli = CLI_FOR.get(provider)
    if cli:
        found = shutil.which(cli) is not None
        results.append(line(f"{cli} on PATH", found, "" if found else f"install the {provider} CLI"))
        if found:
            try:
                subprocess.run(IDENTITY_CMD[provider], capture_output=True, check=True, timeout=30)
                results.append(line("credentials", True, "identity resolved"))
            except Exception as exc:
                results.append(line("credentials", False, f"{type(exc).__name__} — run the login command"))
    else:
        line("cli", True, "local provider — no CLI needed (not valid for submission)")

    docker_ok = shutil.which("docker") is not None
    results.append(line("docker on PATH", docker_ok))

    passed = sum(results)
    print(f"\n{passed}/{len(results)} checks passed")
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
