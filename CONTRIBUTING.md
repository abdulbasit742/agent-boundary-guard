# Contributing

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Validation

Run the full local validation set before opening a PR:

```bash
python -m unittest discover -s tests -v
python -m agent_boundary_guard scan tests/fixtures/risky_repo --format json
```

## Contribution rules

- keep runtime dependencies at zero unless there is a security-critical reason
- add or update tests with every behavior change
- document user-visible changes in `README.md`
- update `docs/security-audit.md` for every changed-area audit
- keep PRs small and focused

## Secure development notes

- never commit real secrets to fixtures or docs
- use placeholders such as `example-token` or `replace_me`
- do not expand CI permissions without documenting why
