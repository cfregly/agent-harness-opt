#!/usr/bin/env python3
"""Validate shareable finding packets and local evidence links."""

from __future__ import annotations

import contextlib
from collections import Counter
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
        failures.extend(_check_model_matrix_summary(rel, summary, results))
        failures.extend(_check_model_matrix_passed(rel, payload, results))
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
            elif result.get("passed") is not (result.get("status") == "passed"):
                failures.append(f"{rel}: results[{idx}].passed must match status")
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


def _check_model_matrix_summary(
    rel: Path,
    summary: dict[str, Any],
    results: list[Any],
) -> list[str]:
    failures: list[str] = []
    statuses = _model_matrix_status_counts(results)
    expected_counts = {
        "errors": statuses["error"],
        "failed_cases": statuses["failed"],
        "passed_cases": statuses["passed"],
        "planned": len(results),
        "skipped": statuses["skipped"],
        "total": len(results),
    }
    for field, expected in expected_counts.items():
        value = summary.get(field)
        if field == "total" and (not isinstance(value, int) or value <= 0):
            failures.append(f"{rel}: summary.total must be a positive integer")
            continue
        if not isinstance(value, int):
            failures.append(f"{rel}: summary.{field} must be an integer")
            continue
        if value != expected:
            if field in {"planned", "total"}:
                failures.append(f"{rel}: summary.{field} must equal result count")
            else:
                failures.append(f"{rel}: summary.{field} must match result rows")
    expected_score = _raw_matrix_score(statuses, live=True)
    if "score" not in summary:
        failures.append(f"{rel}: summary.score must be present")
    else:
        try:
            value = float(summary["score"])
        except (TypeError, ValueError):
            failures.append(f"{rel}: summary.score must be numeric")
        else:
            if round(value, 3) != expected_score:
                failures.append(f"{rel}: summary.score must match result rows")
    return failures


def _check_model_matrix_passed(
    rel: Path,
    payload: dict[str, Any],
    results: list[Any],
) -> list[str]:
    expected = _model_matrix_passed_from_results(results)
    if expected is None:
        return []
    if payload.get("passed") is not expected:
        return [f"{rel}: passed must match result rows"]
    return []


def _model_matrix_status_counts(results: list[Any]) -> Counter[str]:
    return Counter(
        str(result.get("status", "")).casefold()
        for result in results
        if isinstance(result, dict)
    )


def _model_matrix_passed_from_results(results: list[Any]) -> bool | None:
    statuses = _model_matrix_status_counts(results)
    executed = statuses["passed"] + statuses["failed"] + statuses["error"]
    if executed == 0 or statuses["failed"] or statuses["error"]:
        return False
    if statuses["skipped"]:
        return None
    return True


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
    result_cell_summaries = _model_matrix_cell_summaries(results)
    cell_keys: set[tuple[str, str, str, str]] = set()
    for idx, cell in enumerate(cells):
        if not isinstance(cell, dict):
            continue
        provider = str(cell.get("provider", "")).strip()
        harness = str(cell.get("harness", "")).strip()
        tool_variant = str(cell.get("tool_variant", "")).strip()
        instruction_variant = str(cell.get("instruction_variant", "")).strip()
        cell_key = (provider, harness, tool_variant, instruction_variant)
        cell_keys.add(cell_key)
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
        expected_cell = result_cell_summaries.get(cell_key)
        if expected_cell is None:
            failures.append(f"{rel}: cells[{idx}] has no matching result rows")
        else:
            failures.extend(_check_model_matrix_cell_summary(rel, f"cells[{idx}]", cell, expected_cell))
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


def _model_matrix_cell_summaries(results: list[Any]) -> dict[tuple[str, str, str, str], dict[str, float | int]]:
    groups: dict[tuple[str, str, str, str], list[dict[str, Any]]] = {}
    for result in results:
        if not isinstance(result, dict):
            continue
        key = (
            str(result.get("provider", "")).strip(),
            str(result.get("harness", "")).strip(),
            str(result.get("tool_variant", "")).strip(),
            str(result.get("instruction_variant", "")).strip(),
        )
        groups.setdefault(key, []).append(result)
    summaries: dict[tuple[str, str, str, str], dict[str, float | int]] = {}
    for key, items in groups.items():
        passed = sum(1 for item in items if item.get("status") == "passed")
        failed = sum(1 for item in items if item.get("status") == "failed")
        errors = sum(1 for item in items if item.get("status") == "error")
        skipped = sum(1 for item in items if item.get("status") == "skipped")
        denominator = passed + failed + errors
        score = passed / denominator if denominator else 0.0
        summaries[key] = {
            "errors": errors,
            "failed": failed,
            "passed": passed,
            "score": round(score, 3),
            "skipped": skipped,
        }
    return summaries


