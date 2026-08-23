# Contributing to Goal to Proof

Thank you for helping make AI-agent completion claims more trustworthy. Goal to Proof is intentionally small: it is a closure contract, not a general-purpose agent methodology. Contributions should sharpen that contract without turning simple work into ceremony.

## Good contribution areas

- trigger cases that distinguish non-trivial closure work from simple requests;
- proof patterns for a real target boundary;
- fixes to ambiguous, conflicting, or over-broad instructions;
- package validation across an explicitly named host and version;
- documentation that makes limitations easier to understand;
- accessibility, security, privacy, and install-path improvements.

Large new workflow systems, domain handbooks, unrelated tools, or autonomous goal-setting behavior are unlikely to fit this repository.

## Before opening a change

1. Search existing issues and pull requests.
2. Open an issue first if the change alters the product boundary or user/agent authority split.
3. Keep examples fictional and free of secrets, personal data, or raw conversation material.
4. For behavior changes, write down the failure mode, desired behavior, and a negative case where the skill should not activate.

## Local workflow

Fork the repository, create a focused branch, and install only the development dependencies you need. Run the repository checks before opening a pull request:

```bash
python3 scripts/validate.py
```

When the corresponding tools are available, also validate the native packages:

```bash
skills-ref validate ./skills/goal-to-proof
claude plugin validate . --strict
npx -y skills@latest add . --list
```

Host installation is a separate evidence layer. If you claim that a host works, include the host and version, exact install/invocation path, isolated configuration used, observation made, and any untested boundary. A manifest validator alone does not prove runtime compatibility.

## Behavioral change checklist

A behavior pull request should include:

- one positive case that needs the proposed behavior;
- one adjacent negative case that should remain lightweight or inactive;
- the exact completion claim and matching observation;
- an approval-boundary case when external or irreversible action is relevant;
- wording that remains useful outside software development when the principle is cross-domain.

Avoid tests that merely search for preferred words in a response. Evaluate whether the agent preserved authority, reached the relevant boundary, and described proof honestly.

## Documentation style

- Lead with the result or decision.
- Use plain language and define specialized terms on first use.
- Separate observed fact, inference, and unknown.
- Link to primary or official sources for changing technical facts.
- Do not publish personal prompts or imply that aggregate source-corpus counts are benchmark results.
- Do not claim universal compatibility, productivity gains, or success rates without reproducible evidence.

## Pull request expectations

Keep the pull request focused and explain:

- what failure it prevents;
- what changed;
- how you verified the latest state;
- what remains unverified;
- whether the change affects activation, authority, packaging, or public claims.

By contributing, you agree that your contribution is licensed under the repository's MIT License and that you will follow the [Code of Conduct](CODE_OF_CONDUCT.md).
