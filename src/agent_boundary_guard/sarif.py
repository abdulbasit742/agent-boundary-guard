from __future__ import annotations

from hashlib import sha256
from importlib.metadata import PackageNotFoundError, version
import json
from pathlib import PurePosixPath

from .models import Finding
from .rules import RULES, Rule
from .scanner import summarize

SARIF_SCHEMA = "https://json.schemastore.org/sarif-2.1.0.json"
SARIF_VERSION = "2.1.0"
TOOL_NAME = "Agent Boundary Guard"
TOOL_URI = "https://github.com/abdulbasit742/agent-boundary-guard"

SARIF_LEVELS = {
    "critical": "error",
    "high": "error",
    "medium": "warning",
    "low": "note",
}

SECURITY_SEVERITY = {
    "critical": "9.5",
    "high": "8.0",
    "medium": "5.0",
    "low": "2.0",
}


def _tool_version() -> str:
    try:
        return version("agent-boundary-guard")
    except PackageNotFoundError:
        return "0.2.0"


def _sarif_level(severity: str) -> str:
    return SARIF_LEVELS.get(severity, "warning")


def _normalize_uri(path: str) -> str:
    normalized = path.replace("\\", "/").lstrip("./")
    return str(PurePosixPath(normalized))


def _rule_descriptor(rule: Rule) -> dict[str, object]:
    return {
        "id": rule.rule_id,
        "name": rule.rule_id,
        "shortDescription": {"text": rule.message},
        "fullDescription": {"text": rule.message},
        "defaultConfiguration": {"level": _sarif_level(rule.severity)},
        "help": {
            "text": (
                f"{rule.message} Review the matched agent instruction or configuration "
                "and narrow the boundary before deployment."
            )
        },
        "properties": {
            "precision": "medium",
            "security-severity": SECURITY_SEVERITY.get(rule.severity, "5.0"),
            "severity": rule.severity,
            "tags": ["security", "ai-agent", "mcp"],
        },
    }


def _fingerprint(finding: Finding) -> str:
    material = "\0".join((finding.rule_id, _normalize_uri(finding.path), finding.snippet))
    return sha256(material.encode("utf-8")).hexdigest()


def _result(finding: Finding, rule_index: dict[str, int]) -> dict[str, object]:
    return {
        "ruleId": finding.rule_id,
        "ruleIndex": rule_index[finding.rule_id],
        "level": _sarif_level(finding.severity),
        "message": {"text": finding.message},
        "locations": [
            {
                "physicalLocation": {
                    "artifactLocation": {"uri": _normalize_uri(finding.path)},
                    "region": {"startLine": max(1, finding.line)},
                }
            }
        ],
        "partialFingerprints": {
            "primaryLocationLineHash": _fingerprint(finding),
        },
        "properties": {"severity": finding.severity},
    }


def build_sarif(findings: list[Finding], target: str | None = None) -> dict[str, object]:
    descriptors = [_rule_descriptor(rule) for rule in RULES]
    rule_index = {rule.rule_id: index for index, rule in enumerate(RULES)}
    run_properties: dict[str, object] = {
        "findingCount": len(findings),
        "summary": summarize(findings),
    }
    if target is not None:
        run_properties["target"] = target

    run: dict[str, object] = {
        "tool": {
            "driver": {
                "name": TOOL_NAME,
                "informationUri": TOOL_URI,
                "semanticVersion": _tool_version(),
                "rules": descriptors,
            }
        },
        "results": [_result(finding, rule_index) for finding in findings],
        "invocations": [{"executionSuccessful": True}],
        "properties": run_properties,
    }

    return {
        "$schema": SARIF_SCHEMA,
        "version": SARIF_VERSION,
        "runs": [run],
    }


def format_sarif(findings: list[Finding], target: str | None = None) -> str:
    return json.dumps(build_sarif(findings, target=target), indent=2, sort_keys=True)
