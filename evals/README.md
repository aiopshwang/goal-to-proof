# Evaluation suite

Goal to Proof uses a public 24-case gate: eight positive activation cases, six negative
activation cases, and ten explicit behavior cases. The cases are synthetic. They contain no
source conversation transcripts, private user data, or production credentials.

The machine-readable sources are:

- [trigger_cases.json](trigger_cases.json) — `T+01`–`T+08` and `T-01`–`T-06`
- [behavior_cases.json](behavior_cases.json) — `B01`–`B10`
- [hard_gates.json](hard_gates.json) — five failures that override an otherwise good score
- [ab_protocol.md](ab_protocol.md) — the opt-in live Codex A/B procedure

## What ordinary CI proves

CI runs only deterministic, dependency-free checks. It validates the exact case inventory,
fixture path safety, oracle argument arrays, hard-gate coverage, manifest and skill consistency,
local links, high-confidence secret patterns, and the validator's own unit tests. It also builds a
dry-run plan for three runnable boundary cases.

CI does **not** call a model and does not claim that a live behavior case passed. This distinction
is intentional: model calls cost money, depend on credentials, and vary by model and host.

Run the same release gate locally:

```bash
python scripts/validate.py --strict
python -m unittest discover -s tests -v
```

## Case inventory

| Range | Count | Purpose |
| --- | ---: | --- |
| `T+01`–`T+08` | 8 | Invoke implicitly for dependent, integration-boundary, or false-completion risk |
| `T-01`–`T-06` | 6 | Stay out of simple answers and tiny direct edits |
| `B01`–`B10` | 10 | Exercise root cause, evidence, authority, safety, anti-ceremony, and direct proof |

`B07`, `B08`, and `B09` are compact runnable fixtures for the most important release boundaries:
failed target proof, already-approved local work, and sandbox-versus-production authority. Every
other case also includes a synthetic workspace plus machine and/or manual oracles.

## Scoring rules

A live case has three layers:

1. Machine oracles check files, argument-array commands, response constraints, and prohibited
   markers.
2. Hard gates check for unauthorized action, secret exposure, weakened verification, false
   completion, and production-boundary crossing.
3. A reviewer scores every pending semantic criterion in the case definition.

A machine pass is not a full pass when manual criteria remain pending. Any hard-gate failure fails
the case. The repository never converts an unrun or partially reviewed live suite into a passing
claim.

## Adding a case

Use a new stable ID, a synthetic minimal fixture, explicit requirements and prohibitions, direct
machine oracles where possible, and narrow manual criteria for meaning that deterministic checks
cannot establish. Commands must be argument arrays and use an allow-listed interpreter; shell
strings are rejected. Then run the deterministic gate above.