def _check_model_matrix_cell_summary(
    rel: Path,
    label: str,
    cell: dict[str, Any],
    expected: dict[str, float | int],
) -> list[str]:
    failures: list[str] = []
    for field in ("passed", "failed", "errors"):
        if field not in cell:
            continue
        value = cell.get(field)
        if not isinstance(value, int):
            failures.append(f"{rel}: {label}.{field} must be an integer")
        elif value != expected[field]:
            failures.append(f"{rel}: {label}.{field} does not match result rows")
    if "skipped" in cell:
        value = cell.get("skipped")
        if not isinstance(value, int):
            failures.append(f"{rel}: {label}.skipped must be an integer")
        elif value != expected["skipped"]:
            failures.append(f"{rel}: {label}.skipped does not match result rows")
    if "score" in cell:
        try:
            value = round(float(cell["score"]), 3)
        except (TypeError, ValueError):
            failures.append(f"{rel}: {label}.score must be numeric")
        else:
            if value != expected["score"]:
                failures.append(f"{rel}: {label}.score does not match result rows")
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
        if tools and cases and boundary_pairs:
            failures.extend(
                _check_matrix_coverage_receipt_against_current_audit(
                    rel,
                    matrix_path,
                    tools,
                    cases,
                    boundary_pairs,
                    summary,
                )
            )
    else:
        failures.append(f"{rel}: matrix_path must be present")
    return failures


def _check_matrix_coverage_receipt_against_current_audit(
    rel: Path,
    matrix_path: str,
    tools: list[Any],
    cases: list[Any],
    boundary_pairs: list[Any],
    summary: dict[str, Any],
) -> list[str]:
    failures: list[str] = []
    try:
        audit = audit_matrix_coverage(ROOT / matrix_path)
    except (FileNotFoundError, json.JSONDecodeError):
        return failures
    for field, value in sorted(summary.items()):
        current = audit.get("summary", {}).get(field)
        if current is not None and current != value:
            failures.append(f"{rel}: summary.{field} does not match current matrix audit")
    current_tools = _named_items(audit.get("tools", []))
    receipt_tools = _named_items(tools)
    for name in sorted(receipt_tools - current_tools):
        failures.append(f"{rel}: coverage receipt has stale tool {name!r}")
    for name in sorted(current_tools - receipt_tools):
        failures.append(f"{rel}: coverage receipt missing current tool {name!r}")
    current_cases = _named_items(audit.get("cases", []))
    receipt_cases = _named_items(cases)
    for name in sorted(receipt_cases - current_cases):
        failures.append(f"{rel}: coverage receipt has stale case {name!r}")
    for name in sorted(current_cases - receipt_cases):
        failures.append(f"{rel}: coverage receipt missing current case {name!r}")
    current_pairs = _boundary_pair_keys(audit.get("boundary_pairs", []))
    receipt_pairs = _boundary_pair_keys(boundary_pairs)
    for key in sorted(receipt_pairs - current_pairs):
        failures.append(f"{rel}: coverage receipt has stale boundary pair {key!r}")
    for key in sorted(current_pairs - receipt_pairs):
        failures.append(f"{rel}: coverage receipt missing current boundary pair {key!r}")
    return failures


def _boundary_pair_keys(boundary_pairs: list[Any]) -> set[tuple[str, str, tuple[str, ...]]]:
    keys: set[tuple[str, str, tuple[str, ...]]] = set()
    for pair in boundary_pairs:
        if not isinstance(pair, dict):
            continue
        expected_tool = str(pair.get("expected_tool", "")).strip()
        forbidden_tool = str(pair.get("forbidden_tool", "")).strip()
        cases = tuple(sorted(str(case).strip() for case in pair.get("cases", []) if str(case).strip()))
        keys.add((expected_tool, forbidden_tool, cases))
    return keys


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
    if "## Results" in text:
        failures.extend(_check_model_matrix_markdown_result_rows(path, text))
    if "## Raw Matrix" in text and "## Results" in text:
        failures.extend(_check_raw_matrix_markdown_counts(path, text))
    if "## Cell Summary" in text and "## Results" in text:
        failures.extend(_check_model_matrix_markdown_cell_summary(path, text))
    if "## Optimization Gate" in text and "## Results" in text:
        failures.extend(_check_optimization_gate_markdown_counts(path, text))
    if "coverage" in path.stem:
        failures.extend(_check_coverage_markdown_json_pair(path, text))
    return failures


