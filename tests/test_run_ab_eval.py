"""Unit tests for the A/B runner's host handling."""

import os
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import run_ab_eval  # noqa: E402


class CodexEnvironmentTest(unittest.TestCase):
    def test_env_does_not_redirect_codex_home(self):
        """Redirecting HOME or CODEX_HOME breaks Codex authentication (spec P1)."""
        env = run_ab_eval.eval_env()
        self.assertEqual(env.get("HOME"), os.environ.get("HOME"))
        self.assertEqual(env.get("CODEX_HOME"), os.environ.get("CODEX_HOME"))
        self.assertNotIn("codex-home", str(env.get("CODEX_HOME", "")))

    def test_codex_argv_omits_ignore_user_config(self):
        argv = run_ab_eval.codex_argv(
            codex_bin="codex",
            workspace=Path("/w"),
            model="gpt-5.6-sol",
            effort="xhigh",
            final_path=Path("/w/final.txt"),
        )
        self.assertNotIn("--ignore-user-config", argv)
        self.assertIn("--sandbox", argv)
        self.assertEqual(argv[argv.index("--sandbox") + 1], "workspace-write")
        self.assertIn("project_doc_max_bytes=0", argv)

    def test_candidate_skill_lands_in_workspace(self):
        with tempfile.TemporaryDirectory() as temp:
            workspace = Path(temp)
            run_ab_eval.install_workspace_skill(workspace, REPO_ROOT)
            skill = workspace / ".agents/skills/goal-to-proof/SKILL.md"
            self.assertTrue(skill.is_file())

    def test_activation_requires_the_candidate_arm_to_read_the_skill(self):
        loaded = "Get-Content .agents/skills/goal-to-proof/SKILL.md"
        self.assertTrue(run_ab_eval.skill_activated(loaded, arm="candidate", host="codex"))
        self.assertFalse(run_ab_eval.skill_activated(loaded, arm="baseline", host="codex"))
        self.assertFalse(run_ab_eval.skill_activated("no skill here", arm="candidate", host="codex"))

    def test_resolved_sandbox_reads_header(self):
        header = (
            "workdir: c:\\w\nmodel: gpt-5.6-sol\napproval: never\n"
            "sandbox: workspace-write [workdir]\n"
        )
        self.assertEqual(run_ab_eval.resolved_sandbox(header), "workspace-write")
        self.assertEqual(run_ab_eval.resolved_sandbox("sandbox: read-only\n"), "read-only")
        self.assertIsNone(run_ab_eval.resolved_sandbox("no header here"))


if __name__ == "__main__":
    unittest.main()
