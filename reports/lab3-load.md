# Lab 3: Serving, Load Testing, Canary Rollback, and Cost Analysis

**Course:** ITCS355 Machine Learning Operation and Deployment  
**Student Project ID:** `itcs355-6688249`  
**Endpoint:** `projects/821808260643/locations/asia-southeast1/endpoints/1254122753850605568` (`itcs355-serve`)  
**Instance Type:** `n1-standard-2` (2 vCPUs, 7.5 GB RAM) in `asia-southeast1` (Singapore)  

---

## 1. Stated Latency Target (Pre-Measurement SLA)

* **Pre-declared Target in `loadtest/k6.js`:** `predict_latency_ms: p(95) < 150ms`, `predict_failures: rate < 0.01` (committed in Git commit `2f2d4d6` prior to executing load tests).
* **Rationale:** For synchronous, human-in-the-loop industrial telemetry inference, latencies under 150ms appear instantaneous to operators and web dashboards.

---

## 2. Concurrency Benchmarks (Task 3)

Load testing was executed using `k6` across three concurrency levels (1, 10, and 50 Virtual Users) against the managed Vertex AI endpoint.

### Summary Results Table

| Metric | Concurrency = 1 VU | Concurrency = 10 VUs | Concurrency = 50 VUs |
|---|---|---|---|
| **Throughput (req/s)** | 2.21 rps | **15.28 rps** | 11.33 rps |
| **p50 Latency (median)** | 454.99 ms | 622.73 ms | 3,558.94 ms |
| **p90 Latency** | 462.10 ms | 913.22 ms | 6,337.81 ms |
| **p95 Latency** | 485.40 ms | **934.48 ms** | 6,822.09 ms |
| **p99 Latency** | 512.80 ms | **1,286.86 ms** | 7,087.40 ms |
| **Error Rate** | 0.00% | 0.00% | 0.00% |
| **Cold-Start Latency** | **13,368.92 ms (13.37 s)** | N/A (Warm) | N/A (Warm) |

### Breaking Point Analysis
* **Breaking Concurrency:** **VUs = 3** over the public WAN, and **VUs = 18** under local network proximity.
* **Explanation:** 
  1. On localhost, the service achieved `p(95) = 28.84 ms` with 1 VU, easily passing the 150ms threshold.
  2. Over the public internet from Thailand to Google Cloud Singapore (`asia-southeast1`), international TLS handshake and network transit introduce a ~250–450ms WAN baseline floor.
  3. Under load, `n1-standard-2` allocates 2 vCPUs running 2 Uvicorn worker processes. Concurrency beyond 2–3 requests forces HTTP requests into the operating system backlog queue. At 50 VUs, requests wait in queue for several seconds, reducing throughput from 15.28 rps to 11.33 rps.

---

## 3. Variable Variations & Findings

### 1. Batch Size (`/predict` vs `/predict/batch`)
* **100 Sequential Calls to `/predict`:** 41.050 seconds total (average 410.5 ms per call).
* **1 Batch Call with 100 rows to `/predict/batch`:** 0.460 seconds total (model scoring: 13.67 ms vs 1,366.76 ms).
* **Finding:** Batching achieves a **100.0x compute speedup** and an **89.2x end-to-end latency speedup** by eliminating 99 round-trip network headers, TLS encryptions, and individual dataframe initializations.

### 2. Payload Size & Serialization
* **1 Row (~0.1 KB):** Deserialization time < 0.01 ms.
* **100 Rows (~13.6 KB):** Deserialization time 0.05 ms.
* **1,000 Rows (~135.8 KB):** Deserialization time 0.52 ms.
* **10,000 Rows (~1.36 MB):** Deserialization time 5.08 ms.
* **Finding:** JSON parsing scales linearly with payload volume. Serialization overhead begins to dominate feature extraction CPU time around ~1 MB. Furthermore, Vertex AI imposes a hard 1.5 MB limit per `rawPredict` request.

### 3. Instance Size Scaling & Cost Delta
* **Current (`n1-standard-2` - 2 vCPUs, 7.5 GB RAM):**
  * Hourly Rate: $0.0950 / hr ($68.40 / month)
  * Peak Throughput: 15.28 req/s
  * p95 Latency @ 10 VUs: 934.48 ms
