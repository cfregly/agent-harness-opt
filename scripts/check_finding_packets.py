#!/usr/bin/env python3
"""Validate shareable finding packets and local evidence links."""

from __future__ import annotations

import contextlib
import io
import json
import re
import shlex
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from claude_agent_harness_opt.matrix_coverage import audit_matrix_coverage  # noqa: E402
from claude_agent_harness_opt.cli import build_parser  # noqa: E402

FINDINGS_DIR = ROOT / "docs" / "findings"
PR_PACKETS_DIR = ROOT / "evals" / "pr_packets"
RESULTS_DIR = ROOT / "evals" / "results"
TARGETS_DIR = ROOT / "evals" / "targets"
REPO_LINK_RE = re.compile(
    r"https://github\.com/cfregly/claude-agent-harness-opt/(?:blob|tree)/main/([^)\s]+)"
)
LOCAL_ARTIFACT_RE = re.compile(r"`((?:docs|evals|README\.md)[^`]+)`")
MATRIX_LINK_RE = re.compile(r"evals/model_matrix/[^)`\s]+\.json")
REQUIRED_PACKET_SECTIONS = ("## Result", "## Evidence", "## Reproduce")
REQUIRED_PACKET_FILES = ("README.md",)
REQUIRED_PACKET_ARTIFACT_PREFIXES = (
    "docs/",
    "evals/model_matrix/",
    "evals/results/",
    "evals/pr_packets/",
)
REQUIRED_PR_PACKET_FILES = ("PR_TITLE.txt", "PR_BODY.md", "REPRODUCTION.md", "evidence.json")
REQUIRED_COMPARISON_FIELDS = (
    "baseline_score",
    "baseline_variant",
    "candidate_score",
    "candidate_variant",
    "delta",
    "minimum_delta",
    "promote",
)


def main() -> int:
    failures = check_finding_packets()
    if failures:
        print("\n".join(sorted(failures)))
        return 1
    print("finding packet check passed")
    return 0


def check_finding_packets() -> list[str]:
    failures: list[str] = []
    index_text = _read_required(FINDINGS_DIR / "README.md", failures)
    ledger_text = _read_required(ROOT / "docs" / "confirmed-improvements.md", failures)
    if not index_text or not ledger_text:
        return failures

    packet_dirs = [
        path
        for path in sorted(FINDINGS_DIR.iterdir())
        if path.is_dir()
    ]
    if not packet_dirs:
        return ["docs/findings: no finding packet directories found"]

    for packet_dir in packet_dirs:
        failures.extend(_check_packet_dir(packet_dir, index_text, ledger_text))
    failures.extend(_check_repo_links(FINDINGS_DIR / "README.md", index_text))
    failures.extend(_check_repo_links(ROOT / "docs" / "confirmed-improvements.md", ledger_text))
    failures.extend(_check_pr_packet_dirs())
    failures.extend(_check_result_artifacts())
    failures.extend(_check_matrix_surface_coverage())
    return failures


def _check_packet_dir(packet_dir: Path, index_text: str, ledger_text: str) -> list[str]:
    failures: list[str] = []
    rel_dir = packet_dir.relative_to(ROOT)
    slug = packet_dir.name
    for filename in REQUIRED_PACKET_FILES:
        path = packet_dir / filename
        if not path.exists():
            failures.append(f"{rel_dir}: missing {filename}")
            return failures

    readme = packet_dir / "README.md"
    text = readme.read_text(encoding="utf-8")
    rel_readme = readme.relative_to(ROOT)
    for section in REQUIRED_PACKET_SECTIONS:
        if section not in text:
            failures.append(f"{rel_readme}: missing section {section}")
    if "Share link:" not in text:
        failures.append(f"{rel_readme}: missing share link")
    if "adversarially-confirmed to add value" not in text:
        failures.append(f"{rel_readme}: missing value-bar phrase")
    if not MATRIX_LINK_RE.search(text):
        failures.append(f"{rel_readme}: missing matrix link")
    if f"docs/findings/{slug}" not in index_text:
        failures.append(f"{rel_dir}: missing from docs/findings/README.md")
    if f"docs/findings/{slug}" not in ledger_text:
        failures.append(f"{rel_dir}: missing from docs/confirmed-improvements.md")

    local_refs = _local_refs(text)
    evidence_refs = [
        ref
        for ref in local_refs
        if ref.startswith(REQUIRED_PACKET_ARTIFACT_PREFIXES)
    ]
    if not evidence_refs:
        failures.append(f"{rel_readme}: no local evidence references")
    for ref in sorted(local_refs):
        failures.extend(_check_local_ref(rel_readme, ref))
    failures.extend(_check_repo_links(readme, text))
    return failures


