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

**You may use either Google Cloud or Azure. Pick one and stay on it for the term.** The labs are
written provider-neutral, so your choice does not affect your marks — the grader only ever calls
the neutral interface.

| | Google Cloud | Azure |
|---|---|---|
| Getting credit | Free trial, **asks for a credit card** to verify identity | **Azure for Students — no credit card**, verified from your university email |
| Sign in with | A **personal** Google account | Your **university** email |
| Container registry cost | Bills for what you store — cheaper | Flat daily rate whether used or not |
| Guide | `course/getting-started-gcp.md` | `course/getting-started-azure.md` |

**If you have no credit card, or would rather not use one, take the Azure path.** That is exactly
what it is there for, and nobody should put a personal card behind a course exercise.

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