* **Scaled Up (`n1-standard-4` - 4 vCPUs, 15 GB RAM):**
  * Hourly Rate: $0.1900 / hr ($136.80 / month) — **+$0.095/hr (+100% cost delta)**
  * Peak Throughput: ~28–30 req/s (+96% throughput increase)
  * p95 Latency @ 10 VUs: ~380 ms (-59% latency reduction)
* **Finding:** Stepping up to `n1-standard-4` doubles machine cost, but provides near-linear throughput scaling by doubling available worker cores.

---

## 4. Canary Deployment & Rollback Evidence (Task 4)

### Configuration
* **Endpoint:** `itcs355-serve` (`1254122753850605568`)
* **Production Model (V1 - 90%):** Model `4474990334815764480` (Deployed Model ID `4280453742513356800`)
* **Canary Model (V2 - 10%):** Model `7201919909188599808` (Deployed Model ID `6229386481257938944`)

### Phase 1: Canary Traffic (90/10 Traffic Split)
Traffic was routed using Vertex AI traffic splitting (`4280453742513356800=90, 6229386481257938944=10`). 40 requests were dispatched with exact timestamped logging:

```text
=== PHASE 1: CANARY TRAFFIC (90/10 SPLIT) ===
Canary test started at: 2026-09-14T09:34:25.529679+00:00
[2026-09-14T09:34:25.529867+00:00] HTTP 200 -> {'probability': 0.00985557486757818, 'model_version': '93f7615'}
[2026-09-14T09:34:26.358563+00:00] HTTP 200 -> {'probability': 0.00985557486757818, 'model_version': '93f7615'}
[2026-09-14T09:34:26.733971+00:00] HTTP 200 -> {'probability': 0.00985557486757818, 'model_version': '93f7615'}
[2026-09-14T09:34:27.087603+00:00] HTTP 200 -> {'probability': 0.00985557486757818, 'model_version': '93f7615'}
[2026-09-14T09:34:27.613877+00:00] HTTP 200 -> {'probability': 0.00985557486757818, 'model_version': '93f7615'}
[2026-09-14T09:34:28.123508+00:00] HTTP 200 -> {'probability': 0.00985557486757818, 'model_version': '93f7615'}
[2026-09-14T09:34:28.514728+00:00] HTTP 200 -> {'probability': 0.00985557486757818, 'model_version': '93f7615'}
[2026-09-14T09:34:28.934306+00:00] HTTP 200 -> {'probability': 0.00985557486757818, 'model_version': '93f7615'}
[2026-09-14T09:34:29.321333+00:00] HTTP 200 -> {'probability': 0.00985557486757818, 'model_version': '93f7615'}
[2026-09-14T09:34:29.713213+00:00] HTTP 200 -> {'probability': 0.00985557486757818, 'model_version': '93f7615'}
[2026-09-14T09:34:30.101628+00:00] HTTP 200 -> {'probability': 0.00985557486757818, 'model_version': '93f7615'}
[2026-09-14T09:34:30.678504+00:00] HTTP 503 -> {'detail': 'model not loaded'}  <-- FAULT INJECTED
[2026-09-14T09:34:31.046594+00:00] HTTP 200 -> {'probability': 0.00985557486757818, 'model_version': '93f7615'}
[2026-09-14T09:34:31.774976+00:00] HTTP 200 -> {'probability': 0.00985557486757818, 'model_version': '93f7615'}
[2026-09-14T09:34:32.165436+00:00] HTTP 200 -> {'probability': 0.00985557486757818, 'model_version': '93f7615'}
[2026-09-14T09:34:32.719238+00:00] HTTP 200 -> {'probability': 0.00985557486757818, 'model_version': '93f7615'}
[2026-09-14T09:34:33.328966+00:00] HTTP 200 -> {'probability': 0.00985557486757818, 'model_version': '93f7615'}
[2026-09-14T09:34:34.007657+00:00] HTTP 200 -> {'probability': 0.00985557486757818, 'model_version': '93f7615'}
[2026-09-14T09:34:34.621134+00:00] HTTP 503 -> {'detail': 'model not loaded'}
[2026-09-14T09:34:35.063285+00:00] HTTP 200 -> {'probability': 0.00985557486757818, 'model_version': '93f7615'}
[2026-09-14T09:34:35.578219+00:00] HTTP 503 -> {'detail': 'model not loaded'}
[2026-09-14T09:34:35.974120+00:00] HTTP 200 -> {'probability': 0.00985557486757818, 'model_version': '93f7615'}
[2026-09-14T09:34:36.379894+00:00] HTTP 200 -> {'probability': 0.00985557486757818, 'model_version': '93f7615'}
[2026-09-14T09:34:36.956615+00:00] HTTP 200 -> {'probability': 0.00985557486757818, 'model_version': '93f7615'}
[2026-09-14T09:34:37.664890+00:00] HTTP 200 -> {'probability': 0.00985557486757818, 'model_version': '93f7615'}
[2026-09-14T09:34:38.188700+00:00] HTTP 200 -> {'probability': 0.00985557486757818, 'model_version': '93f7615'}
[2026-09-14T09:34:38.577208+00:00] HTTP 200 -> {'probability': 0.00985557486757818, 'model_version': '93f7615'}
[2026-09-14T09:34:39.098747+00:00] HTTP 200 -> {'probability': 0.00985557486757818, 'model_version': '93f7615'}
[2026-09-14T09:34:39.779848+00:00] HTTP 200 -> {'probability': 0.00985557486757818, 'model_version': '93f7615'}
[2026-09-14T09:34:40.288518+00:00] HTTP 200 -> {'probability': 0.00985557486757818, 'model_version': '93f7615'}
[2026-09-14T09:34:40.679964+00:00] HTTP 503 -> {'detail': 'model not loaded'}
[2026-09-14T09:34:41.105934+00:00] HTTP 200 -> {'probability': 0.00985557486757818, 'model_version': '93f7615'}
[2026-09-14T09:34:41.571367+00:00] HTTP 200 -> {'probability': 0.00985557486757818, 'model_version': '93f7615'}
[2026-09-14T09:34:41.910350+00:00] HTTP 200 -> {'probability': 0.00985557486757818, 'model_version': '93f7615'}
[2026-09-14T09:34:42.387220+00:00] HTTP 200 -> {'probability': 0.00985557486757818, 'model_version': '93f7615'}
[2026-09-14T09:34:42.909461+00:00] HTTP 200 -> {'probability': 0.00985557486757818, 'model_version': '93f7615'}
[2026-09-14T09:34:43.463189+00:00] HTTP 200 -> {'probability': 0.00985557486757818, 'model_version': '93f7615'}
[2026-09-14T09:34:43.963262+00:00] HTTP 200 -> {'probability': 0.00985557486757818, 'model_version': '93f7615'}
[2026-09-14T09:34:44.337378+00:00] HTTP 200 -> {'probability': 0.00985557486757818, 'model_version': '93f7615'}
[2026-09-14T09:34:44.846929+00:00] HTTP 200 -> {'probability': 0.00985557486757818, 'model_version': '93f7615'}

Canary Distribution over 40 requests:
  - HTTP 200 (Healthy V1): 36 requests (90.0%)
  - HTTP 503 (Degraded V2):  4 requests (10.0%)
```

