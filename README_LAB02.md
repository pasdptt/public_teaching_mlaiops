# ITCS355 Lab 2 — Experiment Tracking and Model Registry

> **Student ID:** 6688249  
> **Cloud Provider:** Google Cloud Platform (GCP) · Vertex AI · Artifact Registry · Cloud Storage  
> **Course:** ITCS355 Machine Learning Operation and Deployment

---

## 1. Quick Verification Commands

```bash
# Task 1: Managed Cloud Training on Vertex AI
make train-remote

# Task 2: Run budgeted hyperparameter study (>=12 trials on spot compute)
make tune

# Task 3: Rank trials and output comparison report
make compare

# Task 4: Register top model with 8 lineage fields and promote to Staging
make register

# Task 5: Reload model from registry and score held-out rows
make reload-check VERSION=1

# Teardown any running compute/jobs
make teardown
```

---

## 2. Task 1 — Managed Compute (Vertex AI CustomJob)

- **Adapter Implementation**: `cloudlayer/gcp.py` implements `submit_training()` and `wait_training()` using `google.cloud.aiplatform.CustomJob`.
- **First Submission Permission Failure**:
  - **Error Encountered**: `400 Vertex AI Service Agent ... does not have permission to access Artifact Registry repository`.
  - **Root Cause**: The submit-time identity (user account via `gcloud`) has job submission permissions, but the runtime service agent (`service-821808260643@gcp-sa-aiplatform-cc.iam.gserviceaccount.com`) did not have permission to pull the container image from Google Artifact Registry.
  - **Fix**: Granted `roles/artifactregistry.reader` to `service-821808260643@gcp-sa-aiplatform-cc.iam.gserviceaccount.com` on the repository `itcs355`.

---

## 3. Task 2 — Budgeted Study (>=12 Trials)

- **Search Space**: Varied 3 hyperparameters:
  - `n_estimators`: `[100, 300]`
  - `max_depth`: `[4, 8, 12]`
  - `min_samples_leaf`: `[1, 5]`
- **Discount Compute**: GCP `e2-standard-4` spot instances with 0.3 spot discount factor (hourly rate: 1.92 THB/hr).
- **Resumability**: Maintained in `reports/tune_checkpoint.json`. Interrupted trials resume seamlessly without re-running or double-billing.
- **Budget Tracking**:
  - Total Spend: **0.0016 THB** of 150.0 THB budget.
  - Per-trial duration, `cost_thb`, validation and test metrics logged to MLflow.

---

## 4. Task 3 — Run Comparison and Justification

Full comparison table exported to `reports/lab2-comparison.md`.

### Top 5 Trials

| run_id   | val_roc_auc | cost_thb | n_estimators | max_depth | min_samples_leaf | thb_per_point |
|:---------|------------:|---------:|-------------:|----------:|-----------------:|--------------:|
| 55e93760 |      0.8426 |   0.0002 |          100 |         4 |                5 |        0.0001 |
| e7768f95 |      0.8424 |   0.0003 |          100 |         4 |                1 |        0.0002 |
| e4ccf157 |      0.8412 |   0.0001 |          300 |         4 |                5 |        0.0001 |
| 668bfe2d |      0.8404 |   0.0001 |          300 |         4 |                1 |        0.0001 |
| 7a41981b |      0.8398 |   0.0001 |          100 |         8 |                5 |        0.0001 |

### Selection Justification (<200 words)

> We registered `n_estimators=100, max_depth=4, min_samples_leaf=5` (run `55e93760`), achieving val ROC-AUC 0.8426 and test ROC-AUC 0.8532 at 0.0002 THB. While tripling trees to 300 (`e4ccf157`) yields 0.8412, it provides no metric gain while tripling compute cost and inference latency. Crucially, across all 12 trials, scores cluster tightly between 0.8257 and 0.8426 (a spread of 0.0169), which is comparable to the random variation across seeds. Deeper trees overfit to noise (depth 12 dropped to 0.8257), so shallow depth-4 with leaf regularization (min_samples_leaf=5) is the most parsimonious, robust choice.
>
> Across 5 evaluation seeds (20260101–20260105), this configuration demonstrated solid generalization: validation ROC-AUC 0.8556 ± 0.0126 and test ROC-AUC 0.8534 ± 0.0086.
>
> Training cost is 0.0002 THB on GCP `e2-standard-4` spot instances (rate 1.92 THB/h). Monthly retraining costs ~0.0002 THB (<0.003 THB annually), well below our 150 THB budget.
>
> This choice could be wrong if future machine degradation manifests as complex high-order sensor interactions that shallow depth-4 trees cannot capture, leading to underfitting if failure patterns become non-linear.

### Model Promotion and Staging Policy
In a production organization, model promotion to Staging should be restricted to the **Lead ML Engineer or MLOps Platform Owner**, requiring an automated CI audit showing:
1. Verified lineage across git commit, data digest, container sha, and training job.
2. Passing data contract and regression tests.
3. Latency p95 within SLA.
4. Demonstrable metric gain exceeding observed seed variance without budget regression.

---

## 5. Task 4 — Model Registry with Complete Lineage

Registered Model: `itcs355-6688249` (Version 1 & 2) in Stage `Staging` (Alias: `staging`).

The registered version carries all 8 required lineage fields as tags:
- `git_commit`: `df296eed3963795c9d662c4fe035d3e97fcf9f71`
- `data_version`: `422cccb9136e8140`
- `mlflow_run_id`: `55e93760219e4a91943e49f315295814`
- `training_job_id`: `projects/821808260643/locations/asia-southeast1/customJobs/708691044316741632`
- `image_digest`: `asia-southeast1-docker.pkg.dev/itcs355-6688249/itcs355/itcs355-lab1@sha256:7bf9ba12fcfd5227644934e14dfb4b304029a6b6fcb3038f4e867d559d3ef572`
- `seed`: `20260101`
- `metric_val`: `0.8426`
- `metric_test`: `0.8532`

---

## 6. Task 5 — Reload Check

Reloading model from registry by version:
```bash
make reload-check VERSION=1
```
Output:
```text
loading models:/itcs355-6688249/1
  reading 125: p(failure)=0.0182
  reading 126: p(failure)=0.0702
  reading 127: p(failure)=0.0289
  reading 128: p(failure)=0.0277
  reading 129: p(failure)=0.0132

PASS  model reloaded from the registry and scored rows
```

---

## 7. Drill 2 Reference Answers

- **Permission Failure on First Submission**: Runtime service agent `service-821808260643@gcp-sa-aiplatform-cc.iam.gserviceaccount.com` lacked `roles/artifactregistry.reader` to pull the training image from Artifact Registry.
- **Chosen Run ID**: `55e93760219e4a91943e49f315295814` (Trial 1, `n_estimators=100, max_depth=4, min_samples_leaf=5`).
- **Seed Variance Measured**: Val ROC-AUC $0.8556 \pm 0.0126$, Test ROC-AUC $0.8534 \pm 0.0086$ (spread across seeds is $\approx 0.035$, which is wider than the $\approx 0.017$ spread between trial 0 and trial 11).
- **Monthly Retraining Cost**: $\approx 0.0002$ THB / month on `e2-standard-4` spot instances ($<0.003$ THB / year).
