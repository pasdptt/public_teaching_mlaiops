# Lab 1 README template

The root `README.md` of the course repository is the course home page. **In your own
repository, replace it with this template** and fill it in. Your README is graded: a grader
with Docker and nothing else from your setup runs one command and compares the result against
your claim line.

```bash
cp course/labs/lab-01-readme-template.md README.md
```

Then delete this introduction — everything above `# <Your project title>` — edit every `<...>`,
and delete every block marked **REPLACE** before you submit. The grading script fails any README
that still contains the word REPLACE.

---

# <Your project title>

Predicting machine failure within 7 days from sensor readings. The model is not the point;
whether a stranger can reproduce it is.

## Reproduce

```bash
make reproduce
```

expected test_roc_auc: 0.848 ± 0.001

Runtime: about 40 seconds on 4 cores. No cloud account or credentials needed for this command —
that is deliberate, and it is why a grader can run it.

**REPLACE:** re-measure and update that claim line after your final change. Keep the exact
format `expected test_roc_auc: <value> ± <tolerance>`; `make verify` parses it, and so does the
grading script.

The tolerance covers the grader's machine, not your choice of seed. `make reproduce` pins the
seed for the dataset and the model both, so the grader runs your exact configuration; anything
they see that differs came from the environment — a different CPU, a different BLAS, a library
that moved under you. Measure it by running `make reproduce` twice, on two machines if you can
get them. On this pipeline it is tiny but not zero: the same seed gives 0.8482511 on an arm64
laptop and 0.8482379 on the amd64 CI runner — different architecture, different Python, same
pins — a gap of 1.3e-5. So ±0.001 is roughly seventy times more room than you need, and ±0.01
is padding.

Changing the seed measures something else. It moves the *split* — which machines land in test —
and that swings `test_roc_auc` across roughly 0.82–0.87 on this data. Write that number down in
your run discussion, because it says how much of your headline metric is luck. It is not your
tolerance.

## The problem

240 machines, 25 readings each, 6 sensor features, binary target `failed_within_7d` with a
positive rate near 12%.

Machines have persistent characteristics — a hot-running machine reads hot in every row. So the
train/validation/test split is **grouped by `machine_id`**: every reading from one machine lands
in exactly one partition. Splitting row-wise instead lets the model memorise the machine and
reports a validation score that will never survive production. `tests/test_data.py` asserts this
property holds, and Lab 4 turns it into a CI gate.

Bringing your own dataset is allowed. Replace `scripts/make_dataset.py`, update the schema in
`src/data.py`, and keep every test passing.

## Setup

```bash
cp cloud.env.example cloud.env      # fill in, never commit
make setup
make cloud-check                    # eight slots, all PASS
make data                           # generate the dataset
make test                           # all tests passing
```

## Reproducibility trade-off

**REPLACE with your answer, 100 words maximum.**

Three things pin your build: hashed dependencies, a digest-pinned base image, and controlled
seeds. Under real time pressure you would keep some and drop others.

Which would you drop first, and what specifically breaks when you do? There is a defensible
answer, and we compare answers in Session 2. An answer that refuses to choose scores zero.

## Notes for the grader

**REPLACE:** anything that would otherwise cause you to answer a question by email. Non-obvious
choices, known limitations, anything that behaves differently on your machine. A README that
requires a conversation has failed the lab regardless of what the code does.

---

## Before you submit

This part is for you, not the grader. Delete it from your README when every box is ticked.

Four `TODO` markers are left in the repository deliberately. Each is a graded decision, not
busywork:

| Where | What |
|---|---|
| `requirements.txt` | Regenerate with `pip-compile --generate-hashes` |
| `Dockerfile` | Pin the base image by digest; add `--require-hashes` |
| `cloudlayer/<your provider>.py` | Implement `upload`, `download`, `push_image` |
| Your README | The reproducibility trade-off question above |

Then push your image and data:

```bash
make image-push        # image reaches your registry, digest-pinned
dvc init && dvc remote add -d storage ${BLOB_URI}/dvc
dvc add data/raw && dvc push
```

Run five or more tracked runs varying something meaningful — not five identical runs with
different seeds.

- [ ] `make reproduce` works from a fresh clone, on a machine that is not yours
- [ ] `make verify` passes against your claim line
- [ ] `make test` — all tests pass
- [ ] `make portability-audit` — clean
- [ ] Image builds for `linux/amd64` and is pushed, digest-pinned
- [ ] `dvc push` completed; a grader can `dvc pull`
- [ ] Five or more tracked runs with params, metrics, data fingerprint, and commit SHA
- [ ] Every instruction block is gone, and no `<...>` placeholder is left
- [ ] `make scan-secrets` is clean

That last check is not optional. A credential in Git history is an automatic deduction in this
course, and rotating it is your responsibility, not the grader's. The scan reads *history*, not
your working tree, because deleting the file is the thing that makes people believe they are
safe. If it finds something, rotate the credential first and rewrite history second — in that
order, because the first one is the only step that actually helps.

The full handout is [Lab 1](lab-01-reproducible-training.md).
