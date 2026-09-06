# Class announcement — cloud account access

Send to the whole cohort as soon as the billing decision is made, and **before** Session 1.
Fill the bracketed block; everything else stands as written.

No student names or addresses in this file — it is a template, and this repository is public.

**Why this goes to everyone.** "You do not have access to Google Cloud Platform" on a
university address is a Workspace tenant setting, not a student mistake. Every student who
follows the guide with their university email hits it. One student asking means the rest are
stuck and have not written in yet.

---

**Subject:** ITCS355 — use your personal Google account, and what to do this weekend

---

Hello everyone,

A few of you have hit the same wall setting up Week 0, so here is one message for the whole
class.

## Your university email will not work for Google Cloud

If you signed in with your `@student.mahidol.ac.th` address and saw **"You do not have access
to Google Cloud Platform"**, nothing is wrong with your account and there is nothing for you to
fix. Google Cloud is not enabled for student accounts in the university's Workspace tenant.

**Use a personal Google account instead.** Create your project named `itcs355-<studentid>` —
please keep that naming, it is how I find your work.

## Billing

[FILL: one of —
 • "The faculty billing account is being attached to your projects. Send me your project ID and
    I will confirm when it is active."
 • "Please enable the Google Cloud free trial when you create the project. It gives $300 of
    credit for 90 days, which is far more than this course needs."
 • "We are using Azure for this course instead. $100 of credit, no credit card required, and it
    verifies with your university email. A setup guide follows."]

If you cannot get billing sorted, tell me. Do not spend a weekend fighting it, and do not put a
personal credit card at risk for a course exercise.

## What to do this weekend regardless

**Lab 1's graded command deliberately needs no cloud account at all.** This is not a fallback,
it is the design — a grader has to be able to reproduce your work with Docker and nothing else
from your setup. So start here, whatever your billing situation:

```bash
make setup
make data
make test
make portability-audit
make reproduce
make verify
```

`make reproduce` is the single command your work is judged by. Getting it working is most of
Lab 1, and none of it waits on me.

Then run this and post the output in [course channel]:

```bash
make cloud-check
```

It will pass even without billing — it checks your CLI, your credentials and Docker, not your
bucket. Post it even if lines say FAIL. That is what it is for: I would rather see thirty
imperfect outputs on Sunday than debug them one at a time on Monday morning.

## What actually waits for billing

Creating the storage bucket, creating the Artifact Registry repository, `make image-push`, and
`dvc push`. Nothing else. You will not need them in the first session.

## One rule, permanently

**Never send me — or anyone — your account password, a service-account key, or an API key.**
Not in chat, not in email, not in a screenshot. I will never ask for one. Everything I need to
help you is in the output of `make cloud-check`, which contains no secrets.

Bring your blockers to Monday. Setup problems are a normal part of this subject, not a sign you
are behind.

See you then.

[instructor name]
