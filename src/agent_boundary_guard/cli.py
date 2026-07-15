from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from .models import Finding
from .sarif import format_sarif
from .scanner import exceeds_threshold, scan_path, summarize


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="agent-boundary-guard")
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan = subparsers.add_parser("scan", help="Scan a repository or file for risky agent boundaries.")
    scan.add_argument("target", help="Directory or file to scan.")
    scan.add_argument("--format", choices=("text", "json", "sarif"), default="text")
    scan.add_argument("--output", help="Write the report to this file instead of stdout.")
    scan.add_argument("--max-size-kb", type=int, default=256)
    scan.add_argument("--fail-on", choices=("low", "medium", "high", "critical"), default="medium")
    return parser


def format_text(findings: list[dict[str, object]], summary: dict[str, int]) -> str:
    lines = [f"Agent Boundary Guard: {len(findings)} finding(s)"]
    for finding in findings:
        lines.append(
            f"- {str(finding['severity']).upper()} {finding['rule_id']} {finding['path']}:{finding['line']} {finding['message']}"
        )
        lines.append(f"  snippet: {finding['snippet']}")
    lines.append(
        "Summary: "
        + " ".join(f"{severity}={count}" for severity, count in summary.items())
    )
    return "\n".join(lines)


def _render_report(
    report_format: str,
    target: str,
    finding_dicts: list[dict[str, object]],
    findings: list[Finding],
    summary: dict[str, int],
) -> str:
    if report_format == "json":
        payload = {
            "target": target,
            "finding_count": len(finding_dicts),
            "summary": summary,
            "findings": finding_dicts,
        }
        return json.dumps(payload, indent=2, sort_keys=True)
    if report_format == "sarif":
        return format_sarif(findings, target=target)
    return format_text(finding_dicts, summary)


def _write_report(report: str, output: str | None) -> bool:
    if output is None:
        print(report)
        return True

    destination = Path(output)
    try:
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(report + "\n", encoding="utf-8")
    except OSError as exc:
        print(f"agent-boundary-guard: unable to write report: {exc}", file=sys.stderr)
        return False
    return True


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "scan":
        findings = scan_path(args.target, max_size_kb=args.max_size_kb)
        summary = summarize(findings)
        finding_dicts = [finding.to_dict() for finding in findings]
        report = _render_report(args.format, args.target, finding_dicts, findings, summary)

        if not _write_report(report, args.output):
            return 2
        return 1 if exceeds_threshold(findings, args.fail_on) else 0

    parser.error("Unsupported command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
