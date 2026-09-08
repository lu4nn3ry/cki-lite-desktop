# ADR-0003: Unfiltered NVIDIA Model Catalog

- Status: Accepted
- Date: 2026-09-08

## Decision

Display every model returned by NVIDIA NIM `/models`, subject only to the
provider response and optional local selection ordering.

## Rationale

Users need access to the complete provider catalog. The previous family-based
filter hid valid models and made the selector misleading.

## Consequences

Specialized models may appear and may not support the agent tool contract. The
user selects the model explicitly. The NIM service can also return a global
catalog while a model is not enabled for the account; a model-level HTTP 404 is
reported directly instead of causing fallback noise through every catalog item.

Optional manual optimization benchmarks the returned catalog against the actual
terminal tool contract, removes failed/high-latency entries, orders the result,
and stores it in a date-based cache. This is never performed automatically at
startup.
