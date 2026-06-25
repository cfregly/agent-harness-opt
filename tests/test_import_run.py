from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest

from claude_agent_harness_optimization.import_run import import_run_export


ROOT = Path(__file__).resolve().parents[1]


class ImportRunTests(unittest.TestCase):
    def test_import_run_writes_trace_and_bundle(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = import_run_export(
                ROOT / "evals" / "examples" / "import_run_cursor_export.json",
                adapter="cursor",
                out_dir=tmp,
            )
            trace_path = Path(result["trace"])
            bundle_path = Path(result["bundle"])

            self.assertTrue(trace_path.exists())
            self.assertTrue(bundle_path.exists())
            trace = json.loads(trace_path.read_text(encoding="utf-8"))
            bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
            self.assertEqual("tool_call", trace["steps"][1]["type"])
            self.assertEqual("Task", bundle["tools"][0]["name"])
            self.assertIn("value_bar", bundle)

    def test_cli_import_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "claude_agent_harness_optimization",
                    "import-run",
                    "evals/examples/import_run_cursor_export.json",
                    "--adapter",
                    "cursor",
                    "--out-dir",
                    tmp,
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertIn("agent_audit_bundle.json", result.stdout)

    def test_import_run_accepts_codex_jsonl(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = import_run_export(
                ROOT / "evals" / "examples" / "codex_repo_inspection_events.jsonl",
                adapter="codex_jsonl",
                name="codex repo inspection",
                out_dir=tmp,
            )
            trace = json.loads(Path(result["trace"]).read_text(encoding="utf-8"))

            self.assertEqual("codex repo inspection", trace["name"])
            self.assertEqual("Bash", trace["steps"][1]["name"])
            self.assertEqual(5, result["trace_steps"])


if __name__ == "__main__":
    unittest.main()