def _local_refs(text: str) -> set[str]:
    refs = {match.group(1) for match in REPO_LINK_RE.finditer(text)}
    for match in LOCAL_ARTIFACT_RE.finditer(text):
        ref = match.group(1).strip()
        if ref.startswith(("docs/", "evals/", "README.md")):
            refs.add(ref)
    return refs


def _check_repo_links(path: Path, text: str) -> list[str]:
    failures: list[str] = []
    rel = path.relative_to(ROOT)
    for ref in sorted({match.group(1) for match in REPO_LINK_RE.finditer(text)}):
        failures.extend(_check_local_ref(rel, ref))
    return failures


def _check_local_ref(rel_source: Path, ref: str) -> list[str]:
    failures: list[str] = []
    candidate = ROOT / ref
    if not candidate.exists():
        failures.append(f"{rel_source}: local evidence link missing: {ref}")
    return failures


def _check_pr_packet_dirs() -> list[str]:
    failures: list[str] = []
    if not PR_PACKETS_DIR.exists():
        return ["evals/pr_packets: missing"]
    packet_dirs = [path for path in sorted(PR_PACKETS_DIR.iterdir()) if path.is_dir()]
    if not packet_dirs:
        return ["evals/pr_packets: no PR packet directories found"]
    for packet_dir in packet_dirs:
        failures.extend(_check_pr_packet_dir(packet_dir))
    return failures


def _check_pr_packet_dir(packet_dir: Path) -> list[str]:
    failures: list[str] = []
    rel_dir = packet_dir.relative_to(ROOT)
    for filename in REQUIRED_PR_PACKET_FILES:
        path = packet_dir / filename
        if not path.exists():
            failures.append(f"{rel_dir}: missing {filename}")
            continue
        if not path.read_text(encoding="utf-8").strip():
            failures.append(f"{path.relative_to(ROOT)}: empty")

    evidence_path = packet_dir / "evidence.json"
    if not evidence_path.exists():
        return failures
    try:
        evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        failures.append(f"{evidence_path.relative_to(ROOT)}: invalid JSON: {exc}")
        return failures
    if not isinstance(evidence, dict):
        failures.append(f"{evidence_path.relative_to(ROOT)}: evidence must be an object")
        return failures
    failures.extend(_check_pr_packet_evidence(evidence_path, evidence))
    return failures


