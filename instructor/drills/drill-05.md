# Drill 5 — Operating LLM systems and defending the bill

**3 marks · 15 minutes · start of the final week · CLO2 1, CLO3 2**

Covers Session 5 and Lab 5, both parts. Closed-book except for the student's own repository,
which they will need for Section B.

Section B must be prepared per student from their submitted Lab 5 before the session — see
[`README.md`](README.md). The bracketed fields below are filled in from their report.

---

## Section A — concepts (1.5 marks)

### A1 · 0.5 · CLO2

> Last week your evaluation gate reported 7 of 8 cases passing. Today it reports 8 of 8. A
> teammate concludes the system improved and ships it.
>
> Describe a situation in which that conclusion is wrong, and name the check that catches it.

**Model answer.** A case that passed last week now fails, while two that were failing now
pass. The rate rose from 7/8 to 8/8 and a real regression is hidden inside the average. The
check is a **per-case comparison against the baseline** — any case that passed before and
fails now is a regression, whatever the rate did.

**Full marks** require naming per-case comparison. "Run more tests" or "check the failures"
does not earn it — the point is that the aggregate is the wrong instrument, not that they
should look harder.

### A2 · 0.5 · CLO3

> You cap `max_output_tokens` and your bill halves. What do you run before shipping that
> change, and what result would make you revert it?

**Model answer.** Run the golden-set gate. Revert if any case regresses — typically the
answer is now truncated mid-JSON so `json_field` checks fail, or a refusal loses the
reasoning that made it a refusal. A cheaper system that answers worse is not an optimisation.

**Full marks** require both halves: the gate, *and* a concrete failure that would justify
reverting. "Check it still works" is half an answer.

### A3 · 0.5 · CLO3

> A team enables prompt caching on a prefix that includes the current timestamp. Predict what
> happens to the bill, and explain why.

**Model answer.** The bill goes **up**. The prefix differs on every request, so every request
is a cache miss; a cache *write* is billed at more than a normal input token (~1.25×), so they
now pay a surcharge on every request and never collect a hit. Their hit rate is zero, far
below the break-even rate.

**Full marks** require the direction (up) *and* the write surcharge as the reason. "No
benefit" scores nothing — the trap is that it actively costs more, and the sign of the answer
is the whole question.

---

## Section B — evidence (1.5 marks)

From the student's own submission. They may open their repository.

### B1 · 0.5 · CLO2

> Read out one case from your golden set that has **ever failed**. What was the failure, and
> what did you change?

**Marking.** Full marks for a real case, a real failure, and a real change. **Zero if the
answer is that no case ever failed** — a golden set that has never failed has not been
tested, which is stated in the handout's acceptance criteria. Expect a few of these; it is
the most instructive failure in the lab and worth naming in the debrief, anonymously.

### B2 · 0.5 · CLO3

> Your cost report states **[X]** THB per 1,000 requests. Where exactly did the token counts
> behind that number come from?

**Marking.** Full marks only for naming the provider's own usage field from the response.
**Zero for any estimate** — counting words, characters/4, a tokeniser library run locally
rather than the returned usage. The handout says an estimated token count in a cost report is
a fabricated number, and this question is where that is enforced.

### B3 · 0.5 · CLO3

> In Task 2 you removed **[permission]** and something broke. What broke, and what did the
> error actually say?

**Marking.** Full marks for the failure and the substance of the message. A student who did
the task remembers this vividly; a student who wrote the report from the documentation cannot
produce the error text. Accept paraphrase, not "it said permission denied" alone — ask which
operation was denied.

---

## Marking summary

| | Topic | CLO | Marks |
|---|---|---|---|
| A1 | Per-case regression versus pass rate | CLO2 | 0.5 |
| A2 | Output caps validated by the gate | CLO3 | 0.5 |
| A3 | Prompt-cache write surcharge | CLO3 | 0.5 |
| B1 | A golden-set case that failed | CLO2 | 0.5 |
| B2 | Provenance of the token counts | CLO3 | 0.5 |
| B3 | Least privilege, observed | CLO3 | 0.5 |
| | **Total** | **CLO2 1, CLO3 2** | **3** |

Matches the Drill 5 row on the *Assessment Blueprint* sheet.

## Wrong answers worth expecting

| Answer | Why it scores nothing |
|---|---|
| A1: "Add more test cases" | More cases do not fix an aggregate that hides a regression |
| A2: "Nothing — it's cheaper and still works" | The claim "still works" is exactly what the gate exists to establish |
| A3: "No benefit, so no change to the bill" | Wrong sign. Cache writes cost more than normal tokens |
| B1: "All my cases passed" | Zero. Restate the acceptance criterion in the debrief |
| B2: "I estimated from the word count" | Zero, and it invalidates their reported cost figure |

## Running it

Fifteen minutes, on paper or in the LMS, at 0:00 before the debrief. Mark during the debrief
that follows — six short answers per student is about 3 minutes each.

Do not read A3 aloud before students have written A2; A2's answer hints at A3's.
