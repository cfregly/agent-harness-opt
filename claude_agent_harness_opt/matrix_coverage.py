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
            "total_case_expectation_gaps": sum(
                audit["summary"]["case_expectation_gap_count"]
                for audit in audits
            ),
            "total_cases": sum(audit["summary"]["case_count"] for audit in audits),
            "total_identity_gaps": sum(audit["summary"]["identity_gap_count"] for audit in audits),
            "total_instruction_variants": sum(
                audit["summary"]["instruction_variant_count"]
                for audit in audits
            ),
            "total_profiles": sum(audit["summary"]["profile_count"] for audit in audits),
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
    profiles = matrix.get("profiles", [])
    instruction_variants = matrix.get("instruction_variants") or [{"name": "default"}]
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
    identity_gaps = _identity_gaps(
        cases=cases,
        instruction_variants=instruction_variants,
        profiles=profiles,
        tool_variants=variants,
    )
    case_expectation_gaps = _case_expectation_gaps(cases, variants)
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
    if unknown_expected:
        warnings.append("some expected tool names are not in the matrix catalog")
    if unknown_forbidden:
        warnings.append("some forbidden tool names are not in the matrix catalog or external allow-list")
    if duplicate_tool_names:
        warnings.append("some tool variants contain duplicate tool names")
    if variant_surface_mismatches:
        warnings.append("some tool variants do not expose the same tool surface")
    if identity_gaps:
        warnings.append("some matrix identities or case definitions are ambiguous")
    if case_expectation_gaps:
        warnings.append("some case expectations are contradictory or impossible")
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
            "case_expectation_gap_count": len(case_expectation_gaps),
            "case_count": len(cases),
            "case_count_with_check_family": len(cases) - len(cases_without_check_family),
            "identity_gap_count": len(identity_gaps),
            "instruction_variant_count": len(instruction_variants),
            "profile_count": len(profiles),
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
            "case_expectation_gaps": case_expectation_gaps,
            "expected_without_argument_check": expected_without_argument_check,
            "duplicate_tool_names": duplicate_tool_names,
            "identity_gaps": identity_gaps,
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
        f"Profiles: {summary['profile_count']}",
        f"Instruction variants: {summary['instruction_variant_count']}",
        f"Expected tool coverage: {summary['tool_expected_coverage']:.3f}",
        f"Forbidden tool coverage: {summary['forbidden_tool_coverage']:.3f}",
        f"Cases with argument checks: {summary['argument_case_count']}",
        f"Boundary pairs: {summary['boundary_pair_count']}",
        f"Cases with check_family: {summary['case_count_with_check_family']}",
        f"Case expectation gaps: {summary['case_expectation_gap_count']}",
        f"Identity gaps: {summary['identity_gap_count']}",
        f"Required check-family coverage: {summary['required_check_family_coverage']:.3f}",
        f"Variant surface parity: {summary['variant_surface_parity']:.3f}",
        "",
        "## Gaps",
        "",
    ]
    for label, key in (
        ("Never expected", "never_expected"),
        ("Never forbidden", "never_forbidden"),
        ("Case expectation gaps", "case_expectation_gaps"),
        ("Expected without argument checks", "expected_without_argument_check"),
        ("Duplicate tool names", "duplicate_tool_names"),
        ("Identity gaps", "identity_gaps"),
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
        f"Total profiles: {summary['total_profiles']}",
        f"Total instruction variants: {summary['total_instruction_variants']}",
        f"Total argument cases: {summary['total_argument_cases']}",
        f"Total boundary pairs: {summary['total_boundary_pairs']}",
        f"Total case expectation gaps: {summary['total_case_expectation_gaps']}",
        f"Total identity gaps: {summary['total_identity_gaps']}",
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
                ("Case expectation gaps", "case_expectation_gaps"),
                ("Expected without argument checks", "expected_without_argument_check"),
                ("Duplicate tool names", "duplicate_tool_names"),
                ("Identity gaps", "identity_gaps"),
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


def _identity_gaps(
    *,
    cases: list[dict[str, Any]],
    instruction_variants: list[dict[str, Any]],
    profiles: list[dict[str, Any]],
    tool_variants: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    gaps: list[dict[str, Any]] = []

    case_names = [str(case.get("name", "")).strip() for case in cases]
    _append_missing_or_duplicate_name_gaps(gaps, "cases.name", case_names)
    for index, case in enumerate(cases, start=1):
        label = _case_label(case, index)
        expected = case.get("expected_tools", [])
        forbidden = case.get("forbidden_tools", [])
        arg_checks = case.get("expected_args_contains", {})
        if not str(case.get("task", "")).strip():
            gaps.append({"case": label, "field": "cases.task", "problem": "missing"})
        if not isinstance(expected, list):
            gaps.append({"case": label, "field": "cases.expected_tools", "problem": "not_list"})
            expected = []
        if not isinstance(forbidden, list):
            gaps.append({"case": label, "field": "cases.forbidden_tools", "problem": "not_list"})
        if arg_checks and not isinstance(arg_checks, dict):
            gaps.append(
                {
                    "case": label,
                    "field": "cases.expected_args_contains",
                    "problem": "not_object",
                }
            )
        if not expected and not case.get("allow_no_tool", False):
            gaps.append(
                {
                    "case": label,
                    "field": "cases.expected_tools",
                    "problem": "missing_without_allow_no_tool",
                }
            )

    variant_names = [str(variant.get("name", "")).strip() for variant in tool_variants]
    _append_missing_or_duplicate_name_gaps(gaps, "tool_variants.name", variant_names)

    instruction_names = [
        str(instruction.get("name", "")).strip()
        for instruction in instruction_variants
    ]
    _append_missing_or_duplicate_name_gaps(gaps, "instruction_variants.name", instruction_names)

    profile_names = [
        str(profile.get("name") or profile.get("provider") or "").strip()
        for profile in profiles
    ]
    _append_missing_or_duplicate_name_gaps(gaps, "profiles.name_or_provider", profile_names)
    for index, profile in enumerate(profiles, start=1):
        label = profile_names[index - 1] or f"#{index}"
        if not str(profile.get("provider", "")).strip():
            gaps.append({"field": "profiles.provider", "problem": "missing", "profile": label})
        harnesses = profile.get("harnesses")
        if not harnesses:
            gaps.append({"field": "profiles.harnesses", "problem": "missing", "profile": label})
            continue
        if not isinstance(harnesses, list):
            gaps.append({"field": "profiles.harnesses", "problem": "not_list", "profile": label})
            continue
        duplicate_harnesses = _duplicates([str(harness).strip() for harness in harnesses])
        if duplicate_harnesses:
            gaps.append(
                {
                    "field": "profiles.harnesses",
                    "problem": "duplicate",
                    "profile": label,
                    "values": duplicate_harnesses,
                }
            )
    return gaps


def _case_expectation_gaps(
    cases: list[dict[str, Any]],
    variants: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    gaps: list[dict[str, Any]] = []
    for index, case in enumerate(cases, start=1):
        label = _case_label(case, index)
        expected = case.get("expected_tools", [])
        forbidden = case.get("forbidden_tools", [])
        arg_checks = case.get("expected_args_contains", {}) or {}
        if not isinstance(expected, list) or not isinstance(forbidden, list):
            continue
        expected_names = [str(tool) for tool in expected if str(tool)]
        forbidden_names = [str(tool) for tool in forbidden if str(tool)]

        duplicate_expected = _duplicates(expected_names)
        if duplicate_expected:
            gaps.append(
                {
                    "case": label,
                    "field": "cases.expected_tools",
                    "problem": "duplicate",
                    "values": duplicate_expected,
                }
            )
        duplicate_forbidden = _duplicates(forbidden_names)
        if duplicate_forbidden:
            gaps.append(
                {
                    "case": label,
                    "field": "cases.forbidden_tools",
                    "problem": "duplicate",
                    "values": duplicate_forbidden,
                }
            )

        overlap = sorted(set(expected_names) & set(forbidden_names))
        if overlap:
            gaps.append(
                {
                    "case": label,
                    "field": "cases.expected_tools/cases.forbidden_tools",
                    "problem": "overlap",
                    "values": overlap,
                }
            )
        if case.get("allow_no_tool", False) and expected_names:
            gaps.append(
                {
                    "case": label,
                    "field": "cases.allow_no_tool",
                    "problem": "expected_tools_present",
                    "values": expected_names,
                }
            )
        if case.get("allow_no_tool", False) and arg_checks:
            gaps.append(
                {
                    "case": label,
                    "field": "cases.expected_args_contains",
                    "problem": "no_tool_case_has_argument_checks",
                    "values": sorted(str(key) for key in arg_checks),
                }
            )
        if isinstance(arg_checks, dict) and arg_checks and expected_names:
            available_args = {
                argument
                for tool in expected_names
                for argument in _tool_argument_names(variants, tool)
            }
            unknown_args = sorted(str(key) for key in arg_checks if str(key) not in available_args)
            if unknown_args:
                gaps.append(
                    {
                        "available_arguments": sorted(available_args),
                        "case": label,
                        "field": "cases.expected_args_contains",
                        "problem": "argument_not_in_expected_tool_schema",
                        "values": unknown_args,
                    }
                )
    return gaps


def _append_missing_or_duplicate_name_gaps(
    gaps: list[dict[str, Any]],
    field: str,
    names: list[str],
) -> None:
    missing = [index for index, name in enumerate(names, start=1) if not name]
    if missing:
        gaps.append({"field": field, "indexes": missing, "problem": "missing"})
    duplicates = _duplicates(names)
    if duplicates:
        gaps.append({"field": field, "problem": "duplicate", "values": duplicates})


def _duplicates(values: list[str]) -> list[str]:
    seen = set()
    repeated = set()
    for value in values:
        if not value:
            continue
        if value in seen:
            repeated.add(value)
        seen.add(value)
    return sorted(repeated)


def _case_label(case: dict[str, Any], index: int) -> str:
    name = str(case.get("name", "")).strip()
    return name or f"#{index}"


def _tool_argument_names(variants: list[dict[str, Any]], name: str) -> set[str]:
    arguments: set[str] = set()
    for variant in variants:
        for tool in variant.get("tools", []):
            if tool.get("name") != name:
                continue
            schema = tool.get("input_schema", {})
            properties = schema.get("properties", {})
            if isinstance(properties, dict):
                arguments.update(str(key) for key in properties)
            required = schema.get("required", [])
            if isinstance(required, list):
                arguments.update(str(key) for key in required)
    return arguments


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
