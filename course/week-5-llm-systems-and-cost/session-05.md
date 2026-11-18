---
marp: true
theme: default
paginate: true
title: ITCS355 Session 5 — Operating LLM systems and defending the bill
---

<!--
Teaching deck for Session 5. Two halves: managed platform + cost, then LLM operations.
Run `make llm-gate` live — it fails on purpose and the four regressions it catches are
the lesson. The architecture clinic at the end is not optional; teams that skip it submit
incomplete monitoring.
-->

# Session 5
## Operating LLM systems and defending the bill

**CLO2 · CLO3** · 3 hours · Take-home: Lab 5 (~7 hours, two parts)

---

## Today

| Time | What |
|---|---|
| 0:00–0:10 | **Drill 4** — 2 questions, 3 marks |
| 0:10–0:35 | Lab 4 debrief |
| 0:35–1:25 | Managed platforms, identity, and the shape of a cloud bill |
| 1:25–1:50 | **`make llm-gate` on screen** — it fails, and we read why |
| 1:50–2:15 | Cost teardown of a running service |
| 2:15–3:00 | Capstone architecture clinic — 15 min per team |

---

## Every managed platform sells the same eleven operations

Different names, same catalogue.

| Capability | AWS | Azure | GCP |
|---|---|---|---|
| Object storage | S3 | Blob Storage | Cloud Storage |
| Registry | ECR | ACR | Artifact Registry |
| Managed training | SageMaker | Azure ML job | Vertex AI |
| Online endpoint | SageMaker Endpoint | Managed Online Endpoint | Vertex Endpoint |
| Managed LLM | Bedrock | Azure OpenAI | Vertex generative |

You wrote one adapter against `cloudlayer/base.py`. That is why you can read this table and not care much which column you are in.

**Knowing the category beats knowing a product.**

---

## Least privilege, and the error you will actually see

Your first managed job will fail with a permissions error. Everyone's does.

That is not a detour — it is the lesson. Plan for it:

- The identity that runs a **scheduled** job is not the one at your terminal
- Owning a subscription is not the same as being allowed to read data inside it
- Grant the narrow role, watch what breaks, then grant the next one

**Lab 5 asks you to remove a permission and report what broke.** That is the only way anyone learns what a role actually does.

---

## An LLM step has no metric to watch

A classifier degrades and your ROC AUC moves. **A language model degrades and nothing moves.**

Change the prompt. Change the model version — your provider may do that without telling you. Change the temperature. Every test passes, the dashboard is green, and the answers are quietly worse.

So you build the thing that plays the role of a metric: **a golden set** — cases you have decided the answer to, with checks that can fail.

| Kind | What it asserts |
|---|---|
| **Grounding** | the answer uses only facts in the input |
| **Guardrail** | the model refuses what it must refuse |
| **Injection** | instructions in a data field stay data |
| **Insufficient input** | "I cannot answer this" is the right answer |

---

## The gate that fails on purpose

```bash
make llm-gate
```

```
[FAIL] triage-004   expected NOT to match /\b[A-Z]{2,3}-\d{3,6}\b/ but found 'PN-4471'
[FAIL] triage-007   expected decision='no_action', got 'schedule_urgent'

GATE FAILED — 4 regression(s): triage-003, triage-004, triage-005, triage-007
```

| Case | What degraded |
|---|---|
| `003` | a borderline probability decided instead of escalated |
| `004` | a part number **that appears nowhere in the input** |
| `005` | a sensor reading it was never given |
| `007` | an instruction hidden in an operator note, obeyed |

---

## The question for the room

**Which of those four would a pass-rate threshold have caught?**

<!--
Let them answer before you do. The answer is NONE of them, if the other cases improved
enough. Wait for someone to say "none" rather than telling them.
-->

None — if the other cases improved enough.

That is why the gate compares **per case**: anything that passed before and fails now is a regression, whatever the average did.

Averages are extremely good at hiding the one case you care about.

---

## Three levers on a token bill

An endpoint costs the same serving 10 requests or 10,000. **An LLM step costs a linear function of how verbose you let it be.**

| | Lever | Why in this order |
|---|---|---|
| 1 | **Cap output length** | output costs 3–5× input; one line of config; cannot change correctness, only length |
| 2 | **Prompt caching** | a hit bills at ~10%, but a **write costs more** than a normal token — caching a prefix that changes every request pays extra for nothing |
| 3 | **Smaller model** | often 10–20× cheaper; whether it is good enough is an *evaluation* question, so run the gate before you switch |

Token counts come from the provider's usage fields. **Never estimate them by counting words** — an estimated token count in a cost report is a fabricated number.

---

## Defending the bill

The deliverable is not the spreadsheet. It is one paragraph, for someone who controls budget and does not write code:

> What it costs per 1,000 requests. What you changed. What it costs now. **What you gave up.**

The arithmetic is the easy part. Being able to say what you traded away, without hiding it, is the part that makes you trusted with a budget.

A cheaper system that answers worse is not an optimisation — and the gate is how you prove you did not do that.

---

## Cost teardown — live

```bash
make cost            # the report
make teardown        # and then actually delete it
```

We will take one running service and account for it, line by line, against the actual bill.

**There is always a gap.** The usual causes: the meter ran while you were debugging, something untagged, or a resource nobody remembers creating.

Finding the gap is the exercise. Reporting a number that matches perfectly usually means you did not check.

---

## Capstone architecture clinic — 45 minutes

15 minutes per team. Bring your pipeline, serving, and monitoring design.

Three questions I will ask every team:

1. **What breaks first** under 10× traffic, and how would you know?
2. Where is your **deliberate failure**, and can you demonstrate it on demand?
3. What is your **cost per 1,000 predictions**, and where did that number come from?

<!--
Teams that have not had their architecture questioned before the final week reliably
submit incomplete monitoring. This clinic is the highest-leverage 45 minutes for capstone
marks. Do not let it be cut for the cost teardown.
-->

---

## Lab 5 — handover

**[`lab-05-cloud-mlops-and-cost.md`](lab-05-cloud-mlops-and-cost.md)** · 8 marks · due before final week

**Part A — defending the bill.** Managed platform, least privilege, portability proof, cost report.
**Part B — operating an LLM step.** Your own golden set of 10+ cases, a baseline, a gate run that fails, and three token-cost figures.

Fails when: your golden set contains **no case that has ever failed**, or your token counts were estimated rather than read from the provider.

`make teardown` — and check the bill next week, because deletion is asynchronous on all three providers.

---

## Before the final week

- [ ] Lab 5 pushed, both parts
- [ ] Capstone repository complete — the five rubric criteria are marked from what is in it
- [ ] Presentation ready: 8 minutes plus 5 of questions
- [ ] Drill 5 is held in the final week

**Expect unexpected input during your demo.** Handling it gracefully scores. Crashing scores partial credit if your logging makes the cause obvious within a minute.

There is no final examination. This is the last content session.
