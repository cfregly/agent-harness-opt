import os
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


class CliTests(unittest.TestCase):
    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-m", "claude_agent_harness_optimization", *args],
            cwd=ROOT,
            check=False,
            text=True,
            capture_output=True,
        )

    def test_render_command(self):
        result = self.run_cli("render", "recipes/agentic_search.json")
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("<operating_loop>", result.stdout)
        self.assertIn("<value_bar>", result.stdout)

    def test_score_command(self):
        result = self.run_cli("score", "recipes/agentic_search.json")
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn('"verdict": "agent"', result.stdout)

    def test_eval_command(self):
        result = self.run_cli("eval", "evals/examples/search_answer.json")
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn('"passed": true', result.stdout)

    def test_model_matrix_command(self):
        result = self.run_cli(
            "model-matrix",
            "evals/model_matrix/coding_tool_selection.json",
            "--providers",
            "anthropic",
            "--harnesses",
            "native_tools",
            "--variants",
            "tuned_boundaries",
            "--instruction-variants",
            "boundary_rules",
            "--max-cases",
            "1",
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn('"matrix": "coding file-tool selection matrix"', result.stdout)

    def test_grind_harness_command(self):
        result = self.run_cli(
            "grind-harness",
            "evals/model_matrix/coding_tool_selection.json",
            "--providers",
            "anthropic",
            "--harnesses",
            "native_tools",
            "--instruction-variants",
            "boundary_rules",
            "--cases",
            "investigate trace review flow",
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn('"baseline_variant": "baseline_short"', result.stdout)
        self.assertIn('"projected_live_calls": 2', result.stdout)

    def test_live_harness_command_with_fake_local_harness(self):
        fake_events = [
            {
                "type": "item.started",
                "item": {
                    "id": "call_1",
                    "type": "command_execution",
                    "command": "pwd",
                    "status": "in_progress",
                },
            },
            {
                "type": "item.completed",
                "item": {
                    "id": "call_1",
                    "type": "command_execution",
                    "command": "pwd",
                    "aggregated_output": str(ROOT),
                    "status": "completed",
                },
            },
            {
                "type": "item.completed",
                "item": {
                    "id": "message_1",
                    "type": "agent_message",
                    "text": f"HARNESS_OK fake {ROOT}",
                },
            },
        ]
        code = "import json; events = " + repr(fake_events) + "; [print(json.dumps(item)) for item in events]"
        spec = {
            "cases": [
                {
                    "name": "fake pwd",
                    "prompt_template": "Run {shell_command}. HARNESS_OK {marker}",
                    "required_marker_template": "HARNESS_OK {marker}",
                }
            ],
            "harnesses": [
                {
                    "name": "fake_codex",
                    "marker": "fake",
                    "adapter": "codex_jsonl",
                    "command": [sys.executable, "-c", code],
                    "expected_args_contains": {"command": "pwd"},
                    "expected_tool": "Bash",
                    "version_command": [sys.executable, "--version"],
                }
            ],
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            spec_path = Path(temp_dir) / "fake-live-harness.json"
            out_dir = Path(temp_dir) / "artifacts"
            spec_path.write_text(json.dumps(spec), encoding="utf-8")
            result = self.run_cli("live-harness", str(spec_path), "--out-dir", str(out_dir))

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn('"harness": "fake_codex"', result.stdout)
        self.assertIn('"tool_use_passed": true', result.stdout)

    def test_claude_judge_requires_api_key(self):
        env = os.environ.copy()
        env.pop("ANTHROPIC_API_KEY", None)
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "claude_agent_harness_optimization",
                "review-trace",
                "evals/examples/agent_trace_good.json",
                "--claude-judge",
            ],
            cwd=ROOT,
            check=False,
            text=True,
            capture_output=True,
            env=env,
        )
        self.assertEqual(1, result.returncode)
        self.assertIn("ANTHROPIC_API_KEY is required", result.stdout)


if __name__ == "__main__":
    unittest.main()
