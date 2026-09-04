"""Check that every relative Markdown link resolves.

    python scripts/site/check_links.py

A broken link on a course website is a student emailing you instead of reading. CI runs
this on every push. External http(s) links are not checked — that needs the network and
produces flaky failures.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[2]
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".pytest_cache", "mlruns", "mlartifacts"}
LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


def markdown_files() -> list[Path]:
    return [p for p in ROOT.rglob("*.md")
            if not any(part in SKIP_DIRS for part in p.parts)]


def main() -> int:
    broken: list[str] = []
    checked = 0

    for path in markdown_files():
        in_fence = False
        for lineno, line in enumerate(path.read_text().splitlines(), 1):
            if line.lstrip().startswith("```"):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            for target in LINK.findall(line):
                target = target.strip()
                if target.startswith(("http://", "https://", "mailto:", "#")):
                    continue
                checked += 1
                # Strip any anchor; we verify the file exists, not the heading.
                file_part = unquote(target.split("#", 1)[0])
                if not file_part:
                    continue
                resolved = (path.parent / file_part).resolve()
                if not resolved.exists():
                    rel = path.relative_to(ROOT)
                    broken.append(f"{rel}:{lineno}  ->  {target}")

    for b in broken:
        print(f"  BROKEN  {b}")
    print(f"\n{checked} relative links checked, {len(broken)} broken")
    return 1 if broken else 0


if __name__ == "__main__":
    sys.exit(main())
