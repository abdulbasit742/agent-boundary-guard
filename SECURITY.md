# Security Policy

## Supported versions

This project is in active early development. The latest `main` branch receives security fixes first.

## Reporting

Please report vulnerabilities privately to the repository owner. Do not publish exploit details, live secrets, or reproduction steps that would put downstream users at risk.

## Secure usage guidance

- treat findings as review signals, not autonomous enforcement of policy intent
- pair this scanner with human code review for destructive tool access
- avoid scanning repositories that intentionally store real credentials

## Current security baseline

- zero external runtime dependencies
- no runtime shell execution
- no outbound network access
- least-privilege CI workflows
- changed-area security audit documented in `docs/security-audit.md`
