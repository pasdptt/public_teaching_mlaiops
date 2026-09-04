"""Configuration. The ONLY module in src/ allowed to know about the environment.

Course rule: nothing under src/ may contain a bucket name, a provider hostname, or an
absolute path from your machine. Everything arrives through here, which reads cloud.env.
`make portability-audit` enforces this, and Lab 5 grades it.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = REPO_ROOT / "cloud.env"

# The eight capability slots every lab depends on. scripts/cloud_check.py resolves each.
CAPABILITY_SLOTS = (
    "CLOUD_PROVIDER",
    "PROJECT_ID",
    "REGION",
    "BLOB_URI",
    "CONTAINER_REGISTRY",
    "MLFLOW_TRACKING_URI",
    "MODEL_REGISTRY_NAME",
    "IDENTITY_REF",
)


def _load_env_file(path: Path = ENV_FILE) -> None:
    """Minimal .env loader. An already-exported variable wins, so CI can override cloud.env."""
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip())


_load_env_file()


@dataclass(frozen=True)
class Config:
    provider: str
    project_id: str
    region: str
    blob_uri: str
    container_registry: str
    mlflow_tracking_uri: str
    model_registry_name: str
    identity_ref: str
    data_dir: Path = field(default=REPO_ROOT / "data")
    reports_dir: Path = field(default=REPO_ROOT / "reports")

    @property
    def raw_path(self) -> Path:
        return self.data_dir / "raw" / "sensors.csv"

    def tags(self, lab: int) -> dict[str, str]:
        """Every cloud resource carries these. `make teardown` finds resources by tag."""
        return {"course": "itcs355", "student": self.project_id, "lab": str(lab)}


def load(strict: bool = True) -> Config:
    missing = [s for s in CAPABILITY_SLOTS if not os.environ.get(s)]
    if missing and strict:
        raise RuntimeError(
            "Missing capability slots: " + ", ".join(missing)
            + "\nCopy cloud.env.example to cloud.env, fill it in, then run `make cloud-check`."
        )
    get = os.environ.get
    return Config(
        provider=get("CLOUD_PROVIDER", "local"),
        project_id=get("PROJECT_ID", "unset"),
        region=get("REGION", "unset"),
        blob_uri=get("BLOB_URI", ""),
        container_registry=get("CONTAINER_REGISTRY", ""),
        mlflow_tracking_uri=get("MLFLOW_TRACKING_URI", "sqlite:///mlflow.db"),
        model_registry_name=get("MODEL_REGISTRY_NAME", "itcs355"),
        identity_ref=get("IDENTITY_REF", ""),
    )