def _check_raw_matrix_markdown_counts(path: Path, text: str) -> list[str]:
    failures: list[str] = []
    rel = path.relative_to(ROOT)
    raw_text = _markdown_section_text(text, "Raw Matrix") or text
    rows = _markdown_results_rows(text)
    if not rows:
        return [f"{rel}: Results table has no result rows"]
    statuses = Counter(row[6].casefold() for row in rows if len(row) > 6)
    live = _markdown_summary_value(raw_text, "Live").casefold() == "yes"
    expected_counts = {
        "Planned": len(rows),
        "Passed cases": statuses["passed"],
        "Failed cases": statuses["failed"],
        "Errors": statuses["error"] + statuses["errored"],
        "Skipped": statuses["skipped"] + statuses["skip"],
    }
    for label, expected in expected_counts.items():
        value = _markdown_summary_value(raw_text, label)
        if not value:
            failures.append(f"{rel}: missing {label} summary")
            continue
        try:
            parsed = int(value)
        except ValueError:
            failures.append(f"{rel}: {label} summary is not an integer")
            continue
        if parsed != expected:
            failures.append(f"{rel}: {label} summary does not match Results table")
    value = _markdown_summary_value(raw_text, "Passed")
    expected_passed = _raw_matrix_passed(statuses, live=live)
    if not value:
        failures.append(f"{rel}: missing raw matrix Passed summary")
    elif value.casefold() not in {"yes", "no"}:
        failures.append(f"{rel}: raw matrix Passed summary must be yes or no")
    elif (value.casefold() == "yes") != expected_passed:
        failures.append(f"{rel}: raw matrix Passed summary does not match Results table")
    value = _markdown_summary_value(raw_text, "Score")
    expected_score = _raw_matrix_score(statuses, live=live)
    if not value:
        failures.append(f"{rel}: missing Score summary")
    else:
        try:
            parsed = float(value)
        except ValueError:
            failures.append(f"{rel}: Score summary is not numeric")
        else:
            if round(parsed, 3) != expected_score:
                failures.append(f"{rel}: Score summary does not match Results table")
    return failures


def _raw_matrix_passed(statuses: Counter[str], *, live: bool) -> bool:
    if not live:
        return sum(statuses.values()) > 0
    executed = statuses["passed"] + statuses["failed"] + statuses["error"] + statuses["errored"]
    return executed > 0 and statuses["failed"] == 0 and statuses["error"] == 0 and statuses["errored"] == 0


def _raw_matrix_score(statuses: Counter[str], *, live: bool) -> float:
    if not live:
        return 1.0 if statuses["planned"] else 0.0
    passed = statuses["passed"]
    denominator = passed + statuses["failed"] + statuses["error"] + statuses["errored"]
    return round(passed / denominator, 3) if denominator else 0.0


def _check_model_matrix_markdown_result_rows(path: Path, text: str) -> list[str]:
    failures: list[str] = []
    rel = path.relative_to(ROOT)
    rows = _markdown_results_rows(text)
    if not rows:
        return [f"{rel}: Results table has no result rows"]
    seen: set[tuple[str, str, str, str, str, str]] = set()
    allowed_statuses = {"planned", "passed", "failed", "error", "errored", "skipped", "skip"}
    for idx, row in enumerate(rows, start=1):
        if len(row) < 8:
            failures.append(f"{rel}: Results row {idx} has too few columns")
            continue
        for offset, field in (
            (0, "Provider"),
            (1, "Model"),
            (2, "Harness"),
            (3, "Tool Variant"),
            (4, "Instruction Variant"),
            (5, "Case"),
            (6, "Status"),
        ):
            if not row[offset].strip():
                failures.append(f"{rel}: Results row {idx} missing {field}")
        status = row[6].casefold()
        if status and status not in allowed_statuses:
            failures.append(f"{rel}: Results row {idx} unknown status {row[6]!r}")
        key = (row[0], row[1], row[2], row[3], row[4], row[5])
        if key in seen:
            failures.append(f"{rel}: duplicate Results row {_result_row_key_label(key)}")
        seen.add(key)
    return failures


def _result_row_key_label(key: tuple[str, str, str, str, str, str]) -> str:
    return f"{key[0]!r}/{key[1]!r}/{key[2]!r}/{key[3]!r}/{key[4]!r}/{key[5]!r}"


