# Welcome email — send before Session 1

Draft for the instructor to send. Fill the bracketed fields, then paste into mail.
Reusable next term: the only date-specific parts are the bracketed ones.

**Send:** the Thursday or Friday before Session 1, not the weekend — students need a working
day to reach whoever administers their cloud project.

---

**Subject:** ITCS355 starts Monday — 90 minutes of setup to do first

---

Hello everyone,

Welcome to **ITCS355 Machine Learning Operation and Deployment**. We start on **Monday [date],
[time], [room]**.

This course is about the part that comes after the model works: getting it out of a notebook
and running it as a service other people depend on — reproducibly, with monitoring, and with a
bill someone has to justify. Five sessions, one repository that grows across the term, and a
capstone that is an extension of what you have already built rather than a separate effort.

Everything is here:
**https://github.com/pasdptt/public_teaching_mlaiops**

## Please do these three things before Monday

**1. Set up your machine and your cloud account — about 90 minutes.**
Follow `course/getting-started-gcp.md` in the repository. It takes you from an empty laptop to
a working setup, step by step, and it assumes you have only basic access to a Google Cloud
project.

You will install Python 3.11+, Docker, git and the gcloud CLI, then create a storage bucket and
an image repository, and finish by running two commands that check everything at once:

```
make setup
make cloud-check
```

**Start this today or tomorrow, not Sunday night.** The setup itself is short, but if your
Google Cloud project needs to be created for you, or billing needs attaching, that depends on
somebody else answering — and that is not something we can fix at 9am on Monday. If you hit a
wall you cannot get past, message me *before* the weekend and say exactly where you stopped.

**2. Post your `make cloud-check` output in [course channel].**
Every line should say PASS. If some do not, post it anyway — that is the whole point. We fix
blockers before Session 1 rather than spending the first session on them.

**3. Read one paper and bring one question — about 30 minutes.**
Sculley et al., *Hidden Technical Debt in Machine Learning Systems* (NeurIPS 2015). Nine pages.
It is the argument the whole course rests on. Bring one question you want answered.

## A few things worth knowing now

**There is no final examination.** Your marks come from the labs (40), the capstone system (30)
and its live demo (15), and a short drill at the start of each session (15).

**The labs are the largest single component.** There is one after every session, and they
compound — skipping Lab 1 makes Lab 3 impossible. They are marked met-or-not-met against
criteria printed in each handout, so you always know what passing looks like before you start.

**Model accuracy is not graded anywhere in this course.** A 0.71 AUC model with clean lineage,
a working rollback and an honest cost report scores better than a 0.94 model that only runs on
its author's laptop. This surprises people every year, so I am saying it in writing first.

**Cloud costs.** Target for the whole term is under 800 THB, and every lab ends with a teardown
step that we check. Set a budget alert during setup — the guide shows you where.

If anything above is unclear, or your cloud access is not sorted, tell me before Monday rather
than after.

See you on Monday.

Dr. Pasd Putthapipat
Asst. Prof. Dr. Thanapon Noraset
Faculty of ICT, Mahidol University