def _check_pr_packet_evidence(path: Path, evidence: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    rel = path.relative_to(ROOT)
    cases = evidence.get("cases")
    if not isinstance(cases, list) or not cases:
        failures.append(f"{rel}: cases must be a nonempty list")
    comparison = evidence.get("comparison")
    if not isinstance(comparison, dict):
        failures.append(f"{rel}: comparison must be an object")
        comparison = {}
    for field in REQUIRED_COMPARISON_FIELDS:
        if field not in comparison:
            failures.append(f"{rel}: comparison missing {field}")
    baseline_variant = str(comparison.get("baseline_variant", "")).strip()
    candidate_variant = str(comparison.get("candidate_variant", "")).strip()
    for field in ("baseline_score", "candidate_score", "delta", "minimum_delta"):
        if field in comparison and not isinstance(comparison[field], (int, float)):
            failures.append(f"{rel}: comparison.{field} must be numeric")
    if comparison.get("promote") is not True:
        failures.append(f"{rel}: comparison.promote must be true for committed PR packets")
    if (
        isinstance(comparison.get("delta"), (int, float))
        and isinstance(comparison.get("minimum_delta"), (int, float))
        and comparison["delta"] < comparison["minimum_delta"]
    ):
        failures.append(f"{rel}: comparison delta is below minimum_delta")

    result = evidence.get("result")
    if not isinstance(result, dict):
        failures.append(f"{rel}: result must be an object")
        result = {}
    if result.get("live") is not True:
        failures.append(f"{rel}: result.live must be true")
    if not isinstance(result.get("results"), list) or not result.get("results"):
        failures.append(f"{rel}: result.results must be a nonempty list")
    if not isinstance(result.get("cells"), list) or not result.get("cells"):
        failures.append(f"{rel}: result.cells must be a nonempty list")
    if not isinstance(result.get("summary"), dict) or not result["summary"].get("total"):
        failures.append(f"{rel}: result.summary.total must be present")
    matrix_path = str(result.get("matrix_path", "")).strip()
    if matrix_path and not (ROOT / matrix_path).exists():
        failures.append(f"{rel}: result.matrix_path missing locally: {matrix_path}")

    matrix = evidence.get("matrix")
    if not isinstance(matrix, dict):
        failures.append(f"{rel}: matrix must be an object")
        matrix = {}
    matrix_variants = {
        str(variant.get("name", ""))
        for variant in matrix.get("tool_variants", [])
        if isinstance(variant, dict)
    }
    for variant_name in (baseline_variant, candidate_variant):
        if variant_name and variant_name not in matrix_variants:
            failures.append(f"{rel}: comparison variant missing from matrix: {variant_name}")
    result_variants = {
        str(item.get("tool_variant", ""))
        for item in result.get("results", [])
        if isinstance(item, dict)
    }
    for variant_name in (baseline_variant, candidate_variant):
        if variant_name and variant_name not in result_variants:
            failures.append(f"{rel}: comparison variant missing from result cells: {variant_name}")

    source = evidence.get("source")
    if not isinstance(source, dict) or not source:
        failures.append(f"{rel}: source must be a nonempty object")
    return failures


def _check_result_artifacts() -> list[str]:
    failures: list[str] = []
    if not RESULTS_DIR.exists():
        return ["evals/results: missing"]
    artifacts = sorted(path for path in RESULTS_DIR.iterdir() if path.is_file())
    if not artifacts:
        return ["evals/results: no result artifacts found"]
    for path in artifacts:
        if path.suffix == ".json":
            failures.extend(_check_result_json(path))
        elif path.suffix == ".md":
            failures.extend(_check_result_markdown(path))
        else:
            failures.append(f"{path.relative_to(ROOT)}: unsupported result artifact type")
    return failures


def _check_matrix_surface_coverage() -> list[str]:
    failures: list[str] = []
    paths = _matrix_surface_paths()
    if not paths:
        return ["evals: no matrix surfaces found"]
    for path in paths:
        rel = path.relative_to(ROOT)
        try:
            audit = audit_matrix_coverage(path)
        except FileNotFoundError:
            continue
        except Exception as exc:  # noqa: BLE001 - surface gates should report all malformed matrices.
            failures.append(f"{rel}: matrix coverage audit crashed: {exc}")
            continue
        if not audit["passed"]:
            warnings = "; ".join(audit.get("warnings", []))
            failures.append(f"{rel}: matrix coverage failed: {warnings}")
    return failures


def _matrix_surface_paths() -> list[Path]:
    paths: list[Path] = []
    seen: set[Path] = set()
    for path in sorted((ROOT / "evals" / "model_matrix").glob("*.json")):
        seen.add(path)
        paths.append(path)
    if TARGETS_DIR.exists():
        for path in sorted(TARGETS_DIR.rglob("*.json")):
            if path in seen:
                continue
            if _looks_like_matrix(path):
                seen.add(path)
                paths.append(path)
    return paths


def _looks_like_matrix(path: Path) -> bool:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return False
    except json.JSONDecodeError:
        return False
    return isinstance(payload, dict) and {"cases", "profiles", "tool_variants"}.issubset(payload)


def _check_result_json(path: Path) -> list[str]:
    failures: list[str] = []
    rel = path.relative_to(ROOT)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"{rel}: invalid JSON: {exc}"]
    if not isinstance(payload, dict):
        return [f"{rel}: JSON result must be an object"]

    if {"results", "cells", "summary"}.issubset(payload):
        failures.extend(_check_model_matrix_receipt(path, payload))
    elif {"audits", "matrix_paths", "summary"}.issubset(payload):
        failures.extend(_check_coverage_suite_receipt(path, payload))
    elif {"tools", "cases", "boundary_pairs", "summary"}.issubset(payload):
        failures.extend(_check_matrix_coverage_receipt(path, payload))
    elif {"items", "hash", "snapshot_version"}.issubset(payload):
        failures.extend(_check_surface_snapshot_receipt(path, payload))
    elif {"packages", "passed", "value_bar"}.issubset(payload):
        failures.extend(_check_surface_inventory_receipt(path, payload))
    elif {"cells", "summary", "source_spec"}.issubset(payload):
        failures.extend(_check_live_harness_receipt(path, payload))
    else:
        failures.append(f"{rel}: unknown JSON result shape")
    return failures


