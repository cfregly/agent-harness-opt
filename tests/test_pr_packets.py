from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest

from claude_agent_harness_opt.pr_packets import (
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
                    evidence_url=(
                        "https://github.com/cfregly/claude-agent-harness-opt/blob/main/"
                        "evals/results/example.json"
                    ),
                    finding_url=(
                        "https://github.com/cfregly/claude-agent-harness-opt/tree/main/"
                        "docs/findings/example"
                    ),
                    minimum_delta=0.1,
                    packet_url=(
                        "https://github.com/cfregly/claude-agent-harness-opt/tree/main/"
                        "evals/pr_packets/example"
                    ),
                    target_actions=("Add an explicit tuned-tool routing regression.",),
                ),
            )
            body = packet["files"]["PR_BODY.md"]
            title = packet["files"]["PR_TITLE.txt"]
            self.assertTrue(packet["passed"])
            self.assertEqual("Tighten Example MCP retrieval routing with live evals\n", title)
            self.assertIn("Suggested title: Tighten Example MCP retrieval routing with live evals", body)
            self.assertIn("## Summary", body)
            self.assertLess(body.index("## Summary"), body.index("## Why This Matters"))
            self.assertNotIn("## Founder Summary", body)
            self.assertIn("### Exact Text To Apply", body)
            self.assertIn("| Where to edit | Baseline text | Suggested replacement text |", body)
            self.assertIn("| Target tool or instruction surface |", body)
            self.assertIn("Current wording does not make the measured boundary explicit.", body)
            self.assertIn("Encode the measured Example MCP boundary in the tool or skill surface before the agent chooses a tool.", body)
            self.assertIn("### Baseline / Suggested Behavior", body)
            self.assertLess(body.index("### Exact Text To Apply"), body.index("### Baseline / Suggested Behavior"))
            self.assertIn("| Suggested change | Baseline / before description | Suggested / after description | Result |", body)
            self.assertIn("| Clarify when to call the tuned tool.", body)
            self.assertIn(
                "| Add an explicit tuned-tool routing regression.",
                body,
            )
            self.assertIn("`stock` scored 0.000; failures clustered on single page extraction.", body)
            self.assertIn("`tuned` scored 1.000, a 1.000 gain. This clears the adversarially-confirmed to add value bar", body)
            self.assertIn("## Why This Matters", body)
            self.assertIn("helps agents choose the intended Example MCP workflow", body)
            self.assertIn("## Recommended Actions", body)
            self.assertIn("Apply suggested change: Clarify when to call the tuned tool.", body)
            self.assertIn("Add an explicit tuned-tool routing regression.", body)
            self.assertIn("## Model Coverage", body)
            self.assertIn("| Anthropic | `stock` 0/1 passed, 1 failed, 0 errors.", body)
            self.assertIn("Provider/model rows are evidence lanes", body)
            self.assertIn("## Run This In Your Repo", body)
            self.assertLess(body.index("## Recommended Actions"), body.index("## Run This In Your Repo"))
            self.assertLess(body.index("## Run This In Your Repo"), body.index("## Model Coverage"))
            self.assertLess(body.index("## Model Coverage"), body.index("## Evidence Bundle"))
            self.assertIn("codex exec -C /path/to/repo --sandbox read-only -", body)
            self.assertIn("claude -p --permission-mode plan", body)
            self.assertIn("gemini --approval-mode plan --output-format text", body)
            self.assertIn("Review this action-first finding:", body)
            self.assertIn("https://github.com/cfregly/claude-agent-harness-opt/tree/main/docs/findings/example", body)
            self.assertIn("## Evidence Bundle", body)
            self.assertIn("evals/pr_packets/example/evidence.json", body)
            self.assertNotIn("Founder handoff:", body)
            self.assertNotIn("## Evidence\n", body)
            self.assertNotIn("## Suggested Change", body)
            self.assertNotIn("## Actions By Company", body)
            self.assertNotIn("### Anthropic", body)
            self.assertIn("## What Already Works", body)
            self.assertIn("## How This Is Proven Useful", body)
            self.assertIn("## Current Frontier Coverage", body)
            self.assertIn("Treat this packet as historical or compatibility evidence", body)
            self.assertIn("## Downside If Not Changed", body)
            self.assertIn("same tasks, providers, harnesses, and instruction variants", body)
            self.assertIn("Routing ambiguity can make agents choose broader or higher-cost tool paths", body)
            self.assertIn("commit: abc123", body)
            self.assertIn("baseline score: 0.000", body)
            self.assertIn("candidate score: 1.000", body)
            self.assertIn("delta: 1.000", body)
            self.assertIn("provider=anthropic", body)
            self.assertIn("passed=1", body)
            self.assertIn("single page extraction", body)
            self.assertIn("python -m claude_agent_harness_opt model-matrix", body)
            self.assertIn("public harness repo: https://github.com/cfregly/claude-agent-harness-opt", body)
            self.assertIn("## What We Learned", body)
            self.assertIn("`tuned` beat `stock` by 1.000", body)
            self.assertIn("confusable alternatives checked: example_stock", body)
            self.assertNotIn("forbidden:", body)

            written = write_upstream_pr_packet(packet, Path(tmp) / "packet")
            self.assertTrue(Path(written["PR_TITLE.txt"]).exists())
            self.assertTrue(Path(written["PR_BODY.md"]).exists())
            self.assertTrue(Path(written["REPRODUCTION.md"]).exists())
            self.assertTrue(Path(written["evidence.json"]).exists())
            reproduction = Path(written["REPRODUCTION.md"]).read_text(encoding="utf-8")
            self.assertIn("This is supporting evidence for the founder handoff", reproduction)
            self.assertIn("Start with `PR_BODY.md` for Summary, Recommended Actions, and Run This In Your Repo", reproduction)

    def test_frontier_cells_are_called_out_separately(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = _sample_result()
            for cell in result["cells"]:
                cell["tier"] = "frontier"
                cell["profile"] = "provider-frontier"
            for item in result["results"]:
                item["tier"] = "frontier"
                item["profile"] = "provider-frontier"
                item["model"] = "example-frontier-model"
            result_path = Path(tmp) / "result.json"
            result_path.write_text(json.dumps(result), encoding="utf-8")
            packet = build_upstream_pr_packet(
                result_path,
                options=PacketOptions(
                    baseline_variant="stock",
                    candidate_variant="tuned",
                    target_name="Example MCP",
                    minimum_delta=0.1,
                ),
            )

            body = packet["files"]["PR_BODY.md"]
            self.assertIn("Frontier-only score moved from 0.000 to 1.000", body)
            self.assertIn("Frontier profiles covered: provider-frontier", body)
            self.assertIn("Use frontier cells for upstream-facing claims", body)

    def test_guardrail_packet_keeps_cta_but_does_not_promote_change(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = _sample_result()
            for cell in result["cells"]:
                cell["passed"] = 1
                cell["failed"] = 0
                cell["score"] = 1.0
            result["summary"] = {"errors": 0, "failed_cases": 0, "passed_cases": 2, "score": 1.0, "total": 2}
            result_path = Path(tmp) / "result.json"
            result_path.write_text(json.dumps(result), encoding="utf-8")
            packet = build_upstream_pr_packet(
                result_path,
                options=PacketOptions(
                    baseline_variant="stock",
                    candidate_variant="tuned",
                    target_name="Example MCP",
                    minimum_delta=0.1,
                ),
            )

            body = packet["files"]["PR_BODY.md"]
            self.assertFalse(packet["passed"])
            self.assertIn("### Exact Text To Apply", body)
            self.assertIn("| Where to edit | Baseline text | Suggested replacement text |", body)
            self.assertIn("| No upstream text change promoted. |", body)
            self.assertIn("Current tool descriptions already passed this retained slice.", body)
            self.assertIn("### Baseline / Suggested Behavior", body)
            self.assertLess(body.index("### Exact Text To Apply"), body.index("### Baseline / Suggested Behavior"))
            self.assertIn("No wording change promoted from this slice.", body)
            self.assertIn("- No upstream change is promoted from this slice.", body)
            self.assertIn("`tuned` also scored 1.000. Keep the cases as regression coverage.", body)
            self.assertIn("Keep the selected cases below as regression coverage", body)
            self.assertIn("## Run This In Your Repo", body)
            self.assertIn("Review this action-first finding:", body)
            self.assertIn("## Model Coverage", body)
            self.assertLess(body.index("## Recommended Actions"), body.index("## Run This In Your Repo"))
            self.assertLess(body.index("## Run This In Your Repo"), body.index("## Model Coverage"))
            self.assertNotIn("0.000 gain", body)
            self.assertNotIn("## Actions By Company", body)
            self.assertNotIn("Apply this change:", body)

    def test_cli_upstream_pr_packet(self):
        with tempfile.TemporaryDirectory() as tmp:
            result_path = Path(tmp) / "result.json"
            out_dir = Path(tmp) / "packet"
            result_path.write_text(json.dumps(_sample_result()), encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "claude_agent_harness_opt",
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
