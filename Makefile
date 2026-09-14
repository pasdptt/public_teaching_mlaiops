# ITCS355 Lab 1
# `make reproduce` is the one command a grader runs. Keep it working.

SHELL := /bin/bash
IMAGE ?= itcs355-lab1
TAG   ?= $(shell git rev-parse --short HEAD 2>/dev/null || echo dev)
PLATFORM ?= linux/amd64
SEED ?= 20260101
LAB ?= 3

.PHONY: help setup cloud-check data test portability-audit train train-remote image image-push reproduce verify clean teardown \
        tune compare register lineage-check reload-check serve serve-image serve-image-push deploy smoke loadtest drift inject-drift pipeline cost swap-check llm-eval llm-gate

help:
	@grep -E "^[a-zA-Z_-]+:.*?## .*$$" $(MAKEFILE_LIST) | awk -F":.*?## " "{printf \"  %-20s %s\\n\", \$$1, \$$2}"

setup: ## Install dependencies and print environment status
	python -m pip install --upgrade pip
	pip install -r requirements.txt
	@echo "environment ok"

cloud-check: ## Resolve the eight capability slots
	python scripts/cloud_check.py

data: ## Generate the default dataset (deterministic)
	@if [ -f data/raw/sensors.csv ]; then \
		echo "data/raw/sensors.csv already exists"; \
	elif command -v python3 >/dev/null 2>&1 && python3 -c "import pandas, numpy" 2>/dev/null; then \
		python3 scripts/make_dataset.py --seed $(SEED); \
	elif command -v python >/dev/null 2>&1 && python -c "import pandas, numpy" 2>/dev/null; then \
		python scripts/make_dataset.py --seed $(SEED); \
	else \
		echo "Local Python missing numpy/pandas. Generating data inside Docker..."; \
		docker run --rm -v "$$PWD:/app" -w /app python:3.11-slim bash -c "pip install --quiet numpy pandas && python scripts/make_dataset.py --seed $(SEED)"; \
	fi

test: ## Run data contract and split property tests
	pytest -q tests/

portability-audit: ## Fail if provider strings leak into src/
	python scripts/portability_audit.py

train: ## Train locally, outside the container
	python -m src.train --seed $(SEED) --metrics-out reports/metrics.json

image: ## Build the training image for linux/amd64
	docker buildx build --platform $(PLATFORM) -t $(IMAGE):$(TAG) --load .

image-push: image ## Push to CONTAINER_REGISTRY via your adapter
	python -c "from src import config; from cloudlayer.factory import get_adapter; \
	print(get_adapter(config.load()).push_image(\"$(IMAGE):$(TAG)\"))"

reproduce: data image ## THE ONE COMMAND. Grader runs this.
	@mkdir -p reports && (chmod 777 reports 2>/dev/null || true)
	docker run --rm \
	  -v "$$PWD/data:/app/data:ro" \
	  -v "$$PWD/reports:/app/reports" \
	  -e MLFLOW_TRACKING_URI=sqlite:////app/reports/mlflow.db \
	  -e GIT_COMMIT=$(shell git rev-parse HEAD 2>/dev/null || echo unknown) \
	  $(IMAGE):$(TAG) --seed $(SEED) --metrics-out /app/reports/metrics.json

verify: ## Check the produced metric against the README claim
	python scripts/verify_metric.py

teardown: ## Delete every resource tagged course=itcs355 for this lab
	python -c "from src import config; from cloudlayer.factory import get_adapter; \
	cfg=config.load(); print(get_adapter(cfg).teardown(cfg.tags($(LAB))))"

clean: ## Remove local artifacts
	rm -rf mlruns mlartifacts mlflow.db reports/metrics.json .pytest_cache

# --- Lab 2 -------------------------------------------------------------------
train-remote: image ## Submit training to managed cloud compute (Vertex AI)
	python -c "from src import config; from cloudlayer.factory import get_adapter; \
	cfg = config.load(); adapter = get_adapter(cfg); \
	adapter.upload('data/raw/sensors.csv', 'data/raw/sensors.csv'); \
	img = adapter.push_image('$(IMAGE):$(TAG)'); \
	job_id = adapter.submit_training(img, {'seed': $(SEED)}); \
	print(f'Submitted training job: {job_id}'); \
	res = adapter.wait_training(job_id); \
	print('Job result:', res)"