def _check_model_matrix_markdown_cell_summary(path: Path, text: str) -> list[str]:
    failures: list[str] = []
    rel = path.relative_to(ROOT)
    result_rows = _markdown_results_rows(text)
    if not result_rows:
        return [f"{rel}: Cell Summary has no result rows"]
    expected = _markdown_cell_summaries(result_rows)
    rows = _markdown_table_rows(_markdown_section_text(text, "Cell Summary"))
    if not rows:
        return [f"{rel}: Cell Summary table has no cell rows"]
    seen: set[tuple[str, str, str, str]] = set()
    for row in rows:
        if len(row) < 8:
            failures.append(f"{rel}: Cell Summary row has too few columns")
            continue
        key = tuple(row[:4])
        cell = expected.get(key)
        if cell is None:
            failures.append(f"{rel}: Cell Summary table has stale cell {_cell_key_label(key)}")
            continue
        if key in seen:
            failures.append(f"{rel}: Cell Summary table has duplicate cell {_cell_key_label(key)}")
        seen.add(key)
        for offset, field in ((4, "passed"), (5, "failed"), (6, "errors")):
            try:
                parsed = int(row[offset])
            except ValueError:
                failures.append(f"{rel}: Cell Summary {_cell_key_label(key)} {field} is not an integer")
                continue
            if parsed != cell[field]:
                failures.append(f"{rel}: Cell Summary {_cell_key_label(key)} {field} does not match Results table")
        score_offset = 7
        if len(row) >= 9:
            try:
                skipped = int(row[7])
            except ValueError:
                failures.append(f"{rel}: Cell Summary {_cell_key_label(key)} skipped is not an integer")
            else:
                if skipped != cell["skipped"]:
                    failures.append(f"{rel}: Cell Summary {_cell_key_label(key)} skipped does not match Results table")
            score_offset = 8
        try:
            score = float(row[score_offset])
        except ValueError:
            failures.append(f"{rel}: Cell Summary {_cell_key_label(key)} score is not numeric")
            continue
        if round(score, 3) != cell["score"]:
            failures.append(f"{rel}: Cell Summary {_cell_key_label(key)} score does not match Results table")
    for key in sorted(set(expected) - seen):
        failures.append(f"{rel}: Cell Summary table missing current cell {_cell_key_label(key)}")
    return failures


def _markdown_cell_summaries(rows: list[list[str]]) -> dict[tuple[str, str, str, str], dict[str, int | float]]:
    groups: dict[tuple[str, str, str, str], list[list[str]]] = {}
    for row in rows:
        if len(row) <= 6:
            continue
        key = (row[0], row[2], row[3], row[4])
        groups.setdefault(key, []).append(row)
    summaries: dict[tuple[str, str, str, str], dict[str, int | float]] = {}
    for key, items in groups.items():
        statuses = Counter(row[6].casefold() for row in items if len(row) > 6)
        passed = statuses["passed"]
        failed = statuses["failed"]
        errors = statuses["error"] + statuses["errored"]
        skipped = statuses["skipped"] + statuses["skip"]
        denominator = passed + failed + errors
        score = round(passed / denominator, 3) if denominator else 0.0
        summaries[key] = {
            "errors": errors,
            "failed": failed,
            "passed": passed,
            "score": score,
            "skipped": skipped,
        }
    return summaries


def _cell_key_label(key: tuple[str, str, str, str]) -> str:
    return f"{key[0]!r}/{key[1]!r}/{key[2]!r}/{key[3]!r}"


