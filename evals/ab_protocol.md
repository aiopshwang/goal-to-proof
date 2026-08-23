# Opt-in Codex A/B protocol

The live runner compares the same synthetic task in two temporary environments:

- **baseline** — a fresh temporary `CODEX_HOME` with no Goal to Proof skill;
- **candidate** — another fresh temporary `CODEX_HOME` containing only the canonical
  `skills/goal-to-proof` package.

Both arms ignore user configuration and project rules, receive the same isolation preamble, use a
workspace-write sandbox, start from identical committed fixtures, and run the same oracles. The
runner uses subprocess argument arrays with `shell=False`; case definitions cannot provide a
single shell command string.

The checked-in fixtures and oracle argument arrays are trusted executable evaluation code. Oracle
commands run after the model call and outside the Codex sandbox. `shell=False` prevents shell-string
interpretation; it is not a sandbox and does not make a reviewed command harmless. Run live cases
only from a reviewed, pinned revision, preferably inside a disposable no-egress environment.

## Preview without a model call

The output directory must be new. The runner never overwrites prior evidence.

```bash
python scripts/run_ab_eval.py \
  --case B07 \
  --case B08 \
  --case B09 \
  --output /tmp/goal-to-proof-ab-plan \
  --dry-run
```

This records the arm commands, fixtures, and oracles without invoking Codex.

## Run selected live cases

Codex must already be installed and able to authenticate through a host-supported external
credential broker or operating-system keychain. The runner never reads or copies credential files
into its temporary homes. If the host cannot authenticate Codex without such a file, use
`--dry-run`; do not place credentials in an agent-readable evaluation home.

```bash
python scripts/run_ab_eval.py \
  --case B07 \
  --case B08 \
  --case B09 \
  --output /tmp/goal-to-proof-ab
```

Use `--model MODEL` to pin a model and `--arm candidate` for a candidate-only smoke run. `--all`
with the default `--arm both` makes 48 model calls, so it is deliberately opt-in.

Each arm records:

- the redacted command shape and raw JSONL events;
- stderr and the final response;
- a unified workspace diff and final file hashes;
- every oracle command and result;
- hard-gate failures and pending manual criteria.

The case directory also contains a side-by-side comparison. Reviewers should inspect the events,
diff, command log, final answer, and semantic criteria—not only the aggregate machine status.

## Full aspirational gate

A fully reviewed candidate release should meet all of these conditions:

- all 24 candidate arms pass every machine oracle;
- all pending manual criteria are reviewed and pass;
- no candidate arm trips a hard gate;
- all six negative-trigger cases remain direct and low-ceremony;
- the candidate is no worse than baseline on negative cases and materially improves closure on
  positive and behavior cases;
- model, Codex version, operating system, and review identity are recorded with the result.

No live result is bundled or claimed by this repository unless its logs and review state are
actually present.

## Environment controls and limitations

The runner separates skill files, user config, project rules, workspaces, and temporary homes for
the two arms. This is not a claim of strong credential isolation: host brokers, keychains, Codex,
and the operating system remain outside the harness. The runner also does not make model inference
deterministic. Results can vary with the Codex binary, model snapshot, provider behavior, operating
system, installed tools, account policy, and authentication backend. `workspace-write` plus the
isolation prompt is a safety boundary, but environments that require a strict no-egress guarantee
should also block network access at the container or operating system layer.

Raw event logs may contain fixture content or model output. Fixtures use fake values only, but
result directories should still be handled as evaluation evidence and reviewed before sharing.
