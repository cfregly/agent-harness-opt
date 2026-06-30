"""Coverage audits for model-matrix tool-selection cases."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .model_matrix import load_matrix


SPECIAL_TOOLS = {"NO_TOOL"}


def audit_matrix_coverage(path: str | Path) -> dict[str, Any]:
    matrix_path = Path(path)
    matrix = load_matrix(matrix_path)
    audit = audit_matrix_coverage_data(matrix, matrix_path=str(matrix_path))
    return audit


def audit_matrix_coverage_suite(paths: list[str | Path]) -> dict[str, Any]:
    matrix_paths = _expand_matrix_paths(paths)
    audits = [audit_matrix_coverage(path) for path in matrix_paths]
    return {
        "audits": audits,
        "matrix_paths": [str(path) for path in matrix_paths],
        "passed": all(audit["passed"] for audit in audits),
        "summary": {
            "failed_matrices": sum(1 for audit in audits if not audit["passed"]),
            "matrix_count": len(audits),
            "passed_matrices": sum(1 for audit in audits if audit["passed"]),
            "total_argument_cases": sum(audit["summary"]["argument_case_count"] for audit in audits),
            "total_boundary_pairs": sum(audit["summary"]["boundary_pair_count"] for audit in audits),
            "total_cases": sum(audit["summary"]["case_count"] for audit in audits),
            "total_tools": sum(audit["summary"]["tool_count"] for audit in audits),
        },
    }


def audit_matrix_coverage_data(
    matrix: dict[str, Any],
    *,
    matrix_path: str = "",
) -> dict[str, Any]:
    variants = matrix.get("tool_variants", [])
    tools = _tool_names(variants)
    coverage = matrix.get("coverage", {})
    external_forbidden = set(coverage.get("external_forbidden_tools", []))
    allow_variant_tool_delta = bool(coverage.get("allow_variant_tool_delta", False))
    required_check_families = {
        str(family)
        for family in coverage.get("required_check_families", [])
        if str(family).strip()
    }
    cases = matrix.get("cases", [])
    expected_cases = {tool: [] for tool in tools}
    forbidden_cases = {tool: [] for tool in tools}
    arg_cases = {tool: [] for tool in tools}
    boundary_pairs: dict[tuple[str, str], list[str]] = {}
    case_rows = []
    check_families: dict[str, list[str]] = {}
    unknown_expected: set[str] = set()
    unknown_forbidden: set[str] = set()

    for case in cases:
        name = str(case.get("name", ""))
        expected = [str(tool) for tool in case.get("expected_tools", [])]
        forbidden = [str(tool) for tool in case.get("forbidden_tools", [])]
        arg_checks = case.get("expected_args_contains") or {}
        check_family = str(case.get("check_family", "")).strip()
        if check_family:
            check_families.setdefault(check_family, []).append(name)
        for tool in expected:
            if tool in expected_cases:
                expected_cases[tool].append(name)
            elif tool not in SPECIAL_TOOLS:
                unknown_expected.add(tool)
            if arg_checks and tool in arg_cases:
                arg_cases[tool].append(name)
        for tool in forbidden:
            if tool in forbidden_cases:
                forbidden_cases[tool].append(name)
            elif tool not in SPECIAL_TOOLS and tool not in external_forbidden:
                unknown_forbidden.add(tool)
        for expected_tool in expected:
            for forbidden_tool in forbidden:
                boundary_pairs.setdefault((expected_tool, forbidden_tool), []).append(name)
        case_rows.append(
            {
                "allow_no_tool": bool(case.get("allow_no_tool", False)),
                "argument_checks": sorted(arg_checks),
                "check_family": check_family,
                "expected_tools": expected,
                "forbidden_tools": forbidden,
                "name": name,
                "task": str(case.get("task", "")),
            }
        )

    tools_detail = []
    for tool in tools:
        tool_def = _first_tool_def(variants, tool)
        missing_quality_checks = not bool(tool_def.get("quality_checks"))
        tools_detail.append(
            {
                "argument_cases": arg_cases[tool],
                "expected_cases": expected_cases[tool],
                "forbidden_cases": forbidden_cases[tool],
                "has_quality_checks": not missing_quality_checks,
                "name": tool,
            }
        )

    operational_tools = [tool for tool in tools if tool not in SPECIAL_TOOLS]
    never_expected = [tool for tool in operational_tools if not expected_cases[tool]]
    never_forbidden = [
        tool
        for tool in operational_tools
        if len(operational_tools) > 1 and not forbidden_cases[tool]
    ]
    expected_without_argument_check = [
        tool
        for tool in operational_tools
        if expected_cases[tool] and not arg_cases[tool] and _tool_accepts_arguments(variants, tool)
    ]
    missing_quality_checks = [
        item["name"]
        for item in tools_detail
        if not item["has_quality_checks"]
    ]
    cases_without_forbidden = [
        row["name"]
        for row in case_rows
        if row["expected_tools"] and not row["forbidden_tools"]
    ]
    cases_without_check_family = [
        row["name"]
        for row in case_rows
        if not row["check_family"]
    ]
    missing_required_check_families = sorted(required_check_families - set(check_families))
    duplicate_tool_names = _duplicate_tool_names(variants)
    variant_surface_mismatches = (
        []
        if allow_variant_tool_delta
        else _variant_surface_mismatches(variants)
    )
    source_tool_count_mismatch = _source_tool_count_mismatch(matrix.get("source", {}), operational_tools)
    warnings = []
    if never_expected:
        warnings.append("some catalog tools are never expected by a case")
    if never_forbidden:
        warnings.append("some catalog tools are never tested as confusable negatives")
    if expected_without_argument_check:
        warnings.append("some expected tools never have argument checks")
    if missing_quality_checks:
        warnings.append("some tuned tools have no quality checks")
    if cases_without_forbidden:
        warnings.append("some cases do not name forbidden confusable tools")
    if cases_without_check_family:
        warnings.append("some cases do not name a check_family")
    if missing_required_check_families:
        warnings.append("some required check families are not covered")
    if duplicate_tool_names:
        warnings.append("some tool variants contain duplicate tool names")
    if variant_surface_mismatches:
        warnings.append("some tool variants do not expose the same tool surface")
    if source_tool_count_mismatch:
        warnings.append("source tool_count does not match matrix tool surface")

    return {
        "boundary_pairs": [
            {
                "cases": names,
                "expected_tool": expected_tool,
                "forbidden_tool": forbidden_tool,
            }
            for (expected_tool, forbidden_tool), names in sorted(boundary_pairs.items())
        ],
        "cases": case_rows,
        "check_families": {
            family: names
            for family, names in sorted(check_families.items())
        },
        "matrix": matrix.get("name", ""),
        "matrix_path": matrix_path,
        "passed": not bool(warnings),
        "source": matrix.get("source", {}),
        "coverage": coverage,
        "summary": {
            "argument_case_count": sum(1 for row in case_rows if row["argument_checks"]),
            "boundary_pair_count": len(boundary_pairs),
            "case_count": len(cases),
            "case_count_with_check_family": len(cases) - len(cases_without_check_family),
            "required_check_family_count": len(required_check_families),
            "required_check_family_coverage": _ratio(
                len(required_check_families) - len(missing_required_check_families),
                len(required_check_families),
            ),
            "variant_surface_parity": _ratio(
                len(variants) - len(variant_surface_mismatches),
                len(variants),
            ),
            "forbidden_tool_coverage": _ratio(
                len(operational_tools) - len(never_forbidden),
                len(operational_tools),
            ),
            "no_tool_case_count": sum(1 for row in case_rows if row["allow_no_tool"]),
            "tool_count": len(operational_tools),
            "tool_expected_coverage": _ratio(
                len(operational_tools) - len(never_expected),
                len(operational_tools),
            ),
            "tool_variant_count": len(variants),
        },
        "tool_variants": [
            {
                "name": str(variant.get("name", "")),
                "tool_count": len(variant.get("tools", [])),
            }
            for variant in variants
        ],
        "tools": tools_detail,
        "uncovered": {
            "cases_without_check_family": cases_without_check_family,
            "cases_without_forbidden": cases_without_forbidden,
            "expected_without_argument_check": expected_without_argument_check,
            "duplicate_tool_names": duplicate_tool_names,
            "missing_quality_checks": missing_quality_checks,
            "missing_required_check_families": missing_required_check_families,
            "never_expected": never_expected,
            "never_forbidden": never_forbidden,
            "source_tool_count_mismatch": source_tool_count_mismatch,
            "unknown_expected_tools": sorted(unknown_expected),
            "unknown_forbidden_tools": sorted(unknown_forbidden),
            "variant_surface_mismatches": variant_surface_mismatches,
        },
        "warnings": warnings,
    }


def render_matrix_coverage_markdown(audit: dict[str, Any]) -> str:
    summary = audit["summary"]
    uncovered = audit["uncovered"]
    lines = [
        f"# Matrix Coverage: {audit['matrix']}",
        "",
        f"Passed: {'yes' if audit['passed'] else 'no'}",
        f"Tools: {summary['tool_count']}",
        f"Cases: {summary['case_count']}",
        f"Expected tool coverage: {summary['tool_expected_coverage']:.3f}",
        f"Forbidden tool coverage: {summary['forbidden_tool_coverage']:.3f}",
        f"Cases with argument checks: {summary['argument_case_count']}",
        f"Boundary pairs: {summary['boundary_pair_count']}",
        f"Cases with check_family: {summary['case_count_with_check_family']}",
        f"Required check-family coverage: {summary['required_check_family_coverage']:.3f}",
        f"Variant surface parity: {summary['variant_surface_parity']:.3f}",
        "",
        "## Gaps",
        "",
    ]
    for label, key in (
        ("Never expected", "never_expected"),
        ("Never forbidden", "never_forbidden"),
        ("Expected without argument checks", "expected_without_argument_check"),
        ("Duplicate tool names", "duplicate_tool_names"),
        ("Missing quality checks", "missing_quality_checks"),
        ("Missing required check families", "missing_required_check_families"),
        ("Variant surface mismatches", "variant_surface_mismatches"),
        ("Source tool count mismatch", "source_tool_count_mismatch"),
        ("Cases without forbidden tools", "cases_without_forbidden"),
        ("Cases without check_family", "cases_without_check_family"),
        ("Unknown expected tools", "unknown_expected_tools"),
        ("Unknown forbidden tools", "unknown_forbidden_tools"),
    ):
        values = uncovered.get(key, [])
        rendered = _render_gap_values(values) if values else "none"
        lines.append(f"- {label}: {rendered}")

    lines.extend(
        [
            "",
            "## Tool Coverage",
            "",
            "| Tool | Expected Cases | Forbidden Cases | Argument Cases | Quality Checks |",
            "|---|---:|---:|---:|---|",
        ]
    )
    for tool in audit["tools"]:
        lines.append(
            "| {name} | {expected} | {forbidden} | {args} | {checks} |".format(
                args=len(tool["argument_cases"]),
                checks="yes" if tool["has_quality_checks"] else "no",
                expected=len(tool["expected_cases"]),
                forbidden=len(tool["forbidden_cases"]),
                name=tool["name"],
            )
        )

    if audit["check_families"]:
        lines.extend(
            [
                "",
                "## Check Families",
                "",
                "| Family | Cases |",
                "|---|---:|",
            ]
        )
        for family, names in audit["check_families"].items():
            lines.append(f"| {family} | {len(names)} |")

    return "\n".join(lines) + "\n"


def render_matrix_coverage_suite_markdown(suite: dict[str, Any]) -> str:
    summary = suite["summary"]
    lines = [
        "# Matrix Coverage Suite",
        "",
        f"Passed: {'yes' if suite['passed'] else 'no'}",
        f"Matrices: {summary['matrix_count']}",
        f"Passed matrices: {summary['passed_matrices']}",
        f"Failed matrices: {summary['failed_matrices']}",
        f"Total tools: {summary['total_tools']}",
        f"Total cases: {summary['total_cases']}",
        f"Total argument cases: {summary['total_argument_cases']}",
        f"Total boundary pairs: {summary['total_boundary_pairs']}",
        "",
        "## Matrix Summary",
        "",
        "| Matrix | Passed | Tools | Cases | Expected | Forbidden | Arg Cases | Check Families | Required Families | Variant Parity | Boundary Pairs |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for audit in suite["audits"]:
        item = audit["summary"]
        lines.append(
            "| {matrix} | {passed} | {tools} | {cases} | {expected:.3f} | {forbidden:.3f} | "
            "{args} | {families} | {required:.3f} | {variant_parity:.3f} | {pairs} |".format(
                args=item["argument_case_count"],
                cases=item["case_count"],
                expected=item["tool_expected_coverage"],
                families=item["case_count_with_check_family"],
                forbidden=item["forbidden_tool_coverage"],
                matrix=audit["matrix"] or audit["matrix_path"],
                pairs=item["boundary_pair_count"],
                passed="yes" if audit["passed"] else "no",
                required=item["required_check_family_coverage"],
                tools=item["tool_count"],
                variant_parity=item["variant_surface_parity"],
            )
        )

    failed = [audit for audit in suite["audits"] if not audit["passed"]]
    if failed:
        lines.extend(["", "## Remaining Gaps", ""])
        for audit in failed:
            lines.append(f"### {audit['matrix'] or audit['matrix_path']}")
            for label, key in (
                ("Never expected", "never_expected"),
                ("Never forbidden", "never_forbidden"),
                ("Expected without argument checks", "expected_without_argument_check"),
                ("Duplicate tool names", "duplicate_tool_names"),
                ("Missing quality checks", "missing_quality_checks"),
                ("Missing required check families", "missing_required_check_families"),
                ("Variant surface mismatches", "variant_surface_mismatches"),
                ("Source tool count mismatch", "source_tool_count_mismatch"),
                ("Cases without forbidden tools", "cases_without_forbidden"),
                ("Cases without check_family", "cases_without_check_family"),
                ("Unknown expected tools", "unknown_expected_tools"),
                ("Unknown forbidden tools", "unknown_forbidden_tools"),
            ):
                values = audit["uncovered"].get(key, [])
                if values:
                    rendered = _render_gap_values(values[:20])
                    suffix = f", plus {len(values) - 20} more" if len(values) > 20 else ""
                    lines.append(f"- {label}: {rendered}{suffix}")
            lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def matrix_coverage_json(audit: dict[str, Any]) -> str:
    return json.dumps(audit, indent=2, sort_keys=True)


def _tool_names(variants: list[dict[str, Any]]) -> list[str]:
    names: list[str] = []
    seen = set()
    for variant in variants:
        for tool in variant.get("tools", []):
            name = str(tool.get("name", ""))
            if name and name not in seen:
                seen.add(name)
                names.append(name)
    return names


def _first_tool_def(variants: list[dict[str, Any]], name: str) -> dict[str, Any]:
    for variant in reversed(variants):
        for tool in variant.get("tools", []):
            if tool.get("name") == name:
                return tool
    return {}


def _tool_accepts_arguments(variants: list[dict[str, Any]], name: str) -> bool:
    schema = _first_tool_def(variants, name).get("input_schema", {})
    properties = schema.get("properties", {})
    required = schema.get("required", [])
    return bool(properties or required)


def _duplicate_tool_names(variants: list[dict[str, Any]]) -> list[dict[str, Any]]:
    duplicates = []
    for variant in variants:
        seen = set()
        repeated = set()
        for tool in variant.get("tools", []):
            name = str(tool.get("name", ""))
            if not name:
                continue
            if name in seen:
                repeated.add(name)
            seen.add(name)
        if repeated:
            duplicates.append(
                {
                    "duplicate_tools": sorted(repeated),
                    "variant": str(variant.get("name", "")),
                }
            )
    return duplicates


def _variant_surface_mismatches(variants: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not variants:
        return []
    canonical = {str(tool.get("name", "")) for tool in variants[0].get("tools", []) if tool.get("name")}
    mismatches = []
    for variant in variants[1:]:
        names = {str(tool.get("name", "")) for tool in variant.get("tools", []) if tool.get("name")}
        missing = sorted(canonical - names)
        extra = sorted(names - canonical)
        if missing or extra:
            mismatches.append(
                {
                    "extra_tools": extra,
                    "missing_tools": missing,
                    "variant": str(variant.get("name", "")),
                }
            )
    return mismatches


def _source_tool_count_mismatch(
    source: dict[str, Any],
    operational_tools: list[str],
) -> list[dict[str, Any]]:
    if "tool_count" not in source:
        return []
    actual = len(operational_tools)
    raw_expected = source.get("tool_count", 0)
    try:
        expected = int(raw_expected)
    except (TypeError, ValueError):
        return [{"actual": actual, "expected": raw_expected}]
    if expected == actual:
        return []
    return [{"actual": actual, "expected": expected}]


def _expand_matrix_paths(paths: list[str | Path]) -> list[Path]:
    expanded: list[Path] = []
    seen = set()
    for raw_path in paths:
        path = Path(raw_path)
        candidates = sorted(path.glob("*.json")) if path.is_dir() else [path]
        for candidate in candidates:
            key = str(candidate)
            if key not in seen:
                seen.add(key)
                expanded.append(candidate)
    return expanded


def _render_gap_values(values: list[Any]) -> str:
    rendered = []
    for value in values:
        if isinstance(value, dict):
            rendered.append(json.dumps(value, sort_keys=True))
        else:
            rendered.append(str(value))
    return ", ".join(rendered)


def _ratio(numerator: int, denominator: int) -> float:
    if not denominator:
        return 1.0
    return round(numerator / denominator, 3)
