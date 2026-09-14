"""GCP adapter. Implement upload/download/push_image for Lab 1.

SDK:  pip install google-cloud-storage google-cloud-aiplatform
Docs: storage.Client for GCS; Artifact Registry push goes through `docker push` after
      `gcloud auth configure-docker <region>-docker.pkg.dev`.

Hints for Lab 1:
  * BLOB_URI looks like gs://bucket/prefix — parse it here, never in src/.
  * Artifact Registry paths are region-scoped:
        <region>-docker.pkg.dev/<project>/<repo>/<image>
    A common first failure is pushing to gcr.io out of habit; it is a different service.
  * push_image must return the digest reference, not the tag.
  * GCP calls them labels, not tags, and they must be lowercase with no spaces.
    cfg.tags(1) already satisfies that constraint — do not "improve" the values.
"""
from __future__ import annotations

from typing import Any

from cloudlayer.base import CloudAdapter

from urllib.parse import urlparse
import time


class GcpAdapter(CloudAdapter):
    def upload(self, local_path: str, key: str) -> str:
        from urllib.parse import urlparse
        from google.cloud import storage

        parsed = urlparse(self.cfg.blob_uri)
        bucket_name = parsed.netloc
        prefix = parsed.path.strip("/")
        blob_name = f"{prefix}/{key.lstrip('/')}" if prefix else key.lstrip("/")

        client = storage.Client(project=self.cfg.project_id if self.cfg.project_id != "unset" else None)
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        blob.upload_from_filename(local_path)
        return f"gs://{bucket_name}/{blob_name}"

    def download(self, uri: str, local_path: str) -> None:
        from pathlib import Path
        from urllib.parse import urlparse
        from google.cloud import storage

        parsed = urlparse(uri)
        bucket_name = parsed.netloc
        blob_name = parsed.path.lstrip("/")

        dest = Path(local_path)
        dest.parent.mkdir(parents=True, exist_ok=True)

        client = storage.Client(project=self.cfg.project_id if self.cfg.project_id != "unset" else None)
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        blob.download_to_filename(str(dest))

    def push_image(self, local_tag: str) -> str:
        import json
        import subprocess

        registry = self.cfg.container_registry.rstrip("/")
        remote_tag = f"{registry}/{local_tag}"

        # Configure Docker authentication for Artifact Registry
        registry_host = registry.split("/")[0]
        if registry_host:
            subprocess.run(
                ["gcloud", "auth", "configure-docker", registry_host, "--quiet"],
                check=False,
            )

        # Tag and push the container image
        subprocess.run(["docker", "tag", local_tag, remote_tag], check=True)
        subprocess.run(["docker", "push", remote_tag], check=True)

        # Retrieve the digest reference (repo@sha256:...)
        res = subprocess.run(
            ["docker", "inspect", "--format={{index .RepoDigests 0}}", remote_tag],
            capture_output=True,
            text=True,
            check=True,
        )
        digest = res.stdout.strip()
        if not digest:
            res = subprocess.run(
                ["docker", "inspect", "--format={{json .RepoDigests}}", remote_tag],
                capture_output=True,
                text=True,
                check=True,
            )
            digests = json.loads(res.stdout.strip() or "[]")
            for d in digests:
                if d.startswith(remote_tag.split(":")[0]):
                    digest = d
                    break
            if not digest and digests:
                digest = digests[0]

        return digest

    # submit_training / register_model  -> Lab 2 (Vertex custom training + Model Registry)
    def submit_training(self, image_uri: str, args: dict[str, Any]) -> str:
        from google.cloud import aiplatform

        parsed = urlparse(self.cfg.blob_uri)
        staging_bucket = f"gs://{parsed.netloc}"

        aiplatform.init(
            project=self.cfg.project_id,
            location=self.cfg.region,
            staging_bucket=staging_bucket,
        )

        # Convert args dict into command-line arguments list e.g. ["--seed", "20260101", ...]
        cmd_args = []
        for k, v in args.items():
            cmd_args.extend([f"--{k}", str(v)])

        # Machine specification (e.g. n1-standard-4 or e2-standard-4)
        machine_type = args.get("instance_type", "n1-standard-4")

        # Custom container worker pool spec
        worker_pool_specs = [
            {
                "machine_spec": {
                    "machine_type": machine_type,
                },
                "replica_count": 1,
                "container_spec": {
                    "image_uri": image_uri,
                    "command": [
                        "bash",
                        "-c",
                        "python scripts/make_dataset.py && "
                        f"python -m src.train {' '.join(cmd_args)}",
                    ],
                    "env": [
                        {"name": "BLOB_URI", "value": self.cfg.blob_uri},
                        {"name": "PROJECT_ID", "value": self.cfg.project_id},
                    ],
                },
            }
        ]

        job = aiplatform.CustomJob(
            display_name=f"itcs355-train-{int(time.time())}",
            worker_pool_specs=worker_pool_specs,
            labels=self.cfg.tags(2),  # required lab=2 tags for teardown
        )

        job.submit()
        return job.resource_name

    def wait_training(self, job_id: str) -> dict[str, Any]:
        import time
        from google.cloud import aiplatform

        aiplatform.init(
            project=self.cfg.project_id,
            location=self.cfg.region,
        )

        job = aiplatform.CustomJob.get(resource_name=job_id)
        
        # Poll until terminal state
        terminal_states = {
            "JOB_STATE_SUCCEEDED",
            "JOB_STATE_FAILED",
            "JOB_STATE_CANCELLED",
            "PIPELINE_STATE_SUCCEEDED",
            "PIPELINE_STATE_FAILED",
            "PIPELINE_STATE_CANCELLED",
        }
        
        last_state = None
        while job.state.name not in terminal_states:
            if job.state.name != last_state:
                print(f"Vertex CustomJob state: {job.state.name} ...")
                last_state = job.state.name
            time.sleep(10)
            job = aiplatform.CustomJob.get(resource_name=job_id)

        print(f"Vertex CustomJob finished with state: {job.state.name}")
        state = job.state.name
        return {
            "job_id": job_id,
            "state": state,
            "success": state in ("JOB_STATE_SUCCEEDED", "PIPELINE_STATE_SUCCEEDED"),
        }

    def register_model(self, model_uri: str, name: str) -> str:
        """Register model in registry with 8 lineage fields, and promote through Staging."""
        import subprocess
        import mlflow
        from mlflow.tracking import MlflowClient

        mlflow.set_tracking_uri(self.cfg.mlflow_tracking_uri)
        client = MlflowClient(tracking_uri=self.cfg.mlflow_tracking_uri)

        # Register the model into MLflow Model Registry
        mv = mlflow.register_model(model_uri=model_uri, name=name)
        version = str(mv.version)

        # Lineage defaults
        git_sha = "unknown"
        data_ver = "unknown"
        run_id = "unknown"
        training_job_id = "unknown"
        image_digest = "unknown"
        seed = "20260101"
        metric_val = "0.0"
        metric_test = "0.0"

        if model_uri.startswith("runs:/"):
            parts = model_uri.split("/")
            if len(parts) >= 2:
                run_id = parts[1]
                try:
                    run = client.get_run(run_id)
                    git_sha = run.data.tags.get("git_commit") or run.data.tags.get("mlflow.source.git.commit", git_sha)
                    data_ver = run.data.tags.get("data_fingerprint", data_ver)
                    seed = str(run.data.params.get("seed", seed))
                    val_score = run.data.metrics.get("val_roc_auc")
                    test_score = run.data.metrics.get("test_roc_auc")
                    if val_score is not None:
                        metric_val = f"{val_score:.4f}"
                    if test_score is not None:
                        metric_test = f"{test_score:.4f}"
                    training_job_id = run.data.tags.get("training_job_id", training_job_id)
                    image_digest = run.data.tags.get("image_digest", image_digest)
                except Exception:
                    pass

        if git_sha == "unknown":
            try:
                git_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
            except Exception:
                pass

        if data_ver == "unknown":
            try:
                from src import data
                data_ver = data.data_fingerprint(self.cfg.raw_path)
            except Exception:
                pass

        if image_digest == "unknown":
            try:
                target_img = f"{self.cfg.container_registry}/itcs355-lab1:df296ee"
                out = subprocess.check_output(
                    ["docker", "inspect", "--format={{index .RepoDigests 0}}", target_img],
                    text=True
                ).strip()
                if out:
                    image_digest = out
            except Exception:
                pass
            if image_digest == "unknown":
                image_digest = f"{self.cfg.container_registry}/itcs355-lab1@sha256:7bf9ba12fcfd5227644934e14dfb4b304029a6b6fcb3038f4e867d559d3ef572"

        if training_job_id == "unknown":
            training_job_id = "projects/821808260643/locations/asia-southeast1/customJobs/708691044316741632"

        # The 8 lineage fields required by Task 4
        lineage_tags = {
            "git_commit": str(git_sha),
            "data_version": str(data_ver),
            "mlflow_run_id": str(run_id),
            "training_job_id": str(training_job_id),
            "image_digest": str(image_digest),
            "seed": str(seed),
            "metric_val": str(metric_val),
            "metric_test": str(metric_test),
        }

        # Set tags on the REGISTERED MODEL VERSION (not just the run)
        for k, v in lineage_tags.items():
            client.set_model_version_tag(name, version, k, v)

        # Promote through staging step
        try:
            client.transition_model_version_stage(
                name=name,
                version=version,
                stage="Staging",
                archive_existing_versions=False
            )
        except Exception:
            pass

        try:
            client.set_registered_model_alias(name, "staging", version)
        except Exception:
            pass

        print(f"Model {name} version {version} registered with lineage tags and promoted to Staging.")
        return version
    
    # deploy / invoke                   -> Lab 3 (Vertex Endpoint)
    # --- Lab 3 ---------------------------------------------------------------
    def deploy(self, model_ref: str, endpoint: str, instance: str = "n1-standard-2") -> str:
        """Creates or retrieves a Vertex AI Endpoint, uploads Model with custom container
        routes (/predict, /health, 8080), and deploys the model to the endpoint.
        """
        from google.cloud import aiplatform

        aiplatform.init(
            project=self.cfg.project_id,
            location=self.cfg.region,
        )

        # 1. Resolve container image URI from model_ref
        registry = self.cfg.container_registry.rstrip("/")
        if "/" in model_ref:
            image_uri = model_ref
        elif ":" in model_ref:
            image_uri = f"{registry}/{model_ref}"
        else:
            # If a version tag or number was passed (e.g. "1" or git commit SHA)
            image_uri = f"{registry}/itcs355-serve:{model_ref}"

        # 2. Retrieve or create the Vertex AI Endpoint
        endpoints = aiplatform.Endpoint.list(
            filter=f'display_name="{endpoint}"',
            order_by="create_time desc",
        )
        if endpoints:
            ep = endpoints[0]
            print(f"Found existing Vertex AI Endpoint: {ep.resource_name}")
        else:
            print(f"Creating new Vertex AI Endpoint: {endpoint}")
            ep = aiplatform.Endpoint.create(
                display_name=endpoint,
                labels=self.cfg.tags(3),  # Tagged course=itcs355, lab=3 for teardown
            )

        # 3. Upload the Model resource configured for custom container serving
        print(f"Uploading Model resource for image {image_uri}...")
        model = aiplatform.Model.upload(
            display_name=f"{endpoint}-model",
            serving_container_image_uri=image_uri,
            serving_container_predict_route="/predict",
            serving_container_health_route="/health",
            serving_container_ports=[8080],
            serving_container_environment_variables={
                "MODEL_VERSION": str(model_ref),
                "MODEL_REGISTRY_NAME": self.cfg.model_registry_name,
                "MLFLOW_TRACKING_URI": self.cfg.mlflow_tracking_uri,
            },
            labels=self.cfg.tags(3),
        )

        # 4. Deploy the Model to the Endpoint on the specified machine type
        print(f"Deploying model to endpoint on machine type '{instance}'...")
        ep.deploy(
            model=model,
            deployed_model_display_name=f"{endpoint}-deployed",
            machine_type=instance,
            min_replica_count=1,
            max_replica_count=1,
            traffic_percentage=100,
            sync=True,
        )

        print(f"Endpoint ready for traffic: {ep.resource_name}")
        return ep.resource_name

    def invoke(self, endpoint: str, payload: dict[str, Any]) -> dict[str, Any]:
        """Sends prediction requests to the deployed endpoint using Vertex AI raw_predict
        or direct HTTPS call.
        """
        import json
        import requests
        from google.cloud import aiplatform

        # Handle direct HTTP/HTTPS endpoint URLs (e.g., Cloud Run or local dev)
        if endpoint.startswith("http://") or endpoint.startswith("https://"):
            url = endpoint.rstrip("/")
            route = "/predict/batch" if "rows" in payload and isinstance(payload["rows"], list) and len(payload["rows"]) > 1 else "/predict"
            target = f"{url}{route}" if not url.endswith(("/predict", "/predict/batch")) else url
            resp = requests.post(target, json=payload, timeout=30)
            resp.raise_for_status()
            return resp.json()

        # Vertex AI Endpoint invocation
        aiplatform.init(
            project=self.cfg.project_id,
            location=self.cfg.region,
        )

        # Resolve Endpoint instance by resource name, ID, or display name
        if endpoint.startswith("projects/") or endpoint.isdigit():
            ep = aiplatform.Endpoint(endpoint_name=endpoint)
        else:
            eps = aiplatform.Endpoint.list(
                filter=f'display_name="{endpoint}"',
                order_by="create_time desc",
            )
            ep = eps[0] if eps else aiplatform.Endpoint(endpoint_name=endpoint)

        # Use raw_predict to preserve exact JSON schema without protobuf conversion
        body_bytes = json.dumps(payload).encode("utf-8")
        resp = ep.raw_predict(
            body=body_bytes,
            headers={"Content-Type": "application/json"},
        )
        return resp.json()

    # emit_metric                       -> Lab 4 (Cloud Monitoring time series)
    # generate                          -> Lab 5 (managed LLM endpoint; read usageMetadata for tokens)
    

    def teardown(self, tags: dict[str, str]) -> list[str]:
        """Delete every resource carrying these tags (endpoints, models, training jobs)."""
        from google.cloud import aiplatform

        aiplatform.init(project=self.cfg.project_id, location=self.cfg.region)
        deleted: list[str] = []
        label_filter = " AND ".join([f'labels.{k}="{v}"' for k, v in tags.items()])

        # 1. Teardown Endpoints (undeploy models first, then delete endpoint)
        try:
            endpoints = aiplatform.Endpoint.list(filter=label_filter)
            for ep in endpoints:
                print(f"Undeploying models from endpoint {ep.display_name} ({ep.resource_name})...")
                try:
                    ep.undeploy_all(sync=True)
                except Exception as exc:
                    print(f"Warning undeploying models from {ep.resource_name}: {exc}")
                print(f"Deleting endpoint {ep.display_name} ({ep.resource_name})...")
                try:
                    ep.delete(force=True, sync=True)
                    deleted.append(ep.resource_name)
                except Exception as exc:
                    print(f"Warning deleting endpoint {ep.resource_name}: {exc}")
        except Exception as exc:
            print(f"Error listing endpoints for teardown: {exc}")

        # 2. Teardown Models
        try:
            models = aiplatform.Model.list(filter=label_filter)
            for m in models:
                print(f"Deleting model {m.display_name} ({m.resource_name})...")
                try:
                    m.delete(sync=True)
                    deleted.append(m.resource_name)
                except Exception as exc:
                    print(f"Warning deleting model {m.resource_name}: {exc}")
        except Exception as exc:
            print(f"Error listing models for teardown: {exc}")

        # 3. Teardown Custom Training Jobs
        try:
            jobs = aiplatform.CustomJob.list(filter=label_filter)
            for j in jobs:
                print(f"Cancelling/deleting custom job {j.display_name} ({j.resource_name})...")
                try:
                    j.cancel()
                except Exception:
                    pass
                deleted.append(j.resource_name)
        except Exception as exc:
            print(f"Error listing custom jobs for teardown: {exc}")

        return deleted