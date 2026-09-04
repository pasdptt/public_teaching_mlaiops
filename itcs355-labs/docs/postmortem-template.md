# Post-mortem — <incident title>

Five lines. Lab 4 grades lines 3 and 4 hardest.

**What fired:**
<the alert, the metric, the threshold crossed, the timestamp>

**True cause:**
<what was actually happening. Distinguish: data drift, concept drift, or a broken pipeline.
They look identical on a dashboard and demand different responses.>

**Retrain, roll back, or no action — and why:**
<"retrain" is not automatically correct. If the cause is a broken upstream pipeline,
retraining on corrupted data makes things permanently worse and destroys your last good
model. Say what you would do and what evidence would change your mind.>

**What this would have cost if unnoticed for a week:**
<in predictions, in money, or in whatever the business actually cares about. An estimate
with stated assumptions beats a precise-looking number with none.>

**How to prevent or detect it faster:**
<one concrete change. A new test, a tighter threshold, an upstream contract, a dashboard
panel. "Be more careful" is not a change.>
