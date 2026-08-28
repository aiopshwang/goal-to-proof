# Changelog

All notable changes to Goal to Proof are documented in this file. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- The first live A/B evaluation with a control arm, recorded in
  `evals/results/2026-08-28-live-ab.md`: the same task run with and without
  the skill on both Codex and Claude Code, scored by a blind judge on the
  opposite host. Neutral prompts (`--prompt-mode neutral`) so the baseline is
  not told to use a skill it lacks, repetitions (`--reps`), metric
  aggregation (`scripts/aggregate_ab.py`), and blind cross-host judging
  (`scripts/blind_judge.py`).
- A `neutral_prompt` on every behavior case, each the explicit prompt with
  the skill invocation removed and nothing else changed.

### Fixed

- The A/B runner could never have produced a valid live result. It redirected
  `HOME` and `CODEX_HOME`, which fails authentication, and passed
  `--ignore-user-config`, which silently overrides `--sandbox` back to
  read-only — and a read-only Codex session on Windows cannot read its own
  workspace. A run whose sandbox does not resolve to `workspace-write` is now
  recorded as invalid rather than scored.
- Oracle argument arrays called `python3`, which on Windows is an App
  Execution Alias stub that exits without running, failing every oracle
  regardless of the agent's work.
- Subprocess output was decoded with the host locale codec, which killed the
  reader thread on a non-UTF-8 console and lost the transcript.
- The temporary workspace was named after the arm, and that path appears in
  the agent's own answer, which the blind judge reads.
- `B09`'s oracle re-ran a script with a side effect after the agent had
  already run it; it now checks the state that script leaves behind.
- Workspace cleanup and an unreadable workspace entry could each destroy a
  matrix after its model calls had been paid for.
- `is_safe_relative_path` accepted a POSIX-absolute path on Windows, where
  `Path("/x").is_absolute()` is false without a drive.
- Two symlink tests errored on hosts that withhold the privilege; they now
  skip with a stated reason, so the published release gate passes on Windows.

## [1.1.0] - 2026-08-24

### Added

- Diagnosis loop merged from `evidence-first-problem-solving`: a
  discriminating-hypothesis reference at
  `references/diagnosis-and-proof.md`, activated when the cause or proof
  boundary is genuinely uncertain.
- A rationalization table and red-flag list hardening the completion gate
  against pressure-driven overclaiming.
- Forward-test fixtures, rubrics, and result records preserved from
  `evidence-first-problem-solving` v0.1.0 under `evals/merged-from-efps/`.
- An "aiopshwang skill family" section linking companion skills.

### Changed

- The skill description now also triggers on genuinely uncertain causes and
  proof boundaries, and no longer summarizes method in the trigger text.

## [1.0.0] - 2026-08-23

### Added

- Initial Goal to Proof skill and proof-pattern reference.
- Codex and Claude Code plugin and marketplace manifests.
- Cross-host interface metadata and explicit invocation prompt.
- Brand icon, logo, and social preview artwork.
- Twenty-four synthetic behavior and trigger cases, five hard gates, an opt-in isolated A/B runner, and deterministic validation tests.
- English and Korean documentation plus a crawlable GitHub Pages site with methodology, comparison, FAQ, validation, privacy, and terms pages.
- MIT license, privacy policy, terms, security policy, and support guide.

[Unreleased]: https://github.com/aiopshwang/goal-to-proof/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/aiopshwang/goal-to-proof/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/aiopshwang/goal-to-proof/releases/tag/v1.0.0