def _markdown_results_rows(text: str) -> list[list[str]]:
    in_results = False
    rows: list[list[str]] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped == "## Results":
            in_results = True
            continue
        if in_results and stripped.startswith("## "):
            break
        if not in_results or not stripped.startswith("|"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if not cells or cells[0] == "Provider" or set(cells[0]) <= {"-", ":"}:
            continue
        rows.append(cells)
    return rows


def _check_optimization_gate_markdown_counts(path: Path, text: str) -> list[str]:
    failures: list[str] = []
    rel = path.relative_to(ROOT)
    gate_text = _markdown_section_text(text, "Optimization Gate") or text
    raw_text = _markdown_section_text(text, "Raw Matrix") or text
    rows = _markdown_results_rows(text)
    if not rows:
        return [f"{rel}: Optimization Gate has no result rows"]
    variants = {row[3] for row in rows if len(row) > 6}
    baseline = _single_variant_name(_markdown_summary_value(gate_text, "Baseline variant"))
    optimized = _variant_names(_markdown_summary_value(gate_text, "Optimized variants"))
    if not baseline:
        failures.append(f"{rel}: missing Baseline variant summary")
    elif baseline not in variants:
        failures.append(f"{rel}: Baseline variant {baseline!r} is not present in Results table")
    if not optimized:
        failures.append(f"{rel}: missing Optimized variants summary")
    for variant in sorted(optimized - variants):
        failures.append(f"{rel}: Optimized variant {variant!r} is not present in Results table")
    expected_passed = _optimization_gate_passed(rows, optimized, _markdown_summary_value(raw_text, "Live"))
    value = _markdown_summary_value(gate_text, "Passed")
    if expected_passed is not None:
        if not value:
            failures.append(f"{rel}: missing Optimization Gate Passed summary")
        elif value.casefold() not in {"yes", "no"}:
            failures.append(f"{rel}: Optimization Gate Passed summary must be yes or no")
        elif (value.casefold() == "yes") != expected_passed:
            failures.append(f"{rel}: Optimization Gate Passed summary does not match Results table")
    expected_counts = {
        "Baseline failures": _variant_failure_count(rows, {baseline}) if baseline else None,
        "Optimized failures": _variant_failure_count(rows, optimized) if optimized else None,
    }
    for label, expected in expected_counts.items():
        if expected is None:
            continue
        value = _markdown_summary_value(gate_text, label)
        if not value:
            failures.append(f"{rel}: missing {label} summary")
            continue
        try:
            parsed = int(value)
        except ValueError:
            failures.append(f"{rel}: {label} summary is not an integer")
            continue
        if parsed != expected:
            failures.append(f"{rel}: {label} summary does not match Results table")
    optional_counts = {
        "Baseline errors": _variant_status_count(rows, {baseline}, {"error", "errored"}) if baseline else None,
        "Baseline skipped": _variant_status_count(rows, {baseline}, {"skipped", "skip"}) if baseline else None,
        "Optimized errors": _variant_status_count(rows, optimized, {"error", "errored"}) if optimized else None,
        "Optimized skipped": _variant_status_count(rows, optimized, {"skipped", "skip"}) if optimized else None,
    }
    for label, expected in optional_counts.items():
        if expected is None:
            continue
        value = _markdown_summary_value(gate_text, label)
        if not value:
            continue
        try:
            parsed = int(value)
        except ValueError:
            failures.append(f"{rel}: {label} summary is not an integer")
            continue
        if parsed != expected:
            failures.append(f"{rel}: {label} summary does not match Results table")
    expected_scores = {
        "Baseline score": _variant_score(rows, {baseline}) if baseline else None,
        "Optimized score": _variant_score(rows, optimized) if optimized else None,
    }
    for label, expected in expected_scores.items():
        if expected is None:
            continue
        value = _markdown_summary_value(gate_text, label)
        if not value:
            failures.append(f"{rel}: missing {label} summary")
            continue
        try:
            parsed = float(value)
        except ValueError:
            failures.append(f"{rel}: {label} summary is not numeric")
            continue
        if round(parsed, 3) != round(expected, 3):
            failures.append(f"{rel}: {label} summary does not match Results table")
    return failures


def _variant_failure_count(rows: list[list[str]], variants: set[str]) -> int:
    return _variant_status_count(rows, variants, {"failed"})


def _variant_score(rows: list[list[str]], variants: set[str]) -> float | None:
    selected = [row for row in rows if len(row) > 6 and row[3] in variants]
    if not selected:
        return None
    passed = _variant_status_count(rows, variants, {"passed"})
    denominator = passed + _variant_status_count(rows, variants, {"failed", "error", "errored"})
    return passed / denominator if denominator else 0.0


def _optimization_gate_passed(rows: list[list[str]], variants: set[str], live_value: str) -> bool | None:
    selected = [row for row in rows if len(row) > 6 and row[3] in variants]
    if not selected:
        return None
    failed = _variant_status_count(rows, variants, {"failed"})
    errors = _variant_status_count(rows, variants, {"error", "errored"})
    skipped = _variant_status_count(rows, variants, {"skipped", "skip"})
    planned = _variant_status_count(rows, variants, {"planned"})
    if failed or errors or skipped:
        return False
    if live_value.casefold() == "yes":
        return _variant_status_count(rows, variants, {"passed"}) > 0 and planned == 0
    return True


def _variant_status_count(rows: list[list[str]], variants: set[str], statuses: set[str]) -> int:
    return sum(
        1
        for row in rows
        if len(row) > 6 and row[3] in variants and row[6].casefold() in statuses
    )


def _single_variant_name(value: str) -> str:
    names = _variant_names(value)
    return sorted(names)[0] if len(names) == 1 else ""


def _variant_names(value: str) -> set[str]:
    code_spans = {name.strip() for name in re.findall(r"`([^`]+)`", value) if name.strip()}
    if code_spans:
        return code_spans
    cleaned = value.replace("`", "")
    return {name.strip() for name in cleaned.split(",") if name.strip()}


def _check_coverage_markdown_json_pair(path: Path, text: str) -> list[str]:
    failures: list[str] = []
    rel = path.relative_to(ROOT)
    json_path = path.with_suffix(".json")
    if not json_path.exists():
        failures.append(f"{rel}: coverage Markdown missing sibling JSON receipt {json_path.relative_to(ROOT)}")
        return failures
    try:
        payload = json.loads(json_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        failures.append(f"{rel}: sibling JSON receipt is invalid: {exc}")
        return failures
    if not isinstance(payload, dict):
        failures.append(f"{rel}: sibling JSON receipt must be an object")
        return failures
    expected_passed = "yes" if payload.get("passed") is True else "no" if payload.get("passed") is False else ""
    markdown_passed = _markdown_summary_value(text, "Passed")
    if expected_passed and markdown_passed and markdown_passed.casefold() != expected_passed:
        failures.append(f"{rel}: Passed summary does not match sibling JSON receipt")
    summary = payload.get("summary")
    if not isinstance(summary, dict):
        failures.append(f"{rel}: sibling JSON receipt missing summary object")
        return failures
    count_fields = {
        "Matrices": "matrix_count",
        "Passed matrices": "passed_matrices",
        "Failed matrices": "failed_matrices",
        "Total tools": "total_tools",
        "Total cases": "total_cases",
        "Total profiles": "total_profiles",
        "Total instruction variants": "total_instruction_variants",
        "Total argument cases": "total_argument_cases",
        "Total boundary pairs": "total_boundary_pairs",
        "Total case expectation gaps": "total_case_expectation_gaps",
        "Total identity gaps": "total_identity_gaps",
        "Total value bars": "total_value_bars",
        "Total value-bar gaps": "total_value_bar_gaps",
        "Tools": "tool_count",
        "Cases": "case_count",
        "Profiles": "profile_count",
        "Instruction variants": "instruction_variant_count",
        "Cases with argument checks": "argument_case_count",
        "Boundary pairs": "boundary_pair_count",
        "Cases with check_family": "case_count_with_check_family",
        "Case expectation gaps": "case_expectation_gap_count",
        "Identity gaps": "identity_gap_count",
        "Value bars": "value_bar_count",
        "Value-bar gaps": "value_bar_gap_count",
    }
    for label, field in count_fields.items():
        markdown_value = _markdown_summary_value(text, label)
        if not markdown_value or field not in summary:
            continue
        try:
            parsed = int(markdown_value)
        except ValueError:
            failures.append(f"{rel}: {label} summary is not an integer")
            continue
        if summary.get(field) != parsed:
            failures.append(f"{rel}: {label} summary does not match sibling JSON receipt")
    float_fields = {
        "Expected tool coverage": "tool_expected_coverage",
        "Forbidden tool coverage": "forbidden_tool_coverage",
        "Required check-family coverage": "required_check_family_coverage",
        "Variant surface parity": "variant_surface_parity",
    }
    for label, field in float_fields.items():
        markdown_value = _markdown_summary_value(text, label)
        if not markdown_value or field not in summary:
            continue
        try:
            parsed = float(markdown_value)
        except ValueError:
            failures.append(f"{rel}: {label} summary is not numeric")
            continue
        if round(float(summary.get(field, 0.0)), 3) != round(parsed, 3):
            failures.append(f"{rel}: {label} summary does not match sibling JSON receipt")
    failures.extend(_check_coverage_markdown_gaps(path, text, payload))
    failures.extend(_check_coverage_markdown_matrix_summary_table(path, text, payload))
    failures.extend(_check_coverage_markdown_tool_table(path, text, payload))
    failures.extend(_check_coverage_markdown_check_family_table(path, text, payload))
    return failures


def _markdown_summary_value(text: str, label: str) -> str:
    match = re.search(rf"^{re.escape(label)}:\s*(.+?)\s*$", text, flags=re.MULTILINE)
    return match.group(1).strip() if match else ""


def _markdown_section_text(text: str, title: str) -> str:
    in_section = False
    lines: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped == f"## {title}":
            in_section = True
            continue
        if in_section and stripped.startswith("## "):
            break
        if in_section:
            lines.append(line)
    return "\n".join(lines)


def _markdown_table_rows(section_text: str) -> list[list[str]]:
    rows: list[list[str]] = []
    for line in section_text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if not cells or set(cells[0]) <= {"-", ":"}:
            continue
        rows.append(cells)
    return rows[1:] if rows else []


def _check_coverage_markdown_gaps(
    path: Path,
    text: str,
    payload: dict[str, Any],
) -> list[str]:
    section_text = _markdown_section_text(text, "Gaps")
    if not section_text:
        return []
    failures: list[str] = []
    rel = path.relative_to(ROOT)
    uncovered = payload.get("uncovered")
    if not isinstance(uncovered, dict):
        return [f"{rel}: Gaps section present but sibling JSON receipt has no uncovered object"]
    label_map = {
        "Never expected": "never_expected",
        "Never forbidden": "never_forbidden",
        "Case expectation gaps": "case_expectation_gaps",
        "Expected without argument checks": "expected_without_argument_check",
        "Duplicate tool names": "duplicate_tool_names",
        "Identity gaps": "identity_gaps",
        "Missing quality checks": "missing_quality_checks",
        "Missing required check families": "missing_required_check_families",
        "Variant surface mismatches": "variant_surface_mismatches",
        "Source tool count mismatch": "source_tool_count_mismatch",
        "Cases without forbidden tools": "cases_without_forbidden",
        "Cases without check_family": "cases_without_check_family",
        "Unknown expected tools": "unknown_expected_tools",
        "Unknown forbidden tools": "unknown_forbidden_tools",
        "Value-bar gaps": "value_bar_gaps",
    }
    for line in section_text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("- ") or ":" not in stripped:
            continue
        label, value = stripped[2:].split(":", 1)
        key = label_map.get(label.strip())
        if not key:
            continue
        values = uncovered.get(key, [])
        expected = _coverage_gap_values(values) if isinstance(values, list) and values else "none"
        if value.strip() != expected:
            failures.append(f"{rel}: Gaps {label.strip()!r} does not match sibling JSON receipt")
    return failures


def _coverage_gap_values(values: list[Any]) -> str:
    rendered = []
    for value in values:
        if isinstance(value, dict):
            rendered.append(json.dumps(value, sort_keys=True))
        else:
            rendered.append(str(value))
    return ", ".join(rendered)


def _check_coverage_markdown_matrix_summary_table(
    path: Path,
    text: str,
    payload: dict[str, Any],
) -> list[str]:
    section_text = _markdown_section_text(text, "Matrix Summary")
    if not section_text:
        return []
    failures: list[str] = []
    rel = path.relative_to(ROOT)
    audits = payload.get("audits")
    if not isinstance(audits, list):
        return [f"{rel}: Matrix Summary table present but sibling JSON receipt has no audits list"]
    expected = {
        _coverage_audit_label(audit): audit
        for audit in audits
        if isinstance(audit, dict) and _coverage_audit_label(audit)
    }
    rows = _markdown_table_rows(section_text)
    if not rows:
        return [f"{rel}: Matrix Summary table has no matrix rows"]
    seen: set[str] = set()
    for row in rows:
        if len(row) < 11:
            failures.append(f"{rel}: Matrix Summary row has too few columns")
            continue
        label = row[0]
        audit = expected.get(label)
        if audit is None:
            failures.append(f"{rel}: Matrix Summary table has stale matrix {label!r}")
            continue
        seen.add(label)
        summary = audit.get("summary")
        if not isinstance(summary, dict):
            failures.append(f"{rel}: Matrix Summary {label!r} sibling audit missing summary")
            continue
        expected_passed = "yes" if audit.get("passed") is True else "no" if audit.get("passed") is False else ""
        if row[1].casefold() != expected_passed:
            failures.append(f"{rel}: Matrix Summary {label!r} Passed does not match sibling JSON receipt")
        int_fields = {
            "Tools": (2, "tool_count"),
            "Cases": (3, "case_count"),
            "Arg Cases": (6, "argument_case_count"),
            "Check Families": (7, "case_count_with_check_family"),
            "Boundary Pairs": (10, "boundary_pair_count"),
        }
        for column, (offset, field) in int_fields.items():
            if field not in summary:
                continue
            try:
                parsed = int(row[offset])
            except ValueError:
                failures.append(f"{rel}: Matrix Summary {label!r} {column} is not an integer")
                continue
            if parsed != summary[field]:
                failures.append(f"{rel}: Matrix Summary {label!r} {column} does not match sibling JSON receipt")
        float_fields = {
            "Expected": (4, "tool_expected_coverage"),
            "Forbidden": (5, "forbidden_tool_coverage"),
            "Required Families": (8, "required_check_family_coverage"),
            "Variant Parity": (9, "variant_surface_parity"),
        }
        for column, (offset, field) in float_fields.items():
            if field not in summary:
                continue
            try:
                parsed = float(row[offset])
            except ValueError:
                failures.append(f"{rel}: Matrix Summary {label!r} {column} is not numeric")
                continue
            if round(parsed, 3) != round(float(summary[field]), 3):
                failures.append(f"{rel}: Matrix Summary {label!r} {column} does not match sibling JSON receipt")
    for label in sorted(set(expected) - seen):
        failures.append(f"{rel}: Matrix Summary table missing current matrix {label!r}")
    return failures


def _coverage_audit_label(audit: dict[str, Any]) -> str:
    return str(audit.get("matrix") or audit.get("matrix_path") or "").strip()


def _check_coverage_markdown_tool_table(
    path: Path,
    text: str,
    payload: dict[str, Any],
) -> list[str]:
    section_text = _markdown_section_text(text, "Tool Coverage")
    if not section_text:
        return []
    failures: list[str] = []
    rel = path.relative_to(ROOT)
    tools = payload.get("tools")
    if not isinstance(tools, list):
        return [f"{rel}: Tool Coverage table present but sibling JSON receipt has no tools list"]
    expected = {
        str(tool.get("name", "")).strip(): tool
        for tool in tools
        if isinstance(tool, dict) and str(tool.get("name", "")).strip()
    }
    rows = _markdown_table_rows(section_text)
    if not rows:
        return [f"{rel}: Tool Coverage table has no tool rows"]
    seen: set[str] = set()
    for row in rows:
        if len(row) < 5:
            failures.append(f"{rel}: Tool Coverage row has too few columns")
            continue
        name = row[0]
        tool = expected.get(name)
        if tool is None:
            failures.append(f"{rel}: Tool Coverage table has stale tool {name!r}")
            continue
        seen.add(name)
        expected_counts = {
            "Expected Cases": len(tool.get("expected_cases", [])) if isinstance(tool.get("expected_cases"), list) else 0,
            "Forbidden Cases": len(tool.get("forbidden_cases", [])) if isinstance(tool.get("forbidden_cases"), list) else 0,
            "Argument Cases": len(tool.get("argument_cases", [])) if isinstance(tool.get("argument_cases"), list) else 0,
        }
        for offset, (label, expected_count) in enumerate(expected_counts.items(), start=1):
            try:
                parsed = int(row[offset])
            except ValueError:
                failures.append(f"{rel}: Tool Coverage {name!r} {label} is not an integer")
                continue
            if parsed != expected_count:
                failures.append(f"{rel}: Tool Coverage {name!r} {label} does not match sibling JSON receipt")
        expected_checks = "yes" if tool.get("has_quality_checks") is True else "no"
        if row[4].casefold() != expected_checks:
            failures.append(f"{rel}: Tool Coverage {name!r} Quality Checks does not match sibling JSON receipt")
    for name in sorted(set(expected) - seen):
        failures.append(f"{rel}: Tool Coverage table missing current tool {name!r}")
    return failures


def _check_coverage_markdown_check_family_table(
    path: Path,
    text: str,
    payload: dict[str, Any],
) -> list[str]:
    section_text = _markdown_section_text(text, "Check Families")
    if not section_text:
        return []
    failures: list[str] = []
    rel = path.relative_to(ROOT)
    check_families = payload.get("check_families")
    if not isinstance(check_families, dict):
        return [f"{rel}: Check Families table present but sibling JSON receipt has no check_families object"]
    expected = {
        str(family): len(names) if isinstance(names, list) else 0
        for family, names in check_families.items()
    }
    rows = _markdown_table_rows(section_text)
    if not rows:
        return [f"{rel}: Check Families table has no family rows"]
    seen: set[str] = set()
    for row in rows:
        if len(row) < 2:
            failures.append(f"{rel}: Check Families row has too few columns")
            continue
        family = row[0]
        if family not in expected:
            failures.append(f"{rel}: Check Families table has stale family {family!r}")
            continue
        seen.add(family)
        try:
            parsed = int(row[1])
        except ValueError:
            failures.append(f"{rel}: Check Families {family!r} count is not an integer")
            continue
        if parsed != expected[family]:
            failures.append(f"{rel}: Check Families {family!r} count does not match sibling JSON receipt")
    for family in sorted(set(expected) - seen):
        failures.append(f"{rel}: Check Families table missing current family {family!r}")
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
