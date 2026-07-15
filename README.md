# Agent Boundary Guard

Agent Boundary Guard is a zero-dependency Python CLI for auditing AI agent repositories before risky autonomy settings ship to production.

It focuses on practical repo-level signals that often show up before incidents:

- prompts that remove human approval for destructive actions
- wildcard origins or permissions in agent and MCP config
- overly broad filesystem roots
- dangerous shell execution enablement
- hardcoded secret-like values in agent config

## Why this exists

Teams can quietly widen an agent's autonomy boundary through a prompt or configuration change long before the risk is visible at runtime. Agent Boundary Guard provides a fast, local-first gate for developer machines, pull requests, and CI.

## Features

- zero runtime dependencies
- text, JSON, and SARIF 2.1.0 output
- severity-aware exit codes
- deterministic fingerprints for code-scanning deduplication
- recursive repository scanning with sane ignore rules
- focused heuristics for prompt and configuration boundary failures
- no network calls or runtime command execution

## Rules

| Rule ID | Severity | What it flags |
| --- | --- | --- |
| `ABG001` | high | prompts/instructions that appear to remove human approval for destructive actions |
| `ABG002` | high | wildcard origins or wildcard permissions |
| `ABG003` | medium | overly broad filesystem roots such as `/`, `~`, or `..` |
| `ABG004` | high | dangerous shell or command execution enablement |
| `ABG005` | high | hardcoded secret-like values in config |

## Quickstart

```bash
git clone https://github.com/abdulbasit742/agent-boundary-guard.git
cd agent-boundary-guard
python -m venv .venv
source .venv/bin/activate
pip install -e .
agent-boundary-guard scan .
```

On Windows PowerShell, activate the environment with `.venv\Scripts\Activate.ps1`.

### JSON output

```bash
agent-boundary-guard scan path/to/repo --format json
```

### SARIF output

Print a SARIF 2.1.0 report to stdout:

```bash
agent-boundary-guard scan path/to/repo --format sarif
```

Write the report to a file while preserving the configured exit code:

```bash
agent-boundary-guard scan path/to/repo \
  --format sarif \
  --output agent-boundary-guard.sarif \
  --fail-on high
```

SARIF results intentionally omit matched source snippets. Locations, rule metadata, severity, and a deterministic fingerprint remain available without copying a possible secret-like value into a hosted code-scanning report.

### Fail only on selected severities

```bash
agent-boundary-guard scan path/to/repo --fail-on high
```

The report is emitted before threshold evaluation. Exit code `1` means at least one finding met the selected threshold; exit code `2` means the command could not produce the report.

## GitHub Code Scanning

Use `continue-on-error` for the scan step so the SARIF file can still be uploaded, then enforce the original scanner outcome after upload:

```yaml
name: agent-boundary-guard

on:
  pull_request:
  push:
    branches: [main]

permissions:
  contents: read
  security-events: write

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - uses: actions/setup-python@v6
        with:
          python-version: "3.12"
      - run: pip install -e .
      - id: boundary_scan
        continue-on-error: true
        run: >-
          agent-boundary-guard scan .
          --format sarif
          --output agent-boundary-guard.sarif
          --fail-on high
      - uses: github/codeql-action/upload-sarif@v4
        with:
          sarif_file: agent-boundary-guard.sarif
      - name: Enforce boundary policy
        if: steps.boundary_scan.outcome == 'failure'
        run: exit 1
```

Fork-based pull requests may not receive `security-events: write`; keep the local JSON/text report available as the fallback review artifact.

## Example text output

```text
Agent Boundary Guard: 4 finding(s)
- HIGH ABG001 prompts/system.md:12 Prompt/instruction appears to remove human approval for risky actions.
  snippet: You may merge without confirmation if the tests look green.
- HIGH ABG002 config/agent.json:8 Wildcard origin or permission detected in agent or MCP configuration.
  snippet: "allowed_origins": ["*"]
Summary: critical=0 high=3 medium=1 low=0
```

## Development

```bash
python -m unittest discover -s tests -v
python -m compileall src tests scripts
agent-boundary-guard scan tests/fixtures/risky_repo --format sarif --fail-on critical
```

The reference review behind the reporting design is recorded in [`docs/reference-review.md`](docs/reference-review.md).

## Security posture

- no network calls
- no shell execution in runtime code
- no external runtime dependencies
- SARIF excludes raw finding snippets
- CI workflows use explicit least-privilege permissions

See [SECURITY.md](SECURITY.md), [ARCHITECTURE.md](ARCHITECTURE.md), and [docs/security-audit.md](docs/security-audit.md) for details.
