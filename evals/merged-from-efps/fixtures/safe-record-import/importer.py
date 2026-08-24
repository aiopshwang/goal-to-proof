"""Intentionally incomplete synthetic importer used by the evaluation scenario."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path


def import_records(source: Path, destination: Path) -> None:
    with source.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    destination.write_text(json.dumps(rows), encoding="utf-8")


def main() -> int:
    import_records(Path(sys.argv[1]), Path(sys.argv[2]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