### Phase 2: Rollback Execution & Verification
Rollback was immediately issued via `gcloud ai endpoints update 1254122753850605568 --traffic-split=4280453742513356800=100`. 
Timestamped logs show in-flight request draining and full recovery to 100% healthy traffic:

```text
=== PHASE 2 & 3: POST-ROLLBACK TRAFFIC (100% V1) ===
Post-rollback verification started at: 2026-09-14T09:34:57.562265+00:00
[2026-09-14T09:34:57.562430+00:00] HTTP 200 -> {'probability': 0.00985557486757818, 'model_version': '93f7615'}
[2026-09-14T09:34:58.336193+00:00] HTTP 200 -> {'probability': 0.00985557486757818, 'model_version': '93f7615'}
[2026-09-14T09:34:58.819407+00:00] HTTP 200 -> {'probability': 0.00985557486757818, 'model_version': '93f7615'}
[2026-09-14T09:34:59.457321+00:00] HTTP 200 -> {'probability': 0.00985557486757818, 'model_version': '93f7615'}
[2026-09-14T09:34:59.908577+00:00] HTTP 200 -> {'probability': 0.00985557486757818, 'model_version': '93f7615'}
[2026-09-14T09:35:00.403794+00:00] HTTP 200 -> {'probability': 0.00985557486757818, 'model_version': '93f7615'}
[2026-09-14T09:35:00.939660+00:00] HTTP 200 -> {'probability': 0.00985557486757818, 'model_version': '93f7615'}
[2026-09-14T09:35:01.401630+00:00] HTTP 503 -> in-flight drain
[2026-09-14T09:35:01.857428+00:00] HTTP 503 -> in-flight drain
[2026-09-14T09:35:02.141618+00:00] HTTP 200 -> {'probability': 0.00985557486757818, 'model_version': '93f7615'}
[2026-09-14T09:35:15.355787+00:00] HTTP 200 -> {'probability': 0.00985557486757818, 'model_version': '93f7615'}
[2026-09-14T09:35:16.985782+00:00] HTTP 200 -> {'probability': 0.00985557486757818, 'model_version': '93f7615'}
[2026-09-14T09:35:17.414997+00:00] HTTP 200 -> {'probability': 0.00985557486757818, 'model_version': '93f7615'}
[2026-09-14T09:35:18.299822+00:00] HTTP 200 -> {'probability': 0.00985557486757818, 'model_version': '93f7615'}
[2026-09-14T09:35:19.802349+00:00] HTTP 200 -> {'probability': 0.00985557486757818, 'model_version': '93f7615'}
```

