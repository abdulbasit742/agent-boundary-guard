from __future__ import annotations

from dataclasses import dataclass
import re


@dataclass(frozen=True)
class Rule:
    rule_id: str
    severity: str
    message: str
    pattern: re.Pattern[str]
    scope: str = "all"


PLACEHOLDER_MARKERS = (
    "example",
    "placeholder",
    "changeme",
    "replace_me",
    "your_",
    "dummy",
    "sample",
    "fake",
    "redacted",
    "test_",
)


RULES = (
    Rule(
        rule_id="ABG001",
        severity="high",
        message="Prompt/instruction appears to remove human approval for risky actions.",
        pattern=re.compile(
            r"(?i)(without (approval|confirmation)|never ask for confirmation|merge without review|auto-merge|autonomously execute|delete .* without confirmation)"
        ),
        scope="prompt",
    ),
    Rule(
        rule_id="ABG002",
        severity="high",
        message="Wildcard origin or permission detected in agent or MCP configuration.",
        pattern=re.compile(
            r"(?i)(allowed_origins?|cors|permissions?|origins?)\s*[=:].*(\*|write-all|all)"
        ),
        scope="config",
    ),
    Rule(
        rule_id="ABG003",
        severity="medium",
        message="Overly broad filesystem root detected in agent or MCP configuration.",
        pattern=re.compile(
            r"(?i)(allowed_paths?|roots?|directories|filesystem)\s*[=:].*((['\"]/(['\"]|\s|,|\]))|(['\"]~(['\"]|\s|,|\]))|(['\"]\.\.(['\"]|\s|,|\])))"
        ),
        scope="config",
    ),
    Rule(
        rule_id="ABG004",
        severity="high",
        message="Dangerous shell or command execution enablement detected.",
        pattern=re.compile(
            r"(?i)((shell|command|exec|subprocess)[^\n]{0,30}[=:]\s*(true|always|enabled|allow)|bash -lc|sh -c|eval\()"
        ),
        scope="config",
    ),
    Rule(
        rule_id="ABG005",
        severity="high",
        message="Hardcoded secret-like value detected in configuration.",
        pattern=re.compile(
            r"(?i)(api[_-]?key|token|secret|password)\s*[=:]\s*['\"]?[A-Za-z0-9_\-]{8,}"
        ),
        scope="config",
    ),
)
