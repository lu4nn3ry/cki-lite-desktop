# ADR-0001: Native WinForms Build

- Status: Accepted
- Date: 2026-09-08

## Decision

Use C# Windows Forms and compile directly with the .NET Framework `csc.exe`.

## Rationale

The Desktop client targets Windows and must remain portable, small, and free of
Visual Studio, .NET SDK, NuGet, Electron, and Tauri requirements.

## Consequences

The source remains C# 5-compatible with BCL-only dependencies. The build is
less expressive than a modern SDK project, but a clean Windows installation can
produce the executable with the included Batch/PowerShell scripts.
