"""Unit tests for the A/B runner's host handling."""

import json
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

    def test_claude_activation_ignores_the_init_listing(self):
        listing = json.dumps({
            "type": "system",
            "subtype": "init",
            "slash_commands": ["goal-to-proof"],
        })
        self.assertFalse(run_ab_eval.skill_activated(listing, arm="candidate", host="claude"))

    def test_claude_activation_counts_a_skill_tool_call(self):
        call = json.dumps({
            "type": "assistant",
            "message": {"content": [
                {"type": "tool_use", "name": "Skill", "input": {"skill": "goal-to-proof"}}
            ]},
        })
        self.assertTrue(run_ab_eval.skill_activated(call, arm="candidate", host="claude"))

    def test_claude_final_response_is_the_result_event(self):
        stream = "\n".join([
            json.dumps({"type": "assistant", "message": {"content": []}}),
            json.dumps({"type": "result", "result": "the final answer"}),
        ])
        self.assertEqual(run_ab_eval.claude_final_response(stream), "the final answer")

    def test_resolved_sandbox_reads_header(self):
        header = (
            "workdir: c:\\w\nmodel: gpt-5.6-sol\napproval: never\n"
            "sandbox: workspace-write [workdir]\n"
        )
        self.assertEqual(run_ab_eval.resolved_sandbox(header), "workspace-write")
        self.assertEqual(run_ab_eval.resolved_sandbox("sandbox: read-only\n"), "read-only")
        self.assertIsNone(run_ab_eval.resolved_sandbox("no header here"))


class ClaudeHostTest(unittest.TestCase):
    def _argv(self, arm):
        return run_ab_eval.claude_argv(
            claude_bin="claude", model="sonnet", arm=arm,
            repo_root=REPO_ROOT, tools="Bash,Read,Write,Edit,Glob,Grep",
        )

    def test_candidate_arm_loads_the_plugin(self):
        argv = self._argv("candidate")
        self.assertIn("--plugin-dir", argv)
        self.assertEqual(argv[argv.index("--plugin-dir") + 1], str(REPO_ROOT))

    def test_baseline_arm_loads_no_plugin(self):
        self.assertNotIn("--plugin-dir", self._argv("baseline"))

    def test_both_arms_exclude_user_settings(self):
        for arm in ("baseline", "candidate"):
            argv = self._argv(arm)
            self.assertIn("--setting-sources", argv)
            self.assertEqual(argv[argv.index("--setting-sources") + 1], "")

    def test_default_tools_include_the_skill_tool(self):
        """Without it the skill is listed but cannot be invoked, and every
        activation count becomes a harness artifact rather than a finding."""
        self.assertIn("Skill", run_ab_eval.DEFAULT_CLAUDE_TOOLS.split(","))

    def test_arms_differ_only_by_the_plugin(self):
        baseline = self._argv("baseline")
        candidate = self._argv("candidate")
        self.assertEqual(baseline, [item for item in candidate
                                    if item not in {"--plugin-dir", str(REPO_ROOT)}])


class InterpreterResolutionTest(unittest.TestCase):
    def test_python3_maps_to_running_interpreter(self):
        resolved = run_ab_eval.resolve_argv(["python3", "-m", "unittest", "-q"])
        self.assertEqual(resolved[0], sys.executable)
        self.assertEqual(resolved[1:], ["-m", "unittest", "-q"])

    def test_other_commands_pass_through(self):
        self.assertEqual(run_ab_eval.resolve_argv(["git", "status"]), ["git", "status"])


class PromptFairnessTest(unittest.TestCase):
    def test_runnable_cases_have_neutral_prompts(self):
        cases = run_ab_eval.load_cases(REPO_ROOT)
        for case_id in ("B07", "B08", "B09"):
            neutral = cases[case_id]["neutral_prompt"]
            self.assertNotIn("goal-to-proof", neutral)
            self.assertNotIn("$", neutral)

    def test_case_prompt_selects_by_mode(self):
        case = run_ab_eval.load_cases(REPO_ROOT)["B07"]
        self.assertIn("$goal-to-proof", run_ab_eval.case_prompt(case, "explicit"))
        self.assertNotIn("goal-to-proof", run_ab_eval.case_prompt(case, "neutral"))

    def test_neutral_mode_refuses_a_case_without_one(self):
        with self.assertRaises(KeyError):
            run_ab_eval.case_prompt({"id": "X01", "prompt": "do it"}, "neutral")


if __name__ == "__main__":
    unittest.main()
