import unittest

from claude_agent_harness_opt.matrix_coverage import (
    audit_matrix_coverage_suite,
    audit_matrix_coverage_data,
    render_matrix_coverage_suite_markdown,
    render_matrix_coverage_markdown,
)


class MatrixCoverageTests(unittest.TestCase):
    def test_audit_reports_missing_positive_negative_and_argument_coverage(self):
        audit = audit_matrix_coverage_data(
            {
                "cases": [
                    {
                        "check_family": "boundary",
                        "expected_args_contains": {"path": ".json"},
                        "expected_tools": ["read_file"],
                        "forbidden_tools": ["search_files"],
                        "name": "read known file",
                        "task": "Read package.json.",
                    },
                    {
                        "expected_tools": ["search_files"],
                        "forbidden_tools": [],
                        "name": "search broad tree",
                        "task": "Find config files.",
                    },
                ],
                "profiles": [{"harnesses": ["prompt_json"], "provider": "trace_fixture"}],
                "tool_variants": [
                    {
                        "name": "test_tools",
                        "tools": [
                            {
                                "name": "read_file",
                                "purpose": "Read one file.",
                                "quality_checks": ["Require a path."],
                            },
                            {
                                "input_schema": {
                                    "properties": {"pattern": "Search pattern"},
                                    "required": ["pattern"],
                                    "type": "object",
                                },
                                "name": "search_files",
                                "purpose": "Search files.",
                            },
                            {"name": "write_file", "purpose": "Write files."},
                        ],
                    }
                ],
            }
        )

        self.assertFalse(audit["passed"])
        self.assertEqual(["write_file"], audit["uncovered"]["never_expected"])
        self.assertEqual(
            ["read_file", "write_file"],
            audit["uncovered"]["never_forbidden"],
        )
        self.assertEqual(
            ["search_files"],
            audit["uncovered"]["expected_without_argument_check"],
        )
        self.assertEqual(
            ["search_files", "write_file"],
            audit["uncovered"]["missing_quality_checks"],
        )
        self.assertEqual(["search broad tree"], audit["uncovered"]["cases_without_check_family"])
        self.assertEqual(["search broad tree"], audit["uncovered"]["cases_without_forbidden"])

    def test_render_matrix_coverage_markdown_includes_summary_and_table(self):
        audit = audit_matrix_coverage_data(
            {
                "cases": [
                    {
                        "check_family": "boundary",
                        "expected_tools": ["lookup"],
                        "forbidden_tools": ["NO_TOOL"],
                        "name": "lookup case",
                        "task": "Lookup a value.",
                    }
                ],
                "name": "sample matrix",
                "profiles": [{"harnesses": ["prompt_json"], "provider": "trace_fixture"}],
                "tool_variants": [
                    {
                        "name": "sample",
                        "tools": [
                            {
                                "name": "lookup",
                                "purpose": "Lookup values.",
                                "quality_checks": ["Use exact ids."],
                            }
                        ],
                    }
                ],
            }
        )

        output = render_matrix_coverage_markdown(audit)

        self.assertIn("# Matrix Coverage: sample matrix", output)
        self.assertIn("Expected tool coverage: 1.000", output)
        self.assertIn("| lookup | 1 | 0 | 0 | yes |", output)

    def test_audit_reports_missing_required_check_family(self):
        audit = audit_matrix_coverage_data(
            {
                "cases": [
                    {
                        "check_family": "lookup",
                        "expected_tools": ["lookup"],
                        "forbidden_tools": ["fallback"],
                        "name": "lookup case",
                        "task": "Lookup a value.",
                    },
                    {
                        "check_family": "fallback",
                        "expected_tools": ["fallback"],
                        "forbidden_tools": ["lookup"],
                        "name": "fallback case",
                        "task": "Fallback.",
                    },
                ],
                "coverage": {"required_check_families": ["lookup", "fallback", "no_tool_safety"]},
                "name": "required family matrix",
                "profiles": [{"harnesses": ["prompt_json"], "provider": "trace_fixture"}],
                "tool_variants": [
                    {
                        "name": "sample",
                        "tools": [
                            {
                                "name": "lookup",
                                "purpose": "Lookup values.",
                                "quality_checks": ["Use exact ids."],
                            },
                            {
                                "name": "fallback",
                                "purpose": "Fallback safely.",
                                "quality_checks": ["Use only for fallback."],
                            },
                        ],
                    }
                ],
            }
        )

        self.assertFalse(audit["passed"])
        self.assertEqual(["no_tool_safety"], audit["uncovered"]["missing_required_check_families"])
        self.assertEqual(0.667, audit["summary"]["required_check_family_coverage"])

    def test_audit_reports_variant_surface_and_source_count_drift(self):
        audit = audit_matrix_coverage_data(
            {
                "cases": [
                    {
                        "check_family": "lookup",
                        "expected_tools": ["lookup"],
                        "forbidden_tools": ["fallback"],
                        "name": "lookup case",
                        "task": "Lookup a value.",
                    },
                    {
                        "check_family": "fallback",
                        "expected_tools": ["fallback"],
                        "forbidden_tools": ["lookup"],
                        "name": "fallback case",
                        "task": "Fallback.",
                    },
                ],
                "coverage": {"required_check_families": ["lookup", "fallback"]},
                "name": "variant drift matrix",
                "profiles": [{"harnesses": ["prompt_json"], "provider": "trace_fixture"}],
                "source": {"tool_count": 4},
                "tool_variants": [
                    {
                        "name": "baseline",
                        "tools": [
                            {"name": "lookup", "purpose": "Lookup.", "quality_checks": ["Check ids."]},
                            {"name": "fallback", "purpose": "Fallback.", "quality_checks": ["Check fallback."]},
                            {"name": "fallback", "purpose": "Fallback duplicate.", "quality_checks": ["Check fallback."]},
                        ],
                    },
                    {
                        "name": "candidate",
                        "tools": [
                            {"name": "lookup", "purpose": "Lookup.", "quality_checks": ["Check ids."]},
                            {"name": "extra", "purpose": "Extra.", "quality_checks": ["Check extra."]},
                        ],
                    },
                ],
            }
        )

        self.assertFalse(audit["passed"])
        self.assertEqual(
            [{"duplicate_tools": ["fallback"], "variant": "baseline"}],
            audit["uncovered"]["duplicate_tool_names"],
        )
        self.assertEqual(
            [{"extra_tools": ["extra"], "missing_tools": ["fallback"], "variant": "candidate"}],
            audit["uncovered"]["variant_surface_mismatches"],
        )
        self.assertEqual([{"actual": 3, "expected": 4}], audit["uncovered"]["source_tool_count_mismatch"])
        self.assertEqual(0.5, audit["summary"]["variant_surface_parity"])

    def test_audit_allows_intentional_variant_surface_delta(self):
        audit = audit_matrix_coverage_data(
            {
                "cases": [
                    {
                        "check_family": "lookup",
                        "expected_tools": ["lookup"],
                        "forbidden_tools": ["extra"],
                        "name": "lookup case",
                        "task": "Lookup a value.",
                    },
                    {
                        "check_family": "extra",
                        "expected_tools": ["extra"],
                        "forbidden_tools": ["lookup"],
                        "name": "extra case",
                        "task": "Use the extra tool.",
                    },
                ],
                "coverage": {
                    "allow_variant_tool_delta": True,
                    "required_check_families": ["lookup", "extra"],
                },
                "name": "intentional delta matrix",
                "profiles": [{"harnesses": ["prompt_json"], "provider": "trace_fixture"}],
                "tool_variants": [
                    {
                        "name": "baseline",
                        "tools": [
                            {"name": "lookup", "purpose": "Lookup.", "quality_checks": ["Check ids."]},
                        ],
                    },
                    {
                        "name": "candidate",
                        "tools": [
                            {"name": "extra", "purpose": "Extra.", "quality_checks": ["Check extra."]},
                        ],
                    },
                ],
            }
        )

        self.assertTrue(audit["passed"])
        self.assertEqual([], audit["uncovered"]["variant_surface_mismatches"])
        self.assertEqual(1.0, audit["summary"]["variant_surface_parity"])

    def test_audit_reports_malformed_source_tool_count_without_crashing(self):
        audit = audit_matrix_coverage_data(
            {
                "cases": [
                    {
                        "check_family": "lookup",
                        "expected_tools": ["lookup"],
                        "forbidden_tools": ["NO_TOOL"],
                        "name": "lookup case",
                        "task": "Lookup a value.",
                    },
                ],
                "name": "malformed source count matrix",
                "profiles": [{"harnesses": ["prompt_json"], "provider": "trace_fixture"}],
                "source": {"tool_count": "many"},
                "tool_variants": [
                    {
                        "name": "sample",
                        "tools": [
                            {"name": "lookup", "purpose": "Lookup.", "quality_checks": ["Check ids."]},
                        ],
                    }
                ],
            }
        )

        self.assertFalse(audit["passed"])
        self.assertEqual(
            [{"actual": 1, "expected": "many"}],
            audit["uncovered"]["source_tool_count_mismatch"],
        )

    def test_audit_fails_unknown_expected_and_forbidden_tools(self):
        audit = audit_matrix_coverage_data(
            {
                "cases": [
                    {
                        "check_family": "lookup",
                        "expected_tools": ["lookup", "missing_tool"],
                        "forbidden_tools": ["fallback", "typo_forbidden"],
                        "name": "lookup case",
                        "task": "Lookup a value.",
                    },
                    {
                        "check_family": "fallback",
                        "expected_tools": ["fallback"],
                        "forbidden_tools": ["lookup"],
                        "name": "fallback case",
                        "task": "Fallback.",
                    },
                ],
                "coverage": {"required_check_families": ["lookup", "fallback"]},
                "name": "unknown tool matrix",
                "profiles": [{"harnesses": ["prompt_json"], "provider": "trace_fixture"}],
                "tool_variants": [
                    {
                        "name": "sample",
                        "tools": [
                            {"name": "lookup", "purpose": "Lookup.", "quality_checks": ["Check ids."]},
                            {"name": "fallback", "purpose": "Fallback.", "quality_checks": ["Check fallback."]},
                        ],
                    }
                ],
            }
        )

        self.assertFalse(audit["passed"])
        self.assertIn(
            "some expected tool names are not in the matrix catalog",
            audit["warnings"],
        )
        self.assertIn(
            "some forbidden tool names are not in the matrix catalog or external allow-list",
            audit["warnings"],
        )
        self.assertEqual(["missing_tool"], audit["uncovered"]["unknown_expected_tools"])
        self.assertEqual(["typo_forbidden"], audit["uncovered"]["unknown_forbidden_tools"])

    def test_audit_reports_matrix_identity_gaps(self):
        audit = audit_matrix_coverage_data(
            {
                "cases": [
                    {
                        "check_family": "lookup",
                        "expected_tools": "lookup",
                        "forbidden_tools": ["fallback"],
                        "name": "duplicate case",
                        "task": "Lookup a value.",
                    },
                    {
                        "allow_no_tool": True,
                        "check_family": "no_tool",
                        "expected_tools": [],
                        "forbidden_tools": [],
                        "name": "duplicate case",
                        "task": "",
                    },
                ],
                "coverage": {"allow_variant_tool_delta": True},
                "instruction_variants": [
                    {"name": "", "instructions": ""},
                    {"name": "rules", "instructions": "Use rules."},
                    {"name": "rules", "instructions": "Duplicate rules."},
                ],
                "name": "identity gap matrix",
                "profiles": [
                    {"harnesses": ["prompt_json", "prompt_json"], "provider": "trace_fixture"},
                    {"harnesses": [], "provider": ""},
                ],
                "tool_variants": [
                    {
                        "name": "sample",
                        "tools": [
                            {"name": "lookup", "purpose": "Lookup.", "quality_checks": ["Check ids."]},
                        ],
                    },
                    {
                        "name": "sample",
                        "tools": [
                            {"name": "fallback", "purpose": "Fallback.", "quality_checks": ["Check fallback."]},
                        ],
                    },
                ],
            }
        )

        self.assertFalse(audit["passed"])
        self.assertIn("some matrix identities or case definitions are ambiguous", audit["warnings"])
        fields = {gap["field"] for gap in audit["uncovered"]["identity_gaps"]}
        self.assertIn("cases.name", fields)
        self.assertIn("cases.task", fields)
        self.assertIn("cases.expected_tools", fields)
        self.assertIn("tool_variants.name", fields)
        self.assertIn("instruction_variants.name", fields)
        self.assertIn("profiles.provider", fields)
        self.assertIn("profiles.harnesses", fields)
        self.assertGreater(audit["summary"]["identity_gap_count"], 0)

    def test_audit_reports_case_expectation_contradictions(self):
        audit = audit_matrix_coverage_data(
            {
                "cases": [
                    {
                        "allow_no_tool": True,
                        "check_family": "no_tool",
                        "expected_args_contains": {"id": "123"},
                        "expected_tools": ["lookup"],
                        "forbidden_tools": ["lookup", "lookup"],
                        "name": "contradictory case",
                        "task": "Do not call a tool, but also lookup id 123.",
                    },
                    {
                        "check_family": "schema",
                        "expected_args_contains": {"missing_arg": "x"},
                        "expected_tools": ["lookup"],
                        "forbidden_tools": ["fallback"],
                        "name": "schema mismatch case",
                        "task": "Lookup a value with the wrong argument.",
                    },
                ],
                "coverage": {"required_check_families": ["no_tool", "schema"]},
                "name": "case expectation gap matrix",
                "profiles": [{"harnesses": ["prompt_json"], "provider": "trace_fixture"}],
                "tool_variants": [
                    {
                        "name": "sample",
                        "tools": [
                            {
                                "input_schema": {
                                    "properties": {"id": "Lookup id"},
                                    "required": ["id"],
                                    "type": "object",
                                },
                                "name": "lookup",
                                "purpose": "Lookup.",
                                "quality_checks": ["Check ids."],
                            },
                            {
                                "name": "fallback",
                                "purpose": "Fallback.",
                                "quality_checks": ["Check fallback."],
                            },
                        ],
                    }
                ],
            }
        )

        self.assertFalse(audit["passed"])
        self.assertIn("some case expectations are contradictory or impossible", audit["warnings"])
        problems = {gap["problem"] for gap in audit["uncovered"]["case_expectation_gaps"]}
        self.assertIn("duplicate", problems)
        self.assertIn("overlap", problems)
        self.assertIn("expected_tools_present", problems)
        self.assertIn("no_tool_case_has_argument_checks", problems)
        self.assertIn("argument_not_in_expected_tool_schema", problems)
        self.assertGreater(audit["summary"]["case_expectation_gap_count"], 0)

    def test_suite_audit_summarizes_multiple_matrices(self):
        suite = audit_matrix_coverage_suite(
            [
                "evals/model_matrix/zymtrace_mcp_tool_selection.json",
                "evals/model_matrix/clickhouse_mcp_tool_selection.json",
            ]
        )

        self.assertEqual(2, suite["summary"]["matrix_count"])
        self.assertEqual(2, suite["summary"]["passed_matrices"])
        self.assertEqual(0, suite["summary"]["failed_matrices"])
        self.assertTrue(suite["passed"])

    def test_render_suite_markdown_lists_remaining_gaps(self):
        suite = {
            "audits": [
                audit_matrix_coverage_data(
                    {
                "cases": [
                    {
                        "check_family": "boundary",
                        "expected_tools": ["lookup"],
                        "forbidden_tools": ["fallback"],
                        "name": "lookup case",
                        "task": "Lookup a value.",
                    },
                    {
                        "check_family": "boundary",
                        "expected_tools": ["fallback"],
                        "forbidden_tools": ["lookup"],
                        "name": "fallback case",
                        "task": "Use fallback.",
                    }
                ],
                "name": "passing matrix",
                "profiles": [{"harnesses": ["prompt_json"], "provider": "trace_fixture"}],
                "tool_variants": [
                            {
                                "name": "sample",
                                "tools": [
                                    {
                                        "name": "lookup",
                                        "purpose": "Lookup values.",
                                        "quality_checks": ["Use exact ids."],
                                    },
                                    {
                                        "name": "fallback",
                                        "purpose": "Fallback safely.",
                                        "quality_checks": ["Use only for fallback."],
                                    }
                                ],
                            }
                        ],
                    }
                ),
                audit_matrix_coverage_data(
                    {
                        "cases": [
                            {
                                "expected_tools": ["search"],
                                "forbidden_tools": [],
                                "name": "search case",
                                "task": "Search.",
                            }
                        ],
                        "name": "failing matrix",
                        "profiles": [{"harnesses": ["prompt_json"], "provider": "trace_fixture"}],
                        "tool_variants": [
                            {
                                "name": "sample",
                                "tools": [
                                    {"name": "search", "purpose": "Search."},
                                ],
                            }
                        ],
                    }
                ),
            ],
            "passed": False,
            "summary": {
                "failed_matrices": 1,
                "matrix_count": 2,
                "passed_matrices": 1,
                "total_argument_cases": 0,
                "total_boundary_pairs": 2,
                "total_case_expectation_gaps": 0,
                "total_cases": 3,
                "total_identity_gaps": 0,
                "total_instruction_variants": 2,
                "total_profiles": 2,
                "total_tools": 3,
            },
        }

        output = render_matrix_coverage_suite_markdown(suite)

        self.assertIn("# Matrix Coverage Suite", output)
        self.assertIn("| passing matrix | yes |", output)
        self.assertIn("### failing matrix", output)
        self.assertIn("Cases without forbidden tools: search case", output)


if __name__ == "__main__":
    unittest.main()
