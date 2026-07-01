from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

from scripts.check_finding_packets import (
    ROOT,
    _check_matrix_surface_coverage,
    _check_pr_packet_evidence,
    _check_pr_packet_text,
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

    def test_pr_packet_evidence_allows_guardrail_without_delta(self):
        failures = _check_pr_packet_evidence(
            ROOT / "evals" / "pr_packets" / "guardrail" / "evidence.json",
            {
                "packet_type": "guardrail",
                "cases": [{"name": "already routed safely"}],
                "comparison": {
                    "baseline_score": 1.0,
                    "baseline_variant": "stock",
                    "candidate_score": 1.0,
                    "candidate_variant": "tuned",
                    "delta": 0.0,
                    "minimum_delta": 0.1,
                    "promote": False,
                },
                "matrix": {
                    "tool_variants": [
                        {"name": "stock", "tools": []},
                        {"name": "tuned", "tools": []},
                    ]
                },
                "result": {
                    "cells": [
                        {
                            "provider": "anthropic",
                            "harness": "prompt_json",
                            "tool_variant": "stock",
                            "instruction_variant": "default",
                        },
                        {
                            "provider": "anthropic",
                            "harness": "prompt_json",
                            "tool_variant": "tuned",
                            "instruction_variant": "default",
                        },
                    ],
                    "live": True,
                    "matrix_path": "evals/model_matrix/humwork_mcp_tool_selection.json",
                    "results": [
                        {
                            "case": "already routed safely",
                            "provider": "anthropic",
                            "harness": "prompt_json",
                            "tool_variant": "stock",
                            "instruction_variant": "default",
                            "status": "passed",
                            "passed": True,
                        },
                        {
                            "case": "already routed safely",
                            "provider": "anthropic",
                            "harness": "prompt_json",
                            "tool_variant": "tuned",
                            "instruction_variant": "default",
                            "status": "passed",
                            "passed": True,
                        },
                    ],
                    "summary": {"total": 2},
                },
                "source": {"repo": "example"},
            },
        )

        self.assertEqual([], failures)

    def test_pr_packet_text_requires_public_evidence_links(self):
        failures = _check_pr_packet_text(
            ROOT / "evals" / "pr_packets" / "sample_packet",
            {
                "packet_type": "improvement",
                "result": {
                    "matrix_path": "evals/model_matrix/sample_matrix.json",
                },
            },
            "Confirmed improvement. This clears the adversarially-confirmed to add value bar.",
            "The result was promoted by value bar: yes.",
        )

        joined = "\n".join(failures)
        self.assertIn(
            "sample_packet/README.md: missing public evidence JSON link to "
            "evals/pr_packets/sample_packet/evidence.json",
            joined,
        )
        self.assertIn(
            "sample_packet/README.md: missing public matrix link to "
            "evals/model_matrix/sample_matrix.json",
            joined,
        )
        self.assertIn("sample_packet/README.md: missing public result artifact link", joined)
        self.assertIn("sample_packet/PR_BODY.md: missing public result artifact link", joined)

    def test_pr_packet_text_requires_packet_type_language(self):
        public_links = """
- Evidence JSON: [evidence.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/sample_guardrail/evidence.json)
- Matrix: [sample_matrix.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/model_matrix/sample_matrix.json)
- Result artifact: [sample_result.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/sample_result.md)
"""
        failures = _check_pr_packet_text(
            ROOT / "evals" / "pr_packets" / "sample_guardrail",
            {
                "packet_type": "guardrail",
                "result": {
                    "matrix_path": "evals/model_matrix/sample_matrix.json",
                },
            },
            f"Guardrail packet.\n{public_links}",
            f"Guardrail coverage retained.\n{public_links}",
        )

        self.assertIn(
            "sample_guardrail/README.md: guardrail packet must say no upstream change is promoted",
            "\n".join(failures),
        )

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

    def test_live_harness_receipt_summary_must_match_cells(self):
        path = ROOT / "evals" / "results" / "bad_live_harness_summary.json"
        path.write_text(
            """
{
  "passed": false,
  "cells": [
    {
      "harness": "claude_agent_sdk_python_latest",
      "case": "sdk custom pwd tool directed smoke",
      "status": "auth_failed",
      "directed_thinking_passed": true
    },
    {
      "harness": "openai_agents_sdk_python_latest",
      "case": "sdk custom pwd tool directed smoke",
      "status": "weird",
      "directed_thinking_passed": false
    },
    {
      "harness": "openai_agents_sdk_python_latest",
      "case": "sdk custom pwd tool final-answer smoke",
      "status": "planned",
      "directed_thinking_passed": false
    }
  ],
  "summary": {
    "passed": 1,
    "failed": 0,
    "errors": 0,
    "not_installed": 0,
    "planned": 0,
    "directed_thinking_visible": 0
  },
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
        self.assertIn("summary.directed_thinking_visible must match live-harness cells", joined)
        self.assertIn("summary.errors must match live-harness cells", joined)
        self.assertIn("summary.passed must match live-harness cells", joined)
        self.assertIn("summary.planned must match live-harness cells", joined)
        self.assertIn("cells[1].status is not a known live-harness status", joined)

    def test_live_harness_receipt_summary_counts_reject_boolean_values(self):
        path = ROOT / "evals" / "results" / "bad_live_harness_boolean_summary.json"
        path.write_text(
            """
{
  "passed": true,
  "cells": [
    {
      "harness": "claude_agent_sdk_python_latest",
      "case": "sdk custom pwd tool directed smoke",
      "status": "passed",
      "directed_thinking_passed": false
    }
  ],
  "summary": {
    "passed": true,
    "failed": 0,
    "errors": 0,
    "not_installed": 0,
    "planned": 0,
    "directed_thinking_visible": 0
  },
  "source_spec": "evals/live_harnesses/sdk_agent_smoke.json",
  "command": "python -m claude_agent_harness_opt live-harness evals/live_harnesses/sdk_agent_smoke.json --harnesses claude_agent_sdk_python_latest --cases 'sdk custom pwd tool directed smoke'"
}
""",
            encoding="utf-8",
        )
        try:
            failures = _check_result_json(path)
        finally:
            path.unlink()

        joined = "\n".join(failures)
        self.assertIn("summary.passed must be an integer", joined)
        self.assertIn("summary cell counts must equal cells count", joined)

    def test_live_harness_receipt_cell_fields_must_be_coherent(self):
        path = ROOT / "evals" / "results" / "bad_live_harness_cell_fields.json"
        path.write_text(
            """
{
  "passed": false,
  "cells": [
    {
      "harness": "claude_agent_sdk_python_latest",
      "case": "sdk custom pwd tool directed smoke",
      "status": "passed",
      "exit_code": "1",
      "tool_use_passed": "no",
      "directed_thinking_passed": "yes",
      "tool_call_count": -1
    },
    {
      "harness": "openai_agents_sdk_python_latest",
      "case": "sdk custom pwd tool directed smoke",
      "status": "auth_failed",
      "exit_code": 0,
      "tool_use_passed": true,
      "directed_thinking_passed": false,
      "tool_call_count": 0
    }
  ],
  "summary": {
    "passed": 1,
    "failed": 0,
    "errors": 1,
    "not_installed": 0,
    "planned": 0,
    "directed_thinking_visible": 0
  },
  "source_spec": "evals/live_harnesses/sdk_agent_smoke.json",
  "command": "python -m claude_agent_harness_opt live-harness evals/live_harnesses/sdk_agent_smoke.json --harnesses claude_agent_sdk_python_latest,openai_agents_sdk_python_latest --cases 'sdk custom pwd tool directed smoke'"
}
""",
            encoding="utf-8",
        )
        try:
            failures = _check_result_json(path)
        finally:
            path.unlink()

        joined = "\n".join(failures)
        self.assertIn("cells[0].exit_code must be an integer or null", joined)
        self.assertIn("cells[0].tool_use_passed must be boolean", joined)
        self.assertIn("cells[0].directed_thinking_passed must be boolean", joined)
        self.assertIn("cells[0].tool_call_count must be a nonnegative integer", joined)
        self.assertIn("cells[0].passed status must have exit_code 0", joined)
        self.assertIn("cells[0].passed status must have tool_use_passed true", joined)
        self.assertIn("cells[1].auth_failed status must have nonzero exit_code", joined)
        self.assertIn("cells[1].auth_failed status must have tool_use_passed false", joined)

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

    def test_model_matrix_receipt_result_passed_must_match_status(self):
        path = ROOT / "evals" / "results" / "bad_model_matrix_status_receipt.json"
        path.write_text(
            """
{
  "live": true,
  "passed": true,
  "results": [
    {
      "case": "default project metrics discovery skips search",
      "provider": "anthropic",
      "harness": "prompt_json",
      "tool_variant": "tuned_zymtrace_mcp_boundaries",
      "instruction_variant": "zymtrace_host_and_skill_rules",
      "status": "failed",
      "passed": true,
      "chosen_tools": ["project_metrics_activity_aggr"]
    }
  ],
  "cells": [
    {
      "provider": "anthropic",
      "harness": "prompt_json",
      "tool_variant": "tuned_zymtrace_mcp_boundaries",
      "instruction_variant": "zymtrace_host_and_skill_rules",
      "passed": 0,
      "failed": 1,
      "errors": 0,
      "skipped": 0,
      "score": 0.0
    }
  ],
  "case_definitions": [
    {"name": "default project metrics discovery skips search"}
  ],
  "summary": {
    "errors": 0,
    "failed_cases": 1,
    "passed_cases": 0,
    "planned": 1,
    "score": 0.0,
    "skipped": 0,
    "total": 1
  },
  "matrix_path": "evals/model_matrix/zymtrace_mcp_tool_selection.json",
  "matrix": "zymtrace mcp tool-selection matrix",
  "source": {"commit": "sample"}
}
""",
            encoding="utf-8",
        )
        try:
            failures = _check_result_json(path)
        finally:
            path.unlink()

        self.assertIn("results[0].passed must match status", "\n".join(failures))

    def test_model_matrix_receipt_result_status_must_be_known(self):
        path = ROOT / "evals" / "results" / "bad_model_matrix_unknown_status_receipt.json"
        path.write_text(
            """
{
  "live": true,
  "passed": false,
  "results": [
    {
      "case": "default project metrics discovery skips search",
      "provider": "anthropic",
      "harness": "prompt_json",
      "tool_variant": "tuned_zymtrace_mcp_boundaries",
      "instruction_variant": "zymtrace_host_and_skill_rules",
      "status": "weird",
      "passed": false,
      "chosen_tools": []
    }
  ],
  "cells": [
    {
      "provider": "anthropic",
      "harness": "prompt_json",
      "tool_variant": "tuned_zymtrace_mcp_boundaries",
      "instruction_variant": "zymtrace_host_and_skill_rules",
      "passed": 0,
      "failed": 0,
      "errors": 0,
      "skipped": 0,
      "score": 0.0
    }
  ],
  "case_definitions": [
    {"name": "default project metrics discovery skips search"}
  ],
  "summary": {
    "errors": 0,
    "failed_cases": 0,
    "passed_cases": 0,
    "planned": 1,
    "score": 0.0,
    "skipped": 0,
    "total": 1
  },
  "matrix_path": "evals/model_matrix/zymtrace_mcp_tool_selection.json",
  "matrix": "zymtrace mcp tool-selection matrix",
  "source": {"commit": "sample"}
}
""",
            encoding="utf-8",
        )
        try:
            failures = _check_result_json(path)
        finally:
            path.unlink()

        self.assertIn("results[0].status is not a known model-matrix status", "\n".join(failures))

    def test_model_matrix_receipt_cell_summaries_must_match_rows(self):
        path = ROOT / "evals" / "results" / "bad_model_matrix_cell_receipt.json"
        path.write_text(
            """
{
  "live": true,
  "passed": true,
  "results": [
    {
      "case": "default project metrics discovery skips search",
      "provider": "anthropic",
      "harness": "prompt_json",
      "tool_variant": "tuned_zymtrace_mcp_boundaries",
      "instruction_variant": "zymtrace_host_and_skill_rules",
      "status": "passed",
      "passed": true,
      "chosen_tools": ["project_metrics_activity_aggr"]
    },
    {
      "case": "default project metrics discovery skips search",
      "provider": "anthropic",
      "harness": "prompt_json",
      "tool_variant": "tuned_zymtrace_mcp_boundaries",
      "instruction_variant": "zymtrace_host_and_skill_rules",
      "status": "skipped",
      "passed": false,
      "chosen_tools": []
    }
  ],
  "cells": [
    {
      "provider": "anthropic",
      "harness": "prompt_json",
      "tool_variant": "tuned_zymtrace_mcp_boundaries",
      "instruction_variant": "zymtrace_host_and_skill_rules",
      "passed": 2,
      "failed": 0,
      "errors": 0,
      "skipped": 0,
      "score": 0.5
    }
  ],
  "case_definitions": [
    {"name": "default project metrics discovery skips search"}
  ],
  "summary": {"total": 2, "planned": 2},
  "matrix_path": "evals/model_matrix/zymtrace_mcp_tool_selection.json",
  "matrix": "zymtrace mcp tool-selection matrix",
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
        self.assertIn("cells[0].passed does not match result rows", joined)
        self.assertIn("cells[0].skipped does not match result rows", joined)
        self.assertIn("cells[0].score does not match result rows", joined)

    def test_model_matrix_receipt_counts_reject_boolean_values(self):
        path = ROOT / "evals" / "results" / "bad_model_matrix_boolean_counts.json"
        path.write_text(
            """
{
  "live": true,
  "passed": true,
  "results": [
    {
      "case": "default project metrics discovery skips search",
      "provider": "anthropic",
      "harness": "prompt_json",
      "tool_variant": "tuned_zymtrace_mcp_boundaries",
      "instruction_variant": "zymtrace_host_and_skill_rules",
      "status": "passed",
      "passed": true,
      "chosen_tools": ["project_metrics_activity_aggr"]
    }
  ],
  "cells": [
    {
      "provider": "anthropic",
      "harness": "prompt_json",
      "tool_variant": "tuned_zymtrace_mcp_boundaries",
      "instruction_variant": "zymtrace_host_and_skill_rules",
      "passed": true,
      "failed": 0,
      "errors": 0,
      "skipped": 0,
      "score": 1.0
    }
  ],
  "case_definitions": [
    {"name": "default project metrics discovery skips search"}
  ],
  "summary": {
    "errors": 0,
    "failed_cases": 0,
    "passed_cases": true,
    "planned": 1,
    "score": 1.0,
    "skipped": 0,
    "total": 1
  },
  "matrix_path": "evals/model_matrix/zymtrace_mcp_tool_selection.json",
  "matrix": "zymtrace mcp tool-selection matrix",
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
        self.assertIn("summary.passed_cases must be an integer", joined)
        self.assertIn("cells[0].passed must be an integer", joined)

    def test_model_matrix_receipt_summary_must_match_rows(self):
        path = ROOT / "evals" / "results" / "bad_model_matrix_summary_receipt.json"
        path.write_text(
            """
{
  "live": true,
  "passed": true,
  "results": [
    {
      "case": "default project metrics discovery skips search",
      "provider": "anthropic",
      "harness": "prompt_json",
      "tool_variant": "tuned_zymtrace_mcp_boundaries",
      "instruction_variant": "zymtrace_host_and_skill_rules",
      "status": "passed",
      "passed": true,
      "chosen_tools": ["project_metrics_activity_aggr"]
    },
    {
      "case": "cpu rank first containerized apps",
      "provider": "anthropic",
      "harness": "prompt_json",
      "tool_variant": "tuned_zymtrace_mcp_boundaries",
      "instruction_variant": "zymtrace_host_and_skill_rules",
      "status": "failed",
      "passed": false,
      "chosen_tools": ["flamegraph"]
    },
    {
      "case": "gpu inference workflow starts with metrics",
      "provider": "anthropic",
      "harness": "prompt_json",
      "tool_variant": "tuned_zymtrace_mcp_boundaries",
      "instruction_variant": "zymtrace_host_and_skill_rules",
      "status": "skipped",
      "passed": false,
      "chosen_tools": []
    }
  ],
  "cells": [
    {
      "provider": "anthropic",
      "harness": "prompt_json",
      "tool_variant": "tuned_zymtrace_mcp_boundaries",
      "instruction_variant": "zymtrace_host_and_skill_rules",
      "passed": 1,
      "failed": 1,
      "errors": 0,
      "skipped": 1,
      "score": 0.5
    }
  ],
  "case_definitions": [
    {"name": "default project metrics discovery skips search"},
    {"name": "cpu rank first containerized apps"},
    {"name": "gpu inference workflow starts with metrics"}
  ],
  "summary": {
    "errors": 1,
    "failed_cases": 0,
    "passed_cases": 3,
    "planned": 3,
    "score": 1.0,
    "skipped": 0,
    "total": 3
  },
  "matrix_path": "evals/model_matrix/zymtrace_mcp_tool_selection.json",
  "matrix": "zymtrace mcp tool-selection matrix",
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
        self.assertIn("summary.errors must match result rows", joined)
        self.assertIn("summary.failed_cases must match result rows", joined)
        self.assertIn("summary.passed_cases must match result rows", joined)
        self.assertIn("summary.skipped must match result rows", joined)
        self.assertIn("summary.score must match result rows", joined)
        self.assertIn("passed must match result rows", joined)

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

    def test_coverage_suite_receipt_counts_reject_boolean_values(self):
        path = ROOT / "evals" / "results" / "bad_coverage_suite_boolean_counts.json"
        path.write_text(
            """
{
  "passed": true,
  "matrix_paths": [
    "evals/model_matrix/zymtrace_mcp_tool_selection.json"
  ],
  "audits": [
    {
      "matrix_path": "evals/model_matrix/zymtrace_mcp_tool_selection.json",
      "passed": true,
      "summary": {"case_count": true, "tool_count": 1}
    }
  ],
  "summary": {
    "failed_matrices": false,
    "matrix_count": true,
    "passed_matrices": true,
    "total_cases": 1,
    "total_tools": true
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
        self.assertIn("summary.failed_matrices must be an integer", joined)
        self.assertIn("summary.matrix_count must be an integer", joined)
        self.assertIn("summary.passed_matrices must be an integer", joined)
        self.assertIn("audits[0].summary.case_count must be an integer", joined)
        self.assertIn("summary.total_tools must be an integer", joined)

    def test_matrix_coverage_receipt_must_match_current_audit(self):
        path = ROOT / "evals" / "results" / "bad_matrix_coverage_receipt.json"
        path.write_text(
            """
{
  "passed": true,
  "matrix_path": "evals/model_matrix/zymtrace_mcp_tool_selection.json",
  "tools": [{"name": "stale_tool"}],
  "cases": [{"name": "stale case"}],
  "boundary_pairs": [
    {"expected_tool": "stale_tool", "forbidden_tool": "other_tool", "cases": ["stale case"]}
  ],
  "summary": {
    "tool_count": 1,
    "case_count": 1,
    "boundary_pair_count": 1
  },
  "uncovered": {}
}
""",
            encoding="utf-8",
        )
        try:
            failures = _check_result_json(path)
        finally:
            path.unlink()

        joined = "\n".join(failures)
        self.assertIn("summary.tool_count does not match current matrix audit", joined)
        self.assertIn("coverage receipt has stale tool 'stale_tool'", joined)
        self.assertIn("coverage receipt missing current tool 'flamegraph'", joined)
        self.assertIn("coverage receipt has stale case 'stale case'", joined)
        self.assertIn("coverage receipt has stale boundary pair", joined)

    def test_matrix_coverage_receipt_counts_reject_boolean_values(self):
        path = ROOT / "evals" / "results" / "bad_matrix_coverage_boolean_counts.json"
        path.write_text(
            """
{
  "passed": true,
  "matrix_path": "evals/model_matrix/zymtrace_mcp_tool_selection.json",
  "tools": [{"name": "flamegraph"}],
  "cases": [{"name": "default project metrics discovery skips search"}],
  "boundary_pairs": [
    {
      "expected_tool": "project_metrics_activity_aggr",
      "forbidden_tool": "search",
      "cases": ["default project metrics discovery skips search"]
    }
  ],
  "summary": {
    "tool_count": true,
    "case_count": 1,
    "boundary_pair_count": 1
  },
  "uncovered": {}
}
""",
            encoding="utf-8",
        )
        try:
            failures = _check_result_json(path)
        finally:
            path.unlink()

        self.assertIn("summary.tool_count must be an integer", "\n".join(failures))

    def test_matrix_coverage_receipt_items_must_be_structured(self):
        path = ROOT / "evals" / "results" / "bad_matrix_coverage_items.json"
        path.write_text(
            """
{
  "passed": true,
  "matrix_path": "evals/model_matrix/zymtrace_mcp_tool_selection.json",
  "tools": [
    {"name": "flamegraph"},
    {"name": "flamegraph"},
    "not an object",
    {"description": "missing name"}
  ],
  "cases": [
    {"name": "default project metrics discovery skips search"},
    {"name": "default project metrics discovery skips search"},
    7,
    {"name": ""}
  ],
  "boundary_pairs": [
    {
      "expected_tool": "project_metrics_activity_aggr",
      "forbidden_tool": "search",
      "cases": ["default project metrics discovery skips search"]
    },
    {
      "expected_tool": "project_metrics_activity_aggr",
      "forbidden_tool": "search",
      "cases": ["default project metrics discovery skips search"]
    },
    "not an object",
    {
      "expected_tool": "",
      "forbidden_tool": "search",
      "cases": []
    },
    {
      "expected_tool": "flamegraph",
      "forbidden_tool": "",
      "cases": [42, ""]
    }
  ],
  "summary": {
    "tool_count": 4,
    "case_count": 4,
    "boundary_pair_count": 5
  },
  "uncovered": {}
}
""",
            encoding="utf-8",
        )
        try:
            failures = _check_result_json(path)
        finally:
            path.unlink()

        joined = "\n".join(failures)
        self.assertIn("duplicate coverage receipt tool 'flamegraph'", joined)
        self.assertIn("tools[2] must be an object", joined)
        self.assertIn("tools[3] missing name", joined)
        self.assertIn("duplicate coverage receipt case 'default project metrics discovery skips search'", joined)
        self.assertIn("cases[2] must be an object", joined)
        self.assertIn("cases[3] missing name", joined)
        self.assertIn("duplicate coverage receipt boundary pair 'project_metrics_activity_aggr'/'search'", joined)
        self.assertIn("boundary_pairs[2] must be an object", joined)
        self.assertIn("boundary_pairs[3] missing expected_tool", joined)
        self.assertIn("boundary_pairs[3].cases must be a nonempty list", joined)
        self.assertIn("boundary_pairs[4] missing forbidden_tool", joined)
        self.assertIn("boundary_pairs[4].cases[0] must be a nonempty string", joined)
        self.assertIn("boundary_pairs[4].cases[1] must be a nonempty string", joined)

    def test_matrix_coverage_receipt_uncovered_buckets_must_be_known_lists(self):
        path = ROOT / "evals" / "results" / "bad_matrix_coverage_uncovered.json"
        path.write_text(
            """
{
  "passed": true,
  "matrix_path": "evals/model_matrix/zymtrace_mcp_tool_selection.json",
  "tools": [{"name": "flamegraph"}],
  "cases": [{"name": "default project metrics discovery skips search"}],
  "boundary_pairs": [
    {
      "expected_tool": "project_metrics_activity_aggr",
      "forbidden_tool": "search",
      "cases": ["default project metrics discovery skips search"]
    }
  ],
  "summary": {
    "tool_count": 1,
    "case_count": 1,
    "boundary_pair_count": 1
  },
  "uncovered": {
    "never_expected": "",
    "never_forbidden": {},
    "typo_gap": [],
    "missing_quality_checks": ["flamegraph"]
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
        self.assertIn("uncovered.never_expected must be a list", joined)
        self.assertIn("uncovered.never_forbidden must be a list", joined)
        self.assertIn("uncovered.typo_gap is not a known matrix-coverage gap bucket", joined)
        self.assertIn("uncovered.missing_quality_checks must be empty", joined)

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

    def test_coverage_markdown_summary_must_match_sibling_json(self):
        path = ROOT / "evals" / "results" / "bad_coverage_receipt.md"
        json_path = path.with_suffix(".json")
        path.write_text(
            "# Matrix Coverage\n\n"
            "Passed: yes\n"
            "Tools: 99\n"
            "Cases: 1\n"
            "Boundary pairs: 1\n\n"
            "## Gaps\n\n"
            "- none\n",
            encoding="utf-8",
        )
        json_path.write_text(
            """
{
  "passed": false,
  "summary": {
    "tool_count": 2,
    "case_count": 1,
    "boundary_pair_count": 1
  }
}
""",
            encoding="utf-8",
        )
        try:
            failures = _check_result_markdown(path)
        finally:
            path.unlink()
            json_path.unlink()

        joined = "\n".join(failures)
        self.assertIn("Passed summary does not match sibling JSON receipt", joined)
        self.assertIn("Tools summary does not match sibling JSON receipt", joined)

    def test_coverage_markdown_requires_summary_fields_backed_by_sibling_json(self):
        path = ROOT / "evals" / "results" / "bad_coverage_missing_summary_fields.md"
        json_path = path.with_suffix(".json")
        gap_lines = "\n".join(
            [
                "- Never expected: none",
                "- Never forbidden: none",
                "- Case expectation gaps: none",
                "- Expected without argument checks: none",
                "- Duplicate tool names: none",
                "- Identity gaps: none",
                "- Missing quality checks: none",
                "- Missing required check families: none",
                "- Variant surface mismatches: none",
                "- Source tool count mismatch: none",
                "- Cases without forbidden tools: none",
                "- Cases without check_family: none",
                "- Unknown expected tools: none",
                "- Unknown forbidden tools: none",
                "- Value-bar gaps: none",
            ]
        )
        path.write_text(
            "# Matrix Coverage\n\n"
            "Passed: yes\n"
            "Tools: 1\n"
            "Cases: 1\n\n"
            "## Gaps\n\n"
            f"{gap_lines}\n",
            encoding="utf-8",
        )
        json_path.write_text(
            """
{
  "passed": true,
  "summary": {
    "tool_count": 1,
    "case_count": 1,
    "argument_case_count": 1,
    "tool_expected_coverage": 1.0
  },
  "uncovered": {}
}
""",
            encoding="utf-8",
        )
        try:
            failures = _check_result_markdown(path)
        finally:
            path.unlink()
            json_path.unlink()

        joined = "\n".join(failures)
        self.assertIn("missing Cases with argument checks summary", joined)
        self.assertIn("missing Expected tool coverage summary", joined)

    def test_coverage_markdown_rejects_duplicate_summary_lines(self):
        path = ROOT / "evals" / "results" / "bad_coverage_duplicate_summaries.md"
        json_path = path.with_suffix(".json")
        gap_lines = "\n".join(
            [
                "- Never expected: none",
                "- Never forbidden: none",
                "- Case expectation gaps: none",
                "- Expected without argument checks: none",
                "- Duplicate tool names: none",
                "- Identity gaps: none",
                "- Missing quality checks: none",
                "- Missing required check families: none",
                "- Variant surface mismatches: none",
                "- Source tool count mismatch: none",
                "- Cases without forbidden tools: none",
                "- Cases without check_family: none",
                "- Unknown expected tools: none",
                "- Unknown forbidden tools: none",
                "- Value-bar gaps: none",
            ]
        )
        path.write_text(
            "# Matrix Coverage\n\n"
            "Passed: yes\n"
            "Passed: no\n"
            "Tools: 1\n"
            "Tools: 99\n"
            "Cases: 1\n"
            "Expected tool coverage: 1.000\n"
            "Expected tool coverage: 0.000\n\n"
            "## Gaps\n\n"
            f"{gap_lines}\n",
            encoding="utf-8",
        )
        json_path.write_text(
            """
{
  "passed": true,
  "summary": {
    "tool_count": 1,
    "case_count": 1,
    "tool_expected_coverage": 1.0
  },
  "uncovered": {}
}
""",
            encoding="utf-8",
        )
        try:
            failures = _check_result_markdown(path)
        finally:
            path.unlink()
            json_path.unlink()

        joined = "\n".join(failures)
        self.assertIn("duplicate Passed summary", joined)
        self.assertIn("duplicate Tools summary", joined)
        self.assertIn("duplicate Expected tool coverage summary", joined)

    def test_coverage_markdown_tables_must_match_sibling_json(self):
        path = ROOT / "evals" / "results" / "bad_coverage_table_receipt.md"
        json_path = path.with_suffix(".json")
        path.write_text(
            "# Matrix Coverage\n\n"
            "Passed: yes\n"
            "Tools: 1\n"
            "Cases: 2\n"
            "Expected tool coverage: 0.000\n"
            "Forbidden tool coverage: 0.000\n\n"
            "## Tool Coverage\n\n"
            "| Tool | Expected Cases | Forbidden Cases | Argument Cases | Quality Checks |\n"
            "|---|---:|---:|---:|---|\n"
            "| lookup | 1 | 0 | 0 | no |\n"
            "| stale | 0 | 0 | 0 | no |\n\n"
            "## Check Families\n\n"
            "| Family | Cases |\n"
            "|---|---:|\n"
            "| lookup | 1 |\n"
            "| stale_family | 1 |\n",
            encoding="utf-8",
        )
        json_path.write_text(
            """
{
  "passed": true,
  "summary": {
    "tool_count": 1,
    "case_count": 2,
    "tool_expected_coverage": 1.0,
    "forbidden_tool_coverage": 1.0
  },
  "tools": [
    {
      "name": "lookup",
      "expected_cases": ["first", "second"],
      "forbidden_cases": ["second"],
      "argument_cases": ["first"],
      "has_quality_checks": true
    }
  ],
  "check_families": {
    "lookup": ["first", "second"]
  }
}
""",
            encoding="utf-8",
        )
        try:
            failures = _check_result_markdown(path)
        finally:
            path.unlink()
            json_path.unlink()

        joined = "\n".join(failures)
        self.assertIn("Expected tool coverage summary does not match sibling JSON receipt", joined)
        self.assertIn("Forbidden tool coverage summary does not match sibling JSON receipt", joined)
        self.assertIn("Tool Coverage 'lookup' Expected Cases does not match sibling JSON receipt", joined)
        self.assertIn("Tool Coverage 'lookup' Forbidden Cases does not match sibling JSON receipt", joined)
        self.assertIn("Tool Coverage 'lookup' Argument Cases does not match sibling JSON receipt", joined)
        self.assertIn("Tool Coverage 'lookup' Quality Checks does not match sibling JSON receipt", joined)
        self.assertIn("Tool Coverage table has stale tool 'stale'", joined)
        self.assertIn("Check Families 'lookup' count does not match sibling JSON receipt", joined)
        self.assertIn("Check Families table has stale family 'stale_family'", joined)

    def test_coverage_markdown_gaps_must_match_sibling_json(self):
        path = ROOT / "evals" / "results" / "bad_coverage_gap_receipt.md"
        json_path = path.with_suffix(".json")
        path.write_text(
            "# Matrix Coverage\n\n"
            "Passed: no\n"
            "Tools: 1\n"
            "Cases: 1\n\n"
            "## Gaps\n\n"
            "- Never expected: none\n"
            "- Missing quality checks: stale_tool\n"
            "- Duplicate tool names: none\n",
            encoding="utf-8",
        )
        json_path.write_text(
            """
{
  "passed": false,
  "summary": {
    "tool_count": 1,
    "case_count": 1
  },
  "uncovered": {
    "never_expected": ["write_file"],
    "missing_quality_checks": [],
    "duplicate_tool_names": [
      {"variant": "baseline", "duplicate_tools": ["lookup"]}
    ]
  }
}
""",
            encoding="utf-8",
        )
        try:
            failures = _check_result_markdown(path)
        finally:
            path.unlink()
            json_path.unlink()

        joined = "\n".join(failures)
        self.assertIn("Gaps 'Never expected' does not match sibling JSON receipt", joined)
        self.assertIn("Gaps 'Missing quality checks' does not match sibling JSON receipt", joined)
        self.assertIn("Gaps 'Duplicate tool names' does not match sibling JSON receipt", joined)

    def test_coverage_markdown_gaps_must_have_complete_label_set(self):
        missing_path = ROOT / "evals" / "results" / "bad_coverage_missing_gaps.md"
        missing_json_path = missing_path.with_suffix(".json")
        missing_path.write_text(
            "# Matrix Coverage\n\n"
            "Passed: yes\n"
            "Tools: 1\n"
            "Cases: 1\n\n"
            "## Tool Coverage\n\n"
            "| Tool | Expected Cases | Forbidden Cases | Argument Cases | Quality Checks |\n"
            "|---|---:|---:|---:|---|\n",
            encoding="utf-8",
        )
        missing_json_path.write_text(
            """
{
  "passed": true,
  "summary": {"tool_count": 1, "case_count": 1},
  "uncovered": {}
}
""",
            encoding="utf-8",
        )
        try:
            missing_failures = _check_result_markdown(missing_path)
        finally:
            missing_path.unlink()
            missing_json_path.unlink()

        path = ROOT / "evals" / "results" / "bad_coverage_gap_labels.md"
        json_path = path.with_suffix(".json")
        path.write_text(
            "# Matrix Coverage\n\n"
            "Passed: yes\n"
            "Tools: 1\n"
            "Cases: 1\n\n"
            "## Gaps\n\n"
            "- Never expected: none\n"
            "- Never expected: none\n"
            "- Typo gap: none\n",
            encoding="utf-8",
        )
        json_path.write_text(
            """
{
  "passed": true,
  "summary": {"tool_count": 1, "case_count": 1},
  "uncovered": {}
}
""",
            encoding="utf-8",
        )
        try:
            failures = _check_result_markdown(path)
        finally:
            path.unlink()
            json_path.unlink()

        joined = "\n".join(missing_failures + failures)
        self.assertIn("missing Gaps section", joined)
        self.assertIn("Gaps has duplicate label 'Never expected'", joined)
        self.assertIn("Gaps has unknown label 'Typo gap'", joined)
        self.assertIn("Gaps missing label 'Never forbidden'", joined)

    def test_coverage_markdown_requires_tables_backed_by_sibling_json(self):
        path = ROOT / "evals" / "results" / "bad_coverage_missing_tables.md"
        json_path = path.with_suffix(".json")
        gap_lines = "\n".join(
            [
                "- Never expected: none",
                "- Never forbidden: none",
                "- Case expectation gaps: none",
                "- Expected without argument checks: none",
                "- Duplicate tool names: none",
                "- Identity gaps: none",
                "- Missing quality checks: none",
                "- Missing required check families: none",
                "- Variant surface mismatches: none",
                "- Source tool count mismatch: none",
                "- Cases without forbidden tools: none",
                "- Cases without check_family: none",
                "- Unknown expected tools: none",
                "- Unknown forbidden tools: none",
                "- Value-bar gaps: none",
            ]
        )
        path.write_text(
            "# Matrix Coverage\n\n"
            "Passed: yes\n"
            "Tools: 1\n"
            "Cases: 1\n\n"
            "## Gaps\n\n"
            f"{gap_lines}\n",
            encoding="utf-8",
        )
        json_path.write_text(
            """
{
  "passed": true,
  "summary": {"tool_count": 1, "case_count": 1},
  "tools": [
    {
      "name": "lookup",
      "expected_cases": ["first"],
      "forbidden_cases": [],
      "argument_cases": [],
      "has_quality_checks": true
    }
  ],
  "check_families": {"lookup": ["first"]},
  "uncovered": {}
}
""",
            encoding="utf-8",
        )
        try:
            failures = _check_result_markdown(path)
        finally:
            path.unlink()
            json_path.unlink()

        suite_path = ROOT / "evals" / "results" / "bad_coverage_suite_missing_matrix_summary.md"
        suite_json_path = suite_path.with_suffix(".json")
        suite_path.write_text(
            "# Matrix Coverage Suite\n\n"
            "Passed: yes\n"
            "Matrices: 1\n",
            encoding="utf-8",
        )
        suite_json_path.write_text(
            """
{
  "passed": true,
  "summary": {"matrix_count": 1},
  "audits": [
    {
      "matrix": "first matrix",
      "matrix_path": "evals/model_matrix/first.json",
      "passed": true,
      "summary": {"tool_count": 1, "case_count": 1}
    }
  ]
}
""",
            encoding="utf-8",
        )
        try:
            suite_failures = _check_result_markdown(suite_path)
        finally:
            suite_path.unlink()
            suite_json_path.unlink()

        joined = "\n".join(failures + suite_failures)
        self.assertIn("missing Tool Coverage section", joined)
        self.assertIn("missing Check Families section", joined)
        self.assertIn("missing Matrix Summary section", joined)

    def test_coverage_suite_markdown_matrix_summary_must_match_sibling_json(self):
        path = ROOT / "evals" / "results" / "bad_coverage_suite_table_receipt.md"
        json_path = path.with_suffix(".json")
        path.write_text(
            "# Matrix Coverage Suite\n\n"
            "Passed: yes\n"
            "Matrices: 2\n"
            "Passed matrices: 2\n"
            "Failed matrices: 0\n"
            "Total tools: 3\n"
            "Total cases: 3\n\n"
            "## Matrix Summary\n\n"
            "| Matrix | Passed | Tools | Cases | Expected | Forbidden | Arg Cases | Check Families | Required Families | Variant Parity | Boundary Pairs |\n"
            "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|\n"
            "| first matrix | no | 99 | 1 | 0.000 | 1.000 | 0 | 1 | 1.000 | 0.500 | 9 |\n"
            "| stale matrix | yes | 1 | 1 | 1.000 | 1.000 | 1 | 1 | 1.000 | 1.000 | 1 |\n",
            encoding="utf-8",
        )
        json_path.write_text(
            """
{
  "passed": true,
  "summary": {
    "matrix_count": 2,
    "passed_matrices": 2,
    "failed_matrices": 0,
    "total_tools": 3,
    "total_cases": 3
  },
  "audits": [
    {
      "matrix": "first matrix",
      "matrix_path": "evals/model_matrix/first.json",
      "passed": true,
      "summary": {
        "tool_count": 2,
        "case_count": 1,
        "tool_expected_coverage": 1.0,
        "forbidden_tool_coverage": 1.0,
        "argument_case_count": 1,
        "case_count_with_check_family": 1,
        "required_check_family_coverage": 1.0,
        "variant_surface_parity": 1.0,
        "boundary_pair_count": 2
      }
    },
    {
      "matrix": "second matrix",
      "matrix_path": "evals/model_matrix/second.json",
      "passed": true,
      "summary": {
        "tool_count": 1,
        "case_count": 2,
        "tool_expected_coverage": 1.0,
        "forbidden_tool_coverage": 1.0,
        "argument_case_count": 2,
        "case_count_with_check_family": 2,
        "required_check_family_coverage": 1.0,
        "variant_surface_parity": 1.0,
        "boundary_pair_count": 3
      }
    }
  ]
}
""",
            encoding="utf-8",
        )
        try:
            failures = _check_result_markdown(path)
        finally:
            path.unlink()
            json_path.unlink()

        joined = "\n".join(failures)
        self.assertIn("Matrix Summary 'first matrix' Passed does not match sibling JSON receipt", joined)
        self.assertIn("Matrix Summary 'first matrix' Tools does not match sibling JSON receipt", joined)
        self.assertIn("Matrix Summary 'first matrix' Expected does not match sibling JSON receipt", joined)
        self.assertIn("Matrix Summary 'first matrix' Arg Cases does not match sibling JSON receipt", joined)
        self.assertIn("Matrix Summary 'first matrix' Variant Parity does not match sibling JSON receipt", joined)
        self.assertIn("Matrix Summary 'first matrix' Boundary Pairs does not match sibling JSON receipt", joined)
        self.assertIn("Matrix Summary table has stale matrix 'stale matrix'", joined)
        self.assertIn("Matrix Summary table missing current matrix 'second matrix'", joined)

    def test_coverage_markdown_tables_reject_duplicate_rows(self):
        path = ROOT / "evals" / "results" / "bad_coverage_duplicate_table_rows.md"
        json_path = path.with_suffix(".json")
        gap_lines = "\n".join(
            [
                "- Never expected: none",
                "- Never forbidden: none",
                "- Case expectation gaps: none",
                "- Expected without argument checks: none",
                "- Duplicate tool names: none",
                "- Identity gaps: none",
                "- Missing quality checks: none",
                "- Missing required check families: none",
                "- Variant surface mismatches: none",
                "- Source tool count mismatch: none",
                "- Cases without forbidden tools: none",
                "- Cases without check_family: none",
                "- Unknown expected tools: none",
                "- Unknown forbidden tools: none",
                "- Value-bar gaps: none",
            ]
        )
        path.write_text(
            "# Matrix Coverage\n\n"
            "Passed: yes\n"
            "Tools: 1\n"
            "Cases: 1\n\n"
            "## Gaps\n\n"
            f"{gap_lines}\n\n"
            "## Tool Coverage\n\n"
            "| Tool | Expected Cases | Forbidden Cases | Argument Cases | Quality Checks |\n"
            "|---|---:|---:|---:|---|\n"
            "| lookup | 1 | 0 | 0 | yes |\n"
            "| lookup | 1 | 0 | 0 | yes |\n\n"
            "## Check Families\n\n"
            "| Family | Cases |\n"
            "|---|---:|\n"
            "| lookup | 1 |\n"
            "| lookup | 1 |\n",
            encoding="utf-8",
        )
        json_path.write_text(
            """
{
  "passed": true,
  "summary": {"tool_count": 1, "case_count": 1},
  "tools": [
    {
      "name": "lookup",
      "expected_cases": ["first"],
      "forbidden_cases": [],
      "argument_cases": [],
      "has_quality_checks": true
    }
  ],
  "check_families": {"lookup": ["first"]},
  "uncovered": {}
}
""",
            encoding="utf-8",
        )
        try:
            failures = _check_result_markdown(path)
        finally:
            path.unlink()
            json_path.unlink()

        suite_path = ROOT / "evals" / "results" / "bad_coverage_duplicate_matrix_rows.md"
        suite_json_path = suite_path.with_suffix(".json")
        suite_path.write_text(
            "# Matrix Coverage Suite\n\n"
            "Passed: yes\n"
            "Matrices: 1\n\n"
            "## Matrix Summary\n\n"
            "| Matrix | Passed | Tools | Cases | Expected | Forbidden | Arg Cases | Check Families | Required Families | Variant Parity | Boundary Pairs |\n"
            "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|\n"
            "| first matrix | yes | 1 | 1 | 1.000 | 1.000 | 1 | 1 | 1.000 | 1.000 | 1 |\n"
            "| first matrix | yes | 1 | 1 | 1.000 | 1.000 | 1 | 1 | 1.000 | 1.000 | 1 |\n",
            encoding="utf-8",
        )
        suite_json_path.write_text(
            """
{
  "passed": true,
  "summary": {"matrix_count": 1},
  "audits": [
    {
      "matrix": "first matrix",
      "matrix_path": "evals/model_matrix/first.json",
      "passed": true,
      "summary": {
        "tool_count": 1,
        "case_count": 1,
        "tool_expected_coverage": 1.0,
        "forbidden_tool_coverage": 1.0,
        "argument_case_count": 1,
        "case_count_with_check_family": 1,
        "required_check_family_coverage": 1.0,
        "variant_surface_parity": 1.0,
        "boundary_pair_count": 1
      }
    }
  ]
}
""",
            encoding="utf-8",
        )
        try:
            suite_failures = _check_result_markdown(suite_path)
        finally:
            suite_path.unlink()
            suite_json_path.unlink()

        joined = "\n".join(failures + suite_failures)
        self.assertIn("Tool Coverage table has duplicate tool 'lookup'", joined)
        self.assertIn("Check Families table has duplicate family 'lookup'", joined)
        self.assertIn("Matrix Summary table has duplicate matrix 'first matrix'", joined)

    def test_coverage_markdown_tables_require_recognized_headers(self):
        path = ROOT / "evals" / "results" / "bad_coverage_table_headers.md"
        json_path = path.with_suffix(".json")
        gap_lines = "\n".join(
            [
                "- Never expected: none",
                "- Never forbidden: none",
                "- Case expectation gaps: none",
                "- Expected without argument checks: none",
                "- Duplicate tool names: none",
                "- Identity gaps: none",
                "- Missing quality checks: none",
                "- Missing required check families: none",
                "- Variant surface mismatches: none",
                "- Source tool count mismatch: none",
                "- Cases without forbidden tools: none",
                "- Cases without check_family: none",
                "- Unknown expected tools: none",
                "- Unknown forbidden tools: none",
                "- Value-bar gaps: none",
            ]
        )
        path.write_text(
            "# Matrix Coverage\n\n"
            "Passed: yes\n"
            "Tools: 1\n"
            "Cases: 1\n\n"
            "## Gaps\n\n"
            f"{gap_lines}\n\n"
            "## Tool Coverage\n\n"
            "| lookup | 1 | 0 | 0 | yes |\n"
            "|---|---:|---:|---:|---|\n"
            "| lookup | 1 | 0 | 0 | yes |\n\n"
            "## Check Families\n\n"
            "| lookup | 1 |\n"
            "|---|---:|\n"
            "| lookup | 1 |\n",
            encoding="utf-8",
        )
        json_path.write_text(
            """
{
  "passed": true,
  "summary": {"tool_count": 1, "case_count": 1},
  "tools": [
    {
      "name": "lookup",
      "expected_cases": ["first"],
      "forbidden_cases": [],
      "argument_cases": [],
      "has_quality_checks": true
    }
  ],
  "check_families": {"lookup": ["first"]},
  "uncovered": {}
}
""",
            encoding="utf-8",
        )
        try:
            failures = _check_result_markdown(path)
        finally:
            path.unlink()
            json_path.unlink()

        suite_path = ROOT / "evals" / "results" / "bad_coverage_matrix_header.md"
        suite_json_path = suite_path.with_suffix(".json")
        suite_path.write_text(
            "# Matrix Coverage Suite\n\n"
            "Passed: yes\n"
            "Matrices: 1\n\n"
            "## Matrix Summary\n\n"
            "| first matrix | yes | 1 | 1 | 1.000 | 1.000 | 1 | 1 | 1.000 | 1.000 | 1 |\n"
            "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|\n"
            "| first matrix | yes | 1 | 1 | 1.000 | 1.000 | 1 | 1 | 1.000 | 1.000 | 1 |\n",
            encoding="utf-8",
        )
        suite_json_path.write_text(
            """
{
  "passed": true,
  "summary": {"matrix_count": 1},
  "audits": [
    {
      "matrix": "first matrix",
      "matrix_path": "evals/model_matrix/first.json",
      "passed": true,
      "summary": {
        "tool_count": 1,
        "case_count": 1,
        "tool_expected_coverage": 1.0,
        "forbidden_tool_coverage": 1.0,
        "argument_case_count": 1,
        "case_count_with_check_family": 1,
        "required_check_family_coverage": 1.0,
        "variant_surface_parity": 1.0,
        "boundary_pair_count": 1
      }
    }
  ]
}
""",
            encoding="utf-8",
        )
        try:
            suite_failures = _check_result_markdown(suite_path)
        finally:
            suite_path.unlink()
            suite_json_path.unlink()

        joined = "\n".join(failures + suite_failures)
        self.assertIn("Tool Coverage table header is not recognized", joined)
        self.assertIn("Check Families table header is not recognized", joined)
        self.assertIn("Matrix Summary table header is not recognized", joined)

    def test_raw_matrix_markdown_counts_must_match_results_table(self):
        path = ROOT / "evals" / "results" / "bad_matrix_report.md"
        path.write_text(
            "# Matrix Report\n\n"
            "Passed: no\n\n"
            "## Raw Matrix\n\n"
            "Live: yes\n"
            "Passed: yes\n"
            "Planned: 99\n"
            "Passed cases: 0\n"
            "Failed cases: 0\n"
            "Errors: 0\n"
            "Skipped: 0\n"
            "Score: 1.000\n\n"
            "## Results\n\n"
            "| Provider | Model | Harness | Tool Variant | Instruction Variant | Case | Status | Chosen |\n"
            "|---|---|---|---|---|---|---|---|\n"
            "| anthropic | model | prompt_json | stock | rules | first | passed | tool |\n"
            "| anthropic | model | prompt_json | stock | rules | second | failed | tool |\n",
            encoding="utf-8",
        )
        try:
            failures = _check_result_markdown(path)
        finally:
            path.unlink()

        joined = "\n".join(failures)
        self.assertIn("Planned summary does not match Results table", joined)
        self.assertIn("Passed cases summary does not match Results table", joined)
        self.assertIn("Failed cases summary does not match Results table", joined)
        self.assertIn("raw matrix Passed summary does not match Results table", joined)
        self.assertIn("Score summary does not match Results table", joined)

    def test_model_matrix_markdown_result_rows_require_shape_status_and_identity(self):
        path = ROOT / "evals" / "results" / "bad_result_rows_report.md"
        path.write_text(
            "# Matrix Report\n\n"
            "Passed: no\n\n"
            "## Raw Matrix\n\n"
            "Live: yes\n"
            "Passed: no\n"
            "Planned: 4\n"
            "Passed cases: 2\n"
            "Failed cases: 0\n"
            "Errors: 0\n"
            "Skipped: 0\n"
            "Score: 1.000\n\n"
            "## Results\n\n"
            "| Provider | Model | Harness | Tool Variant | Instruction Variant | Case | Status | Chosen |\n"
            "|---|---|---|---|---|---|---|---|\n"
            "| anthropic | model | prompt_json | stock | rules | duplicate | passed | tool |\n"
            "| anthropic | model | prompt_json | stock | rules | duplicate | passed | tool |\n"
            "| anthropic | model | prompt_json | stock | rules | malformed | passed |\n"
            "| anthropic |  | prompt_json | stock | rules | bad status | weird | tool |\n",
            encoding="utf-8",
        )
        try:
            failures = _check_result_markdown(path)
        finally:
            path.unlink()

        joined = "\n".join(failures)
        self.assertIn("duplicate Results row 'anthropic'/'model'/'prompt_json'/'stock'/'rules'/'duplicate'", joined)
        self.assertIn("Results row 3 has too few columns", joined)
        self.assertIn("Results row 4 missing Model", joined)
        self.assertIn("Results row 4 unknown status 'weird'", joined)

    def test_model_matrix_markdown_cell_summary_must_match_results_table(self):
        path = ROOT / "evals" / "results" / "bad_cell_summary_report.md"
        path.write_text(
            "# Matrix Report\n\n"
            "Passed: no\n\n"
            "## Raw Matrix\n\n"
            "Live: yes\n"
            "Passed: no\n"
            "Planned: 3\n"
            "Passed cases: 1\n"
            "Failed cases: 1\n"
            "Errors: 0\n"
            "Skipped: 1\n"
            "Score: 0.500\n\n"
            "## Results\n\n"
            "| Provider | Model | Harness | Tool Variant | Instruction Variant | Case | Status | Chosen |\n"
            "|---|---|---|---|---|---|---|---|\n"
            "| anthropic | model | prompt_json | stock | rules | first | passed | tool |\n"
            "| anthropic | model | prompt_json | stock | rules | second | failed | tool |\n"
            "| anthropic | model | prompt_json | tuned | rules | third | skipped |  |\n\n"
            "## Cell Summary\n\n"
            "| Provider | Harness | Tool Variant | Instruction Variant | Passed | Failed | Errors | Skipped | Score |\n"
            "|---|---|---|---|---:|---:|---:|---:|---:|\n"
            "| anthropic | prompt_json | stock | rules | 2 | 0 | 0 | 1 | 1.000 |\n"
            "| anthropic | prompt_json | stale | rules | 0 | 0 | 0 | 0 | 0.000 |\n",
            encoding="utf-8",
        )
        try:
            failures = _check_result_markdown(path)
        finally:
            path.unlink()

        joined = "\n".join(failures)
        self.assertIn("Cell Summary 'anthropic'/'prompt_json'/'stock'/'rules' passed does not match Results table", joined)
        self.assertIn("Cell Summary 'anthropic'/'prompt_json'/'stock'/'rules' failed does not match Results table", joined)
        self.assertIn("Cell Summary 'anthropic'/'prompt_json'/'stock'/'rules' skipped does not match Results table", joined)
        self.assertIn("Cell Summary 'anthropic'/'prompt_json'/'stock'/'rules' score does not match Results table", joined)
        self.assertIn("Cell Summary table has stale cell 'anthropic'/'prompt_json'/'stale'/'rules'", joined)
        self.assertIn("Cell Summary table missing current cell 'anthropic'/'prompt_json'/'tuned'/'rules'", joined)

    def test_optimization_gate_markdown_counts_must_match_results_table(self):
        path = ROOT / "evals" / "results" / "bad_optimization_gate_report.md"
        path.write_text(
            "# Matrix Report\n\n"
            "## Optimization Gate\n\n"
            "Passed: yes\n"
            "Optimized variants: `tuned`, `missing_tuned`\n"
            "Baseline variant: `stock`\n"
            "Baseline score: 1.000\n"
            "Optimized score: 0.000\n"
            "Baseline failures: 0\n"
            "Optimized failures: 1\n\n"
            "## Raw Matrix\n\n"
            "Live: yes\n"
            "Passed: no\n"
            "Planned: 2\n"
            "Passed cases: 1\n"
            "Failed cases: 1\n"
            "Errors: 0\n"
            "Skipped: 0\n"
            "Score: 0.500\n\n"
            "## Results\n\n"
            "| Provider | Model | Harness | Tool Variant | Instruction Variant | Case | Status | Chosen |\n"
            "|---|---|---|---|---|---|---|---|\n"
            "| anthropic | model | prompt_json | stock | rules | first | failed | tool |\n"
            "| anthropic | model | prompt_json | tuned | rules | first | passed | tool |\n",
            encoding="utf-8",
        )
        try:
            failures = _check_result_markdown(path)
        finally:
            path.unlink()

        joined = "\n".join(failures)
        self.assertIn("Optimized variant 'missing_tuned' is not present in Results table", joined)
        self.assertIn("Baseline failures summary does not match Results table", joined)
        self.assertIn("Optimized failures summary does not match Results table", joined)
        self.assertIn("Baseline score summary does not match Results table", joined)
        self.assertIn("Optimized score summary does not match Results table", joined)

    def test_optimization_gate_markdown_passed_must_match_live_results(self):
        path = ROOT / "evals" / "results" / "bad_optimization_gate_pass_report.md"
        path.write_text(
            "# Matrix Report\n\n"
            "## Optimization Gate\n\n"
            "Passed: yes\n"
            "Optimized variants: `tuned`\n"
            "Baseline variant: `stock`\n"
            "Baseline score: 1.000\n"
            "Optimized score: 0.000\n"
            "Baseline failures: 0\n"
            "Baseline errors: 0\n"
            "Baseline skipped: 0\n"
            "Optimized failures: 0\n"
            "Optimized errors: 0\n"
            "Optimized skipped: 0\n\n"
            "optimized variants passed every selected cell\n\n"
            "## Raw Matrix\n\n"
            "Live: yes\n"
            "Passed: yes\n"
            "Planned: 2\n"
            "Passed cases: 1\n"
            "Failed cases: 0\n"
            "Errors: 0\n"
            "Skipped: 1\n"
            "Score: 1.000\n\n"
            "## Results\n\n"
            "| Provider | Model | Harness | Tool Variant | Instruction Variant | Case | Status | Chosen |\n"
            "|---|---|---|---|---|---|---|---|\n"
            "| anthropic | model | prompt_json | stock | rules | first | passed | tool |\n"
            "| anthropic | model | prompt_json | tuned | rules | first | skipped |  |\n",
            encoding="utf-8",
        )
        try:
            failures = _check_result_markdown(path)
        finally:
            path.unlink()

        joined = "\n".join(failures)
        self.assertIn("Optimization Gate Passed summary does not match Results table", joined)
        self.assertIn("Optimized skipped summary does not match Results table", joined)

    def test_optimization_gate_markdown_allows_dry_planned_results(self):
        path = ROOT / "evals" / "results" / "dry_optimization_gate_report.md"
        path.write_text(
            "# Matrix Report\n\n"
            "## Optimization Gate\n\n"
            "Passed: yes\n"
            "Optimized variants: `tuned`\n"
            "Baseline variant: `stock`\n"
            "Baseline score: 0.000\n"
            "Optimized score: 0.000\n"
            "Baseline failures: 0\n"
            "Optimized failures: 0\n\n"
            "optimized variants passed every selected cell\n\n"
            "## Raw Matrix\n\n"
            "Live: no\n"
            "Passed: yes\n"
            "Planned: 2\n"
            "Passed cases: 0\n"
            "Failed cases: 0\n"
            "Errors: 0\n"
            "Skipped: 0\n"
            "Score: 1.000\n\n"
            "## Results\n\n"
            "| Provider | Model | Harness | Tool Variant | Instruction Variant | Case | Status | Chosen |\n"
            "|---|---|---|---|---|---|---|---|\n"
            "| anthropic | model | prompt_json | stock | rules | first | planned |  |\n"
            "| anthropic | model | prompt_json | tuned | rules | first | planned |  |\n",
            encoding="utf-8",
        )
        try:
            failures = _check_result_markdown(path)
        finally:
            path.unlink()

        self.assertEqual([], failures)

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
