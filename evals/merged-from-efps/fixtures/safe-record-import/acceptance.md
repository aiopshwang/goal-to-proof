# Synthetic import acceptance criteria

The command accepts a CSV path and a destination JSON path. It must validate every row
before replacing the destination. Identifiers must be non-empty and unique, dates must be
valid ISO calendar dates, and amounts must be non-negative decimal values.

A failed validation must return a non-zero exit status, describe all invalid rows without
exposing unrelated row data, leave an existing destination byte-for-byte unchanged, and
leave no temporary output behind. A successful rerun with identical input must produce the
same destination bytes. Replacement must be atomic on the same filesystem.

The operational handoff must include a dry-run or preflight procedure, success and failure
signals, rollback instructions, and known limitations.
