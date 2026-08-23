---
layout: default
title: Product principles
description: The Goal to Proof product contract, activation boundary, authority split, and non-goals.
permalink: /product-principles/
---

# Goal to Proof product principles

Goal to Proof is a lightweight closure contract for authorized, non-trivial AI-agent work. Its job is narrow: turn approved work into an observed outcome, not a plausible completion claim.

## Authority contract

**The user owns the goal, value judgments, authority, risk tolerance, material choices, and final decisions.**

**The agent owns the method, sequencing, reversible implementation choices, execution, diagnostics, and verification inside the authorized boundary.**

This split avoids two opposite failures: asking the user to approve every ordinary intermediate step, and treating a broad goal as permission for publication, spending, disclosure, irreversible action, or unrelated scope expansion.

## Activation boundary

The contract activates for authorized work when meaningful completion depends on multiple steps, a real integration or audience boundary, or proof stronger than artifact existence.

It stays lightweight or inactive for:

- simple questions and direct factual answers;
- translation, formatting, or transcription;
- open-ended ideation without a defined deliverable;
- routine self-contained edits with an obvious direct check;
- read-only requests whose sole deliverable is an answer and that do not exercise a target workflow.

A non-trivial diagnosis, evidence-backed decision memo, executable plan, analysis, or document remains a positive closure case when that artifact is itself the requested result. The contract verifies the quality and evidence boundary of that deliverable; it does not infer permission to execute beyond it.

## Four closure fields

1. **Result:** what must be different when the task is done.
2. **Target:** who or what must be able to use or observe it.
3. **Proof:** the most direct practical observation that distinguishes success from plausible-looking failure.
4. **Boundaries:** what is authorized, excluded, or requires new authority.

These fields may remain internal when obvious. They are surfaced when ambiguity or authority would materially change the work.

## Proof contract

Proof is shaped like the claim. It comes from the latest relevant state and reaches the real target boundary when practical. A file's existence does not prove a usable document; a unit test does not prove an integrated user path; a successful push does not prove public availability.

When direct verification is unavailable, the agent narrows its report to what was actually observed and names the missing layer.

## Non-goals

Goal to Proof is not:

- a generic discovery or product-strategy framework;
- a complete software-development methodology;
- an invitation for an agent to choose the user's goals;
- a substitute for host permissions, credentials, tools, or human authority;
- a requirement to expose a checklist for every task;
- a guarantee that any agent or model will complete every task successfully.

## Low-ceremony rule

Use the lightest workflow that protects the outcome. Planning, root-cause analysis, subagents, research, checkpoints, and multiple test layers are tools, not rituals. Their value depends on whether they reduce a real closure risk.

## Completion language

- **Verified:** identify the direct command, observation, artifact, or external state.
- **Partially verified:** identify the proven layer and the untested layer.
- **Not verified:** identify the missing access, environment, evidence, or authority.

Never imply that a broader outcome was observed when only a narrower proxy was checked.
