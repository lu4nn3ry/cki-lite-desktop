# ADR-0009: Trace and Session Workspace

- Status: Accepted
- Date: 2026-09-08

## Decision

Use a left session sidebar, central Chat/Terminal tabs, fixed input area, and a
collapsible Agent trace panel.

## Rationale

This makes the Desktop client a visual terminal agent rather than a general
purpose IDE while preserving observability for tool execution.

## Consequences

The UI exposes session operations and basic loop/tool results without exposing
hidden model chain-of-thought.
