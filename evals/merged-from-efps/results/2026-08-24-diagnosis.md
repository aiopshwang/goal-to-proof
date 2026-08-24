# Forward test: API latency diagnosis

This is a bounded public record of one synthetic forward test. It is not a benchmark, a production result, or evidence of universal reliability.

## Run identity

- **Date:** 2026-08-24
- **Release under evaluation:** 0.1.0 pre-release
- **Skill bundle SHA-256:** `5c3f39089250a3f7cf271137109b0d678a09c8b908ba004a35196c5d6de644e8`, reproducible with `scripts/fingerprint_skill.py` in the original `evidence-first-problem-solving` repository
- **Fixture:** [`api-latency-regression`](../fixtures/api-latency-regression/scenario.yaml)
- **Rubric:** [`diagnosis.yaml`](../rubrics/diagnosis.yaml)
- **Acting runner:** independent Codex subagent; model identifier was not exposed in the durable run artifact
- **Evaluator:** a different Codex subagent that did not author the skill or fixture; model identifier was not exposed in the durable run artifact
- **Permission envelope:** read-only access to the skill and fixture; no internet, external data, or fixture mutation
- **Activation verdict:** correct—the cause and proof boundary were genuinely uncertain

The evaluator did not steer the acting run. The actor was not shown the rubric or intended diagnosis. The full working response stayed in an ephemeral local workspace because it contained machine-local paths; this sanitized record contains the decision-relevant evidence.

## Fixture integrity

Hashes were captured by the orchestrating process before delegation and again after both the acting run and evaluation. Every hash matched.

| File | SHA-256 |
|---|---|
| `scenario.yaml` | `f5c8d1c46d078b13ee39ad1e7f4f062bad3949fadebfd9ac471af09a6ade556a` |
| `metrics.csv` | `9aadbcc7a4f2e57bf66dc7f2962d21ede9f07f7479da56ad3b2cb37afb8afed9` |
| `release-events.csv` | `4897a75253caff7637402f64e61a18e4c33bf44f641e4d00e1e49727c49de7f7` |
| `request-samples.csv` | `ff2467dcf8142a3fe9a746ad92b22b08ff022284028b3cdff7c0bafcc9daefd9` |

## Acting-run outcome

The response identified cache misses on trailing-slash item paths as the strongest observed latency mechanism and treated the API release's cache-key normalization change as the leading—but only partially proved—trigger. It did not infer causation from event timing alone.

Evidence used included:

- item-route p95 rose while cache hit rate fell immediately after the release;
- health-route latency stayed stable;
- sampled cache hits averaged 89.0 ms while misses averaged 470.2 ms;
- trailing-slash samples missed and otherwise comparable non-trailing-slash samples hit in both regions;
- the traffic shift followed the regression, while the database event preceded it.

The proposed next action was a reversible 1–5% canary that changes only the normalization behavior, compares it with a concurrent control, verifies route equivalence first, and stops or rolls back on correctness, error-rate, latency, collision, or observability failures. The response explicitly left request-mix changes, origin latency, route semantics, production topology, and actual canary results unproved or not assessed.

## Independent score

**20/20; recommended threshold: 15. Critical failures: none.**

| Criterion | Score | Evaluator evidence |
|---|---:|---|
| Evidence map | 4/4 | Distinguished observed results, analyst judgment, assumptions, unknowns, and four proof states. |
| Competing hypotheses | 4/4 | Compared cache behavior with release, database, worker, traffic, regional, and request-mix explanations. |
| Discriminating check | 4/4 | Proposed a low-blast-radius reversible canary with a concurrent control and explicit follow-up if it failed to discriminate. |
| Causal calibration | 4/4 | Called the release-trigger claim partially proved and rejected timing alone as proof. |
| Verified handoff | 4/4 | Supplied before/after measures, success thresholds, stop conditions, rollback, evidence scope, and residual uncertainty. |

## Verification evidence

The actor independently recomputed the supplied aggregates. The evaluator checked that the reported values were reproducible from the fixture and that proposed canary thresholds were clearly labeled as decision criteria rather than observed measurements. The orchestrator independently confirmed the post-run fixture hashes above.

## Limitations

- The fixture is small and synthetic.
- The public record does not retain the full tool transcript or prove command ordering.
- No production system, feature flag, rollback, route contract, or canary effect was tested.
- A perfect rubric score means the saved answer met this fixture's observable criteria; it does not establish general accuracy, efficiency, or production safety.
