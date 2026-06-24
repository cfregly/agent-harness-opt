from pathlib import Path
import subprocess
import sys
import unittest

from claude_agent_prompting.trace_suite import run_trace_suite


ROOT = Path(__file__).resolve().parents[1]


class TraceSuiteTests(unittest.TestCase):
    def test_trace_suite_expectations_pass(self):
        result = run_trace_suite(ROOT / "evals" / "suites" / "agent_trace_suite.json")
        self.assertTrue(result["passed"])
        self.assertEqual(3, result["summary"]["cases"])
        self.assertEqual(3, result["summary"]["met_expectations"])

    def test_cli_trace_suite(self):
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "claude_agent_prompting",
                "trace-suite",
                "evals/suites/agent_trace_suite.json",
            ],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn('"passed": true', result.stdout)


if __name__ == "__main__":
    unittest.main()
