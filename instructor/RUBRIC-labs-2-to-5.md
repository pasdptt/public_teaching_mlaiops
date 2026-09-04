# Marking Notes — Labs 2 to 5

Lab 1 has its own file. These four share a pattern: run the mechanical script, then spend
your time on the judgement items, which are listed per lab below and are where the actual
learning shows up.

Each lab is worth **8 marks**, awarded against the acceptance criteria in its handout — met
or not met. They also feed **Drills 2–5** and the capstone criteria: Lab 2 to R1 (Reproducible
ML Pipeline), Lab 3 to R2 (Deployment & CI/CD), Lab 4 to R3 (Monitoring & Reliability) and R4
(Failure Handling & Technical Defense), Lab 5 to R5 (Documentation & Presentation). Draw each
drill's evidence questions from the student's own submission; that is what makes copying a lab
useless, and it matters all the more now that labs carry 40 of the 100 marks.

Award the 8 marks when the mechanical script passes and the judgement items below hold.
Award 0 otherwise. Partial credit on a binary criterion invites argument and costs you hours
you do not have across five labs.

---

## Lab 2 — Tracking and registry

```bash
instructor/grade_lab.sh 2 <repo-url>
```

**Judgement items**

*The 200-word justification* is the whole lab. Four things must be addressed: why not the
highest scorer, seed variance, training and retraining cost, and one way the choice could
be wrong. Full marks need a real argument. In the reference implementation, trials cluster
between 0.826 and 0.843 val ROC AUC — a spread narrower than seed variance, which means
almost any "best model" claim is noise. A student who notices that has understood the lab;
one who confidently registers the 0.843 has not.

*Is it a study or a sweep of noise?* Five seeds of one configuration is not a study. Look
for three hyperparameters varied with intent.

*Did the budget bind?* Students whose study cost nothing have not run on managed compute.
`make tune` with `--instance local` produces zero-cost trials, and the comparison table's
cost-per-point column goes degenerate. That is the tell.

*Reload check.* Run `scripts/reload_check.py` yourself against their registry. It is the
single most predictive check for whether the project will work in the final week.

**Common situations**

| Situation | Response |
|---|---|
| Lineage tags on the run instead of the registered version | Half credit. Explain the difference; it matters at promotion time |
| Justification names only the metric | Zero on that item, regardless of quality elsewhere |
| Study run locally, no managed job | Incomplete. CLO2 depends on this working |

---

## Lab 3 — Serving and rollback

**Judgement items**

*Was the latency target set before measuring?* Check the commit history: the target should
appear in `loadtest/k6.js` in a commit that predates the results in `reports/lab3-load.md`.
A target committed alongside the results was chosen to be met.

*Mean instead of percentiles.* The commonest failure. If they report a flattering average
and no p99, the lab is incomplete, however good the service is.

*Rollback evidence.* Timestamps must show traffic actually moving. A description of a
rollback is not a rollback. Ask for the metric that revealed the degradation — if they
looked at which variant was which, they did not detect anything.

*Health versus readiness.* Cheap to check, and a good verbal question during the demo: what
happens if readiness returns 200 while the model is still loading?

---

## Lab 4 — CI/CD, observability, drift

**Judgement items**

*The blocked commit.* Required artifact. A green pipeline proves nothing about whether the
tests work. Look for the failing run and the named test.

*Threshold justification.* PSI thresholds of 0.10 and 0.25 come from credit scoring, where
features are stable and volumes are enormous. A student who cites them without asking
whether their problem resembles credit scoring has copied, not reasoned. Accept any
defended number; reject an undefended default.

*The post-mortem, lines 3 and 4.* Retraining is not automatically correct. If the injected
fault was a schema change or upstream breakage, retraining on corrupted data destroys the
last good model. Students who reach for "retrain" reflexively should be pushed on it in the
debrief — anonymously, since roughly half the cohort does it.

*Which statistic caught which fault.* Worth asking directly. In the reference setup,
`--mode scale` leaves the mean at 79.58 and unchanged, yet PSI reports 0.274 while KS only
reaches 0.13. `--mode mix` — the realistic one — often stays below threshold entirely. A
student who has run all three modes and noticed this understands drift detection better
than one whose alert simply fired.

---

## Lab 5 — Cloud migration, portability, cost

*Session 5 is officially 'Operating LLM systems and defending the bill'. The LLM-operations half
is not yet written; see the content-gap note on the Session Detail sheet.*

**Judgement items**

*Is the gate real?* Try to make it fail. `scripts/evaluation_gate.py --incumbent 0.90`
against a weaker candidate must exit non-zero and must stop registration. A pipeline that
registers unconditionally has no gate, whatever the YAML says.

*What broke when they removed a permission?* This is the assessed part of Task 2, not the
permissions table. Anyone can write a table.

*The portability verdict.* Task 4 asks whether the abstraction was worth building. **A
well-argued "no" earns full marks.** Deliberate lock-in is a legitimate engineering choice.
Reject only unargued answers in either direction.

*Cost gap.* Required within 20%. Ask what caused the gap before accepting the number — the
usual answers are the meter running during debugging, storage and egress omitted from the
estimate, or an endpoint left warm overnight. Any of those, stated plainly, is a pass.

*Teardown screenshot.* Required. Then check yourself a week later; asynchronous deletion
means a clean script output and a live resource can coexist.

---

## Time budget

Roughly 15 minutes per student per lab: 5 for the script, 10 for judgement. For 40 students
across four labs that is about 40 hours, so distribute it across the term rather than
letting it pile up before final week.
