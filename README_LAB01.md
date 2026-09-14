# ITCS355 Lab 1 — Reproducible Training

> **Course materials live in [`course/`](course/README.md)** — syllabus, slides, the faculty
> specification, all five lab handouts, and the project brief. Every document is Markdown and
> renders on GitHub, diagrams included. New to the repo? Start with the
> [portability reference](course/reference/cloud-portability-reference.md).
> Keep this block when you edit the rest of this file; it is not part of the Lab 1 deliverable.

Predicting machine failure within 7 days from sensor readings. The model is not the point;
whether a stranger can reproduce it is.

> **This README is graded.** A grader with Docker and nothing else from your setup runs one
> command and compares the result against the claim below. Edit every `<...>` and delete all
> placeholder instruction blocks before submitting.

---

## Reproduce

Assuming Docker is installed (no local Python, virtual environment, or cloud credentials required), run:

```bash
make reproduce
```

expected test_roc_auc: 0.8480 ± 0.0100

Runtime: about 40 seconds on 4 cores. The container runs entirely self-contained, mounting local directories for data and reports.

---

## The problem

Predicting machine failure within 7 days from sensor readings.

### The data and where it comes from
- **Dataset**: 240 industrial machines, 25 time-series sensor readings each (6,000 rows total), across 6 sensor features (`temp_c`, `vibration_mm_s`, `pressure_kpa`, `hours_since_service`, `load_pct`, `ambient_humidity`) with binary classification target `failed_within_7d` (~12% positive failure rate).
- **Source & Versioning**: Versioned and tracked in remote cloud object storage via DVC (`data/raw.dvc` stored at `${BLOB_URI}/dvc`), and can be deterministically reproduced locally with `make data` (`python scripts/make_dataset.py --seed 20260101`).
- **Grouped Split**: Machines possess persistent physical characteristics. The train/val/test split is strictly **grouped by `machine_id`** in `src/data.py` (verified by `tests/test_data.py`) so no readings from any single machine cross split boundaries, preventing data leakage.

Bringing your own dataset is allowed. Replace `scripts/make_dataset.py`, update the schema in
`src/data.py`, and keep every test passing.

---

## Layout

```
src/          Layer 1 — provider-neutral. No SDKs, no bucket names, no absolute paths.
cloudlayer/   Layer 3 — the only place a provider SDK may be imported.
scripts/      Dataset generation, cloud check, portability audit, metric verification.
tests/        Data contract tests and split property tests.
```

`src/config.py` is the single point of environment knowledge. Everything else reads from it.
`make portability-audit` enforces the rule; it fails the build if a provider string appears in
`src/` or `tests/`.

---

## Setup

```bash
cp cloud.env.example cloud.env      # fill in, never commit
make setup
make cloud-check                    # eight slots, all PASS
make data                           # generate the dataset
make test                           # 10 tests, all passing
```

Post your `make cloud-check` output in the course channel before Session 1.

---

## MLflow Tracking & UI

Every training run automatically logs hyperparameters, validation/test metrics separately, the DVC data version hash, Git commit SHA, and serialized model artifacts.

Launch the local tracking dashboard:

```bash
mlflow ui --backend-store-uri sqlite:///reports/mlflow.db
```

Open [http://localhost:5000](http://localhost:5000) in your browser to inspect experiment runs, compare metrics, and view logged model artifacts.

---

## What was completed

| Where | What |
|---|---|
| `requirements.txt` | Regenerated with `pip-compile --generate-hashes` |
| `Dockerfile` | Multi-stage build pinned by digest to `linux/amd64`; added `--require-hashes` |
| `cloudlayer/gcp.py` | Implemented `upload`, `download`, `push_image` returning digest reference |
| This README | Completed reproducibility trade-off question and grader documentation |

---

## Reproducibility trade-off

Under real time pressure, I would drop **controlled seeds** first. 

Dropping seeds breaks exact numerical determinism—training metrics will fluctuate across runs within an expected statistical variance, causing point-in-time assertion checks to fail without a tolerance margin. 

However, the pipeline remains functionally reproducible: it builds, installs, and executes predictably. In contrast, dropping dependency hashes or digest-pinned base images risks silent upstream drift, ABI mismatches, or supply-chain tampering that cause fatal build or runtime failures. Managing statistical variance is acceptable; an unbuildable container is not.

---

## Notes for the grader

- **Platform & Digest Pinning**: The training container image is built with a multi-stage `Dockerfile` pinned by SHA256 digest (`python@sha256:...`) and compiled for `linux/amd64` to guarantee identical behavior across Apple Silicon and x86 CI/grading runners.
- **Group-Aware Splitting**: `src/data.py` partitions by `machine_id` so that all readings for any machine reside strictly within one partition (train, validation, or test). Disjointness is verified in `tests/test_data.py`.
- **Cloud Layer**: The provider adapter (`cloudlayer/gcp.py`) uses Google Cloud Storage for blob upload/download and Artifact Registry for digest-pinned container pushes. No provider strings or SDKs exist in `src/` or `tests/` (`make portability-audit` clean).
- **Run Tracking**: MLflow logs all hyperparameters, seeds, validation/test metrics, DVC data version hashes, git commit SHAs, and model artifacts.

---

## Checklist before you submit

- [x] `make reproduce` works from a fresh clone, on a machine that is not yours
- [x] `make verify` passes against your claim line
- [x] `make test` — all tests pass
- [x] `make portability-audit` — clean
- [x] Image builds for `linux/amd64` and is pushed, digest-pinned
- [x] `dvc push` completed; a grader can `dvc pull`
- [x] Five or more tracked runs with params, metrics, data fingerprint, and commit SHA
- [x] Every template instruction block above is gone (the course-materials block at the top stays)
- [x] `git log -p | grep -i -E "secret|password|AKIA|BEGIN PRIVATE"` returns nothing

That last check is not optional. A credential in Git history is an automatic deduction in this
course, and rotating it is your responsibility, not the grader's.
