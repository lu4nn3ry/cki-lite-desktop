# cki-lite Desktop

**A small, native Windows AI operator for NVIDIA NIM.**

cki-lite Desktop is a C# + Windows Forms rewrite of the cki-lite terminal
agent. It is intentionally not an IDE, code editor, browser, or Cursor clone.
Its job is simple: let an AI agent inspect and operate a Windows machine through
a visible chat, a model selector, PowerShell, and CMD.

The repository also contains the original Python CLI for Unix-like systems.

## Product Principles

- Native WinForms, small executable, few dependencies.
- NVIDIA NIM as the primary provider.
- PowerShell as the default Windows automation surface.
- Explicit command confirmation with `Safe`, `Ask`, and `Auto` modes.
- Transparent tool output and session persistence.
- No MCP, plugins, embedded browser, Git UI, or code editor in v1.

## Features

- Chat with OpenAI-compatible tool calling.
- NVIDIA NIM model catalog via `/models` and `/chat/completions`.
- Complete NVIDIA model catalog, without an artificial family filter.
- Clear handling when a catalog model is not enabled for the current NIM account.
- Groq, OpenRouter, Ollama, and Google Gemini providers.
- Visible provider and model selectors.
- API key and base URL configuration dialog.
- `.env` support without committing secrets.
- Automatic fallback across available models.
- PowerShell-first `terminal` tool with optional CMD.
- Command timeout, working directory, stdout, stderr, and exit code.
- `Safe`, `Ask` (default), and `Auto` command modes.
- Session sidebar with create, load, delete, and export actions.
- Chat copy menu and collapsible Agent trace.
- DNS, TCP, TLS, and HTTP connection diagnostics.
- Generated application icon embedded in the executable.

## Requirements

For the Desktop client:

- Windows 10 or Windows 11.
- .NET Framework 4.x with `csc.exe` available.
- An API key for the selected cloud provider.
- No Visual Studio, .NET SDK, NuGet, MSBuild, Electron, or Tauri required.

For the Python CLI:

- Python 3.8+.
- An NVIDIA NIM API key.

## Build Desktop

From a Windows PowerShell or Command Prompt:

```bat
build.bat
```

Or:

```powershell
.\build.ps1
```

The scripts invoke the built-in .NET Framework compiler and produce:

```text
bin\cki-lite.exe
```

Run it with:

```bat
bin\cki-lite.exe
```

## Configuration

Use the **Config** button to set the active provider key, optional base URL,
and command execution mode. Keys can be loaded from environment variables or a
`.env` file in the executable directory, `~\.cki-lite\.env`, or the current
directory.

Example:

```dotenv
NVIDIA_API_KEY=nvapi-...
NIM_BASE_URL=https://integrate.api.nvidia.com/v1
```

Supported keys:

| Provider | Environment key | Default base URL |
| --- | --- | --- |
| NVIDIA NIM | `NVIDIA_API_KEY` | `https://integrate.api.nvidia.com/v1` |
| Groq | `GROQ_API_KEY` | `https://api.groq.com/openai/v1` |
| OpenRouter | `OPENROUTER_API_KEY` | `https://openrouter.ai/api/v1` |
| Ollama | `OLLAMA_API_KEY` | `http://localhost:11434/v1` |
| Google Gemini | `GEMINI_API_KEY` | `https://generativelanguage.googleapis.com/v1beta` |

`.env`, `bin/`, `work/`, sessions, and private key files are ignored by Git.
Never commit an API key.

## Command Execution

The agent exposes one tool:

```text
terminal(command, cwd, timeout, shell)
```

PowerShell is used by default. CMD can be selected by the model when needed.
The application runs commands with the permissions of the current Windows
process, so use `Auto` only on machines and sessions you control.

NVIDIA may return a global catalog from `/models` while only some models are
enabled for an account. A model-level `HTTP 404` is therefore reported directly
and does not trigger a noisy fallback through every catalog entry. Select an
enabled model in the model selector.

## Tests

Run the same compiler-based harness used by the project:

```bat
test.bat
```

The harness covers JSON, providers, `.env`, shell execution, TLS, and live
connection diagnostics. Live provider checks require network access and valid
keys. The deterministic checks should remain usable without external APIs.

## Python CLI

The original CLI remains available:

```sh
export NVIDIA_API_KEY='nvapi-...'
python3 cki-lite.py --list-models
python3 cki-lite.py
```

Its platform target is Unix-like systems, while the WinForms client targets
Windows.

## Architecture Decisions

Implementation decisions are recorded in [`docs/adr/`](docs/adr/README.md),
including the native build, provider client, unfiltered NIM catalog, TLS,
configuration, shell, safety modes, sessions, trace, diagnostics, and tests.

## Project Scope

The remaining v1 work and acceptance criteria are tracked in [`TODO.md`](TODO.md).
Explicitly out of scope: MCP, editor features, advanced diffs, Git UI, browser,
plugins, marketplace, multi-agent orchestration, database, and cross-platform
Desktop support.

## Contributing

Small, focused changes are preferred. Keep the no-install build working, do not
add secrets or generated binaries, update tests and ADRs for behavioral changes,
and preserve the Windows operator focus.

## License

MIT. See [`LICENSE`](LICENSE).
