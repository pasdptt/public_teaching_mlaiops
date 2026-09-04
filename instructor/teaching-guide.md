# ITCS355 — Instructor Teaching Guide

Companion to `Course_Specification_ITCS355_merged.xlsx`. The workbook is the authoritative
specification; this document holds the teaching judgement that does not fit in a template cell.

**Course:** ITCS355 Machine Learning Operation and Deployment · 1(1-0-2) · Semester 1 · Class level 4
**Delivery:** 5 sessions × 3 hours + final week · 15 lecture hours · ~42 hours self-study
**Instructors:** Dr. Pasd Putthapipat · Asst. Prof. Dr. Thanapon Noraset

---

## 1. How this plan relates to the specification

The five topic names, the three CLOs, and the four-component assessment split — Capstone demo
& defense 15, Capstone System 30, In-class drills 15, Labs 40 — come from the faculty
specification in the university system and are not changed. What was added: subtopic detail,
in-class activity design, a mark-level assessment blueprint that reconciles to 35/35/30, and
five take-home labs.

**The one structural decision worth understanding.** The credit structure is 1(1-0-2): one
lecture hour, zero lab hours, two self-study hours per week. But the Teaching Method sheet
ticks *Lab* for all three CLOs, and MLOps cannot be taught without hands-on work.

The specification resolves this by making Labs the largest single component — 40 marks, 8 per
lab — awarded against the acceptance criteria in each handout. The in-class drills additionally
carry evidence questions drawn from each student's own lab output: their p95 figure, their run
ID, the true cause behind their drift alert. That second mechanism is what makes a copied lab
worthless, and it is worth keeping even though the labs carry substantial marks of their own.

**There is no final examination**, and there are no quizzes. The former quiz component is now
*In-class drills* at 15 marks, 3 per session. The capstone is split across two specification
lines: *Capstone System* (30, the five rubric criteria) and *Capstone demo & defense* (15).

**Grading load is the real cost of this choice.** Five labs marked by cloning and running is
roughly 15 minutes per student per lab — about 50 hours across a term for a cohort of 40.
The scripts in `instructor/` reduce it but do not remove it. Budget TA time from the start,
or reduce the cohort's lab count to four by folding Lab 5 into the project.

## 2. Session-by-session teaching notes

Full subtopic lists are on the **Session Detail** sheet. What follows is what the sheet cannot hold.

**Session 1 — From Notebook to Reproducible ML.** The centrepiece is the partner-reproduction
exercise in the last 50 minutes: students swap repositories and try to reproduce each other's run.
Most pairs fail. Do not rescue them; let the failure land, then debrief it. This single exercise
does more to motivate the whole course than any lecture on technical debt. Budget the full 50
minutes — it always runs long.

**Session 2 — Pipelines, features, and managed training.** The budgeted tuning contest scores teams
on *cost per point of metric*, not on the metric. Students find this genuinely disorienting, which
is the point. Announce the scoring rule before they start, or they will optimise the wrong thing and
feel cheated.

**Session 3 — Deployment, scaling, and release safety.** Students will report mean latency because it flatters them. Insist
on p95 and p99 from the first measurement. The timed rollback drill works best if the canary model
is only *slightly* worse — an obviously broken model teaches nothing about detection.

**Session 4 — CI/CD/CT, monitoring, and drift.** The 50-minute incident simulation is the highest-value block
in the course. Inject one of: a shifted feature distribution, a schema change, or a latency
regression. Teams must diagnose, decide retrain-versus-rollback, and write a five-line post-mortem.
Score the reasoning, not the speed. Prepare three fault variants so adjacent teams cannot copy.

**Session 5 — Operating LLM systems and defending the bill.** Both halves now have lab material.
The LLM half is Lab 5 Part B: an evaluation gate, guardrails, and token accounting, built on
`scripts/llm_eval.py` and `src/llmcost.py`. Slides for that half and Drill 5 questions on it are
still to write — see the note on the *Session Detail* sheet.

