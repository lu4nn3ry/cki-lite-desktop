# ADR-0004: Explicit Modern TLS

- Status: Accepted
- Date: 2026-09-08

## Decision

Configure TLS 1.2 and TLS 1.3 explicitly at startup and before HTTP requests.

## Rationale

The .NET Framework default protocol can resolve to legacy SSL3/TLS1.0 on
Windows 11, causing modern provider requests to fail with a secure-channel
error.

## Consequences

Numeric enum values are used for compatibility with the .NET Framework 4.0
reference assemblies. The application also exposes DNS/TCP/TLS/HTTP diagnosis.
