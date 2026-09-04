"""Adapter selection. The only place that maps CLOUD_PROVIDER to an implementation."""
from __future__ import annotations

from cloudlayer.base import CloudAdapter, LocalAdapter


def get_adapter(cfg) -> CloudAdapter:
    provider = (cfg.provider or "local").lower()
    if provider == "local":
        return LocalAdapter(cfg)
    if provider == "aws":
        from cloudlayer.aws import AwsAdapter
        return AwsAdapter(cfg)
    if provider == "azure":
        from cloudlayer.azure import AzureAdapter
        return AzureAdapter(cfg)
    if provider == "gcp":
        from cloudlayer.gcp import GcpAdapter
        return GcpAdapter(cfg)
    raise ValueError(f"Unknown CLOUD_PROVIDER={provider!r}. Use aws, azure, gcp, or local.")
