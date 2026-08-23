# Proof Patterns

Proof is claim-shaped. Select the strongest practical observation needed for the requested outcome; do not mechanically run every layer.

## Evidence ladder

1. **Artifact inspection** — the intended files, records, or configuration exist and contain the right substance.
2. **Focused checks** — syntax, schema, unit tests, calculations, citations, or targeted review pass.
3. **Integrated execution** — connected components or the full workflow run together.
4. **Target observation** — the actual device, deployment, account, audience, rendered file, or published artifact behaves as promised.
5. **Outcome evidence** — a real user, stakeholder, metric, or operational state confirms the intended effect when the claim requires it.

Stop at the lowest layer that directly proves the stated claim. Name higher layers as unverified rather than implying them.

## Software change

- Map acceptance criteria to tests or observations.
- Run focused tests, then regression checks proportional to impact.
- Exercise the user-visible, API, or integration path when behavior is claimed.
- If release or deployment is in scope, inspect the released artifact or environment; source changes alone are insufficient.

## Bug diagnosis and fix

- Capture the original reproduction or strongest available symptom evidence.
- Identify a supported root cause, not only the changed line.
- Show that the reproduction no longer fails.
- Add or run a regression check and inspect likely sibling failure paths.
- Verify the environment where the user experienced the problem when that environment is part of the claim.

## Research or recommendation

- State decision criteria and date-sensitive assumptions.
- Support material facts with primary or authoritative sources when available.
- Include contrary evidence or the strongest viable alternative.
- Separate sourced fact, inference, and unknown.
- Avoid “best”, “safe”, or “proven” when evidence covers only a narrow sample.

## Product, business, or strategy

- Tie the proposal to a specific user, pain, behavior, and current alternative.
- Distinguish firsthand evidence from a plausible narrative.
- Test desirability, feasibility, viability, and material risk at a depth proportionate to the requested decision.
- Define the smallest meaningful experiment and the observation that would change the decision.

## Document, curriculum, or visual artifact

- Verify factual coverage and consistency with source material.
- Open or render the final artifact rather than trusting generation success.
- Check readability and actionability for the real audience.
- Ensure it stands alone without hidden chat context.
- Rehearse the actual read, presentation, install, or handoff path when comprehension or timing is claimed.

## Demo, prototype, or proof of concept

- Prove the experience or technical uncertainty the artifact exists to test.
- Do not add production infrastructure that does not improve that proof.
- Keep simulated data and unimplemented behavior explicit.
- Do not generalize prototype success to production readiness.

## External operation

- Resolve the exact account, organization, destination, and object before acting.
- Observe the resulting remote state after the action.
- Report identifiers or links that let the user verify it without exposing secrets.

Git push success alone does not prove public availability. A public-release claim requires reading the repository, default branch, files, and release from the public remote.
