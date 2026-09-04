#!/usr/bin/env bash
# ITCS355 Lab 1 — mechanical grading pass.
#
#   ./grade_lab1.sh <student-repo-url> [workdir]
#
# Runs the checks that need no judgement. What remains for you: the README trade-off
# answer, the quality of the five tracked runs, and whether the tolerance is honest
# given the variance the student's own runs show.
#
# Run this on a machine that is NOT the student's, ideally a different architecture
# than most of the cohort. That is the whole point of the lab.

set -uo pipefail

REPO="${1:?usage: grade_lab1.sh <repo-url> [workdir]}"
WORK="${2:-$(mktemp -d)}"
PASS=0; FAIL=0

check() {  # check <name> <command...>
  local name="$1"; shift
  if "$@" >/tmp/lab1_check.log 2>&1; then
    printf '  [PASS] %s\n' "$name"; PASS=$((PASS+1))
  else
    printf '  [FAIL] %s\n' "$name"; FAIL=$((FAIL+1))
    sed 's/^/         /' /tmp/lab1_check.log | tail -6
  fi
}

echo "ITCS355 Lab 1 grading — $REPO"
echo "workdir: $WORK"
echo

git clone --quiet "$REPO" "$WORK/repo" || { echo "cannot clone"; exit 1; }
cd "$WORK/repo" || exit 1

echo "1. Hygiene"
check "cloud.env not committed"        bash -c '! git log --all --name-only --pretty=format: | grep -qx "cloud.env"'
check "no credentials in history"      bash -c '! git log -p --all | grep -qiE "AKIA[0-9A-Z]{16}|BEGIN (RSA |EC )?PRIVATE KEY|password[[:space:]]*=[[:space:]]*[^ ]"'
check "README has a claim line"        grep -qiE "expected[[:space:]]+test_roc_auc[[:space:]]*[:=]" README.md
check "no REPLACE blocks remain"       bash -c '! grep -q "REPLACE" README.md'

echo
echo "2. Reproducibility"
check "dependencies carry hashes"      grep -q -- "--hash=sha256:" requirements.txt
check "base image pinned by digest"    grep -qE "^FROM .*@sha256:" Dockerfile
check "Dockerfile uses non-root"       grep -qE "^USER " Dockerfile
check "no credentials baked in image"  bash -c '! grep -qiE "^(ENV|ARG).*(SECRET|PASSWORD|KEY|TOKEN)" Dockerfile'

echo
echo "3. Code quality gates"
check "portability audit clean"        python scripts/portability_audit.py
check "data tests pass"                bash -c 'make data >/dev/null && make test'
check "leakage test present"           grep -q "def test_no_machine_leaks_across_splits" tests/test_data.py

echo
echo "4. The one command"
check "make reproduce succeeds"        make reproduce
check "metric matches the claim"       make verify

echo
echo "5. Cloud artifacts (manual confirmation needed)"
echo "  [ ? ] image present in the student's registry, digest-pinned"
echo "  [ ? ] dvc remote reachable: try 'dvc pull' with your own credentials"
echo "  [ ? ] five or more tracked runs, varying something meaningful"

echo
echo "mechanical: $PASS passed, $FAIL failed"
echo "still to judge by hand:"
echo "  - the reproducibility trade-off answer (is a real choice made and defended?)"
echo "  - is the stated tolerance honest against the variance in their own runs?"
echo "  - are the five runs a real study, or five seeds of the same configuration?"
