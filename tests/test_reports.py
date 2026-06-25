from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from claude_agent_harness_optimization.reports import render_html_report, render_pr_comment


ROOT = Path(__file__).resolve().parents[1]


class ReportTests(unittest.TestCase):
    def test_render_html_and_pr_comment(self):
        payload = {
            "name": "sample",
            "passed": False,
            "results": [{"case": "case one", "passed": False, "status": "failed"}],
            "summary": {"errors": 0, "failed_cases": 1, "passed_cases": 0, "score": 0.0, "total": 1},
        }
        html = render_html_report(payload, title="Sample Report")
        comment = render_pr_comment(payload, title="Sample Report")
        self.assertIn("<title>Sample Report</title>", html)
        self.assertIn("case one", html)
        self.assertIn("case one", comment)

    def test_cli_report_commands(self):
        with tempfile.TemporaryDirectory() as tmp:
            matrix_out = Path(tmp) / "matrix.json"
            html_out = Path(tmp) / "report.html"
            md_out = Path(tmp) / "comment.md"
            matrix = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "claude_agent_harness_optimization",
                    "model-matrix",
                    "evals/model_matrix/harness_trace_adapters.json",
                    "--providers",
                    "trace_fixture",
                    "--max-cases",
                    "1",
                    "--out",
                    str(matrix_out),
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(0, matrix.returncode, matrix.stderr)
            html_result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "claude_agent_harness_optimization",
                    "render-report",
                    str(matrix_out),
                    "--out",
                    str(html_out),
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            pr_result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "claude_agent_harness_optimization",
                    "pr-comment",
                    str(matrix_out),
                    "--out",
                    str(md_out),
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(0, html_result.returncode, html_result.stderr)
            self.assertEqual(0, pr_result.returncode, pr_result.stderr)
            self.assertTrue(html_out.exists())
            self.assertTrue(md_out.exists())


if __name__ == "__main__":
    unittest.main()
