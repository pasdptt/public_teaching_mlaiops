# ITCS355 Machine Learning Operation and Deployment

Faculty of ICT, Mahidol University · 1(1-0-2) · five 3-hour sessions, then a final week of
presentations.

You take one small model — predicting machine failure from sensor readings — and turn it into a
system a stranger can reproduce, deploy, monitor and afford. The model is not the point.
Everything around it is.

## Start here

1. **Set up your cloud account.** Pick one provider and stay on it all term.
   - [Google Cloud](course/getting-started-gcp.md) — the free trial asks for a credit card
   - [Azure](course/getting-started-azure.md) — Azure for Students, no card needed
2. **Read the [portability reference](course/reference/cloud-portability-reference.md).** It
   explains why the code is split the way it is.
3. **Open this week's lab** from the table below.

Stuck on setup? Post your `make cloud-check` output in the course channel — don't wait for the
session.

## Sessions and labs

| Session | Topic | Lab | Slides |
|---|---|---|---|
| 1 | From notebook to reproducible ML | [Lab 1](course/labs/lab-01-reproducible-training.md) | [Session 1](course/slides/session-01.md) |
| 2 | Pipelines, features and managed training | [Lab 2](course/labs/lab-02-tracking-and-registry.md) | [Session 2](course/slides/session-02.md) |
| 3 | Deployment, scaling and release safety | [Lab 3](course/labs/lab-03-serving-and-rollback.md) | [Session 3](course/slides/session-03.md) |
| 4 | CI/CD/CT, monitoring and drift | [Lab 4](course/labs/lab-04-cicd-monitoring-drift.md) | [Session 4](course/slides/session-04.md) |
| 5 | Operating LLM systems and defending the bill | [Lab 5](course/labs/lab-05-cloud-mlops-and-cost.md) | [Session 5](course/slides/session-05.md) |
| Final | Presentation and defence | [Capstone brief](course/project/project-brief.md) | |

## Find something else

| Looking for | Go to |
|---|---|
| Marks, assessment and how the course runs | [Course overview](course/README.md) |
| What to put in your own README | [Lab 1 README template](course/labs/lab-01-readme-template.md) |
| How the code is organised | [Repository guide](docs/REPO-GUIDE.md) |
| The whole course on one page | [Course deck](course/slides/course-deck.md) |
| The official course specification | [Specification](course/spec/course-specification.md) |

## Run the reference model

```bash
make reproduce
```

expected test_roc_auc: 0.848 ± 0.001

This trains the reference model in Docker. It takes about 40 seconds on 4 cores and needs no
cloud account. `make verify` then checks the result against the line above.

In your own repository, this file becomes your project's README. Start from the
[Lab 1 README template](course/labs/lab-01-readme-template.md).
