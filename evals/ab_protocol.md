# Opt-in live A/B protocol

The live runner gives the same synthetic task to two agents that differ in exactly one way: one
can reach the skill, the other cannot.

- **baseline** — no Goal to Proof skill available;
- **candidate** — the canonical `skills/goal-to-proof` package available, and nothing else changed.

How the skill reaches the candidate depends on the host:

| Host | Candidate receives | Baseline receives |
| --- | --- | --- |
| Codex | `.agents/skills/goal-to-proof/` copied into the temporary workspace | nothing |
| Claude Code | `--plugin-dir <repository>` | no plugin flag |

Both arms receive the same isolation preamble, start from identical committed fixtures, run in a
fresh temporary workspace, and are scored by the same oracles. The runner uses subprocess argument
arrays with `shell=False`, and the prompt travels on stdin rather than in the argument array; case
definitions cannot provide a single shell command string.

## Prompt fairness

`--prompt-mode neutral` gives both arms a prompt that does not name the skill. This is the honest
A/B condition: an explicit prompt would tell the baseline to use a skill it does not have, and it
would also hide whether the skill triggers on its own. Activation is therefore part of what gets
measured, and every candidate run records whether the skill was actually loaded.

`--prompt-mode explicit` uses the original prompts that name the skill. Those belong to the
activation suite and to a secondary "does the content help once it is in play" comparison. A
result from the explicit mode is never reported as an A/B.

## What the harness controls, and what it only holds constant

The two arms must be *identical*, not *pristine*. The runner keeps the host's own Codex or Claude
credential and user configuration and loads them identically in both arms, then records them.
Configuration cannot produce the contrast; it bounds how far the result generalizes.

Two host facts make the older, stricter isolation impossible rather than merely inconvenient:

- Redirecting `HOME` and `CODEX_HOME` into a temporary directory answers `401`. Codex documents
  that `--ignore-user-config` still authenticates through `CODEX_HOME`; the credential is not
  copied anywhere.
- **`--ignore-user-config` silently overrides `--sandbox`.** With that flag, `-s workspace-write`
  still resolves to `sandbox: read-only`, and on Windows a read-only Codex session cannot even
  read its own workspace. A run configured that way produces two crippled arms and a meaningless
  comparison.

Because of the second point the runner reads the sandbox mode back out of the Codex header and
marks any run that did not resolve to `workspace-write` as **invalid**. Invalid runs are excluded
from every rate and reported separately.

The checked-in fixtures and oracle argument arrays are trusted executable evaluation code. Oracle
commands run after the model call and outside the agent sandbox. `shell=False` prevents
shell-string interpretation; it is not a sandbox and does not make a reviewed command harmless.
Run live cases only from a reviewed, pinned revision, preferably inside a disposable no-egress
environment.

## Blinding

The blind judge reads only the two final responses. Every mention of the skill is redacted, the
responses are labelled X and Y in an order the arm cannot predict, and the mapping is written to a
separate file the judge never receives. The temporary workspace is named `ab-eval-…` for the same
reason: a directory named after the arm would appear in the agent's own output and tell the judge
which response it was reading.

Codex runs are judged by Claude and Claude runs by Codex, so no model grades its own work.

## Preview without a model call

The output directory must be new. The runner never overwrites prior evidence.

```bash
python scripts/run_ab_eval.py \
  --case B07 --case B08 --case B09 \
  --host codex --prompt-mode neutral \
  --output /tmp/goal-to-proof-ab-plan \
  --dry-run
```

This records the arm commands, fixtures, prompts, and oracles without invoking a model.

## Run the live matrix

```bash
python scripts/run_ab_eval.py \
  --case B07 --case B08 --case B09 \
  --host codex --prompt-mode neutral --reps 3 \
  --output /tmp/goal-to-proof-ab/codex

python scripts/run_ab_eval.py \
  --case B07 --case B08 --case B09 \
  --host claude --model sonnet --prompt-mode neutral --reps 3 \
  --output /tmp/goal-to-proof-ab/claude
```

Three repetitions per cell is the minimum that distinguishes an effect from a coin flip, and even
three is small: a one-run difference is not an effect and must not be reported as one.

Then aggregate and judge:

```bash
python scripts/aggregate_ab.py /tmp/goal-to-proof-ab/codex
python scripts/blind_judge.py /tmp/goal-to-proof-ab/codex --judge claude
python scripts/blind_judge.py /tmp/goal-to-proof-ab/claude --judge codex
```

Each run records the command shape, the full session transcript, the final response, a unified
workspace diff, file hashes, every oracle command with both its declared and resolved argument
array, hard-gate failures, the resolved sandbox mode, and whether the skill was activated.

## Metrics

Fixed before any run, in `docs/superpowers/specs/2026-08-28-live-ab-eval-design.md`:

| Metric | Meaning | Source |
| --- | --- | --- |
| M1 | machine-oracle pass rate | oracles |
| M2 | hard-gate violations | gates |
| M3 | unsupported completion claims | blind judge (`H04` is its machine proxy) |
| M4 | asking for permission the task already granted | final response |
| M5 | candidate runs that actually loaded the skill | transcript |

A candidate cell with M5 below 3/3 is an activation finding, not a behavioral one, and is reported
as such rather than counted as a success or a null.

## Limitations

The runner does not make model inference deterministic. Results vary with the Codex or Claude
binary, the model snapshot, provider behavior, the operating system, installed tools, account
policy, and the authentication backend. `workspace-write` plus the isolation prompt is a safety
boundary; environments needing a strict no-egress guarantee should also block network access at
the container or operating-system layer.

Raw transcripts may contain fixture content or model output. Fixtures use fake values only, but
result directories should still be handled as evaluation evidence and reviewed before sharing.

No live result is claimed by this repository unless its logs and review state are actually present
under `evals/results/`.
