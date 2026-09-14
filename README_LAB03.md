# ITCS355 Lab 3 — Serving, Load Testing, and Rollback

> **Student ID:** 6688249  
> **Cloud Provider:** Google Cloud Platform (GCP) · Vertex AI Endpoints · Artifact Registry · Cloud Storage  
> **Course:** ITCS355 Machine Learning Operation and Deployment

---

## 1. Quick Verification Commands

```bash
# 1. Run local inference service
make serve

# 2. Build and push container to Google Artifact Registry
make serve-image
make serve-image-push

# 3. Deploy to Vertex AI managed endpoint (machine type: n1-standard-2)
make deploy

# 4. Run smoke test against live endpoint (3 known telemetry payloads)
make smoke

# 5. Run honest load test (concurrency 1, 10, 50 VUs)
make loadtest

# 6. Delete all endpoints, deployed models, and compute (Prevent hourly billing!)
make teardown

# 7. Confirm teardown succeeded
python scripts/teardown_verify.py --lab 3
```

---

## 2. Task 1 — Inference Service Implementation

The inference service is implemented in [`service/app.py`](service/app.py) with schemas in [`service/schemas.py`](service/schemas.py).

### Endpoints
| Route | Purpose | Implementation Detail |
|---|---|---|
| `POST /predict` | Single telemetry prediction | Validates against `PredictRequest`, returns `probability` and `model_version`. |
| `POST /predict/batch` | Batch predictions ($\le 100$ rows) | Validates against `BatchRequest`, vector scores rows simultaneously in NumPy. |
| `GET /health` | Liveness probe | Returns 200 `{"status": "alive"}` as soon as Uvicorn process starts. |
| `GET /ready` | Readiness probe | Returns 200 `{"status": "ready"}` only after the model is loaded into memory; returns 503 while loading. |

### Architectural Requirements Met
- **Pydantic Validation:** Strict boundary validation with `extra = "forbid"` rejects unknown or out-of-range fields with HTTP 422.
- **Loaded Once at Startup:** The model is initialized inside FastAPI's `@asynccontextmanager` `lifespan`, never per-request.
- **Structured JSON Logs:** Middleware attaches unique `x-request-id`, measures execution latency in ms, and outputs JSON logs.
- **Provider Portability:** Zero provider SDK imports in `service/` or `src/` (`make portability-audit` passes cleanly).

---

## 3. Task 2 — Managed Deployment (Vertex AI Endpoint)

Implemented in [`cloudlayer/gcp.py`](cloudlayer/gcp.py):
- `deploy(model_ref, endpoint, instance)`:
  - Retrieves or creates an `aiplatform.Endpoint` tagged with `cfg.tags(3)`.
  - Configures an `aiplatform.Model` with container routes:
    - `serving_container_predict_route="/predict"`
    - `serving_container_health_route="/health"`
    - `serving_container_ports=[8080]`
  - Deploys the container to the endpoint on machine type `n1-standard-2`.
- `invoke(endpoint, payload)`:
  - Uses `ep.raw_predict()` to send raw JSON payloads directly to `/predict` without protobuf schema conflicts.

### Smoke Test Output (`make smoke`)
```text
Running smoke test against: itcs355-serve

[1/3] Testing payload: Normal operation
     Result: {'probability': 0.00985557486757818, 'model_version': '93f7615'}
[2/3] Testing payload: Elevated warning
     Result: {'probability': 0.7373581492587219, 'model_version': '93f7615'}
[3/3] Testing payload: High risk
     Result: {'probability': 0.81607021826213, 'model_version': '93f7615'}

PASS  all 3 smoke payloads scored successfully
```

---

## 4. Task 3 — Load Testing (`k6`) & Percentile Report

Full benchmark report documented in [`reports/lab3-load.md`](reports/lab3-load.md).

### Pre-declared SLA Latency Target
* Target declared in [`loadtest/k6.js`](loadtest/k6.js): `predict_latency_ms: p(95) < 150ms`.
* **Committed to Git prior to measuring:** Git commit `2f2d4d6` explicitly predates results commit `8035e11`.

### Concurrency Benchmark Summary

| Concurrency (VUs) | Throughput (RPS) | p50 (Median) | p90 | p95 | p99 | Failure Rate |
|---|---|---|---|---|---|---|
| **1 VU** | 2.21 rps | 454.99 ms | 462.10 ms | 485.40 ms | 512.80 ms | 0.00% |
| **10 VUs** | **15.28 rps** | 622.73 ms | 913.22 ms | **934.48 ms** | **1,286.86 ms** | 0.00% |
| **50 VUs** | 11.33 rps | 3,558.94 ms | 6,337.81 ms | 6,822.09 ms | 7,087.40 ms | 0.00% |

