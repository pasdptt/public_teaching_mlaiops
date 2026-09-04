# ITCS355 — Lab 1: Reproducible Training Container

**Released:** end of Session 1 · **Due:** before Session 2 · **Effort:** ~4 hours
**CLO1** · **Marks:** 8 · **Also assessed through:** Drill 1 and Capstone criterion R1 (Reproducible ML Pipeline)
**Cloud used:** object storage only — this lab is deliberately the least cloud-dependent

**In this repository**

Files: `src/train.py` · `src/data.py` · `src/config.py` · `Dockerfile` · `tests/test_data.py` · `scripts/make_dataset.py` · `scripts/verify_metric.py` · `cloudlayer/<provider>.py`

Commands: `make data · make test · make portability-audit · make reproduce · make verify · make image-push`

Every `TODO` marker in those files is a graded decision. Everything around them already works, so you debug your own choices rather than the scaffolding.

---

## Objective

Make your training run reproducible by a stranger who has nothing but your repository URL. Not
"documented" — reproducible. A grader on a different operating system and a different CPU
architecture will clone your repo, run one command, and compare the number that comes out against
the number you claimed.

```mermaid
flowchart LR
    R["repo URL"] --> C["git clone"] --> M["make reproduce"]
    M --> D["data<br>DVC hash"]
    M --> E["environment<br>hashed lock file"]
    M --> I["image<br>digest-pinned base"]
    M --> S["seeds<br>logged as params"]
    D & E & I & S --> N["the same number"]
    N --> V{"make verify<br>within tolerance?"}
    V -->|yes| P["PASS"]
    V -->|no| F["one of the four links is loose<br>— find which"]
```

Any one of those four links breaking produces a different number. The lab is about finding
out which one is loose in your own repo.

## Before you start

- `make cloud-check` passes on all eight slots
- Your provider CLI is authenticated
- `cloud.env` is filled in and is listed in `.gitignore`

---

## Task 1 — Structure the project (30 min)

Move out of the notebook. The target layout:

```
itcs355/
├── cloud.env.example
├── Dockerfile
├── Makefile
├── requirements.txt        # or pyproject.toml with a lock file
├── data/                   # DVC-tracked, not Git-tracked
│   └── .gitignore
├── src/
│   ├── train.py
│   ├── data.py
│   └── config.py           # reads cloud.env, no hardcoded paths
├── tests/
│   └── test_data.py
└── README.md
```

Keep your original notebook in `notebooks/` for reference, but nothing in the grading path may
import from it.

**Constraint:** no string in `src/` may contain a bucket name, a provider hostname, or an absolute
path from your machine. Everything comes from `config.py`, which reads `cloud.env`.

## Task 2 — Pin the environment properly (40 min)

`pip freeze` is not reproducibility. It captures what you happen to have installed, on your platform,
today. Do all three of these:

1. **Pin with hashes.** Use `pip-compile --generate-hashes` (or `uv pip compile`, or Poetry's lock
   file). The lock file is committed.
2. **Pin the base image by digest,** not by tag. `python:3.11-slim` moves; `python:3.11-slim@sha256:…`
   does not.
3. **Set the seeds and record them.** Python's `random`, NumPy, and your framework each have their
   own. Log the seed as a parameter, not as a comment.

In your README, state plainly which of these three you would drop first under time pressure, and why.
There is a defensible answer; we will compare answers in Session 2.

## Task 3 — Containerise the training job (60 min)

Write a `Dockerfile` that builds an image capable of running the full training end to end.

Requirements:
- Multi-stage build, so the final image does not carry the compiler toolchain
- Non-root user
- No credentials baked into any layer — they arrive at runtime from `SECRET_STORE_PATH`
- Builds for `linux/amd64` even if you are on Apple Silicon: `docker buildx build --platform linux/amd64`

The last requirement catches out roughly a third of every cohort. If your image builds on your laptop
and fails on the grader's machine, this is almost always why.

Then push it:

```bash
make image-push      # calls adapter.push_image() → your provider's registry
```

## Task 4 — Version the data (45 min)

Initialise DVC, point its remote at `${BLOB_URI}/dvc`, and track your raw dataset.

```bash
dvc init
dvc remote add -d storage ${BLOB_URI}/dvc
dvc add data/raw
git add data/raw.dvc .dvc/config && git commit -m "track raw data"
dvc push
```

Then build your train/validation/test split **inside the pipeline**, not by hand, and make the split
deterministic given the seed. Write one test in `tests/test_data.py` that fails if any identifier
appears in more than one split. Leakage is the failure this catches, and it is the most common silent
error in student projects.

## Task 5 — Track at least five runs (45 min)

Point MLflow at `MLFLOW_TRACKING_URI` and log, for every run:

- all hyperparameters, including the seed
- the metric you care about, on validation and test separately
- the data version (the DVC hash) and the Git commit SHA
- the trained model as an artifact

Five runs minimum, varying something meaningful — not five identical runs with different seeds.

## Task 6 — Write the README that does the work (30 min)

The README must get a stranger from clone to reproduced metric in **one command**. Assume they have
Docker and nothing else from your setup.

It must state: what the problem is, what the data is and where it comes from, the one command, the
expected metric and tolerance, and roughly how long it takes.

```bash
make reproduce       # the one command
```

---

## Deliverables checklist

- [ ] Repository with the layout above, pushed and accessible
- [ ] Lock file with hashes; base image pinned by digest
- [ ] `Dockerfile` building for `linux/amd64`, non-root, no baked credentials
- [ ] Image pushed to your provider's registry
- [ ] DVC remote configured and `dvc push` completed
- [ ] Leakage test in `tests/test_data.py`, passing
- [ ] Five or more tracked runs with params, metrics, data version, commit SHA, and artifact
- [ ] `README.md` with the one command, expected metric, and tolerance
- [ ] `cloud.env` absent from Git history — check, do not assume

## Acceptance criteria

**Passes when** a grader on a different OS and architecture runs your single command and reaches your
reported metric within your stated tolerance, without asking you a question.

**Fails when** any of: the command needs an undocumented environment variable; the image will not run
on `linux/amd64`; the metric differs beyond tolerance with no explanation; a credential appears
anywhere in Git history.

## Common failure modes

| Symptom | Cause |
|---|---|
| `exec format error` on the grader's machine | Built for `arm64` on Apple Silicon |
| Metric differs by a small amount every run | A seed you did not set — check your data loader's shuffling |
| `dvc pull` fails for the grader | Remote is private, or credentials were assumed rather than documented |
| Container cannot read data | Absolute local path leaked into `src/` |
| Build succeeds, run fails on import | Dependency installed in the build stage but not copied to the final stage |

## Teardown

Nothing persistent is created in this lab beyond storage, which costs almost nothing. Still run
`make teardown` to confirm the tagging and teardown path works — you will rely on it from Lab 3
onward, and finding out it is broken then is expensive.

## What Drill 1 covers

Concept questions on technical debt, container layering, and leakage. Plus evidence questions
answerable only from your own work: your data version hash, your five runs' parameter spread, and
the answer you wrote for "which pinning would you drop first, and why".
