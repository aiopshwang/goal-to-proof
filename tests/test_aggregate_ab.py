"""Unit tests for the pre-registered metric aggregation."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import aggregate_ab  # noqa: E402


def _write_rep(root, case, arm, rep, *, passed, gates, activated, final="done", invalid=False):
    directory = root / case / arm / f"rep-{rep}"
    directory.mkdir(parents=True)
    (directory / "oracle.json").write_text(json.dumps({
        "machine_status": "pass" if passed else "fail",
        "hard_gate_failures": gates,
        "skill_activated": activated,
        "invalid": invalid,
    }), encoding="utf-8")
    (directory / "final.txt").write_text(final, encoding="utf-8")


class AggregateTest(unittest.TestCase):
    def test_counts_passes_gates_and_activation(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for rep in (1, 2, 3):
                _write_rep(root, "B07", "candidate", rep, passed=True, gates=[], activated=True)
                _write_rep(root, "B07", "baseline", rep, passed=rep == 1,
                           gates=["H04"] if rep > 1 else [], activated=False)
            summary = aggregate_ab.aggregate(root)
            self.assertEqual(summary["cases"]["B07"]["candidate"]["m1"], "3/3")
            self.assertEqual(summary["cases"]["B07"]["baseline"]["m1"], "1/3")
            self.assertEqual(summary["cases"]["B07"]["baseline"]["m2"], 2)
            self.assertEqual(summary["cases"]["B07"]["candidate"]["m5"], "3/3")

    def test_ceremony_is_counted_from_the_final_response(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            _write_rep(root, "B08", "candidate", 1, passed=True, gates=[], activated=True,
                       final="Shall I proceed with the edit?")
            _write_rep(root, "B08", "candidate", 2, passed=True, gates=[], activated=True,
                       final="Set telemetry_enabled to false and validated the JSON.")
            summary = aggregate_ab.aggregate(root)
            self.assertEqual(summary["cases"]["B08"]["candidate"]["m4"], 1)

    def test_invalid_runs_are_excluded_and_reported(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            _write_rep(root, "B09", "candidate", 1, passed=True, gates=[], activated=True)
            _write_rep(root, "B09", "candidate", 2, passed=False, gates=["H01"], activated=False,
                       invalid=True)
            summary = aggregate_ab.aggregate(root)
            self.assertEqual(summary["cases"]["B09"]["candidate"]["m1"], "1/1")
            self.assertEqual(summary["cases"]["B09"]["candidate"]["invalid"], 1)


if __name__ == "__main__":
    unittest.main()
