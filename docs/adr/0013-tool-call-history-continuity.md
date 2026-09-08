# ADR-0013: Tool-call History Continuity

- Status: Accepted
- Date: 2026-09-08

## Decision

Preserve assistant `tool_calls` and tool `tool_call_id` fields when rebuilding
the next OpenAI-compatible request. Preserve the corresponding Gemini
`functionCall` and `functionResponse` parts as well.

## Rationale

Without the IDs and function metadata, a model can receive a tool result as an
unrelated message and repeat the same tool call until the agent loop limit.

## Consequences

The model can correlate each terminal result with its request and continue the
conversation normally. The same terminal tool remains available after fallback
requests.