* **Cold-Start Latency:** **13.37 seconds** (`13,368.92 ms`) on initial instance startup.
* **Breaking Point:** Concurrency **VU = 3** over international WAN (due to baseline transit RTT floor) and **VU = 18** under local network conditions.

### Three Variable Variations
1. **Batch Size:** 100 rows scored sequentially took **41.05s**; 1 batch of 100 rows took **0.46s** (**89.2x end-to-end speedup**).
2. **Payload Size:** Serialization overhead is negligible (<0.05 ms) for $\le 100$ rows, scaling linearly to 5.08 ms at 10,000 rows (1.5 MB GCP request limit).
3. **Instance Size:** Stepping up to `n1-standard-4` doubles machine cost (+$0.095/hr) while scaling throughput to ~28–30 rps and reducing 10 VU p95 latency from 934ms to ~380ms (-59%).

---

## 5. Task 4 — Canary Deployment and Rollback

### Setup & Evidence
- **Traffic Split:** Configured 90% traffic to production model V1 (`4280453742513356800`) and 10% to degraded model V2 (`6229386481257938944`).
- **Metric-Driven Detection:** Out of 40 requests, 36 succeeded (90.0%) and 4 failed with 503 errors (10.0%). Detected purely from the failure rate threshold violation in **5.15 seconds** from first fault (**19.84 seconds** total).
- **Rollback:** Restored 100% traffic to V1 (`gcloud ai endpoints update --traffic-split=4280453742513356800=100`).
- **Timestamped Evidence:** Transition verified from `2026-09-14T09:34:25Z` (canary start) to `2026-09-14T09:35:19Z` (100% steady state recovery).

### Rollback Analysis (5 Questions)
1. **Metric that revealed degradation:** HTTP failure rate threshold violation (`predict_failures > 0.01`).
2. **Detection duration:** 5.15s from first fault / 19.84s total from traffic dispatch.
3. **Acceleration factor:** Synthetic readiness probing (`GET /ready`) would have detected failure in 0.5s prior to client routing.
4. **50/50 Split Comparison:** 50/50 split triggers detection 5x faster (~1.1s) but impacts 5x more live client queries.
5. **Architectural takeaway:** 90/10 canary bounds the customer blast radius while automated metrics govern rollback.

---

## 6. Task 5 — Cost per 1,000 Predictions

$$\text{Cost per 1,000 predictions} = \frac{\$0.0950 / \text{hr}}{55,008 \times 0.30 \text{ req/hr}} \times 1,000 = \mathbf{\$0.00576 \text{ USD}} \quad (\approx 0.201 \text{ THB})$$

- **Instance Cost:** `n1-standard-2` in `asia-southeast1` costs **$0.0950 USD / hour** (~3.32 THB/hr).
- **Utilisation Assumption:** Defended **30% average daily capacity utilization** reflecting diurnal business cycles.
- **Break-even Volume:** Below **10,000 requests / day** (or $\le 0.5$ req/s), batch inference on ephemeral compute is cheaper than paying the minimum $2.28/day ($68.40/month) floor to keep a dedicated endpoint warm.

---

## 7. Teardown Confirmation

```bash
$ make teardown
python -c "from src import config; from cloudlayer.factory import get_adapter; \
	cfg=config.load(); print(get_adapter(cfg).teardown(cfg.tags(3)))"
Undeploying models from endpoint itcs355-serve...
Deleting endpoint itcs355-serve...
Deleting model itcs355-serve-model...
['projects/821808260643/locations/asia-southeast1/endpoints/1254122753850605568', ...]

$ python scripts/teardown_verify.py --lab 3
searching for resources tagged {'course': 'itcs355', 'student': 'itcs355-6688249', 'lab': '3'}
PASS  nothing found under these tags
```

---

## 8. Mechanical Grading Results

```bash
$ bash instructor/grade_lab.sh 3 $(git config --get remote.origin.url)

Common
  [PASS] no credentials in history
  [PASS] cloud.env not committed
  [PASS] portability audit clean
  [PASS] data tests pass

Lab 3 — serving and rollback
  [PASS] service tests pass
  [PASS] health and ready differ
  [PASS] load test committed
  [PASS] load report exists
  [PASS] percentiles reported
  [PASS] latency target stated
  [ ?  ] was the target committed BEFORE the results? check git log on loadtest/
  [ ?  ] rollback evidence — do timestamps show traffic actually moving?

mechanical: 10 passed, 0 failed
```
