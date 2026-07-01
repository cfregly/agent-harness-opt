from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

from scripts.check_finding_packets import (
    ROOT,
    _check_matrix_surface_coverage,
    _check_pr_packet_evidence,
    _check_result_json,
    _check_result_markdown,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


class CheckFindingPacketsScriptTests(unittest.TestCase):
    def test_script_passes_current_repo(self):
        result = subprocess.run(
            [sys.executable, "scripts/check_finding_packets.py"],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("finding packet check passed", result.stdout)

    def test_pr_packet_evidence_requires_promoted_live_variant_result(self):
        failures = _check_pr_packet_evidence(
            ROOT / "evals" / "pr_packets" / "bad" / "evidence.json",
            {
                "cases": [],
                "comparison": {
                    "baseline_score": 0.8,
                    "baseline_variant": "stock",
                    "candidate_score": 0.81,
                    "candidate_variant": "tuned",
                    "delta": 0.01,
                    "minimum_delta": 0.1,
                    "promote": False,
                },
                "matrix": {"tool_variants": [{"name": "stock", "tools": []}]},
                "result": {
                    "cells": [],
                    "live": False,
                    "matrix_path": "evals/model_matrix/missing.json",
                    "results": [],
                    "summary": {"total": 0},
                },
                "source": {},
            },
        )

        joined = "\n".join(failures)
        self.assertIn("cases must be a nonempty list", joined)
        self.assertIn("comparison.promote must be true", joined)
        self.assertIn("comparison delta is below minimum_delta", joined)
        self.assertIn("result.live must be true", joined)
        self.assertIn("comparison variant missing from matrix: tuned", joined)

    def test_result_json_rejects_unknown_receipt_shape(self):
        path = ROOT / "evals" / "results" / "unknown_shape.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('{"notes": "not a receipt"}', encoding="utf-8")
        try:
            failures = _check_result_json(path)
        finally:
            path.unlink()

        self.assertIn("unknown JSON result shape", "\n".join(failures))

    def test_live_harness_receipt_requires_command_to_match_source_spec(self):
        path = ROOT / "evals" / "results" / "bad_live_harness_receipt.json"
        path.write_text(
            """
{
  "passed": true,
  "cells": [
    {"harness": "sample", "case": "case", "status": "passed"}
  ],
  "summary": {"passed": 1, "failed": 0, "errors": 0, "not_installed": 0},
  "source_spec": "evals/live_harnesses/sdk_agent_smoke.json",
  "command": "python -m claude_agent_harness_opt live-harness evals/live_harnesses/headless_cli_smoke.json"
}
""",
            encoding="utf-8",
        )
        try:
            failures = _check_result_json(path)
        finally:
            path.unlink()

        joined = "\n".join(failures)
        self.assertIn("command spec 'evals/live_harnesses/headless_cli_smoke.json'", joined)
        self.assertIn("does not match source_spec 'evals/live_harnesses/sdk_agent_smoke.json'", joined)

    def test_live_harness_receipt_cells_must_match_source_spec(self):
        path = ROOT / "evals" / "results" / "bad_live_harness_cells.json"
        path.write_text(
            """
{
  "passed": true,
  "cells": [
    {"harness": "missing_harness", "case": "sdk custom pwd tool directed smoke", "status": "passed"}
  ],
  "summary": {"passed": 0, "failed": 0, "errors": 0, "not_installed": 0},
  "source_spec": "evals/live_harnesses/sdk_agent_smoke.json",
  "command": "python -m claude_agent_harness_opt live-harness evals/live_harnesses/sdk_agent_smoke.json"
}
""",
            encoding="utf-8",
        )
        try:
            failures = _check_result_json(path)
        finally:
            path.unlink()

        joined = "\n".join(failures)
        self.assertIn("summary cell counts must equal cells count", joined)
        self.assertIn("unexpected live-harness cell 'missing_harness'", joined)
        self.assertIn("missing live-harness result cell 'openai_agents_sdk_python_latest'", joined)

    def test_model_matrix_receipt_requires_live_and_consistent_rows(self):
        path = ROOT / "evals" / "results" / "bad_model_matrix_receipt.json"
        path.write_text(
            """
{
  "live": false,
  "passed": false,
  "results": [
    {
      "case": "missing definition",
      "provider": "anthropic",
      "harness": "prompt_json",
      "tool_variant": "stock",
      "instruction_variant": "rules",
      "status": "failed",
      "passed": false,
      "chosen_tools": []
    }
  ],
  "cells": [
    {
      "provider": "anthropic",
      "harness": "prompt_json",
      "tool_variant": "stock",
      "instruction_variant": "rules"
    }
  ],
  "case_definitions": [
    {"name": "defined case"}
  ],
  "summary": {"total": 2, "planned": 2},
  "matrix_path": "evals/model_matrix/missing.json",
  "matrix": {},
  "source": {}
}
""",
            encoding="utf-8",
        )
        try:
            failures = _check_result_json(path)
        finally:
            path.unlink()

        joined = "\n".join(failures)
        self.assertIn("model-matrix result.live must be true", joined)
        self.assertIn("summary.total must equal result count", joined)
        self.assertIn("result cases missing from case_definitions", joined)
        self.assertIn("local evidence link missing: evals/model_matrix/missing.json", joined)
        self.assertIn("source must be a nonempty object", joined)

    def test_model_matrix_receipt_rows_must_match_matrix_surface(self):
        path = ROOT / "evals" / "results" / "bad_model_matrix_surface_receipt.json"
        path.write_text(
            """
{
  "live": true,
  "passed": true,
  "results": [
    {
      "case": "missing case",
      "provider": "anthropic",
      "harness": "prompt_json",
      "tool_variant": "stock_zymtrace_mcp",
      "instruction_variant": "zymtrace_host_and_skill_rules",
      "status": "passed",
      "passed": true,
      "chosen_tools": []
    }
  ],
  "cells": [
    {
      "provider": "missing_provider",
      "harness": "missing_harness",
      "tool_variant": "missing_variant",
      "instruction_variant": "missing_instruction"
    }
  ],
  "case_definitions": [
    {"name": "missing case"}
  ],
  "summary": {"total": 1, "planned": 1},
  "matrix_path": "evals/model_matrix/zymtrace_mcp_tool_selection.json",
  "matrix": {},
  "source": {"commit": "sample"}
}
""",
            encoding="utf-8",
        )
        try:
            failures = _check_result_json(path)
        finally:
            path.unlink()

        joined = "\n".join(failures)
        self.assertIn("case_definitions[0] unknown matrix case 'missing case'", joined)
        self.assertIn("cells[0] unknown matrix provider 'missing_provider'", joined)
        self.assertIn("cells[0] unknown matrix harness 'missing_harness'", joined)
        self.assertIn("cells[0] unknown matrix tool_variant 'missing_variant'", joined)
        self.assertIn("cells[0] unknown matrix instruction_variant 'missing_instruction'", joined)
        self.assertIn("results[0] unknown matrix case 'missing case'", joined)
        self.assertIn("results[0] has no matching planned cell", joined)

    def test_coverage_suite_receipt_audits_must_match_summary_and_paths(self):
        path = ROOT / "evals" / "results" / "bad_coverage_suite_receipt.json"
        path.write_text(
            """
{
  "passed": true,
  "matrix_paths": [
    "evals/model_matrix/zymtrace_mcp_tool_selection.json",
    "evals/model_matrix/zymtrace_mcp_tool_selection.json",
    "evals/model_matrix/coding_tool_selection.json"
  ],
  "audits": [
    {
      "matrix_path": "evals/model_matrix/zymtrace_mcp_tool_selection.json",
      "passed": false,
      "summary": {"case_count": 2, "tool_count": 3}
    },
    {
      "matrix_path": "evals/model_matrix/missing.json",
      "passed": "yes",
      "summary": {"case_count": 5, "tool_count": 7}
    }
  ],
  "summary": {
    "failed_matrices": 0,
    "matrix_count": 3,
    "passed_matrices": 2,
    "total_cases": 999,
    "total_tools": 10
  }
}
""",
            encoding="utf-8",
        )
        try:
            failures = _check_result_json(path)
        finally:
            path.unlink()

        joined = "\n".join(failures)
        self.assertIn("duplicate matrix_paths entry 'evals/model_matrix/zymtrace_mcp_tool_selection.json'", joined)
        self.assertIn("audits[0] must pass", joined)
        self.assertIn("audits[1].passed must be boolean", joined)
        self.assertIn("matrix_paths entry missing audit 'evals/model_matrix/coding_tool_selection.json'", joined)
        self.assertIn("audit matrix_path missing from matrix_paths 'evals/model_matrix/missing.json'", joined)
        self.assertIn("summary.passed_matrices must equal passing audit count", joined)
        self.assertIn("summary.failed_matrices must equal failed audit count", joined)
        self.assertIn("summary.total_cases must equal audit case_count sum", joined)

    def test_result_markdown_requires_summary_and_review_section(self):
        path = ROOT / "evals" / "results" / "bad_receipt.md"
        path.write_text("# Receipt\n\nNo structured result here.\n", encoding="utf-8")
        try:
            failures = _check_result_markdown(path)
        finally:
            path.unlink()

        joined = "\n".join(failures)
        self.assertIn("missing Passed summary", joined)
        self.assertIn("missing review section", joined)

    def test_matrix_surface_coverage_reports_target_matrix_gaps(self):
        target_dir = ROOT / "evals" / "targets" / "temporary_bad_matrix"
        target_dir.mkdir(parents=True, exist_ok=True)
        path = target_dir / "bad_matrix.json"
        path.write_text(
            """
{
  "cases": [
    {
      "expected_tools": ["lookup"],
      "forbidden_tools": [],
      "name": "lookup case",
      "task": "Lookup a value."
    }
  ],
  "profiles": [{"harnesses": ["prompt_json"], "provider": "trace_fixture"}],
  "tool_variants": [
    {
      "name": "sample",
      "tools": [
        {"name": "lookup", "purpose": "Lookup values.", "quality_checks": ["Check ids."]},
        {"name": "fallback", "purpose": "Fallback safely.", "quality_checks": ["Check fallback."]}
      ]
    }
  ]
}
""",
            encoding="utf-8",
        )
        try:
            failures = _check_matrix_surface_coverage()
        finally:
            path.unlink()
            target_dir.rmdir()

        joined = "\n".join(failures)
        self.assertIn("evals/targets/temporary_bad_matrix/bad_matrix.json", joined)
        self.assertIn("matrix coverage failed", joined)

    def test_matrix_surface_coverage_skips_disappearing_paths(self):
        gone = ROOT / "evals" / "targets" / "temporary_bad_matrix" / "gone.json"
        with (
            patch("scripts.check_finding_packets._matrix_surface_paths", return_value=[gone]),
            patch("scripts.check_finding_packets.audit_matrix_coverage", side_effect=FileNotFoundError("gone")),
        ):
            failures = _check_matrix_surface_coverage()

        self.assertEqual([], failures)


if __name__ == "__main__":
    unittest.main()