def _check_model_matrix_receipt(path: Path, payload: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    rel = path.relative_to(ROOT)
    if payload.get("live") is not True:
        failures.append(f"{rel}: model-matrix result.live must be true")
    _require_bool(rel, payload, "passed", failures)
    results = _require_nonempty_list(rel, payload, "results", failures)
    cells = _require_nonempty_list(rel, payload, "cells", failures)
    case_definitions = _require_nonempty_list(rel, payload, "case_definitions", failures)
    summary = _require_object(rel, payload, "summary", failures)
    if results and summary:
        total = summary.get("total")
        if not isinstance(total, int) or total <= 0:
            failures.append(f"{rel}: summary.total must be a positive integer")
        elif total != len(results):
            failures.append(f"{rel}: summary.total must equal result count")
        planned = summary.get("planned")
        if isinstance(planned, int) and planned != len(results):
            failures.append(f"{rel}: summary.planned must equal result count")
    if case_definitions:
        case_names = {str(item.get("name", "")) for item in case_definitions if isinstance(item, dict)}
        result_case_names = {str(item.get("case", "")) for item in results if isinstance(item, dict)}
        missing_case_defs = sorted(name for name in result_case_names if name and name not in case_names)
        if missing_case_defs:
            failures.append(f"{rel}: result cases missing from case_definitions: {', '.join(missing_case_defs)}")
    if cells:
        for idx, cell in enumerate(cells):
            if not isinstance(cell, dict):
                failures.append(f"{rel}: cells[{idx}] must be an object")
                continue
            for field in ("provider", "harness", "tool_variant", "instruction_variant"):
                if not str(cell.get(field, "")).strip():
                    failures.append(f"{rel}: cells[{idx}] missing {field}")
    if results:
        saw_failed = False
        for idx, result in enumerate(results):
            if not isinstance(result, dict):
                failures.append(f"{rel}: results[{idx}] must be an object")
                continue
            for field in ("case", "provider", "harness", "tool_variant", "instruction_variant", "status"):
                if not str(result.get(field, "")).strip():
                    failures.append(f"{rel}: results[{idx}] missing {field}")
            if not isinstance(result.get("passed"), bool):
                failures.append(f"{rel}: results[{idx}].passed must be boolean")
            if not isinstance(result.get("chosen_tools"), list):
                failures.append(f"{rel}: results[{idx}].chosen_tools must be a list")
            if result.get("passed") is False:
                saw_failed = True
        if payload.get("passed") is False and not saw_failed:
            failures.append(f"{rel}: failed model-matrix receipt has no failed result rows")
    matrix_path = str(payload.get("matrix_path", "")).strip()
    if not matrix_path:
        failures.append(f"{rel}: matrix_path must be present")
    else:
        failures.extend(_check_local_ref(rel, matrix_path))
    if matrix_path and results and cells:
        failures.extend(
            _check_model_matrix_receipt_against_matrix(
                rel,
                matrix_path,
                results,
                cells,
                case_definitions,
            )
        )
    matrix = payload.get("matrix")
    if "matrix" in payload and not (
        isinstance(matrix, dict) or str(matrix or "").strip()
    ):
        failures.append(f"{rel}: matrix must be an object or display name")
    if not isinstance(payload.get("source"), dict) or not payload.get("source"):
        failures.append(f"{rel}: source must be a nonempty object")
    return failures


def _check_model_matrix_receipt_against_matrix(
    rel: Path,
    matrix_path: str,
    results: list[Any],
    cells: list[Any],
    case_definitions: list[Any],
) -> list[str]:
    failures: list[str] = []
    try:
        matrix = json.loads((ROOT / matrix_path).read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return failures
    if not isinstance(matrix, dict):
        return failures
    matrix_cases = _named_items(matrix.get("cases", []))
    matrix_tool_variants = _named_items(matrix.get("tool_variants", []))
    matrix_instruction_variants = _named_items(matrix.get("instruction_variants", []))
    matrix_providers = {
        str(profile.get("provider", "")).strip()
        for profile in matrix.get("profiles", [])
        if isinstance(profile, dict) and str(profile.get("provider", "")).strip()
    }
    matrix_harnesses = {
        str(harness).strip()
        for profile in matrix.get("profiles", [])
        if isinstance(profile, dict)
        for harness in profile.get("harnesses", [])
        if str(harness).strip()
    }
    for idx, case in enumerate(case_definitions):
        if not isinstance(case, dict):
            continue
        name = str(case.get("name", "")).strip()
        if name and matrix_cases and name not in matrix_cases:
            failures.append(f"{rel}: case_definitions[{idx}] unknown matrix case {name!r}")
    cell_keys: set[tuple[str, str, str, str]] = set()
    for idx, cell in enumerate(cells):
        if not isinstance(cell, dict):
            continue
        provider = str(cell.get("provider", "")).strip()
        harness = str(cell.get("harness", "")).strip()
        tool_variant = str(cell.get("tool_variant", "")).strip()
        instruction_variant = str(cell.get("instruction_variant", "")).strip()
        cell_keys.add((provider, harness, tool_variant, instruction_variant))
        failures.extend(
            _check_matrix_dimensions(
                rel,
                f"cells[{idx}]",
                provider,
                harness,
                tool_variant,
                instruction_variant,
                matrix_providers,
                matrix_harnesses,
                matrix_tool_variants,
                matrix_instruction_variants,
            )
        )
    seen_results: set[tuple[str, str, str, str, str]] = set()
    for idx, result in enumerate(results):
        if not isinstance(result, dict):
            continue
        case_name = str(result.get("case", "")).strip()
        provider = str(result.get("provider", "")).strip()
        harness = str(result.get("harness", "")).strip()
        tool_variant = str(result.get("tool_variant", "")).strip()
        instruction_variant = str(result.get("instruction_variant", "")).strip()
        if matrix_cases and case_name and case_name not in matrix_cases:
            failures.append(f"{rel}: results[{idx}] unknown matrix case {case_name!r}")
        failures.extend(
            _check_matrix_dimensions(
                rel,
                f"results[{idx}]",
                provider,
                harness,
                tool_variant,
                instruction_variant,
                matrix_providers,
                matrix_harnesses,
                matrix_tool_variants,
                matrix_instruction_variants,
            )
        )
        if cell_keys and (provider, harness, tool_variant, instruction_variant) not in cell_keys:
            failures.append(f"{rel}: results[{idx}] has no matching planned cell")
        result_key = (case_name, provider, harness, tool_variant, instruction_variant)
        if result_key in seen_results:
            failures.append(f"{rel}: duplicate matrix result row {case_name!r}/{provider!r}/{harness!r}/{tool_variant!r}/{instruction_variant!r}")
        seen_results.add(result_key)
    return failures


def _named_items(items: Any) -> set[str]:
    return {
        str(item.get("name", "")).strip()
        for item in items
        if isinstance(item, dict) and str(item.get("name", "")).strip()
    }


def _check_matrix_dimensions(
    rel: Path,
    label: str,
    provider: str,
    harness: str,
    tool_variant: str,
    instruction_variant: str,
    matrix_providers: set[str],
    matrix_harnesses: set[str],
    matrix_tool_variants: set[str],
    matrix_instruction_variants: set[str],
) -> list[str]:
    failures: list[str] = []
    if matrix_providers and provider and provider not in matrix_providers:
        failures.append(f"{rel}: {label} unknown matrix provider {provider!r}")
    if matrix_harnesses and harness and harness not in matrix_harnesses:
        failures.append(f"{rel}: {label} unknown matrix harness {harness!r}")
    if matrix_tool_variants and tool_variant and tool_variant not in matrix_tool_variants:
        failures.append(f"{rel}: {label} unknown matrix tool_variant {tool_variant!r}")
    if matrix_instruction_variants and instruction_variant and instruction_variant not in matrix_instruction_variants:
        failures.append(f"{rel}: {label} unknown matrix instruction_variant {instruction_variant!r}")
    return failures


def _check_coverage_suite_receipt(path: Path, payload: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    rel = path.relative_to(ROOT)
    if payload.get("passed") is not True:
        failures.append(f"{rel}: coverage-suite receipt must pass")
    audits = _require_nonempty_list(rel, payload, "audits", failures)
    matrix_paths = _require_nonempty_list(rel, payload, "matrix_paths", failures)
    summary = _require_object(rel, payload, "summary", failures)
    if summary:
        if summary.get("failed_matrices") != 0:
            failures.append(f"{rel}: summary.failed_matrices must be 0")
        matrix_count = summary.get("matrix_count")
        if audits and matrix_count != len(audits):
            failures.append(f"{rel}: summary.matrix_count must equal audit count")
        if matrix_paths and matrix_count != len(matrix_paths):
            failures.append(f"{rel}: summary.matrix_count must equal matrix_paths count")
    for matrix_path in matrix_paths:
        if isinstance(matrix_path, str):
            failures.extend(_check_local_ref(rel, matrix_path))
        else:
            failures.append(f"{rel}: matrix_paths entries must be strings")
    if audits and matrix_paths and summary:
        failures.extend(_check_coverage_suite_audits(rel, audits, matrix_paths, summary))
    return failures


def _check_coverage_suite_audits(
    rel: Path,
    audits: list[Any],
    matrix_paths: list[Any],
    summary: dict[str, Any],
) -> list[str]:
    failures: list[str] = []
    listed_paths = [path for path in matrix_paths if isinstance(path, str)]
    duplicate_paths = sorted({path for path in listed_paths if listed_paths.count(path) > 1})
    for matrix_path in duplicate_paths:
        failures.append(f"{rel}: duplicate matrix_paths entry {matrix_path!r}")
    audit_paths: list[str] = []
    passed_count = 0
    failed_count = 0
    for idx, audit in enumerate(audits):
        if not isinstance(audit, dict):
            failures.append(f"{rel}: audits[{idx}] must be an object")
            continue
        matrix_path = str(audit.get("matrix_path", "")).strip()
        if not matrix_path:
            failures.append(f"{rel}: audits[{idx}] missing matrix_path")
        else:
            audit_paths.append(matrix_path)
            if matrix_path not in listed_paths:
                failures.append(f"{rel}: audits[{idx}] matrix_path {matrix_path!r} missing from matrix_paths")
            failures.extend(_check_local_ref(rel, matrix_path))
        if audit.get("passed") is True:
            passed_count += 1
        elif audit.get("passed") is False:
            failed_count += 1
            failures.append(f"{rel}: audits[{idx}] must pass")
        else:
            failures.append(f"{rel}: audits[{idx}].passed must be boolean")
        audit_summary = audit.get("summary")
        if not isinstance(audit_summary, dict):
            failures.append(f"{rel}: audits[{idx}].summary must be an object")
    duplicate_audit_paths = sorted({path for path in audit_paths if audit_paths.count(path) > 1})
    for matrix_path in duplicate_audit_paths:
        failures.append(f"{rel}: duplicate audit matrix_path {matrix_path!r}")
    missing_audits = sorted(set(listed_paths) - set(audit_paths))
    for matrix_path in missing_audits:
        failures.append(f"{rel}: matrix_paths entry missing audit {matrix_path!r}")
    extra_audits = sorted(set(audit_paths) - set(listed_paths))
    for matrix_path in extra_audits:
        failures.append(f"{rel}: audit matrix_path missing from matrix_paths {matrix_path!r}")
    if summary.get("passed_matrices") != passed_count:
        failures.append(f"{rel}: summary.passed_matrices must equal passing audit count")
    if summary.get("failed_matrices") != failed_count:
        failures.append(f"{rel}: summary.failed_matrices must equal failed audit count")
    aggregate_fields = {
        "total_argument_cases": "argument_case_count",
        "total_boundary_pairs": "boundary_pair_count",
        "total_case_expectation_gaps": "case_expectation_gap_count",
        "total_cases": "case_count",
        "total_identity_gaps": "identity_gap_count",
        "total_instruction_variants": "instruction_variant_count",
        "total_profiles": "profile_count",
        "total_tools": "tool_count",
        "total_value_bar_gaps": "value_bar_gap_count",
        "total_value_bars": "value_bar_count",
    }
    for suite_field, audit_field in aggregate_fields.items():
        if suite_field not in summary:
            continue
        total = sum(
            int(audit.get("summary", {}).get(audit_field, 0))
            for audit in audits
            if isinstance(audit, dict) and isinstance(audit.get("summary"), dict)
        )
        if summary.get(suite_field) != total:
            failures.append(f"{rel}: summary.{suite_field} must equal audit {audit_field} sum")
    return failures


def _check_matrix_coverage_receipt(path: Path, payload: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    rel = path.relative_to(ROOT)
    if payload.get("passed") is not True:
        failures.append(f"{rel}: matrix-coverage receipt must pass")
    tools = _require_nonempty_list(rel, payload, "tools", failures)
    cases = _require_nonempty_list(rel, payload, "cases", failures)
    boundary_pairs = _require_nonempty_list(rel, payload, "boundary_pairs", failures)
    summary = _require_object(rel, payload, "summary", failures)
    if summary:
        _check_summary_count(rel, summary, "tool_count", tools, failures)
        _check_summary_count(rel, summary, "case_count", cases, failures)
        _check_summary_count(rel, summary, "boundary_pair_count", boundary_pairs, failures)
    uncovered = payload.get("uncovered")
    if isinstance(uncovered, dict):
        for name, entries in sorted(uncovered.items()):
            if entries:
                failures.append(f"{rel}: uncovered.{name} must be empty")
    else:
        failures.append(f"{rel}: uncovered must be an object")
    matrix_path = str(payload.get("matrix_path", "")).strip()
    if matrix_path:
        failures.extend(_check_local_ref(rel, matrix_path))
    else:
        failures.append(f"{rel}: matrix_path must be present")
    return failures


def _check_surface_snapshot_receipt(path: Path, payload: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    rel = path.relative_to(ROOT)
    if not str(payload.get("hash", "")).strip():
        failures.append(f"{rel}: hash must be present")
    if not str(payload.get("snapshot_version", "")).strip():
        failures.append(f"{rel}: snapshot_version must be present")
    items = _require_nonempty_list(rel, payload, "items", failures)
    for idx, item in enumerate(items):
        if not isinstance(item, dict):
            failures.append(f"{rel}: items[{idx}] must be an object")
            continue
        item_path = str(item.get("path", "")).strip()
        if not item_path:
            failures.append(f"{rel}: items[{idx}] missing path")
        else:
            failures.extend(_check_local_ref(rel, item_path))
        if not str(item.get("hash", "")).strip():
            failures.append(f"{rel}: items[{idx}] missing hash")
    return failures


def _check_surface_inventory_receipt(path: Path, payload: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    rel = path.relative_to(ROOT)
    _require_bool(rel, payload, "passed", failures)
    packages = _require_nonempty_list(rel, payload, "packages", failures)
    if not isinstance(payload.get("value_bar"), dict):
        failures.append(f"{rel}: value_bar must be an object")
    for idx, package in enumerate(packages):
        if not isinstance(package, dict):
            failures.append(f"{rel}: packages[{idx}] must be an object")
            continue
        if not str(package.get("package", package.get("module", ""))).strip():
            failures.append(f"{rel}: packages[{idx}] missing package or module")
        _require_bool(rel, package, "passed", failures, prefix=f"packages[{idx}]")
        checks = _require_nonempty_list(rel, package, "checks", failures, prefix=f"packages[{idx}]")
        for check_idx, check in enumerate(checks):
            if not isinstance(check, dict):
                failures.append(f"{rel}: packages[{idx}].checks[{check_idx}] must be an object")
                continue
            if not str(check.get("name", "")).strip():
                failures.append(f"{rel}: packages[{idx}].checks[{check_idx}] missing name")
            _require_bool(rel, check, "passed", failures, prefix=f"packages[{idx}].checks[{check_idx}]")
    return failures


def _check_live_harness_receipt(path: Path, payload: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    rel = path.relative_to(ROOT)
    _require_bool(rel, payload, "passed", failures)
    cells = _require_nonempty_list(rel, payload, "cells", failures)
    summary = _require_object(rel, payload, "summary", failures)
    source_spec = str(payload.get("source_spec", "")).strip()
    if source_spec:
        failures.extend(_check_local_ref(rel, source_spec))
    else:
        failures.append(f"{rel}: source_spec must be present")
    command = str(payload.get("command", "")).strip()
    if not command:
        failures.append(f"{rel}: command must be present")
        command_args = None
    else:
        failures.extend(_check_live_harness_receipt_command(rel, command, source_spec))
        command_args = _live_harness_command_args(command)
        if isinstance(command_args, list):
            command_args = None
    if summary and cells:
        counted = sum(
            int(summary.get(field, 0))
            for field in ("passed", "failed", "errors", "not_installed")
            if isinstance(summary.get(field, 0), int)
        )
        if counted != len(cells):
            failures.append(f"{rel}: summary cell counts must equal cells count")
    for idx, cell in enumerate(cells):
        if not isinstance(cell, dict):
            failures.append(f"{rel}: cells[{idx}] must be an object")
            continue
        for field in ("harness", "case", "status"):
            if not str(cell.get(field, "")).strip():
                failures.append(f"{rel}: cells[{idx}] missing {field}")
    if cells and source_spec and command_args is not None:
        failures.extend(_check_live_harness_receipt_cells(rel, cells, source_spec, command_args))
    return failures


def _check_live_harness_receipt_command(rel: Path, command: str, source_spec: str) -> list[str]:
    failures: list[str] = []
    args = _live_harness_command_args(command)
    if isinstance(args, list):
        return [f"{rel}: {failure}" for failure in args]
    command_spec = str(args.spec)
    if source_spec and command_spec != source_spec:
        failures.append(f"{rel}: command spec {command_spec!r} does not match source_spec {source_spec!r}")
    if command_spec and not (ROOT / command_spec).exists():
        failures.append(f"{rel}: command spec missing locally: {command_spec}")
    return failures


def _live_harness_command_args(command: str) -> Any | list[str]:
    try:
        tokens = shlex.split(command)
    except ValueError as exc:
        return [f"command is not shell-parseable: {exc}"]
    expected_prefix = ["python", "-m", "claude_agent_harness_opt", "live-harness"]
    if tokens[:4] != expected_prefix:
        return [f"command must start with {' '.join(expected_prefix)!r}"]
    parser = build_parser()
    try:
        with contextlib.redirect_stderr(io.StringIO()):
            return parser.parse_args(tokens[3:])
    except SystemExit as exc:
        return [f"command does not parse: exited with {exc.code}"]


def _check_live_harness_receipt_cells(
    rel: Path,
    cells: list[Any],
    source_spec: str,
    command_args: Any,
) -> list[str]:
    failures: list[str] = []
    spec_path = ROOT / source_spec
    try:
        spec = json.loads(spec_path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return failures
    if not isinstance(spec, dict):
        return failures
    cases = {
        str(case.get("name", "")).strip()
        for case in spec.get("cases", [])
        if isinstance(case, dict) and str(case.get("name", "")).strip()
    }
    harnesses = {
        str(harness.get("name", "")).strip()
        for harness in spec.get("harnesses", [])
        if isinstance(harness, dict) and str(harness.get("name", "")).strip()
    }
    selected_cases = _selected_live_harness_names(cases, getattr(command_args, "cases", None))
    selected_harnesses = _selected_live_harness_names(harnesses, getattr(command_args, "harnesses", None))
    for name in sorted(selected_cases - cases):
        failures.append(f"{rel}: command selects unknown live-harness case {name!r}")
    for name in sorted(selected_harnesses - harnesses):
        failures.append(f"{rel}: command selects unknown live-harness harness {name!r}")
    expected_pairs = {
        (harness, case)
        for harness in selected_harnesses & harnesses
        for case in selected_cases & cases
    }
    observed_pairs: set[tuple[str, str]] = set()
    for idx, cell in enumerate(cells):
        if not isinstance(cell, dict):
            continue
        pair = (str(cell.get("harness", "")).strip(), str(cell.get("case", "")).strip())
        if not pair[0] or not pair[1]:
            continue
        if pair in observed_pairs:
            failures.append(f"{rel}: duplicate live-harness result cell {pair[0]!r}/{pair[1]!r}")
        observed_pairs.add(pair)
        if expected_pairs and pair not in expected_pairs:
            failures.append(f"{rel}: cells[{idx}] unexpected live-harness cell {pair[0]!r}/{pair[1]!r}")
    for harness, case in sorted(expected_pairs - observed_pairs):
        failures.append(f"{rel}: missing live-harness result cell {harness!r}/{case!r}")
    return failures


def _selected_live_harness_names(available: set[str], selected: str | None) -> set[str]:
    if not selected:
        return set(available)
    return {item.strip() for item in selected.split(",") if item.strip()}


def _check_result_markdown(path: Path) -> list[str]:
    failures: list[str] = []
    rel = path.relative_to(ROOT)
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        return [f"{rel}: empty"]
    if not text.lstrip().startswith("# "):
        failures.append(f"{rel}: missing top-level title")
    if "Passed:" not in text:
        failures.append(f"{rel}: missing Passed summary")
    if not any(section in text for section in ("## Raw Matrix", "## Matrix Summary", "## Gaps", "## Tool Coverage")):
        failures.append(f"{rel}: missing review section")
    return failures


def _require_bool(
    rel: Path,
    payload: dict[str, Any],
    field: str,
    failures: list[str],
    *,
    prefix: str = "",
) -> bool:
    label = f"{prefix}.{field}" if prefix else field
    if not isinstance(payload.get(field), bool):
        failures.append(f"{rel}: {label} must be boolean")
        return False
    return True


def _require_object(
    rel: Path,
    payload: dict[str, Any],
    field: str,
    failures: list[str],
    *,
    prefix: str = "",
) -> dict[str, Any]:
    label = f"{prefix}.{field}" if prefix else field
    value = payload.get(field)
    if not isinstance(value, dict):
        failures.append(f"{rel}: {label} must be an object")
        return {}
    return value


def _require_nonempty_list(
    rel: Path,
    payload: dict[str, Any],
    field: str,
    failures: list[str],
    *,
    prefix: str = "",
) -> list[Any]:
    label = f"{prefix}.{field}" if prefix else field
    value = payload.get(field)
    if not isinstance(value, list) or not value:
        failures.append(f"{rel}: {label} must be a nonempty list")
        return []
    return value


def _check_summary_count(
    rel: Path,
    summary: dict[str, Any],
    field: str,
    items: list[Any],
    failures: list[str],
) -> None:
    if items and summary.get(field) != len(items):
        failures.append(f"{rel}: summary.{field} must equal {field.removesuffix('_count')} count")


def _read_required(path: Path, failures: list[str]) -> str:
    if not path.exists():
        failures.append(f"{path.relative_to(ROOT)}: missing")
        return ""
    return path.read_text(encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
