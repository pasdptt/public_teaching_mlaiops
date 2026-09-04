"""The portability seam.

Ten methods. Every managed ML platform sells you the same ten operations under
different names; writing this once is the difference between knowing a product and
knowing the category.

You implement exactly ONE of aws.py, azure.py, or gcp.py. Lab 1 needs only `upload`,
`download`, and `push_image`. The rest raise NotImplementedError until the lab that
needs them, which is deliberate — do not implement ahead.

Nothing outside cloudlayer/ may import a provider SDK.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class CloudAdapter(ABC):
    """Provider-neutral interface. The grader only ever calls these."""

    def __init__(self, cfg) -> None:
        self.cfg = cfg

    # --- Lab 1 ---------------------------------------------------------------
    @abstractmethod
    def upload(self, local_path: str, key: str) -> str:
        """Upload a file under BLOB_URI. Returns the full URI of the stored object."""

    @abstractmethod
    def download(self, uri: str, local_path: str) -> None:
        """Fetch an object to a local path. Creates parent directories."""

    @abstractmethod
    def push_image(self, local_tag: str) -> str:
        """Push a locally built image to CONTAINER_REGISTRY. Returns the remote reference,
        which must be digest-pinned (repo@sha256:...), not tag-pinned."""

    # --- Lab 2 ---------------------------------------------------------------
    def submit_training(self, image_uri: str, args: dict[str, Any]) -> str:
        raise NotImplementedError("Lab 2")

    def wait_training(self, job_id: str) -> dict[str, Any]:
        raise NotImplementedError("Lab 2")

    def register_model(self, model_uri: str, name: str) -> str:
        raise NotImplementedError("Lab 2")

    # --- Lab 3 ---------------------------------------------------------------
    def deploy(self, model_ref: str, endpoint: str, instance: str) -> str:
        raise NotImplementedError("Lab 3")

    def invoke(self, endpoint: str, payload: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError("Lab 3")

    # --- Lab 4 ---------------------------------------------------------------
    def emit_metric(self, name: str, value: float, unit: str = "None") -> None:
        raise NotImplementedError("Lab 4")

    # --- Lab 5 ---------------------------------------------------------------
    def teardown(self, tags: dict[str, str]) -> list[str]:
        """Delete every resource carrying these tags. Returns what was deleted.

        Deletion is asynchronous on all three providers — returning successfully does
        not mean the resource is gone. Re-check, and check the bill.
        """
        raise NotImplementedError("Lab 5")


class LocalAdapter(CloudAdapter):
    """Filesystem stand-in so Lab 1 runs before your cloud account is ready.

    Acceptable for developing Lab 1. NOT acceptable for submission — your submitted
    Lab 1 must upload to real object storage and push to a real registry.
    """

    def upload(self, local_path: str, key: str) -> str:
        import shutil
        from pathlib import Path

        dest = Path(self.cfg.data_dir) / "_local_blob" / key
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(local_path, dest)
        return f"local://{dest}"

    def download(self, uri: str, local_path: str) -> None:
        import shutil
        from pathlib import Path

        src = uri.removeprefix("local://")
        Path(local_path).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, local_path)

    def push_image(self, local_tag: str) -> str:
        raise NotImplementedError(
            "LocalAdapter cannot push images. Implement your provider's adapter for Lab 1 submission."
        )
