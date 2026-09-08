# ADR-0012: Persistent User Selection

- Status: Accepted
- Date: 2026-09-08

## Decision

Persist the selected provider, selected/used model, and approval mode in a
user-local `settings.json`. Expose approval modes as `plan`, `accept-edits`, and
`auto-approve` in the main toolbar.

## Rationale

The next launch should return the user to the same provider and model without
requiring another setup step. Approval is a user preference, not a secret.

## Consequences

Settings stay outside the repository and session content. API keys remain in
environment variables or `.env` and are never written to `settings.json`.
