# Evaluation sets

Golden sets and recorded responses for the LLM step. Lab 5 Part B.

```
golden/     the cases and what must be true of an answer
fixtures/   recorded responses, so the harness runs offline, free, and deterministically
```

Run it:

```bash
make llm-eval     # 8 cases against the baseline fixture — everything passes
make llm-gate     # the same cases against a degraded set — fails, on purpose
```

## Case format — `golden/*.jsonl`

One JSON object per line:

```json
{"id": "triage-001", "prompt": "...", "checks": [{"type": "json_field", "field": "decision", "value": "schedule_urgent"}]}
```

| Check | Meaning |
|---|---|
| `contains` / `not_contains` | case-insensitive substring |
| `regex` / `not_regex` | Python regular expression |
| `json_field` | response parses as JSON and `field` equals `value` |
| `max_words` | answer is no longer than `value` words |

A case passes only when every one of its checks passes.

## Response format — `fixtures/*.jsonl`

```json
{"id": "triage-001", "response": "...", "input_tokens": 418, "output_tokens": 41, "latency_ms": 812}
```

Token counts come from the provider's own usage fields. Do not estimate them by counting
words — every provider tokenises differently, and Lab 5 prices a bill from these numbers.

## Why fixtures rather than live calls

The gate has to run on every commit, and a gate that costs money and returns something
different each time is a gate nobody keeps. Record responses, commit them, gate on them.
`--live` routes through your adapter's `generate` when you want a fresh recording.

## Writing your own

The set that ships here is a worked example over the course's own machine-failure data.
Yours must cover at least: **grounding** (only facts from the input), a **guardrail**
(something the model must refuse), an **injection** (instructions inside a data field, to be
treated as data), and **insufficient input** (the right answer is "I cannot answer this").

A golden set that has never failed has not been tested. Break something on purpose and
confirm the gate catches it before you trust it.
