"""AWS adapter. Implement upload/download/push_image for Lab 1.

SDK:  pip install boto3
Docs: S3 -> boto3 client("s3"); ECR -> boto3 client("ecr") for the auth token,
      then `docker push` through subprocess.

Hints for Lab 1:
  * BLOB_URI looks like s3://bucket/prefix — parse it here, never in src/.
  * ECR login expires. If a push that worked yesterday fails today, re-authenticate:
        aws ecr get-login-password --region $REGION | docker login --username AWS \
            --password-stdin <account>.dkr.ecr.<region>.amazonaws.com
  * Return the DIGEST reference from push_image, not the tag. `docker inspect` or the
    push output gives you the sha256.
  * Tag the bucket objects and the ECR repository with cfg.tags(1).
"""
from __future__ import annotations

from typing import Any

from cloudlayer.base import CloudAdapter


class AwsAdapter(CloudAdapter):
    def upload(self, local_path: str, key: str) -> str:
        raise NotImplementedError("TODO Lab 1: put_object into BLOB_URI, return the s3:// URI")

    def download(self, uri: str, local_path: str) -> None:
        raise NotImplementedError("TODO Lab 1: download_file, creating parent directories")

    def push_image(self, local_tag: str) -> str:
        raise NotImplementedError("TODO Lab 1: authenticate to ECR, push, return repo@sha256:...")

    # submit_training / register_model  -> Lab 2 (SageMaker training job + model package group)
    # deploy / invoke                   -> Lab 3 (SageMaker real-time endpoint)
    # emit_metric                       -> Lab 4 (CloudWatch put_metric_data)
    # generate                          -> Lab 5 (managed LLM endpoint; read the usage block for tokens)
    # teardown                          -> Lab 5 (resourcegroupstaggingapi to find by tag)
