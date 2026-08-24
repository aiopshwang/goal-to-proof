# Independent forward-test protocol

Use this protocol only after the skill and repository validators pass. It defines how to
produce evidence; it is not a result record and makes no claim that a run has occurred.

1. Select one fixture without showing its rubric to the acting agent.
2. Copy the fixture directory to a fresh temporary workspace and record hashes of every
   supplied file.
3. Give the acting agent only the scenario prompt, constraints, evidence, and the installed
   skill. The evaluator and skill author must not steer the run.
4. Allow only the permissions needed by the scenario. Record tool calls, changed files,
   commands, command outputs, elapsed time, and any requests for added authority.
5. Hash the original fixture again. For the diagnosis case, all hashes must match. For the
   implementation case, compare the untouched source fixture with the working-copy diff.
6. Have an evaluator score observable evidence against the matching rubric. Apply critical
   failures before calculating the numeric score.
7. Record activation correctness separately from task quality. A good task answer does not
   excuse a false activation, and correct activation does not prove a good outcome.
8. State the run's limits. One scenario can support only a bounded behavior claim and cannot
   establish universal reliability.

A private evidence record may contain the date, skill commit or bundle hash, authorized
runner and model identifiers, fixture ID and hashes, permission envelope, raw transcript
location, working-copy diff, verification outputs, reviewer identity, and other operational
details. Keep it outside the public repository when it contains local paths, private
conversations, account identifiers, sensitive tool output, or non-public evidence.

A publishable summary uses repository-relative artifact IDs, hashes, role labels, sanitized
excerpts, criterion-level scores with cited evidence, critical failures, activation and task
quality verdicts, and explicit limitations. Never publish raw transcripts, machine-local
paths, personal or company identifiers, credentials, or unrelated record contents. Store a
summary in a dated results directory only after the run and a privacy review; never
pre-populate outcomes.

Identify the evaluated skill with `python scripts/fingerprint_skill.py` in the original
`evidence-first-problem-solving` repository. The canonical fingerprint sorts every file
by its case-folded POSIX-style relative path, hashes each file with SHA-256,
joins `relative/path=file_sha256` entries with a single LF and no trailing LF, then hashes
that UTF-8 manifest with SHA-256. Publish the bundle fingerprint; retain the command output
when per-file auditability is needed.
