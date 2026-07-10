from __future__ import annotations

import argparse
import json
import sys

from .scanner import exceeds_threshold, scan_path, summarize


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="agent-boundary-guard")
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan = subparsers.add_parser("scan", help="Scan a repository or file for risky agent boundaries.")
    scan.add_argument("target", help="Directory or file to scan.")
    scan.add_argument("--format", choices=("text", "json"), default="text")
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


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "scan":
        findings = scan_path(args.target, max_size_kb=args.max_size_kb)
        summary = summarize(findings)
        finding_dicts = [finding.to_dict() for finding in findings]

        if args.format == "json":
            payload = {
                "target": args.target,
                "finding_count": len(finding_dicts),
                "summary": summary,
                "findings": finding_dicts,
            }
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print(format_text(finding_dicts, summary))

        return 1 if exceeds_threshold(findings, args.fail_on) else 0

    parser.error("Unsupported command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
