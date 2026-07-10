# Skill Registry

## Prioritization rubric

1. security risk reduction
2. adoption friction removed
3. validation leverage
4. implementation dependency order

## Ready skills

### SKILL-001 — Allowlist / suppression support
- **Why now:** teams need a way to suppress accepted findings without turning the scanner off.
- **Acceptance criteria:** load a local suppression file, mark suppressed findings in JSON output, preserve exit-code behavior for unsuppressed findings, and add tests for rule-based and path-based suppression.

### SKILL-002 — SARIF export
- **Why now:** code-scanning integration will make the tool easier to adopt in GitHub PR workflows.
- **Acceptance criteria:** add SARIF output, stable rule metadata, CI validation, and documentation.

### SKILL-003 — History-aware scanning
- **Why now:** working-tree-only checks miss risky config that lived in recent commits.
- **Acceptance criteria:** add optional Git history scanning mode with clear limits, no secret value echoing, and tests for commit-content traversal.

### SKILL-004 — Structured config parsing
- **Why now:** regex heuristics will miss nested configuration in larger MCP and agent repos.
- **Acceptance criteria:** parse JSON/TOML/YAML into structured checks while preserving a zero-surprise CLI.
