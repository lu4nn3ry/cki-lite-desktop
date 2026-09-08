# ADR-0005: Configuration Outside the Toolbar

- Status: Accepted
- Date: 2026-09-08

## Decision

Keep provider and model selection in the main toolbar, but move API keys,
custom base URLs, and command safety mode into a Config dialog.

## Rationale

The toolbar must remain usable at small window widths, and secret material does
not belong in the primary navigation surface.

## Consequences

The model selector remains visible. Keys can be entered for the current run or
persisted to the user-local `.env` file.
