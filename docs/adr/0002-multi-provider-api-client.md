# ADR-0002: Multi-provider API Client

- Status: Accepted
- Date: 2026-09-08

## Decision

Keep one provider-aware HTTP client and support NVIDIA NIM, Groq, OpenRouter,
Ollama, and Google Gemini behind a small provider registry.

## Rationale

The original identity is NVIDIA NIM, while compatible providers make local and
fallback workflows useful without changing the agent core.

## Consequences

Provider-specific paths and authentication stay isolated. API keys are read
from environment variables, `.env`, or the Config dialog and are not stored in
conversation exports.
