# Lab 1 — Marking Notes

Lab 1 is worth **8 marks**, awarded against the acceptance criteria in the handout — met or
not met, no partial credit for a repo that almost reproduces. It also feeds **Drill 1** and
**Capstone criterion R1 (Reproducible ML Pipeline)**. These notes exist so marking is
consistent across the cohort.

The mechanical script decides most of it. Award the 8 marks when `make reproduce` works from
a fresh clone on a machine that is not the student's and the metric matches the claim. Award
0 when it does not, and put the reason in the debrief. This is a harsh-looking rule that is
kinder in practice: it is unambiguous, it is the same standard for everyone, and a student
who fails Lab 1 still has four labs and the capstone ahead of them.

## Run this first

```bash
instructor/grade_lab1.sh <student-repo-url>
```

Fourteen mechanical checks. Run it on a different architecture from the majority of the
cohort — reproducing across architectures is the thing the lab actually tests.

## What the script cannot judge

**The trade-off answer.** Students must say which of hashed dependencies, digest-pinned base
image, or seed control they would drop first. Strong answers pick one and name the specific
failure that follows. Look for: dropping seeds costs you comparability between runs but not
buildability; dropping hashes leaves you exposed to a republished wheel; dropping the digest pin
is the fastest way to have a build stop reproducing without any commit. An answer that refuses
to choose, or lists all three as equally important, scores zero on this item.

**Is the tolerance honest?** Cross-check the stated tolerance against the spread in the
student's own tracked runs. In the reference implementation, a fixed seed reproduces to within
0.0005 across machines, while varying the seed moves test ROC AUC across roughly 0.82–0.87 —
because the seed moves the split, not just the model. A student who states ±0.05 has quietly
covered up non-determinism they did not investigate. This distinction is a good exam question.

**Are the five runs a study or noise?** Five seeds of one configuration is not a study. Look for
at least one hyperparameter varied with intent.

## Common situations and how to handle them

| Situation | Response |
|---|---|
| Runs on the student's machine, `exec format error` on yours | The lab's central failure. Do not fix it for them; it is worth more as a Session 2 debrief item than as a rescue |
| `dvc pull` fails — remote is private | Half credit. The README should have documented the access path; note it and move on |
| Perfect repo, no cloud artifacts | The image and DVC remote are required. Local-only submissions are incomplete |
| Hashes present but `--require-hashes` missing from the Dockerfile | Minor. Note it; the intent is there |
| Tolerance padded to ±0.1 | Raise it in the debrief anonymously. This is the most instructive failure in the lab |

## Feeding Drill 1

Draw the evidence questions from each student's own submission:

- your data fingerprint
- the parameter you varied across your five runs, and what it did
- your trade-off answer, in one sentence
- your stated tolerance and how you chose it

Concept questions cover technical debt, container layering, digest versus tag pinning, and group
leakage. Three marks total, all CLO1 — half concepts, half evidence, in the shape set out in
[`drills/README.md`](drills/README.md). The full Drill 1 paper is not written yet;
[`drills/drill-05.md`](drills/drill-05.md) is the worked example to follow.

## Time budget

About 12 minutes per student: 4 for the script, 8 for the judgement items. For a cohort of 40
that is roughly 8 hours, so start grading the day the lab closes.
