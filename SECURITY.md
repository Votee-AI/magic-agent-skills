# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability, please report it through [GitHub Security Advisories](https://github.com/Votee-AI/magic-agent-skills/security/advisories/new).

**Do not open a public issue for security vulnerabilities.**

We will acknowledge your report within 72 hours and provide a timeline for a fix.

## Supported Versions

| Version | Supported |
|---------|-----------|
| Latest release | Yes |
| Older releases | No |

## Scope

**In scope:**
- Skills (SKILL.md content, patterns, and procedures)
- Reference scripts (`scripts/*.py`)
- CI/CD configurations
- CLI installer

**Out of scope:**
- User-modified forks or custom adaptations
- Upstream dependencies (report to the respective project)
- Eval test data and fixtures

## A Note on Scripts

Scripts in this project are **reference implementations** — the AI agent reads them to learn patterns, then writes its own adapted code. A security issue in a reference script affects code patterns that users may copy, not a running service. We still treat these seriously and will update patterns promptly.

## Contact

For security matters that cannot go through GitHub Security Advisories: tech@votee.com
