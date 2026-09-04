"""Token accounting and the LLM cost model. Session 5, Lab 5 Part B.

An LLM endpoint is priced per token, not per hour, which breaks every intuition built in
Labs 2 and 3. A classifier that costs the same whether it answers 10 or 10,000 requests
becomes an assistant whose bill is a linear function of how verbose it is allowed to be.
`src/costs.py` prices provisioned compute; this module prices tokens. Lab 5 makes you
report both, because a real system has both.

Three levers move an LLM bill, in the order they are worth pulling:

  1. Output length.   Output tokens cost 3-5x input tokens on every provider. Capping
                      max_output_tokens is the single highest-leverage change available,
                      and it is one line.
  2. Prompt caching.  A cached input token is billed at roughly a tenth of a fresh one.
                      Worth having only when a long prefix is genuinely stable.
  3. Model choice.    A smaller model is often 10-20x cheaper. Whether it is good enough
                      is an evaluation question, not a pricing one — which is why
                      scripts/llm_eval.py exists and why you run it before you switch.

Prices are THB per 1,000,000 tokens. They change often and differ by region.

TODO(Lab 5): verify every rate below against your provider's pricing page for YOUR region
before you cite a cost figure. Record the date you checked in your cost report. A stale
price presented as current is exactly what the report is designed to catch.
"""
from __future__ import annotations

from dataclasses import dataclass

# THB per 1,000,000 tokens: (input, output).
TOKEN_PRICE_TABLE: dict[str, dict[str, tuple[float, float]]] = {
    "local": {"stub": (0.0, 0.0)},
    "aws": {
        "small": (9.0, 36.0),
        "medium": (108.0, 540.0),
        "large": (540.0, 2700.0),
    },
    "azure": {
        "small": (9.5, 38.0),
        "medium": (112.0, 550.0),
        "large": (550.0, 2750.0),
    },
    "gcp": {
        "small": (8.5, 34.0),
        "medium": (105.0, 525.0),
        "large": (525.0, 2625.0),
    },
}

# A cache hit is billed at this fraction of the normal input rate. Roughly right on all
# three providers; verify it, like everything else here.
CACHE_READ_FACTOR = 0.10

# Cache writes usually cost MORE than a normal input token. A prompt cache on a prefix
# that changes every request is a way to pay extra for nothing, and it is a common and
# expensive mistake.
CACHE_WRITE_FACTOR = 1.25


@dataclass(frozen=True)
class Usage:
    """One request's token usage, as every provider reports it under different names."""

    input_tokens: int
    output_tokens: int
    cached_input_tokens: int = 0

    def __post_init__(self) -> None:
        for name in ("input_tokens", "output_tokens", "cached_input_tokens"):
            if getattr(self, name) < 0:
                raise ValueError(f"{name} must not be negative")
        if self.cached_input_tokens > self.input_tokens:
            raise ValueError(
                "cached_input_tokens cannot exceed input_tokens — cached tokens are a "
                "subset of the input, not an addition to it. Misreading this is how "
                "cost reports end up double-counting the prompt."
            )


def token_rates(provider: str, model: str) -> tuple[float, float]:
    """THB per 1M input and output tokens. Raises rather than guessing."""
    table = TOKEN_PRICE_TABLE.get(provider.lower())
    if table is None:
        raise KeyError(
            f"No token price table for provider {provider!r}. Add it to src/llmcost.py."
        )
    if model not in table:
        raise KeyError(
            f"No token rates for {model!r} on {provider}. Known: {sorted(table)}. "
            "Add the model you actually called — do not substitute a similar one silently."
        )
    return table[model]


def request_cost(provider: str, model: str, usage: Usage) -> float:
    """THB for a single request, cache discount included."""
    rate_in, rate_out = token_rates(provider, model)
    fresh_input = usage.input_tokens - usage.cached_input_tokens
    thb = (
        fresh_input * rate_in
        + usage.cached_input_tokens * rate_in * CACHE_READ_FACTOR
        + usage.output_tokens * rate_out
    )
    return thb / 1_000_000


def cost_per_1k_requests(provider: str, model: str, usage: Usage) -> float:
    """THB per 1,000 requests at this average usage.

    The unit the rest of the course reports in, so an LLM path and a classifier path can
    be compared on the same axis in your cost report.
    """
    return request_cost(provider, model, usage) * 1000


def monthly_thb(provider: str, model: str, usage: Usage, requests_per_day: float) -> float:
    """THB per 30-day month at a steady request rate."""
    if requests_per_day < 0:
        raise ValueError("requests_per_day must not be negative")
    return request_cost(provider, model, usage) * requests_per_day * 30


def output_cap_saving(provider: str, model: str, usage: Usage, capped_output: int) -> float:
    """THB per 1,000 requests saved by capping output length.

    Run this before you optimise anything else. On most assistant workloads it beats both
    caching and a model downgrade, and unlike a downgrade it cannot change your answers'
    correctness — only their length.
    """
    if capped_output < 0:
        raise ValueError("capped_output must not be negative")
    if capped_output >= usage.output_tokens:
        return 0.0
    capped = Usage(usage.input_tokens, capped_output, usage.cached_input_tokens)
    return cost_per_1k_requests(provider, model, usage) - cost_per_1k_requests(
        provider, model, capped
    )


def cache_breakeven_hit_rate(provider: str, model: str, prefix_tokens: int) -> float:
    """Cache hit rate above which prompt caching starts paying for itself.

    Below this, the write surcharge on misses costs more than the reads save. Report it
    alongside your measured hit rate; a cache defended without this number is a guess.
    """
    if prefix_tokens <= 0:
        raise ValueError("prefix_tokens must be positive")
    token_rates(provider, model)  # validate provider and model early
    saving_per_hit = 1.0 - CACHE_READ_FACTOR
    extra_per_miss = CACHE_WRITE_FACTOR - 1.0
    return extra_per_miss / (saving_per_hit + extra_per_miss)
