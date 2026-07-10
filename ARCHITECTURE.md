# Architecture

## Design goals

Agent Boundary Guard is intentionally small and boring:

- **local-first:** scan a checked-out repository without network access
- **low-trust by default:** flag autonomy boundary expansion before runtime deployment
- **stdlib-only runtime:** reduce supply-chain risk for a security gate
- **CI-friendly:** deterministic text or JSON output with severity-based exit codes

## Components

### `agent_boundary_guard.rules`
Holds the detection contract for the first release. Each rule has an ID, severity, message, regex pattern, and scan scope.

### `agent_boundary_guard.scanner`
Walks the repository, filters candidate text files, applies rule matching line-by-line, and returns normalized findings.

### `agent_boundary_guard.cli`
Exposes a simple `scan` command with `--format` and `--fail-on` controls.

### `tests/`
Covers rule hits, placeholder suppression, and CLI exit-code behavior.

## Deliberate limitations

- heuristics favor fast review over complete semantic parsing
- no SARIF export yet
- no allowlist or suppression contract yet
- no history scanning yet

Those gaps are tracked in `docs/SKILL_REGISTRY.md`.