tune: ## Budgeted hyperparameter study (>=12 trials)
	python -m src.tune --trials 12 --budget-thb 150

compare: ## Rank runs by metric and by cost per point
	python scripts/compare_runs.py --experiment itcs355-lab2

register: ## Register the best model from the study with lineage tags and promote to Staging
	python scripts/register_model.py

lineage-check: ## Verify the 8 lineage fields on the registered model
	python scripts/lineage_check.py --version $(if $(VERSION),$(VERSION),1)

reload-check: ## Load the registered model by version and score rows
	python scripts/reload_check.py $(if $(MODEL_REGISTRY_NAME),--name $(MODEL_REGISTRY_NAME)) --version $(VERSION)

# --- Lab 3 -------------------------------------------------------------------
serve: ## Run the inference service locally on :8080
	python scripts/export_model.py --out reports/model.joblib
	MODEL_PATH=reports/model.joblib MODEL_VERSION=local uvicorn service.app:app --port 8080

serve-image: ## Build the serving image
	docker buildx build --platform $(PLATFORM) -f service/Dockerfile.serve -t itcs355-serve:$(TAG) --load .

serve-image-push: serve-image ## Push the serving image to CONTAINER_REGISTRY via your adapter
	python -c "from src import config; from cloudlayer.factory import get_adapter; \
	print(get_adapter(config.load()).push_image('itcs355-serve:$(TAG)'))"

deploy: ## Deploy inference container to managed cloud endpoint (Vertex AI)
	python -c "from src import config; from cloudlayer.factory import get_adapter; \
	cfg = config.load(); adapter = get_adapter(cfg); \
	model_ref = '$(if $(MODEL_REF),$(MODEL_REF),$(if $(VERSION),$(VERSION),$(TAG)))'; \
	endpoint = '$(if $(ENDPOINT),$(ENDPOINT),itcs355-serve)'; \
	instance = '$(if $(INSTANCE),$(INSTANCE),n1-standard-2)'; \
	res = adapter.deploy(model_ref, endpoint, instance); \
	print(f'Deployed {model_ref} to endpoint {endpoint}: {res}')"

smoke: ## Smoke test the deployed endpoint with three known payloads
	python scripts/smoke_test.py --endpoint $(if $(ENDPOINT),$(ENDPOINT),itcs355-serve)

TARGET ?= https://asia-southeast1-aiplatform.googleapis.com/v1/projects/itcs355-6688249/locations/asia-southeast1/endpoints/1254122753850605568:rawPredict
DURATION ?= 30s

loadtest: ## Load test at three concurrency levels
	@for vus in 1 10 50; do \
	  echo "=== $$vus VUs ==="; \
	  k6 run -e TARGET=$(TARGET) -e TOKEN=$$(gcloud auth print-access-token 2>/dev/null) -e DURATION=$(DURATION) -e VUS=$$vus loadtest/k6.js || true; \
	done

# --- Lab 4 -------------------------------------------------------------------
inject-drift: ## Shift a feature's distribution on purpose
	python scripts/inject_drift.py --feature temp_c --mode shift --magnitude 6

drift: ## Score drift against the reference window
	python -m monitoring.drift --current data/current.csv

# --- Lab 5 -------------------------------------------------------------------
pipeline: ## Compile pipeline/pipeline.yaml for your provider
	python -c "from cloudlayer.pipelines import compile_for; from src import config; \
	compile_for(config.load().provider)"

llm-eval: ## Run the LLM golden set against recorded responses (offline, free)
	python scripts/llm_eval.py --out reports/llm_eval-baseline.json

llm-gate: ## Prove the gate fails on a degraded set — expected to exit non-zero
	python scripts/llm_eval.py --out reports/llm_eval-baseline.json >/dev/null
	python scripts/llm_eval.py --responses evals/fixtures/triage-regressed.jsonl \
	  --out reports/llm_eval.json --baseline reports/llm_eval-baseline.json

cost: ## Build the cost report
	python scripts/cost_report.py --estimate $(EST) --actual $(ACT) --rps $(RPS) --instance $(INSTANCE)

swap-check: ## Prove the portability seam against a second provider
	python scripts/portability_swap_check.py --second-provider $(SECOND)
