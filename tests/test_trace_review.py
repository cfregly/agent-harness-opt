from pathlib import Path
import subprocess
import sys
import unittest

from claude_agent_prompting.trace_review import load_trace, review_trace


ROOT = Path(__file__).resolve().parents[1]


class TraceReviewTests(unittest.TestCase):
    def test_good_trace_passes(self):
        result = review_trace(load_trace(ROOT / "evals" / "examples" / "agent_trace_good.json"))
        self.assertTrue(result.passed)
        self.assertEqual(1.0, result.score)

    def test_bad_trace_fails(self):
        result = review_trace(load_trace(ROOT / "evals" / "examples" / "agent_trace_bad.json"))
        self.assertFalse(result.passed)
        self.assertLess(result.score, 1.0)

    def test_parallel_trace_passes(self):
        result = review_trace(
            load_trace(ROOT / "evals" / "examples" / "agent_trace_parallel_good.json")
        )
        self.assertTrue(result.passed)
        self.assertEqual(1.0, result.score)
        details = "\n".join(finding.detail for finding in result.findings)
        self.assertIn("parallel group 'initial_research'", details)

    def test_cli_review_trace(self):
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "claude_agent_prompting",
                "review-trace",
                "evals/examples/agent_trace_good.json",
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
