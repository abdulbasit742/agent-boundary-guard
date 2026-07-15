# Architecture

## Design goals

Agent Boundary Guard is intentionally small and boring:

- **local-first:** scan a checked-out repository without network access
- **low-trust by default:** flag autonomy boundary expansion before runtime deployment
- **stdlib-only runtime:** reduce supply-chain risk for a security gate
- **CI-friendly:** deterministic text, JSON, or SARIF output with severity-based exit codes
- **report-safe:** avoid copying secret-like matched text into hosted SARIF results

## Components

### `agent_boundary_guard.rules`

Holds the detection contract. Each rule has a stable ID, severity, message, regex pattern, and scan scope. Stable IDs are also the SARIF rule identity.

### `agent_boundary_guard.scanner`

Walks the repository, filters candidate text files, applies rule matching line-by-line, and returns normalized findings. It has no reporting or network responsibility.

### `agent_boundary_guard.sarif`

Transforms normalized findings into SARIF 2.1.0. It publishes all registered rule descriptors in stable order, maps severities to SARIF levels, normalizes paths, and emits deterministic fingerprints. It does not include raw snippets.

### `agent_boundary_guard.cli`

Exposes the `scan` command with `--format`, `--output`, `--max-size-kb`, and `--fail-on` controls. Reports are written before the severity threshold determines the process exit code, allowing CI to upload SARIF even when policy violations are found.

### `tests/`

Covers rule hits, placeholder suppression, CLI exit-code behavior, SARIF schema structure, path normalization, stable fingerprints, output-file behavior, and snippet redaction.

## Data flow

```text
repository/file
      |
      v
candidate file filter
      |
      v
rule matching -> normalized Finding objects
      |                 |
      |                 +-> severity threshold -> exit code
      v
text / JSON / SARIF formatter
      |
      v
stdout or explicit output file
```

## Deliberate limitations

- heuristics favor fast review over complete semantic parsing
- no allowlist or suppression contract yet
- no history scanning yet
- SARIF locations are line-level because the scanner does not currently retain match columns

Those gaps are tracked in `docs/SKILL_REGISTRY.md`.
