# Diagnosis and Proof

Read this reference when the root cause is unclear, evidence conflicts, or the requested completion claim is consequential. Use only the sections that improve the current decision.

## Build discriminating hypotheses

Describe each hypothesis as a causal claim, not a topic. Include a plausible alternative and the null explanation (measurement error, coincidence, or expected behavior) when relevant.

For each hypothesis, ask:

1. What observation should exist if it is true?
2. What observation would make it unlikely?
3. Which safe check best distinguishes it from its strongest competitor?
4. What downstream behavior should change if the cause is removed?

Use 5 Why to move from a symptom toward a controllable mechanism. Stop when the next “why” would be speculation, leave the relevant system boundary, or stop changing the decision. Branch the chain when several causes can jointly produce the symptom.

## Choose the next check

Rank candidate checks by:

- discrimination: how differently leading hypotheses predict the result;
- authority: whether the evidence is primary and relevant to the claim;
- scope: whether it covers the affected population, path, time, and environment;
- cost and reversibility: time, compute, disruption, and recovery;
- freshness: whether state could have changed since observation.

Prefer a cheap read-only inspection when it can settle the question. Escalate to mutation, external action, or expensive evaluation only when the expected information justifies it and authority exists. A check that all hypotheses predict equally is confirmation theater, not diagnosis.

## Interpret evidence without collapsing categories

- A fact can be stale, narrow, or irrelevant; record its observation time and scope.
- A user decision determines the desired tradeoff but does not demonstrate feasibility.
- A judgment should name the facts and assumptions it depends on.
- An assumption remains unconfirmed even when it is convenient or widely believed.
- Absence of evidence is not evidence of absence unless the observation method should have detected the condition.

When sources disagree, do not average them silently. Compare authority, directness, scope, definitions, time, and collection method; preserve the disagreement if it cannot be resolved.

## Match proof to the claim

Proof selection lives in [proof-patterns.md](proof-patterns.md). Classify each
result as **proved**, **partially proved**, **not proved**, or **not assessed**,
and never promote a narrow result to a broader status.
