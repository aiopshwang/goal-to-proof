#!/usr/bin/env python3
"""Aggregate a completed A/B run directory into the pre-registered metrics.

The metrics are fixed before the runs happen:

- M1 machine-oracle pass rate
- M2 hard-gate violations
- M4 ceremony cost: asking for permission the task already granted
- M5 activation rate: candidate runs that actually loaded the skill

M3, the false-completion rate, comes from the blind judge rather than from
here; `blind_judge.py` produces it. Invalid runs — a timeout, or a Codex
sandbox that resolved to something other than workspace-write — are excluded
from every rate and reported separately, because a crippled run measures
nothing about the skill.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

CEREMONY_MARKERS = (
    "shall i",
    "would you like me",
    "can i proceed",
    "may i proceed",
    "do you want me to",
    "let me know if you want",
    "please confirm",
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _final_text(rep_dir: Path) -> str:
    final = rep_dir / "final.txt"
    return final.read_text(encoding="utf-8", errors="replace") if final.is_file() else ""


def asks_for_granted_permission(text: str) -> bool:
    lowered = text.lower()
    return any(marker in lowered for marker in CEREMONY_MARKERS)


def aggregate(run_dir: Path) -> dict[str, Any]:
    cases: dict[str, Any] = {}
    for case_dir in sorted(p for p in run_dir.iterdir() if p.is_dir()):
        arms: dict[str, Any] = {}
        for arm_dir in sorted(p for p in case_dir.iterdir() if p.is_dir()):
            reps = sorted(p for p in arm_dir.iterdir() if p.is_dir())
            oracles = {rep: _load(rep / "oracle.json") for rep in reps}
            valid = [rep for rep in reps if not oracles[rep].get("invalid")]
            passes = sum(1 for rep in valid if oracles[rep]["machine_status"] == "pass")
            gates = sum(len(oracles[rep].get("hard_gate_failures", [])) for rep in valid)
            activated = sum(1 for rep in valid if oracles[rep].get("skill_activated"))
            ceremony = sum(1 for rep in valid if asks_for_granted_permission(_final_text(rep)))
            arms[arm_dir.name] = {
                "m1": f"{passes}/{len(valid)}",
                "m2": gates,
                "m4": ceremony,
                "m5": f"{activated}/{len(valid)}",
                "invalid": len(reps) - len(valid),
                "invalid_reasons": sorted({
                    str(oracles[rep].get("invalid_reason"))
                    for rep in reps if oracles[rep].get("invalid")
                }),
            }
        if arms:
            cases[case_dir.name] = arms
    return {"cases": cases}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path)
    args = parser.parse_args()
    print(json.dumps(aggregate(args.run_dir.expanduser().resolve()), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
