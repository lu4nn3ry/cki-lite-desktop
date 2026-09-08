# ADR-0007: Safe Command Execution Modes

- Status: Accepted
- Date: 2026-09-08

## Decision

Support `Safe`, `Ask`, and `Auto` execution modes, with `Ask` as the default.

## Rationale

The agent runs with the same Windows permissions as the application. Explicit
user control is required before model-generated commands affect the machine.

## Consequences

Safe blocks agent tools, Ask displays the complete command before execution,
and Auto is available only as an explicit user choice in Config.
