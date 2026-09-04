"""Lab 5 — compile pipeline/pipeline.yaml into your provider's pipeline service.

This module is Layer 3, so provider SDKs are allowed here and nowhere else. The DAG stays
in YAML; only the translation lives here. That separation is what you argue for or against
in Lab 5 Task 4.

Implement ONE compile function, for your provider.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

SPEC = Path(__file__).resolve().parents[1] / "pipeline" / "pipeline.yaml"


def load_spec(path: Path = SPEC) -> dict[str, Any]:
    """Read the neutral DAG and expand ${VAR} references from the environment."""
    raw = path.read_text()
    for key, value in os.environ.items():
        raw = raw.replace(f"${{{key}}}", value)
    return yaml.safe_load(raw)


def compile_aws(spec: dict[str, Any]):
    """SageMaker Pipelines.

    Each step becomes a ProcessingStep or TrainingStep; `condition` becomes a
    ConditionStep. Note that SageMaker's condition steps branch rather than abort, so
    `on_failure: abort` needs a FailStep on the else branch — an asymmetry worth
    mentioning in your Lab 5 write-up.
    """
    raise NotImplementedError("TODO Lab 5: build a sagemaker.workflow.pipeline.Pipeline")


def compile_azure(spec: dict[str, Any]):
    """Azure ML Pipelines.

    Each step becomes a command component; the DAG is expressed as a @pipeline function.
    Conditions use azure.ai.ml.dsl.condition, which is closer to this YAML than the other
    two providers' equivalents.
    """
    raise NotImplementedError("TODO Lab 5: build an azure.ai.ml pipeline job")


def compile_gcp(spec: dict[str, Any]):
    """Vertex AI Pipelines.

    Kubeflow Pipelines underneath: steps become container components, conditions become
    dsl.If blocks. The compiled artifact is a JSON file you submit, so your build step
    produces a file rather than an object — different from the other two.
    """
    raise NotImplementedError("TODO Lab 5: compile a KFP pipeline and submit to Vertex")


COMPILERS = {"aws": compile_aws, "azure": compile_azure, "gcp": compile_gcp}


def compile_for(provider: str, spec: dict[str, Any] | None = None):
    spec = spec or load_spec()
    try:
        return COMPILERS[provider.lower()](spec)
    except KeyError:
        raise ValueError(f"No pipeline compiler for {provider!r}") from None
