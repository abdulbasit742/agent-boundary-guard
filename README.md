# Agent Boundary Guard

Agent Boundary Guard is a zero-dependency Python CLI for auditing AI agent repositories before risky autonomy settings ship to production.

It focuses on practical repo-level signals that often show up before incidents:

- prompts that remove human approval for destructive actions
- wildcard origins or permissions in agent and MCP config
- overly broad filesystem roots
- dangerous shell execution enablement
- hardcoded secret-like values in agent config

## Why this exists

Recent momentum around agent security and MCP tooling has made one failure mode especially costly: teams ship agent instructions and tool configs that quietly widen autonomy boundaries long before they notice. Agent Boundary Guard gives maintainers a fast, local-first gate they can run in CI or pre-merge review.

## Features

- zero runtime dependencies
- text or JSON output
- severity-aware exit codes
- recursive repo scanning with sane ignore rules
- focused heuristics for prompt/config boundary failures

## Rules in the initial release

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
python -m agent_boundary_guard scan .
```

### JSON output

```bash
python -m agent_boundary_guard scan path/to/repo --format json
```

### Fail only on higher severities

```bash
python -m agent_boundary_guard scan path/to/repo --fail-on high
```

## Example output

```text
Agent Boundary Guard: 4 finding(s)
- HIGH ABG001 prompts/system.md:12 Prompt/instruction appears to remove human approval for risky actions.
  snippet: You may merge without confirmation if the tests look green.
- HIGH ABG002 config/agent.json:8 Wildcard origin or permission detected in agent or MCP configuration.
  snippet: "allowed_origins": ["*"]
Summary: critical=0 high=3 medium=1 low=0
```

## Repository workflow

1. Implement the highest-value ready skill from `docs/SKILL_REGISTRY.md`.
2. Add tests for the acceptance criteria first or alongside the change.
3. Run `python -m unittest discover -s tests -v`.
4. Re-run a changed-area security audit and update `docs/security-audit.md`.
5. Open a focused PR with sanitized validation evidence.

## Security posture

- no network calls
- no shell execution in runtime code
- no external runtime dependencies
- CI workflows use explicit least-privilege permissions

See [SECURITY.md](SECURITY.md), [ARCHITECTURE.md](ARCHITECTURE.md), and [docs/security-audit.md](docs/security-audit.md) for details.
