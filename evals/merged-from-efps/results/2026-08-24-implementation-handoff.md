# Forward test: safe record importer implementation and handoff

This is a bounded public record of one synthetic forward test. It is not a benchmark, a production result, or evidence of universal reliability.

## Run identity

- **Date:** 2026-08-24
- **Release under evaluation:** 0.1.0 pre-release
- **Skill bundle SHA-256:** `5c3f39089250a3f7cf271137109b0d678a09c8b908ba004a35196c5d6de644e8`, reproducible with `scripts/fingerprint_skill.py` in the original `evidence-first-problem-solving` repository
- **Fixture:** [`safe-record-import`](../fixtures/safe-record-import/scenario.yaml)
- **Rubric:** [`implementation-handoff.yaml`](../rubrics/implementation-handoff.yaml)
- **Acting runner:** independent Codex subagent; model identifier was not exposed in the durable run artifact
- **Evaluator:** a different Codex subagent that did not author the skill or fixture; model identifier was not exposed in the durable run artifact
- **Permission envelope:** copy the fixture to an isolated working directory; modify only the copy; standard library implementation; no internet or external data
- **Activation verdict:** correct—the task combined consequential validation, atomic publication, failure safety, privacy, verification, and operational handoff requirements

The evaluator did not steer the acting run. The actor was not shown the rubric or intended implementation. The full working copy and handoff stayed in an ephemeral local workspace because they contained machine-local paths; this sanitized record preserves the observable outcome.

## Source integrity

Hashes were captured by the orchestrating process before delegation and again after the acting run and evaluation. Every source-fixture hash matched. The copied `acceptance.md`, `records.csv`, and existing test also matched their source counterparts.

| File | SHA-256 |
|---|---|
| `scenario.yaml` | `fd234c9f3330073d894d658de198d12017aac75b90297e83c49e2fb4941d58fa` |
| `acceptance.md` | `918d5b24fcaa778878716fb4dcc86f37214e463f6e99f82c7bd00e60a8a5ad5b` |
| `importer.py` | `ac71c0b88e7eb6e9c331167480788b2d35ccdca2845c723dc5477a7335e8b136` |
| `records.csv` | `d9370dd20c92891e2d8bce6b4dea7d721f5372f76ad56f8b1387a1a40ab88187` |
| `test_importer_existing.py` | `bcdaa33cdbbbb9d8d4c16c64d50c7211940c8c0ab820e7aca7380c81ee068977` |

## Working-copy diff summary

- Replaced the incomplete importer with full-input validation and aggregate row-safe diagnostics.
- Enforced non-empty unique identifiers, real ISO calendar dates, and finite non-negative decimal amounts.
- Produced deterministic UTF-8 JSON bytes.
- Staged output beside the destination, flushed and synchronized it, then published with `os.replace` and cleaned temporary state on failure.
- Added standard-library tests for success, combined invalid rows, privacy, destination preservation, temporary cleanup, deterministic reruns, header/column errors, CLI status, and simulated replacement failure.
- Added a handoff with preflight, success/failure signals, rollback, verification, and limitations.

The supplied input and existing test were not changed.

## Independent score

**24/24; recommended threshold: 19. Critical failures: none.**

| Criterion | Score | Evaluator evidence |
|---|---:|---|
| Full-input validation | 4/4 | Read and validated all rows, accumulated every invalid row, and wrote only after successful validation. |
| Domain rules | 4/4 | Covered blank and duplicate IDs, real calendar dates, negative and non-finite decimals, and nonnumeric input. |
| Atomic, idempotent output | 4/4 | Same-directory staging, flush and `fsync`, `os.replace`, cleanup, and exact-byte rerun test. |
| Failure safety | 4/4 | Non-zero CLI status plus byte-for-byte destination preservation for validation and replacement failure. |
| Verification depth | 4/4 | Exercised success, combined failures, privacy, preservation, cleanup, repeatability, malformed structure, and the supplied test. |
| Operational handoff | 4/4 | Included preflight, signals, rollback, changed artifacts, exact commands and results, and honest limits. |

## Independent verification output

The evaluator reran the working copy without bytecode or pytest cache generation:

```text
python -B -m unittest discover -v
Ran 6 tests in 0.121s
OK
```

```text
python -B -m pytest -q -p no:cacheprovider
7 passed, 8 subtests passed in 0.17s
```

An independent preflight of the supplied invalid input returned status `1`, reported rows 2, 3, and 4, created no destination, and left zero importer temporary files. The orchestrator separately reproduced `7 passed, 8 subtests passed` and confirmed the post-run source hashes above.

## Limitations

- Atomic replacement relies on the operating system's `os.replace` contract; power-loss and filesystem faults were not injected.
- Concurrent writers, source/destination aliasing, very large inputs, permission preservation, and metadata preservation were not assessed.
- The full working copy and raw tool transcript are not public artifacts.
- The fixture is synthetic. A perfect rubric score establishes only that this run met the fixture's observable criteria, not general implementation quality or production safety.
