# ADR-0008: JSON Session Persistence

- Status: Accepted
- Date: 2026-09-08

## Decision

Persist sessions as plain JSON files under `~/.cki-lite` or `CKI_LITE_HOME`.

## Rationale

JSON keeps the client dependency-free, inspectable, portable, and consistent
with the original CLI's standard-library approach.

## Consequences

Sessions can be listed, loaded, created, deleted, and exported without a
database. API keys are deliberately excluded from session data.
