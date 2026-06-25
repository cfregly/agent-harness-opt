from pathlib import Path
import tempfile
import unittest

from claude_agent_harness_optimization.model_matrix import (
    MatrixFilters,
    evaluate_model_choice,
    load_env_file,
    run_model_matrix,
)


ROOT = Path(__file__).resolve().parents[1]


class ModelMatrixTests(unittest.TestCase):
    def test_load_env_file_reads_keys_without_shelling_out(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            env_path = Path(tmpdir) / ".env"
            env_path.write_text(
                "export ANTHROPIC_API_KEY='test-anthropic'\nOPENAI_API_KEY=\"test-openai\"\n",
                encoding="utf-8",
            )
            values = load_env_file(env_path)
        self.assertEqual("test-anthropic", values["ANTHROPIC_API_KEY"])
        self.assertEqual("test-openai", values["OPENAI_API_KEY"])

    def test_evaluate_model_choice_checks_expected_forbidden_and_args(self):
        result = evaluate_model_choice(
            {"arguments": {"pattern": "**/*.py"}, "tool_name": "Glob"},
            {
                "expected_args_contains": {"pattern": "*.py"},
                "expected_tools": ["Glob"],
                "forbidden_tools": ["Grep", "Read"],
            },
        )
        self.assertTrue(result["passed"])

    def test_evaluate_model_choice_fails_wrong_tool(self):
        result = evaluate_model_choice(
            {"arguments": {"path": "README.md"}, "tool_name": "Read"},
            {
                "expected_tools": ["Grep"],
                "forbidden_tools": ["Read"],
            },
        )
        self.assertFalse(result["passed"])
        self.assertEqual(["Grep"], result["missing_expected"])
        self.assertEqual(["Read"], result["forbidden_used"])

    def test_dry_run_model_matrix_plans_selected_cells(self):
        result = run_model_matrix(
            ROOT / "evals" / "model_matrix" / "coding_tool_selection.json",
            filters=MatrixFilters(
                providers={"anthropic"},
                harnesses={"prompt_json"},
                variants={"tuned_boundaries"},
                instruction_variants={"boundary_rules"},
            ),
            max_cases=2,
        )
        self.assertTrue(result["passed"])
        self.assertFalse(result["live"])
        self.assertEqual(2, result["summary"]["total"])
        self.assertEqual("planned", result["results"][0]["status"])

    def test_dry_run_model_matrix_filters_cases(self):
        result = run_model_matrix(
            ROOT / "evals" / "model_matrix" / "coding_tool_selection.json",
            filters=MatrixFilters(
                providers={"anthropic"},
                harnesses={"prompt_json"},
                variants={"tuned_boundaries"},
                instruction_variants={"boundary_rules"},
                cases={"read known file"},
            ),
        )

        self.assertEqual(1, result["summary"]["total"])
        self.assertEqual("read known file", result["results"][0]["case"])

    def test_trace_fixture_matrix_evaluates_named_harnesses(self):
        result = run_model_matrix(
            ROOT / "evals" / "model_matrix" / "harness_trace_adapters.json",
            live=True,
            require_live=True,
            filters=MatrixFilters(
                providers={"trace_fixture"},
                harnesses={"agent_sdk_trace", "cursor_trace"},
                variants={"exported_trace_tools"},
                instruction_variants={"exported_trace"},
            ),
        )

        self.assertTrue(result["passed"])
        self.assertEqual(4, result["summary"]["total"])
        self.assertEqual(4, result["summary"]["passed_cases"])
        self.assertEqual({"Task"}, {item["chosen_tools"][0] for item in result["results"]})

    def test_agent_audit_skill_matrix_plans_selected_cells(self):
        result = run_model_matrix(
            ROOT / "evals" / "model_matrix" / "agent_audit_skill_selection.json",
            filters=MatrixFilters(
                providers={"anthropic"},
                harnesses={"prompt_json"},
                variants={"thin_workflow_tools"},
                instruction_variants={"agent_audit_skill"},
            ),
            max_cases=2,
        )

        self.assertTrue(result["passed"])
        self.assertFalse(result["live"])
        self.assertEqual(2, result["summary"]["total"])
        self.assertEqual("planned", result["results"][0]["status"])

    def test_github_mcp_matrix_plans_selected_cells(self):
        result = run_model_matrix(
            ROOT / "evals" / "model_matrix" / "github_mcp_tool_selection.json",
            filters=MatrixFilters(
                providers={"anthropic"},
                harnesses={"prompt_json"},
                variants={"stock_github_mcp"},
                instruction_variants={"github_mcp_host_rules"},
            ),
            max_cases=2,
        )

        self.assertTrue(result["passed"])
        self.assertFalse(result["live"])
        self.assertEqual(2, result["summary"]["total"])
        self.assertEqual("planned", result["results"][0]["status"])

    def test_public_mcp_sweep_matrices_plan_selected_cells(self):
        cases = [
            (
                "playwright_mcp_tool_selection.json",
                "stock_playwright_mcp",
                "playwright_host_rules",
            ),
            (
                "slack_mcp_tool_selection.json",
                "stock_slack_mcp",
                "slack_host_rules",
            ),
            (
                "filesystem_mcp_tool_selection.json",
                "stock_filesystem_mcp",
                "filesystem_host_rules",
            ),
            (
                "postgres_mcp_pro_tool_selection.json",
                "stock_postgres_mcp_pro",
                "postgres_host_rules",
            ),
            (
                "firecrawl_mcp_tool_selection.json",
                "tuned_firecrawl_mcp_boundaries",
                "firecrawl_host_rules",
            ),
        ]

        for filename, variant, instruction_variant in cases:
            with self.subTest(filename=filename):
                result = run_model_matrix(
                    ROOT / "evals" / "model_matrix" / filename,
                    filters=MatrixFilters(
                        providers={"anthropic"},
                        harnesses={"prompt_json"},
                        variants={variant},
                        instruction_variants={instruction_variant},
                    ),
                    max_cases=2,
                )

                self.assertTrue(result["passed"])
                self.assertFalse(result["live"])
                self.assertEqual(2, result["summary"]["total"])
                self.assertEqual("planned", result["results"][0]["status"])


if __name__ == "__main__":
    unittest.main()
