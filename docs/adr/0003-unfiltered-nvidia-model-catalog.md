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
user selects the model explicitly, and fallback only uses models returned by
the active catalog.
