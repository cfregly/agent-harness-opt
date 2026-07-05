from pathlib import Path
import tempfile
import unittest

import claude_agent_harness_opt.model_matrix as model_matrix_module
from claude_agent_harness_opt.model_matrix import (
    MatrixFilters,
    ModelMatrixError,
    _cell_summary,
    _first_openai_response_function_call,
    _openai_response_reasoning_summary,
    _openai_response_text,
    _parse_choice_json,
    _tools_for_case,
    evaluate_model_choice,
    load_env_file,
    run_model_matrix,
    validate_matrix,
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

    def test_validate_matrix_rejects_non_list_required_fields(self):
        with self.assertRaisesRegex(ModelMatrixError, "matrix.cases must be a list"):
            validate_matrix(
                {
                    "cases": "not-a-list",
                    "profiles": [{"provider": "trace_fixture"}],
                    "tool_variants": [{"name": "tools", "tools": []}],
                }
            )

    def test_validate_matrix_rejects_non_object_list_items(self):
        with self.assertRaisesRegex(ModelMatrixError, r"matrix\.profiles\[0\] must be an object"):
            validate_matrix(
                {
                    "cases": [{"name": "case"}],
                    "profiles": ["trace_fixture"],
                    "tool_variants": [{"name": "tools", "tools": []}],
                }
            )

    def test_validate_matrix_rejects_malformed_nested_surfaces(self):
        with self.assertRaisesRegex(
            ModelMatrixError,
            r"matrix\.profiles\[0\]\.harnesses must be a list",
        ):
            validate_matrix(
                {
                    "cases": [{"name": "case"}],
                    "profiles": [{"harnesses": "prompt_json", "provider": "trace_fixture"}],
                    "tool_variants": [{"name": "tools", "tools": []}],
                }
            )
        with self.assertRaisesRegex(
            ModelMatrixError,
            r"matrix\.tool_variants\[0\]\.tools must be a list",
        ):
            validate_matrix(
                {
                    "cases": [{"name": "case"}],
                    "profiles": [{"harnesses": ["prompt_json"], "provider": "trace_fixture"}],
                    "tool_variants": [{"name": "tools", "tools": "not-a-list"}],
                }
            )

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

    def test_openai_responses_helpers_parse_tool_and_text_outputs(self):
        response = {
            "output": [
                {"type": "reasoning", "summary": [{"text": "Checked the boundary."}]},
                {"type": "function_call", "name": "gstack_browse", "arguments": '{"request": "test"}'},
                {
                    "type": "message",
                    "content": [{"type": "output_text", "text": '{"tool_name": "gstack_browse"}'}],
                },
            ]
        }

        function_call = _first_openai_response_function_call(response)
        self.assertIsNotNone(function_call)
        self.assertEqual("gstack_browse", function_call["name"])
        self.assertEqual('{"tool_name": "gstack_browse"}', _openai_response_text(response))
        self.assertEqual("Checked the boundary.", _openai_response_reasoning_summary(response))

    def test_parse_choice_json_accepts_frontier_output_wrappers(self):
        self.assertEqual(
            "topfunctions",
            _parse_choice_json(
                '```json\n{"tool_name": "topfunctions", "arguments": {}}\n```\nDone.'
            )["tool_name"],
        )
        self.assertEqual(
            "hot_traces",
            _parse_choice_json(
                '[{"tool_name": "hot_traces", "arguments": {"meta_only": true}}]'
            )["tool_name"],
        )
        self.assertEqual(
            "flamegraph",
            _parse_choice_json(
                'Choice:\n{"name": "flamegraph", "arguments": {"profile_type": "CPU"}}\nReason: explicit request.'
            )["tool_name"],
        )

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
        self.assertEqual("coding file-tool selection matrix", result["matrix"])
        self.assertTrue(result["matrix_path"].endswith("coding_tool_selection.json"))
        self.assertEqual(2, len(result["case_definitions"]))

    def test_cell_summary_preserves_skipped_counts(self):
        cells = _cell_summary(
            [
                {
                    "provider": "anthropic",
                    "harness": "prompt_json",
                    "tool_variant": "candidate",
                    "instruction_variant": "rules",
                    "status": "passed",
                },
                {
                    "provider": "anthropic",
                    "harness": "prompt_json",
                    "tool_variant": "candidate",
                    "instruction_variant": "rules",
                    "status": "skipped",
                },
                {
                    "provider": "anthropic",
                    "harness": "prompt_json",
                    "tool_variant": "candidate",
                    "instruction_variant": "rules",
                    "status": "provider_blocked",
                },
            ]
        )

        self.assertEqual(1, len(cells))
        self.assertEqual(1, cells[0]["passed"])
        self.assertEqual(1, cells[0]["provider_blocked"])
        self.assertEqual(1, cells[0]["skipped"])
        self.assertEqual(1.0, cells[0]["score"])

    def test_anthropic_credit_preflight_fails_closed_before_live_fanout(self):
        calls = []

        def fake_post_json(url, payload, headers, timeout):
            calls.append((url, payload, headers, timeout))
            raise ModelMatrixError(
                "HTTP 400: Your access to the Claude API has been disabled because "
                "your organization is out of usage credits."
            )

        original = model_matrix_module._post_json
        model_matrix_module._post_json = fake_post_json
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                env_path = Path(tmpdir) / ".env"
                env_path.write_text("ANTHROPIC_API_KEY=test-key\n", encoding="utf-8")
                result = run_model_matrix(
                    ROOT / "evals" / "model_matrix" / "coding_tool_selection.json",
                    live=True,
                    require_live=True,
                    env_file=env_path,
                    filters=MatrixFilters(
                        providers={"anthropic"},
                        harnesses={"prompt_json"},
                        variants={"tuned_boundaries"},
                        instruction_variants={"boundary_rules"},
                    ),
                    max_cases=2,
                )
        finally:
            model_matrix_module._post_json = original

        self.assertEqual(1, len(calls))
        self.assertFalse(result["passed"])
        self.assertEqual(2, result["summary"]["provider_blocked"])
        self.assertEqual(0, result["summary"]["errors"])
        self.assertEqual({"provider_blocked"}, {item["status"] for item in result["results"]})
        self.assertEqual("provider_blocked", result["provider_status"][0]["status"])

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

    def test_model_matrix_rejects_filters_that_select_zero_cells(self):
        with self.assertRaisesRegex(
            ModelMatrixError,
            "model matrix selected zero cells",
        ) as context:
            run_model_matrix(
                ROOT / "evals" / "model_matrix" / "coding_tool_selection.json",
                filters=MatrixFilters(
                    providers={"anthropic"},
                    harnesses={"native_tools"},
                    variants={"typo_variant"},
                    instruction_variants={"boundary_rules"},
                ),
            )

        message = str(context.exception)
        self.assertIn("variants requested [typo_variant]", message)
        self.assertIn("baseline_short", message)
        self.assertIn("tuned_boundaries", message)

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

    def test_codex_trace_fixture_matrix_evaluates_jsonl_exports(self):
        result = run_model_matrix(
            ROOT / "evals" / "model_matrix" / "codex_harness_trace_adapter.json",
            live=True,
            require_live=True,
            filters=MatrixFilters(
                providers={"trace_fixture"},
                harnesses={"codex_exec_jsonl"},
                variants={"codex_exported_trace_tools"},
                instruction_variants={"codex_exported_trace"},
            ),
        )

        self.assertTrue(result["passed"])
        self.assertEqual(2, result["summary"]["total"])
        self.assertEqual(2, result["summary"]["passed_cases"])
        self.assertEqual({"Bash", "mcp__context7__get-library-docs"}, {item["chosen_tools"][0] for item in result["results"]})

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
        self.assertEqual(2, len(result["case_definitions"]))

    def test_github_mcp_matrix_plans_selected_cells(self):
        result = run_model_matrix(
            ROOT / "evals" / "model_matrix" / "github_mcp_tool_selection.json",
            filters=MatrixFilters(
                providers={"anthropic-sonnet"},
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
        self.assertEqual("https://github.com/github/github-mcp-server", result["source"]["repo"])
        self.assertEqual(2, len(result["case_definitions"]))

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
            (
                "context7_mcp_tool_selection.json",
                "readme_context7_mcp",
                "context7_host_rules",
            ),
            (
                "supabase_mcp_database_tool_selection.json",
                "tuned_supabase_database_boundaries",
                "supabase_database_host_rules",
            ),
            (
                "clickhouse_mcp_tool_selection.json",
                "tuned_clickhouse_readonly_boundaries",
                "clickhouse_host_rules",
            ),
            (
                "zymtrace_mcp_tool_selection.json",
                "tuned_zymtrace_mcp_boundaries",
                "zymtrace_host_rules",
            ),
            (
                "zymtrace_mcp_tool_selection.json",
                "tuned_zymtrace_mcp_boundaries",
                "zymtrace_host_and_skill_rules",
            ),
            (
                "screenpipe_mcp_tool_selection.json",
                "source_tuned_screenpipe_mcp",
                "screenpipe_host_rules",
            ),
            (
                "humwork_mcp_tool_selection.json",
                "skill_tuned_humwork_mcp",
                "humwork_host_rules",
            ),
            (
                "openwork_ui_mcp_tool_selection.json",
                "source_tuned_openwork_ui_mcp",
                "openwork_ui_host_rules",
            ),
            (
                "insforge_mcp_tool_selection.json",
                "source_tuned_insforge_mcp",
                "insforge_host_rules",
            ),
        ]

        for filename, variant, instruction_variant in cases:
            with self.subTest(filename=filename):
                provider_filter = {"anthropic-sonnet"}
                result = run_model_matrix(
                    ROOT / "evals" / "model_matrix" / filename,
                    filters=MatrixFilters(
                        providers=provider_filter,
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

    def test_zymtrace_skill_rules_plan_heldout_cases(self):
        result = run_model_matrix(
            ROOT / "evals" / "model_matrix" / "zymtrace_mcp_tool_selection.json",
            filters=MatrixFilters(
                providers={"anthropic-sonnet"},
                harnesses={"prompt_json"},
                variants={"tuned_zymtrace_mcp_boundaries"},
                instruction_variants={"zymtrace_host_and_skill_rules"},
                cases={
                    "default project metrics discovery skips search",
                    "gpu inference workflow starts with metrics",
                },
            ),
        )

        self.assertTrue(result["passed"])
        self.assertFalse(result["live"])
        self.assertEqual(2, result["summary"]["total"])
        self.assertEqual(
            {
                "default project metrics discovery skips search",
                "gpu inference workflow starts with metrics",
            },
            {item["case"] for item in result["results"]},
        )

    def test_prompt_json_matrix_can_evaluate_no_tool_safety_case(self):
        result = evaluate_model_choice(
            {"arguments": {}, "tool_name": "NO_TOOL"},
            {
                "allow_no_tool": True,
                "expected_tools": [],
                "forbidden_tools": ["run_select_query"],
            },
        )

        self.assertTrue(result["passed"])

    def test_native_no_tool_case_gets_synthetic_tool(self):
        tools = [{"input_schema": {"properties": {}, "type": "object"}, "name": "real_tool"}]
        names = [tool["name"] for tool in _tools_for_case(tools, {"allow_no_tool": True})]
        self.assertEqual(["real_tool", "NO_TOOL"], names)

    def test_new_guardrail_cases_embed_check_family(self):
        result = run_model_matrix(
            ROOT / "evals" / "model_matrix" / "github_mcp_tool_selection.json",
            filters=MatrixFilters(
                providers={"anthropic"},
                harnesses={"prompt_json"},
                variants={"tuned_github_mcp_boundaries"},
                instruction_variants={"github_mcp_host_rules"},
                cases={
                    "file not found recovers with code search",
                    "list pull requests with small page",
                    "workflow metadata avoids log download",
                    "delete repository has no safe tool",
                },
            ),
        )

        families = {
            case["name"]: case["check_family"]
            for case in result["case_definitions"]
        }
        self.assertEqual("error_recovery", families["file not found recovers with code search"])
        self.assertEqual("output_budget", families["list pull requests with small page"])
        self.assertEqual("resource_vs_tool", families["workflow metadata avoids log download"])
        self.assertEqual("no_tool_safety", families["delete repository has no safe tool"])


if __name__ == "__main__":
    unittest.main()
