# ITCS355 Machine Learning Operation and Deployment

Faculty of ICT, Mahidol University · 1(1-0-2) · five 3-hour sessions, then a final week of
presentations.

You take one small model — predicting machine failure from sensor readings — and turn it into a
system a stranger can reproduce, deploy, monitor and afford. The model is not the point.
Everything around it is.

## Start here

1. **Begin with [Week 0](course/week-0-setup/)** — set up Google Cloud or Azure before
   Session 1.
2. **Each week, open that week's folder.** Every one has the same four parts:

   | | |
   |---|---|
   | **Read** | the session slides, and any reading set for the week |
   | **Prepare** | what to have done before the session starts |
   | **Do** | the lab, and any capstone step |
   | **Due** | what you hand in, by when, and for how many marks |

Stuck on setup? Post your `make cloud-check` output in the course channel — don't wait for the
session.

## Weeks

| Week | Topic | Lab |
|---|---|---|
| [Week 0](course/week-0-setup/) | Set up your cloud account | — |
| [Week 1](course/week-1-reproducible-training/) | From notebook to reproducible ML | Lab 1, due before Session 2 |
| [Week 2](course/week-2-tracking-and-registry/) | Pipelines, features and managed training | Lab 2, due before Session 3 |
| [Week 3](course/week-3-serving-and-rollback/) | Deployment, scaling and release safety | Lab 3, due before Session 4 |
| [Week 4](course/week-4-cicd-monitoring-drift/) | CI/CD/CT, monitoring and drift | Lab 4, due before Session 5 |
| [Week 5](course/week-5-llm-systems-and-cost/) | Operating LLM systems and defending the bill | Lab 5, due before the final week |
| [Final week](course/week-final-capstone/) | Presentation and defence | Capstone |

## Find something else

| Looking for | Go to |
|---|---|
| Marks, assessment and how the course runs | [Course overview](course/README.md) |
| The capstone project | [Capstone brief](course/project/project-brief.md) |
| Why the code is split into three layers | [Portability reference](course/reference/cloud-portability-reference.md) |
| What to put in your own README | [Lab 1 README template](course/week-1-reproducible-training/lab-01-readme-template.md) |
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
[Lab 1 README template](course/week-1-reproducible-training/lab-01-readme-template.md).
