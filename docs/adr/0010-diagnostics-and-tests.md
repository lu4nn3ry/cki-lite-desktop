# ADR-0010: Built-in Diagnostics and Tests

- Status: Accepted
- Date: 2026-09-08

## Decision

Ship a connection test button and a csc-compiled test harness alongside the
application.

## Rationale

Network failures are common on Windows/.NET Framework and must identify the
failing layer instead of reporting only an empty HTTP status.

## Consequences

The harness covers JSON, providers, shell behavior, TLS, and live provider
diagnostics. Live API tests require configured credentials and should be run
separately from deterministic tests.
