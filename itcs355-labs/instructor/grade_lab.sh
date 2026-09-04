#!/usr/bin/env bash
# ITCS355 — mechanical grading for Labs 2-5.
#
#   ./grade_lab.sh <lab-number> <student-repo-url> [workdir]
#
# Lab 1 has its own script. This one covers the checks that need no judgement; what
# remains is in instructor/RUBRIC-labs-2-to-5.md and is where the marks actually are.

set -uo pipefail

LAB="${1:?usage: grade_lab.sh <2|3|4|5> <repo-url> [workdir]}"
REPO="${2:?repo url required}"
WORK="${3:-$(mktemp -d)}"
PASS=0; FAIL=0

check() {
  local name="$1"; shift
  if "$@" >/tmp/lab_check.log 2>&1; then
    printf '  [PASS] %s\n' "$name"; PASS=$((PASS+1))
  else
    printf '  [FAIL] %s\n' "$name"; FAIL=$((FAIL+1))
    sed 's/^/         /' /tmp/lab_check.log | tail -5
  fi
}

manual() { printf '  [ ?  ] %s\n' "$1"; }

git clone --quiet "$REPO" "$WORK/repo" || { echo "cannot clone"; exit 1; }
cd "$WORK/repo" || exit 1
echo "ITCS355 Lab $LAB grading — $REPO"; echo

echo "Common"
check "no credentials in history"  bash -c '! git log -p --all | grep -qiE "AKIA[0-9A-Z]{16}|BEGIN (RSA |EC )?PRIVATE KEY"'
check "cloud.env not committed"    bash -c '! git log --all --name-only --pretty=format: | grep -qx "cloud.env"'
check "portability audit clean"    python scripts/portability_audit.py
check "data tests pass"            bash -c 'make data >/dev/null && pytest -q tests/test_data.py'
echo

case "$LAB" in
  2)
    echo "Lab 2 — tracking and registry"
    check "tune module present"        test -f src/tune.py
    check "12+ trials configured"      bash -c 'grep -qE "trials.*1[2-9]|trials.*[2-9][0-9]" Makefile src/tune.py'
    check "comparison report exists"   test -f reports/lab2-comparison.md
    check "justification written"      bash -c '! grep -q "TODO(Lab 2)" reports/lab2-comparison.md'
    check "cost logged per trial"      grep -q "cost_thb" src/tune.py
    manual "run scripts/reload_check.py against their registry — the most predictive check"
    manual "is the justification a real argument, or a restatement of the metric?"
    manual "did the budget actually bind, or did they run locally at zero cost?"
    ;;
  3)
    echo "Lab 3 — serving and rollback"
    check "service tests pass"         pytest -q tests/test_service.py
    check "health and ready differ"    bash -c 'grep -q "def health" service/app.py && grep -q "def ready" service/app.py'
    check "load test committed"        bash -c 'test -f loadtest/k6.js || test -f loadtest/locustfile.py'
    check "load report exists"         test -f reports/lab3-load.md
    check "percentiles reported"       bash -c 'grep -qi "p99" reports/lab3-load.md'
    check "latency target stated"      bash -c 'grep -qiE "p\(95\)<|p95.*target" loadtest/k6.js reports/lab3-load.md'
    manual "was the target committed BEFORE the results? check git log on loadtest/"
    manual "rollback evidence — do timestamps show traffic actually moving?"
    ;;
  4)
    echo "Lab 4 — CI/CD, observability, drift"
    check "behaviour tests pass"       pytest -q tests/test_model_behaviour.py
    check "CI workflow present"        test -f .github/workflows/ci.yml
    check "CD gated on CI"             grep -q "workflow_run" .github/workflows/cd.yml
    check "images tagged by SHA"       bash -c 'grep -q "github.sha" .github/workflows/ci.yml && ! grep -q ":latest" .github/workflows/ci.yml'
    check "2+ data contract tests"     bash -c '[ "$(grep -c "^def test_" tests/test_data.py)" -ge 2 ]'
    check "drift detector present"     test -f monitoring/drift.py
    check "threshold justified"        bash -c '! grep -q "TODO(Lab 4): state your threshold" monitoring/drift.py'
    check "SLO response filled in"     bash -c '! grep -q "TODO(Lab 4)" monitoring/slo.yaml'
    check "post-mortem written"        bash -c 'ls reports/*postmortem* >/dev/null 2>&1'
    manual "REQUIRED: evidence of the blocked bad commit — a failing CI run"
    manual "post-mortem lines 3 and 4 — is 'retrain' reflexive or reasoned?"
    ;;
  5)
    echo "Lab 5 — cloud MLOps, portability, cost"
    check "pipeline spec present"      test -f pipeline/pipeline.yaml
    check "gate is conditional"        grep -q "condition:" pipeline/pipeline.yaml
    check "gate rejects a weak model"  bash -c 'python -m src.train --metrics-out /tmp/m.json >/dev/null 2>&1; ! python scripts/evaluation_gate.py --metrics /tmp/m.json --incumbent 0.99'
    check "cost report exists"         test -f reports/lab5-cost.md
    check "cost report completed"      bash -c '! grep -q "TODO(Lab 5)" reports/lab5-cost.md'
    check "second adapter attempted"   bash -c 'grep -rqL "NotImplementedError" cloudlayer/aws.py cloudlayer/azure.py cloudlayer/gcp.py'
    manual "REQUIRED: teardown screenshot showing an empty resource list"
    manual "which permission did they remove, and what broke?"
    manual "portability verdict — a well-argued 'no' earns full marks"
    ;;
  *)
    echo "Unknown lab: $LAB"; exit 1;;
esac

echo
echo "mechanical: $PASS passed, $FAIL failed"
echo "items marked [ ? ] need you — see instructor/RUBRIC-labs-2-to-5.md"
