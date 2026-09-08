# ADR-0011: Model Labels and Tool Contract

- Status: Accepted
- Date: 2026-09-08

## Decision

Display the active model name as the assistant chat prefix and include the
`terminal` tool contract in both normal and fallback OpenAI-compatible requests.

## Rationale

The provider name does not identify which model generated a response. Fallback
requests must preserve the same tool contract as normal requests or the model
cannot operate the Windows terminal reliably.

## Consequences

Chat output is attributable to the selected model. Numeric request fields are
serialized as JSON numbers, and a direct NIM check confirms that a compatible
model returns a `terminal` tool call without executing it.
