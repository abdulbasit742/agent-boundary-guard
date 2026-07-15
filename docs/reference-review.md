# Reference Review — Reporting and Adoption

Reviewed on 2026-07-14. The implementation uses original code and only adopts general engineering patterns.

## 1. Snyk Agent Scan (`snyk/agent-scan`)

Useful pattern: agent-specific security tools need explicit risk identities, clear severity communication, and strong warnings about unsafe execution paths. Agent Boundary Guard keeps its narrower static-only model and strengthens the stable identity of each finding through SARIF rule descriptors.

Not copied: remote analysis, MCP server execution, machine-wide discovery, proprietary services, or unstable output contracts.

## 2. NVIDIA garak (`NVIDIA/garak`)

Useful pattern: mature security scanners separate detection families from output/reporting and preserve named vulnerability categories that users can select and reason about. Agent Boundary Guard keeps rule matching independent from its text, JSON, and SARIF formatters.

Not copied: dynamic model probes, generators, detectors, plugins, external model calls, or runtime dependencies.

## 3. Semgrep (`semgrep/semgrep`)

Useful pattern: SARIF is most valuable when rules have stable metadata and findings carry precise locations suitable for code-scanning ingestion. Agent Boundary Guard now emits SARIF 2.1.0 with stable rule order, severity mapping, relative artifact URIs, and deterministic partial fingerprints.

Not copied: Semgrep source code, RPC formatting architecture, semantic parsing engine, or licensed implementation details.

## Resulting design decisions

- keep the scanner and formatter modules separate
- publish every registered rule in stable order
- map high/critical to `error`, medium to `warning`, and low to `note`
- normalize Windows and POSIX paths into repository-relative SARIF URIs
- generate fingerprints from rule ID, path, and matched content so line moves do not create duplicate alerts
- omit raw snippets from SARIF to reduce the chance of uploading secret-like values
- write reports before applying the CI failure threshold
