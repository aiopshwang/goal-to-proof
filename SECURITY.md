# Security Policy

## Supported versions

Security fixes are provided for the latest released version of Goal to Proof.

## Reporting a vulnerability

Please report vulnerabilities privately through GitHub's **Report a vulnerability** flow in the Security tab of this repository. Include the affected version, impact, reproduction steps, and any suggested mitigation.

Do not disclose a vulnerability in a public issue or discussion before a fix is available. Do not include secrets, personal data, or data from systems you do not own or have permission to test.

You should receive an initial response within seven days. Timelines for validation and remediation depend on severity and reproducibility.

## Scope

The core plugin is an instruction skill and declares no MCP servers, apps, hooks, or background network services. Relevant reports include instruction-driven unsafe boundary expansion, misleading verification behavior, manifest or installation issues that create unintended access, and vulnerabilities in project-owned tooling.

Security issues in Codex, Claude Code, GitHub, package managers, or other third-party hosts should be reported to their respective maintainers.