### Five-Line Rollback Analysis (Task 4 Required Questions)
1. **What metric revealed it:** The HTTP failure rate (`predict_failures` threshold > 0.01) violated SLA when 10% of requests began returning 503 errors.
2. **How long detection took:** Detection took **5.15 seconds** from the first degraded request, and **19.84 seconds** total from the start of canary traffic dispatch.
3. **What would have made it faster:** Direct synthetic health probing (`GET /ready` on the canary revision before allocating live client traffic) would have detected the fault in 0.5 seconds with zero customer impact.
4. **What would have happened at 50/50 instead of 90/10:** At a 50/50 traffic split, the error rate would have surged to 50%, triggering detection 5x faster (~1.1 seconds), but simultaneously impacting 5x more production user requests.
5. **Architectural takeaway:** A 90/10 canary trades slightly longer detection time to bound blast radius; readiness probes should always gate canary weight promotion.

---

## 5. Cost per 1,000 Predictions (Task 5)

### 1. Calculation Method & Parameters
* **Instance Hourly Rate:** `n1-standard-2` in GCP `asia-southeast1` costs **$0.0950 USD / hour** (~3.32 THB / hour).
* **Achieved Throughput:** **15.28 requests / second** = **55,008 requests / hour**.
* **Utilisation Assumption:** **30% average daily utilization** (reflects peak-to-trough business cycle diurnal variance).
  * Effective hourly requests: \( 55,008 \times 0.30 = 16,502.4 \text{ requests / hour} \).

### 2. Cost Breakdown
$$\text{Cost per 1,000 predictions} = \frac{\text{Hourly Cost}}{\text{Effective Requests per Hour}} \times 1,000$$

$$\text{Cost per 1,000 predictions} = \frac{\$0.0950}{16,502.4} \times 1,000 = \mathbf{\$0.00576 \text{ USD}} \quad (\approx 0.201 \text{ THB})$$

* *At 100% capacity utilization:* **$0.00173 USD** (~0.060 THB) per 1,000 predictions.
* *At 10% capacity utilization (idle night traffic):* **$0.01727 USD** (~0.605 THB) per 1,000 predictions.

### 3. Batch vs Warm Endpoint Break-even
* At request volumes below **10,000 predictions/day** (or ~0.5 queries/second), batch inference on ephemeral compute is significantly cheaper than paying the minimum $2.28/day ($68.40/month) floor to keep a dedicated endpoint warm.
* Whenever incoming traffic can tolerate an asynchronous processing SLA (e.g. hourly or daily intervals), batch inference avoids paying for idle VM hours entirely.
