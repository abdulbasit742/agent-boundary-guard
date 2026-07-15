# Security Audits

## 2026-07-14 — SARIF reporting slice

### Scope

SARIF 2.1.0 export, report-file writing, CI validation, documentation, and release metadata.

### Changed area reviewed

- new `agent_boundary_guard.sarif` formatter
- CLI format and output-path handling
- deterministic finding fingerprints and path normalization
- SARIF and CLI regression tests
- CI smoke validation and code-scanning guidance

### Audit findings

- **Critical:** 0
- **High:** 0
- **Medium:** 0
- **Low:** 1 residual report-location limitation

### Evidence

- runtime remains Python standard-library only
- formatter performs no network or subprocess calls
- output directories are created only when the user explicitly provides `--output`
- SARIF includes rule messages and locations but excludes raw matched snippets
- deterministic fingerprints hash the snippet rather than exposing it
- report generation happens before threshold exit evaluation, and write failures return exit code `2`
- local-equivalent validation passed compile checks and 8 unit tests

### Residual risk

SARIF currently reports line-level locations without columns. Fingerprints intentionally hash matched content; although the content is not emitted, users with highly sensitive repositories should still treat generated reports as security artifacts.

### Next security action

Implement suppression support that applies consistently to text, JSON, SARIF, summaries, and exit-code evaluation without allowing broad silent exclusions.

---

## 2026-07-10 — Initial vertical slice

### Scope

Initial vertical slice for Agent Boundary Guard.

### Changed area reviewed

- packaging and CLI entry points
- scanner heuristics and severity threshold logic
- unit tests and fixtures
- documentation and CI/security workflows

### Audit findings

- **Critical:** 0
- **High:** 0
- **Medium:** 0
- **Low:** 1 residual heuristic-risk item

### Evidence

- runtime code uses Python standard library only
- no subprocess, shell execution, or outbound network calls in application code
- no committed real secrets in tests or docs; fixtures use obvious fake placeholders
- CI and security workflows declare explicit permissions

### Residual risk

The scanner is heuristic in this release, so some nested or nonstandard config layouts may be missed until structured parsing is added.