Teach Part B with `make llm-gate` on screen. It fails on purpose, and the four regressions it catches
are the lesson: an invented part number, a fabricated sensor reading, an obeyed prompt injection, and
a borderline case decided instead of escalated. Ask the room which of those a pass-rate threshold
would have hidden — the answer is all four, if the other cases improved. That is why the gate
compares per case.

The lab runs on recorded responses, so nobody spends money and everyone gets the same failures. Say
so explicitly; students assume an LLM exercise means an API key and a bill.

On the cloud half, the first failure will be a permissions error, for almost everyone.
Plan for it rather than firefighting: pre-create roles, and treat the first failed job as a live
teaching moment about least privilege. Reserve the last 45 minutes for project architecture clinics —
teams that have not had their architecture questioned before final week tend to submit incomplete
monitoring.

**Final week.** Presentations and Drill 5. There is no final examination. During demos, send
unexpected input yourself — the demo and defence carry 15 of the capstone's 45 marks. Graceful handling
scores; crashing scores partial credit if the team's logging makes the cause obvious within a
minute.

## 3. Recurring pattern: the public failure debrief

Open every session with 20 minutes reviewing anonymised failures from the previous lab. It is the
easiest block to cut when running late, and cutting it is a mistake — normalising broken builds is
most of the cultural content of MLOps, and students will not admit to failures they think are
unusual.

## 4. Where students actually get stuck

In order of frequency: cloud identity and permissions; Docker platform mismatch on Apple Silicon;
forgetting to tear down endpoints; path assumptions that hold only locally; and serialized models
that fail to load under a different library version. Prepare a one-page fix sheet for each and hand
it out rather than debugging live — five students will hit the same issue in the same hour.

## 5. Open decisions

**Cloud platform is not yet named.** The specification does not name one, and Session 5 plus Lab 5
are written platform-neutral. Pick one before materials are finalised:

- *AWS* — S3, SageMaker training and endpoints, ECR, IAM, CloudWatch. Widest industry recognition.
- *GCP* — Cloud Storage, Vertex AI, Artifact Registry, Cloud Monitoring. Cleanest student experience.
- *Azure* — Blob Storage, Azure ML jobs and managed endpoints, ACR, Azure Monitor. Strongest if the
  faculty already has an institutional agreement.

The portable core is the same in all three: Docker, MLflow, DVC, FastAPI, GitHub Actions, and a
drift library such as Evidently. If no credits are available at all, the whole course runs locally
on `k3s` with MinIO substituting for object storage — you lose the cost lessons, which is a real
loss, but nothing else.

**Workload.** The plan totals about 40 self-study hours against a nominal 30. To close the gap:
drop Lab 5 and fold the cloud migration into the project, and trim project scope. A modest overrun
is normal for a project-based course, but it should be a deliberate choice.

**Cost guardrails.** Target under 800 THB per student for the term using free tiers and spot
compute. Set organisational budget caps, not just alarms. Assume at least one student leaves a GPU
endpoint running over a weekend; make the credit allocation survive it, and use it in the next
debrief. Every lab ends with a teardown step, and teardown is graded.

**Grading load.** Budget roughly 20 minutes per student per lab if you grade by cloning and running,
which you should. A `make grade` target that mechanically checks reproducibility converts most of
Lab 1 grading into a script.

## 6. Reading

Assigned:
- Sculley et al., *Hidden Technical Debt in Machine Learning Systems* (2015) — before Session 1
- Google Cloud, *MLOps: Continuous delivery and automation pipelines in ML* — before Session 2
- Breck et al., *The ML Test Score* (2017) — before Session 4

Recommended:
- Huyen, *Designing Machine Learning Systems* (2022) — closest single book to this syllabus
- Beyer et al., *Site Reliability Engineering* — the SLO and post-mortem chapters, before Session 4
- Mitchell et al., *Model Cards for Model Reporting* (2019) — for the project deliverable
