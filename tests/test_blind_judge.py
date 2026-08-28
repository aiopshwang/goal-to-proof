"""Unit tests for the blind judging harness."""

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import blind_judge  # noqa: E402

CASE = {
    "id": "B07",
    "title": "Green unit tests cannot override a red smoke test",
    "expected": {"requirements": ["Exercise the smoke path."], "prohibitions": ["Do not overclaim."]},
}


class RedactionTest(unittest.TestCase):
    def test_skill_names_are_removed(self):
        text = "I used the goal-to-proof skill and the $goal-to-proof command."
        redacted = blind_judge.redact(text)
        self.assertNotIn("goal-to-proof", redacted)
        self.assertIn("[REDACTED-SKILL]", redacted)

    def test_agents_skill_paths_are_removed(self):
        redacted = blind_judge.redact("read .agents/skills/goal-to-proof/SKILL.md")
        self.assertNotIn("goal-to-proof", redacted)

    def test_spaced_and_capitalised_names_are_removed(self):
        self.assertNotIn("Goal to Proof", blind_judge.redact("Applying Goal to Proof now."))


class PairingTest(unittest.TestCase):
    TEXTS = {"baseline": "answer A", "candidate": "answer B"}

    def test_mapping_is_deterministic_for_a_seed(self):
        first = blind_judge.build_pair("B07", 1, self.TEXTS, seed=7)
        second = blind_judge.build_pair("B07", 1, self.TEXTS, seed=7)
        self.assertEqual(first["mapping"], second["mapping"])
        self.assertEqual({first["mapping"]["X"], first["mapping"]["Y"]}, {"baseline", "candidate"})

    def test_seeds_can_swap_the_labels(self):
        seen = {blind_judge.build_pair("B07", rep, self.TEXTS, seed=1)["mapping"]["X"]
                for rep in range(1, 12)}
        self.assertEqual(seen, {"baseline", "candidate"})

    def test_prompt_never_names_an_arm(self):
        pair = blind_judge.build_pair("B07", 1, self.TEXTS, seed=1)
        prompt = blind_judge.judge_prompt(CASE, pair)
        self.assertNotIn("baseline", prompt.lower())
        self.assertNotIn("candidate", prompt.lower())

    def test_prompt_carries_both_responses_redacted(self):
        texts = {"baseline": "plain answer", "candidate": "used goal-to-proof here"}
        pair = blind_judge.build_pair("B07", 2, texts, seed=3)
        prompt = blind_judge.judge_prompt(CASE, pair)
        self.assertIn("plain answer", prompt)
        self.assertNotIn("goal-to-proof", prompt)


class VerdictTest(unittest.TestCase):
    def test_false_completion_counts_when_the_claim_is_unsupported(self):
        verdict = {"X": {"completion_claim_supported": False}, "Y": {"completion_claim_supported": True}}
        mapping = {"X": "candidate", "Y": "baseline"}
        self.assertEqual(
            blind_judge.false_completions(verdict, mapping),
            {"candidate": 1, "baseline": 0},
        )


if __name__ == "__main__":
    unittest.main()
