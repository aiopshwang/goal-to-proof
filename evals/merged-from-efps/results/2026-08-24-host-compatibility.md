# Host compatibility record

This record defines “compatible” as successful package validation, discovery, isolated project installation, and installed-copy validation. It does not claim identical model behavior, perfect activation, or support for every host version and operating system.

## Environment

- **Date:** 2026-08-24
- **Repository version:** 0.1.0 pre-release
- **Skill bundle SHA-256:** `5c3f39089250a3f7cf271137109b0d678a09c8b908ba004a35196c5d6de644e8`, reproducible with `scripts/fingerprint_skill.py` in the original `evidence-first-problem-solving` repository
- **Operating system:** Windows
- **Agent Skills CLI:** 1.5.23
- **Codex CLI:** 0.53.0
- **Claude Code:** 2.1.152

All installs used isolated temporary Git projects and copied the skill. They did not modify the user's global Codex or Claude Code configuration. Machine-local paths and tool startup noise are omitted from this public summary.

## Shared package discovery

```text
npx --yes skills add . --list
exit 0
Found 1 skill: evidence-first-problem-solving
```

This proves that the repository's shared Agent Skills layout was discoverable by the tested CLI version. It does not prove runtime activation.

## Codex

```text
npx --yes skills add <inspected-local-repository> \
  --skill evidence-first-problem-solving --agent codex --copy -y
exit 0
Installed 1 skill for Codex at project scope
```

```text
npx --yes skills list --json --agent codex
exit 0
Exactly one project skill named evidence-first-problem-solving; agents: [Codex]
```

The copied skill then passed the skill-creator quick validator in UTF-8 mode. The repository's `.codex-plugin/plugin.json` independently passed the plugin-creator validator.

**Verdict:** package discovery and isolated project installation proved for the versions and environment above.

## Claude Code

```text
npx --yes skills add <inspected-local-repository> \
  --skill evidence-first-problem-solving --agent claude-code --copy -y
exit 0
Installed 1 skill for Claude Code at project scope
```

```text
npx --yes skills list --json --agent claude-code
exit 0
Exactly one project skill named evidence-first-problem-solving; agents: [Claude Code]
```

The copied skill passed the same UTF-8 skill validator. The native Claude plugin and marketplace metadata also passed:

```text
claude plugin validate . --strict
exit 0
Validation passed
```

**Verdict:** shared-skill discovery, isolated project installation, and native plugin metadata validation proved for the versions and environment above.

## Not proved or not assessed

- Implicit and explicit activation by live Codex or Claude models was not run in these isolated projects.
- Equivalent reasoning behavior across hosts was not assessed.
- A native Claude marketplace install was not performed because it would change persistent host settings; only strict metadata validation was performed.
- macOS, Linux, older host versions, future host versions, global installation, update, and uninstall were not assessed.
- Remote GitHub installation is not covered by this pre-publication record and must be checked after the repository is public.
