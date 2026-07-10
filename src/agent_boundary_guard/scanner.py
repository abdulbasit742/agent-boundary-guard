from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Iterable

from .models import Finding
from .rules import PLACEHOLDER_MARKERS, RULES, Rule

IGNORED_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "venv",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    "node_modules",
    "dist",
    "build",
}

TEXT_EXTENSIONS = {
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".ini",
    ".cfg",
    ".md",
    ".txt",
    ".py",
}

SPECIAL_FILENAMES = {
    ".mcp.json",
    ".clinerules",
    ".cursorignore",
    ".env.example",
}

SEVERITY_ORDER = {"low": 1, "medium": 2, "high": 3, "critical": 4}


def is_prompt_like(relative_path: str) -> bool:
    lowered = relative_path.lower()
    return any(token in lowered for token in ("prompt", "system", "instruction", "agent", "rules", ".md", ".txt"))


def is_config_like(relative_path: str) -> bool:
    lowered = relative_path.lower()
    return any(token in lowered for token in ("config", "mcp", "agent", ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".py"))


def should_scan(path: Path) -> bool:
    if path.name in SPECIAL_FILENAMES:
        return True
    return path.suffix.lower() in TEXT_EXTENSIONS


def is_placeholder_line(line: str) -> bool:
    lowered = line.lower()
    return any(marker in lowered for marker in PLACEHOLDER_MARKERS)


def candidate_files(root: Path, max_size_kb: int) -> Iterable[Path]:
    max_bytes = max_size_kb * 1024
    if root.is_file() and should_scan(root) and root.stat().st_size <= max_bytes:
        yield root
        return

    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in IGNORED_DIRS for part in path.parts):
            continue
        if not should_scan(path):
            continue
        if path.stat().st_size > max_bytes:
            continue
        yield path


def match_rule(rule: Rule, relative_path: str, line: str) -> bool:
    if rule.scope == "prompt" and not is_prompt_like(relative_path):
        return False
    if rule.scope == "config" and not is_config_like(relative_path):
        return False
    if rule.rule_id == "ABG005" and is_placeholder_line(line):
        return False
    return bool(rule.pattern.search(line))


def scan_path(target: str | Path, max_size_kb: int = 256) -> list[Finding]:
    root = Path(target)
    findings: list[Finding] = []
    for path in candidate_files(root, max_size_kb=max_size_kb):
        relative_path = str(path.relative_to(root)) if root.is_dir() else path.name
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for index, line in enumerate(text.splitlines(), start=1):
            for rule in RULES:
                if match_rule(rule, relative_path, line):
                    findings.append(
                        Finding(
                            rule_id=rule.rule_id,
                            severity=rule.severity,
                            message=rule.message,
                            path=relative_path,
                            line=index,
                            snippet=line.strip()[:200],
                        )
                    )
    return sorted(
        findings,
        key=lambda finding: (
            -SEVERITY_ORDER.get(finding.severity, 0),
            finding.path,
            finding.line,
            finding.rule_id,
        ),
    )


def summarize(findings: list[Finding]) -> dict[str, int]:
    counts = Counter(finding.severity for finding in findings)
    return {
        "critical": counts.get("critical", 0),
        "high": counts.get("high", 0),
        "medium": counts.get("medium", 0),
        "low": counts.get("low", 0),
    }


def exceeds_threshold(findings: list[Finding], fail_on: str) -> bool:
    threshold = SEVERITY_ORDER[fail_on]
    return any(SEVERITY_ORDER.get(finding.severity, 0) >= threshold for finding in findings)
