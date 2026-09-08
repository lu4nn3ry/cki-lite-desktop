# ADR-0006: PowerShell-first Terminal

- Status: Accepted
- Date: 2026-09-08

## Decision

Expose one `terminal` tool with PowerShell as the default shell and CMD as an
explicit alternative.

## Rationale

PowerShell is the native Windows automation surface and provides the commands
needed for service, process, event, network, Docker, Git, WSL, and winget work.

## Consequences

PowerShell commands use `-EncodedCommand` to preserve quotes and special
characters. Each execution returns structured stdout, stderr, exit code, and
timeout information.
