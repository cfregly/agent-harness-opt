from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest

from claude_agent_harness_optimization.pr_packets import (
    PacketOptions,
    build_upstream_pr_packet,
    write_upstream_pr_packet,
)


ROOT = Path(__file__).resolve().parents[1]


class PrPacketTests(unittest.TestCase):
    def test_builds_upstream_packet_with_pins_examples_and_delta(self):
        with tempfile.TemporaryDirectory() as tmp:
            result_path = Path(tmp) / "result.json"
            result_path.write_text(json.dumps(_sample_result()), encoding="utf-8")
            packet = build_upstream_pr_packet(
                result_path,
                options=PacketOptions(
                    baseline_variant="stock",
                    candidate_variant="tuned",
                    target_name="Example MCP",
                    target_repo="https://github.com/example/mcp",
                    change_summary="Clarify when to call the tuned tool.",
                    minimum_delta=0.1,
                ),
            )
            body = packet["files"]["PR_BODY.md"]
            title = packet["files"]["PR_TITLE.txt"]
            self.assertTrue(packet["passed"])
            self.assertEqual("Tighten Example MCP retrieval routing with live evals\n", title)
            self.assertIn("Suggested title: Tighten Example MCP retrieval routing with live evals", body)
            self.assertIn("## Value Proposition", body)
            self.assertIn("Helps agents choose the intended Example MCP workflow", body)
            self.assertIn("commit: abc123", body)
            self.assertIn("baseline score: 0.000", body)
            self.assertIn("candidate score: 1.000", body)
            self.assertIn("delta: 1.000", body)
            self.assertIn("provider=anthropic", body)
            self.assertIn("passed=1", body)
            self.assertIn("single page extraction", body)
            self.assertIn("python -m claude_agent_harness_optimization model-matrix", body)
            self.assertIn("public harness repo: https://github.com/cfregly/claude-agent-harness-optimization", body)
            self.assertIn("## What We Learned", body)
            self.assertIn("`tuned` beat `stock` by 1.000", body)
            self.assertIn("confusable alternatives checked: example_stock", body)
            self.assertNotIn("forbidden:", body)

            written = write_upstream_pr_packet(packet, Path(tmp) / "packet")
            self.assertTrue(Path(written["PR_TITLE.txt"]).exists())
            self.assertTrue(Path(written["PR_BODY.md"]).exists())
            self.assertTrue(Path(written["REPRODUCTION.md"]).exists())
            self.assertTrue(Path(written["evidence.json"]).exists())

    def test_cli_upstream_pr_packet(self):
        with tempfile.TemporaryDirectory() as tmp:
            result_path = Path(tmp) / "result.json"
            out_dir = Path(tmp) / "packet"
            result_path.write_text(json.dumps(_sample_result()), encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "claude_agent_harness_optimization",
                    "upstream-pr-packet",
                    str(result_path),
                    "--target-name",
                    "Example MCP",
                    "--baseline-variant",
                    "stock",
                    "--candidate-variant",
                    "tuned",
                    "--out-dir",
                    str(out_dir),
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertIn('"passed": true', result.stdout)
            self.assertTrue((out_dir / "PR_TITLE.txt").exists())
            self.assertTrue((out_dir / "PR_BODY.md").exists())


def _sample_result() -> dict:
    return {
        "case_definitions": [
            {
                "expected_tools": ["example_tuned"],
                "forbidden_tools": ["example_stock"],
                "name": "single page extraction",
                "task": "Extract title and price from one known URL.",
            }
        ],
        "cells": [
            {
                "errors": 0,
                "failed": 1,
                "harness": "prompt_json",
                "instruction_variant": "host_rules",
                "passed": 0,
                "provider": "anthropic",
                "score": 0.0,
                "tool_variant": "stock",
            },
            {
                "errors": 0,
                "failed": 0,
                "harness": "prompt_json",
                "instruction_variant": "host_rules",
                "passed": 1,
                "provider": "anthropic",
                "score": 1.0,
                "tool_variant": "tuned",
            },
        ],
        "filters": {
            "cases": ["single page extraction"],
            "harnesses": ["prompt_json"],
            "instruction_variants": ["host_rules"],
            "providers": ["anthropic"],
            "variants": ["stock", "tuned"],
        },
        "live": True,
        "matrix": "example matrix",
        "matrix_path": "evals/model_matrix/example.json",
        "results": [
            {
                "case": "single page extraction",
                "chosen_tools": ["example_stock"],
                "status": "failed",
                "tool_variant": "stock",
            },
            {
                "case": "single page extraction",
                "chosen_tools": ["example_tuned"],
                "status": "passed",
                "tool_variant": "tuned",
            },
        ],
        "source": {
            "commit": "abc123",
            "package": "example-mcp",
            "repo": "https://github.com/example/mcp",
            "version": "1.2.3",
        },
        "summary": {"errors": 0, "failed_cases": 1, "passed_cases": 1, "score": 0.5, "total": 2},
    }


if __name__ == "__main__":
    unittest.main()
