"""Create upstream-facing PR packets from harness results."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import shlex
from typing import Any

from .adapters import load_json


PROJECT_EVIDENCE_REPO = "https://github.com/cfregly/claude-agent-harness-opt"


@dataclass(frozen=True)
class PacketOptions:
    target_name: str
    target_repo: str = ""
    change_summary: str = ""
    baseline_variant: str = ""
    candidate_variant: str = ""
    evidence_url: str = ""
    minimum_delta: float = 0.01


def build_upstream_pr_packet(
    result_path: str | Path,
    *,
    matrix_path: str | Path | None = None,
    options: PacketOptions,
) -> dict[str, Any]:
    result = _load_object(result_path, "result")
    matrix = _load_object(matrix_path, "matrix") if matrix_path else {}
    source = _merged_source(result, matrix)
    comparison = _compare_variants(
        result,
        baseline_variant=options.baseline_variant,
        candidate_variant=options.candidate_variant,
        minimum_delta=options.minimum_delta,
    )
    cases = _case_definitions(result, matrix)
    repro = _reproduction_command(result, matrix_path, options)
    title = render_upstream_pr_title(
        result=result,
        comparison=comparison,
        options=options,
    )
    body = render_upstream_pr_body(
        result=result,
        source=source,
        comparison=comparison,
        cases=cases,
        repro_command=repro,
        options=options,
    )
    reproduction = render_reproduction_doc(
        result=result,
        source=source,
        comparison=comparison,
        cases=cases,
        repro_command=repro,
        options=options,
    )
    return {
        "case_count": len(cases),
        "comparison": comparison,
        "evidence": {
            "matrix_hash": _hash_json(matrix) if matrix else "",
            "result_hash": _hash_json(result),
            "source": source,
        },
        "files": {
            "PR_TITLE.txt": title + "\n",
            "PR_BODY.md": body,
            "REPRODUCTION.md": reproduction,
            "evidence.json": json.dumps(
                {
                    "cases": cases,
                    "comparison": comparison,
                    "matrix": matrix,
                    "result": result,
                    "source": source,
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
        },
        "passed": bool(comparison.get("promote")),
        "title": title,
        "target_name": options.target_name,
    }


def write_upstream_pr_packet(packet: dict[str, Any], out_dir: str | Path) -> dict[str, str]:
    path = Path(out_dir)
    path.mkdir(parents=True, exist_ok=True)
    written: dict[str, str] = {}
    files = packet.get("files", {})
    if not isinstance(files, dict):
        raise ValueError("packet.files must be an object")
    for name, content in files.items():
        out = path / str(name)
        out.write_text(str(content), encoding="utf-8")
        written[str(name)] = str(out)
    return written


def render_upstream_pr_title(
    *,
    result: dict[str, Any],
    comparison: dict[str, Any],
    options: PacketOptions,
) -> str:
    target = options.target_name or "tool catalog"
    focus = _focus_phrase(_failure_case_names(result, str(comparison.get("baseline_variant") or options.baseline_variant)))
    if focus:
        return f"Tighten {target} {focus} routing with live evals"
    if comparison.get("promote"):
        return f"Improve {target} tool routing with live eval evidence"
    return f"Add data-backed {target} tool-routing evidence"


def render_upstream_pr_body(
    *,
    result: dict[str, Any],
    source: dict[str, Any],
    comparison: dict[str, Any],
    cases: list[dict[str, Any]],
    repro_command: str,
    options: PacketOptions,
) -> str:
    target = options.target_name or "tool catalog"
    change = options.change_summary or "Clarify the tool-selection boundary shown by the eval."
    promote = "yes" if comparison.get("promote") else "no"
    lines = [
        f"Suggested title: {render_upstream_pr_title(result=result, comparison=comparison, options=options)}",
        "",
        "## Value Proposition",
        "",
    ]
    lines.extend(f"- {item}" for item in _value_proposition_lines(result, comparison, options))
    lines.extend([
        "",
        "## What Already Works",
        "",
    ])
    lines.extend(f"- {item}" for item in _what_already_works_lines(result, comparison, options))
    lines.extend([
        "",
        "## How This Is Proven Useful",
        "",
    ])
    lines.extend(f"- {item}" for item in _proof_lines(result, comparison, options))
    lines.extend([
        "",
        "## Current Frontier Coverage",
        "",
    ])
    lines.extend(f"- {item}" for item in _frontier_coverage_lines(result, comparison, options))
    lines.extend([
        "",
        "## Downside If Not Changed",
        "",
    ])
    lines.extend(f"- {item}" for item in _downside_lines(result, comparison, options))
    lines.extend([
        "",
        f"## Proposed change for {target}",
        "",
        change,
        "",
        "## Why",
        "",
        "This change is backed by a harness matrix result, not a prose-only review. The bar is adversarially-confirmed to add value.",
        "",
        "## Pinned surface",
        "",
    ])
    lines.extend(f"- {item}" for item in _source_lines(source))
    if options.target_repo:
        lines.append(f"- target repo: {options.target_repo}")
    lines.extend(
        [
            "",
            "## Result",
            "",
            f"- promoted by value bar: {promote}",
            f"- baseline variant: {comparison.get('baseline_variant', '')}",
            f"- candidate variant: {comparison.get('candidate_variant', '')}",
            f"- baseline score: {_format_score(comparison.get('baseline_score'))}",
            f"- candidate score: {_format_score(comparison.get('candidate_score'))}",
            f"- delta: {_format_score(comparison.get('delta'))}",
            f"- minimum delta: {_format_score(comparison.get('minimum_delta'))}",
            "",
            "## What We Learned",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in _learning_lines(result, comparison, options))
    lines.extend(
        [
            "",
            "## Run surfaces",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in _run_surface_lines(result))
    lines.extend(
        [
            "",
            "## Cell summary",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in _cell_summary_lines(result))
    lines.extend(
        [
            "",
            "## Reproduce",
            "",
            "```bash",
            repro_command,
            "```",
            "",
            "## Examples used",
            "",
        ]
    )
    lines.extend(_case_lines(cases))
    failures = _failure_lines(result, options.baseline_variant)
    passes = _passing_lines(result, options.candidate_variant)
    if failures:
        lines.extend(["", "## Baseline failures", ""])
        lines.extend(f"- {item}" for item in failures)
    if passes:
        lines.extend(["", "## Candidate passes", ""])
        lines.extend(f"- {item}" for item in passes)
    lines.extend(
        [
            "",
            "## Evidence",
            "",
            f"- public harness repo: {PROJECT_EVIDENCE_REPO}",
            "- `REPRODUCTION.md` contains the full local reproduction path.",
            "- `evidence.json` contains the matrix result, selected cases, comparison, and source pins.",
        ]
    )
    if options.evidence_url:
        lines.append(f"- reproducible result artifact: {options.evidence_url}")
    return "\n".join(lines).rstrip() + "\n"


def render_reproduction_doc(
    *,
    result: dict[str, Any],
    source: dict[str, Any],
    comparison: dict[str, Any],
    cases: list[dict[str, Any]],
    repro_command: str,
    options: PacketOptions,
) -> str:
    lines = [
        f"# Reproduction for {options.target_name}",
        "",
        "## Source Pin",
        "",
    ]
    lines.extend(f"- {item}" for item in _source_lines(source))
    lines.extend(
        [
            "",
            "## Command",
            "",
            "```bash",
            repro_command,
            "```",
            "",
            "## Value Bar",
            "",
            f"- baseline: {comparison.get('baseline_variant', '')} at {_format_score(comparison.get('baseline_score'))}",
            f"- candidate: {comparison.get('candidate_variant', '')} at {_format_score(comparison.get('candidate_score'))}",
            f"- delta: {_format_score(comparison.get('delta'))}",
            f"- minimum delta: {_format_score(comparison.get('minimum_delta'))}",
            f"- promote: {'yes' if comparison.get('promote') else 'no'}",
            "",
            "## Cases",
            "",
        ]
    )
    lines.extend(_case_lines(cases, include_task=True))
    summary = result.get("summary")
    if isinstance(summary, dict):
        lines.extend(
            [
                "",
                "## Summary Counts",
                "",
                f"- total: {summary.get('total')}",
                f"- passed cases: {summary.get('passed_cases')}",
                f"- failed cases: {summary.get('failed_cases')}",
                f"- errors: {summary.get('errors')}",
                f"- score: {summary.get('score')}",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def _load_object(path: str | Path | None, label: str) -> dict[str, Any]:
    if path is None:
        return {}
    value = load_json(path)
    if not isinstance(value, dict):
        raise ValueError(f"{label} JSON must be an object")
    return value


def _merged_source(result: dict[str, Any], matrix: dict[str, Any]) -> dict[str, Any]:
    source: dict[str, Any] = {}
    for item in (matrix.get("source"), result.get("source")):
        if isinstance(item, dict):
            source.update(item)
    return source


def _compare_variants(
    result: dict[str, Any],
    *,
    baseline_variant: str,
    candidate_variant: str,
    minimum_delta: float,
) -> dict[str, Any]:
    value_bar = result.get("value_bar")
    if isinstance(value_bar, dict):
        baseline_score = _score(value_bar.get("baseline"))
        candidate_score = _score(value_bar.get("candidate"))
    else:
        scores = _variant_scores(result)
        baseline_score = scores.get(baseline_variant)
        candidate_score = scores.get(candidate_variant)
    delta = (
        candidate_score - baseline_score
        if baseline_score is not None and candidate_score is not None
        else None
    )
    promote = bool(delta is not None and delta >= minimum_delta)
    return {
        "baseline_score": baseline_score,
        "baseline_variant": baseline_variant,
        "candidate_score": candidate_score,
        "candidate_variant": candidate_variant,
        "delta": delta,
        "minimum_delta": minimum_delta,
        "promote": promote,
    }


def _variant_scores(result: dict[str, Any]) -> dict[str, float]:
    cells = result.get("cells")
    if not isinstance(cells, list):
        return {}
    groups: dict[str, list[float]] = {}
    for cell in cells:
        if not isinstance(cell, dict):
            continue
        variant = str(cell.get("tool_variant", ""))
        if not variant or cell.get("score") is None:
            continue
        groups.setdefault(variant, []).append(float(cell["score"]))
    return {
        variant: sum(values) / len(values)
        for variant, values in groups.items()
        if values
    }


def _case_definitions(result: dict[str, Any], matrix: dict[str, Any]) -> list[dict[str, Any]]:
    cases = result.get("case_definitions")
    if isinstance(cases, list) and cases:
        return [case for case in cases if isinstance(case, dict)]
    matrix_cases = matrix.get("cases")
    if isinstance(matrix_cases, list):
        names = {
            str(item.get("case", ""))
            for item in result.get("results", [])
            if isinstance(item, dict) and item.get("case")
        }
        return [
            case
            for case in matrix_cases
            if isinstance(case, dict) and (not names or str(case.get("name", "")) in names)
        ]
    return []


def _reproduction_command(
    result: dict[str, Any],
    matrix_path: str | Path | None,
    options: PacketOptions,
) -> str:
    path = str(matrix_path or result.get("matrix_path") or "<matrix.json>")
    filters = result.get("filters") if isinstance(result.get("filters"), dict) else {}
    parts = [
        "python",
        "-m",
        "claude_agent_harness_opt",
        "model-matrix",
        path,
        "--env-file",
        ".env",
        "--live",
        "--require-live",
    ]
    for flag, key in (
        ("--providers", "providers"),
        ("--harnesses", "harnesses"),
        ("--instruction-variants", "instruction_variants"),
    ):
        values = filters.get(key)
        if isinstance(values, list) and values:
            parts.extend([flag, ",".join(str(item) for item in values)])
    case_values = filters.get("cases")
    if not case_values:
        case_values = [
            str(case.get("name", ""))
            for case in result.get("case_definitions", [])
            if isinstance(case, dict) and case.get("name")
        ]
    if isinstance(case_values, list) and case_values:
        parts.extend(["--cases", ",".join(str(item) for item in case_values)])
    variants = [item for item in (options.baseline_variant, options.candidate_variant) if item]
    if variants:
        parts.extend(["--variants", ",".join(variants)])
    if result.get("max_cases"):
        parts.extend(["--max-cases", str(result["max_cases"])])
    return " ".join(_shell_arg(part) for part in parts)


def _source_lines(source: dict[str, Any]) -> list[str]:
    if not source:
        return ["source: not provided"]
    labels = {
        "commit": "commit",
        "docs": "docs",
        "local_mcp_server": "local MCP server",
        "package": "package",
        "repo": "repo",
        "version": "version",
    }
    lines = []
    for key in sorted(source):
        label = labels.get(key, key.replace("_", " "))
        value = source[key]
        if isinstance(value, list):
            value = ", ".join(str(item) for item in value)
        lines.append(f"{label}: {value}")
    return lines


def _run_surface_lines(result: dict[str, Any]) -> list[str]:
    values = []
    seen: set[tuple[str, str, str, str, str, str]] = set()
    for item in result.get("results", []):
        if not isinstance(item, dict):
            continue
        key = (
            str(item.get("provider", "")),
            str(item.get("profile", "")),
            str(item.get("tier", "")),
            str(item.get("model", "")),
            str(item.get("harness", "")),
            str(item.get("instruction_variant", "")),
        )
        if key in seen:
            continue
        seen.add(key)
        provider, profile, tier, model, harness, instruction = key
        values.append(
            f"provider={provider}, profile={profile}, tier={tier}, model={model}, harness={harness}, instruction={instruction}"
        )
        if len(values) >= 12:
            break
    return values or ["run surface metadata not present"]


def _frontier_coverage_lines(
    result: dict[str, Any],
    comparison: dict[str, Any],
    options: PacketOptions,
) -> list[str]:
    frontier_cells = [
        cell
        for cell in result.get("cells", [])
        if isinstance(cell, dict) and _is_frontier_surface(cell)
    ]
    frontier_results = [
        item
        for item in result.get("results", [])
        if isinstance(item, dict) and _is_frontier_surface(item)
    ]
    if not frontier_cells and not frontier_results:
        return [
            "No current frontier profile metadata is present in this result.",
            "Treat this packet as historical or compatibility evidence until rerun on current latest/frontier models and harness versions.",
            "Older-model wins should not be the headline if the ambiguity is fixed by newer model or harness behavior.",
        ]

    lines = []
    baseline = str(comparison.get("baseline_variant") or options.baseline_variant or "baseline")
    candidate = str(comparison.get("candidate_variant") or options.candidate_variant or "candidate")
    scores = _variant_scores({"cells": frontier_cells})
    if baseline in scores and candidate in scores:
        delta = scores[candidate] - scores[baseline]
        lines.append(
            f"Frontier-only score moved from {_format_score(scores[baseline])} to {_format_score(scores[candidate])}, delta {_format_score(delta)}."
        )
    elif frontier_cells:
        lines.append(f"Frontier cells present: {len(frontier_cells)}.")
    if frontier_results:
        providers = sorted(
            {
                str(item.get("profile") or item.get("provider") or item.get("model"))
                for item in frontier_results
                if item.get("profile") or item.get("provider") or item.get("model")
            }
        )
        if providers:
            lines.append(f"Frontier profiles covered: {', '.join(providers[:8])}.")
    lines.append(
        "Use frontier cells for upstream-facing claims; keep high/balanced or older-model cells as regression coverage."
    )
    return lines


def _is_frontier_surface(item: dict[str, Any]) -> bool:
    tier = str(item.get("tier", "")).lower()
    profile = str(item.get("profile", "")).lower()
    if tier == "frontier" or "frontier" in profile:
        return True
    return False


def _cell_summary_lines(result: dict[str, Any]) -> list[str]:
    values = []
    for cell in result.get("cells", []):
        if not isinstance(cell, dict):
            continue
        values.append(
            "provider={provider}, harness={harness}, variant={variant}, instruction={instruction}, "
            "passed={passed}, failed={failed}, errors={errors}, score={score}".format(
                provider=cell.get("provider", ""),
                harness=cell.get("harness", ""),
                variant=cell.get("tool_variant", ""),
                instruction=cell.get("instruction_variant", ""),
                passed=cell.get("passed", ""),
                failed=cell.get("failed", ""),
                errors=cell.get("errors", ""),
                score=cell.get("score", ""),
            )
        )
        if len(values) >= 12:
            break
    return values or ["cell summary not present"]


def _case_lines(cases: list[dict[str, Any]], *, include_task: bool = False) -> list[str]:
    if not cases:
        return ["- no case definitions were embedded in the result"]
    lines = []
    for case in cases[:8]:
        name = str(case.get("name", "unnamed case"))
        expected = ",".join(str(item) for item in case.get("expected_tools", []))
        confusable = ",".join(str(item) for item in case.get("forbidden_tools", []))
        line = f"- {name}"
        if expected:
            line += f" | expected selection: {expected}"
        if confusable:
            line += f" | confusable alternatives checked: {confusable}"
        lines.append(line)
        if include_task and case.get("task"):
            lines.append(f"  - task: {case['task']}")
    return lines


def _failure_lines(result: dict[str, Any], variant: str) -> list[str]:
    return _status_lines(result, variant, "failed")


def _passing_lines(result: dict[str, Any], variant: str) -> list[str]:
    return _status_lines(result, variant, "passed")


def _status_lines(result: dict[str, Any], variant: str, status: str) -> list[str]:
    lines = []
    for item in result.get("results", []):
        if not isinstance(item, dict):
            continue
        if variant and item.get("tool_variant") != variant:
            continue
        if item.get("status") != status:
            continue
        chosen = ",".join(str(tool) for tool in item.get("chosen_tools", []))
        suffix = f" chose {chosen}" if chosen else ""
        lines.append(f"{item.get('case', 'unnamed case')}{suffix}")
        if len(lines) >= 8:
            break
    return lines


def _learning_lines(result: dict[str, Any], comparison: dict[str, Any], options: PacketOptions) -> list[str]:
    baseline = str(comparison.get("baseline_variant") or options.baseline_variant or "baseline")
    candidate = str(comparison.get("candidate_variant") or options.candidate_variant or "candidate")
    lines = [
        f"`{candidate}` beat `{baseline}` by {_format_score(comparison.get('delta'))} against a minimum delta of {_format_score(comparison.get('minimum_delta'))}.",
    ]
    failures = _failure_lines(result, baseline)
    cases = []
    seen: set[str] = set()
    for item in failures:
        case = item.split(" chose ", 1)[0]
        if case and case not in seen:
            seen.add(case)
            cases.append(case)
    if cases:
        lines.append(f"Baseline mistakes clustered on these cases: {', '.join(cases[:5])}.")
    if comparison.get("promote"):
        lines.append("The suggested change clears the adversarially-confirmed value bar for this pinned surface.")
    else:
        lines.append("The suggested change does not clear the value bar yet, so treat it as diagnostic evidence.")
    return lines


def _value_proposition_lines(result: dict[str, Any], comparison: dict[str, Any], options: PacketOptions) -> list[str]:
    target = options.target_name or "tool catalog"
    baseline = str(comparison.get("baseline_variant") or options.baseline_variant or "baseline")
    candidate = str(comparison.get("candidate_variant") or options.candidate_variant or "candidate")
    total = _summary_total(result)
    value = [
        f"Helps agents choose the intended {target} workflow instead of adjacent tools that look plausible.",
        f"`{candidate}` improved score from {_format_score(comparison.get('baseline_score'))} to {_format_score(comparison.get('candidate_score'))}, a {_format_score(comparison.get('delta'))} gain over `{baseline}`.",
    ]
    if total is not None:
        value.append(f"The signal comes from {total} live matrix cells on a pinned source surface.")
    cases = _failure_case_names(result, baseline)
    if cases:
        value.append(f"Baseline mistakes clustered on {', '.join(cases[:5])}.")
    if comparison.get("promote"):
        value.append("The change clears the adversarially-confirmed value bar for this pinned evaluation.")
    return value


def _what_already_works_lines(result: dict[str, Any], comparison: dict[str, Any], options: PacketOptions) -> list[str]:
    target = options.target_name or "tool catalog"
    counts = _summary_counts(result)
    lines = []
    if counts and counts["total"]:
        lines.append(
            f"The tested {target} surface is already strong: {counts['passed']}/{counts['total']} live cells passed with {counts['errors']} errors."
        )
    candidate_score = comparison.get("candidate_score")
    if isinstance(candidate_score, (float, int)):
        lines.append(f"The candidate score is {_format_score(candidate_score)}, so this is a boundary tightening, not a broad rewrite.")
    lines.append("The packet keeps passing behavior visible so maintainers can see what does not need to change.")
    return lines


def _proof_lines(result: dict[str, Any], comparison: dict[str, Any], options: PacketOptions) -> list[str]:
    baseline = str(comparison.get("baseline_variant") or options.baseline_variant or "baseline")
    candidate = str(comparison.get("candidate_variant") or options.candidate_variant or "candidate")
    lines = [
        f"The proof compares `{baseline}` and `{candidate}` on the same tasks, providers, harnesses, and instruction variants.",
        f"The measured delta is {_format_score(comparison.get('delta'))} against a required minimum of {_format_score(comparison.get('minimum_delta'))}.",
    ]
    counts = _summary_counts(result)
    if counts and counts["total"]:
        lines.append(f"The run contains {counts['total']} matrix cells, with {counts['failed']} failures preserved as evidence instead of hand-waved examples.")
    lines.append("The source pin, exact cases, reproduction command, and result artifact are included so the claim can be rerun or challenged.")
    return lines


def _downside_lines(result: dict[str, Any], comparison: dict[str, Any], options: PacketOptions) -> list[str]:
    baseline = str(comparison.get("baseline_variant") or options.baseline_variant or "baseline")
    cases = _failure_case_names(result, baseline)
    focus = _focus_phrase(cases)
    lines = [
        "Ambiguous descriptions let plausible adjacent tools win, so failures look reasonable in transcripts even when the selected workflow is wrong.",
        "Model or harness upgrades can reintroduce the same mistake unless the boundary is encoded in descriptions and regression cases.",
    ]
    if "browser" in focus:
        lines.append("Browser ambiguity can route a request to a broad compatibility alias instead of the purpose-built browser-testing workflow.")
    if "safety" in focus:
        lines.append("Safety ambiguity can escalate warning-only or directory-only requests into full guard mode, adding constraints the user did not ask for.")
    if "retrieval" in focus:
        lines.append("Routing ambiguity can make agents choose broader or higher-cost tool paths instead of the narrow workflow the user asked for.")
    if "database" in focus:
        lines.append("Database ambiguity can route schema-changing work through ordinary SQL instead of migration-safe workflows.")
    return lines


def _failure_case_names(result: dict[str, Any], variant: str) -> list[str]:
    cases = []
    seen: set[str] = set()
    for item in _failure_lines(result, variant):
        case = item.split(" chose ", 1)[0]
        if case and case not in seen:
            seen.add(case)
            cases.append(case)
    return cases


def _focus_phrase(cases: list[str]) -> str:
    joined = " ".join(cases).lower()
    labels = []
    if "browser" in joined or "browse" in joined:
        labels.append("browser")
    if "careful" in joined or "freeze" in joined or "guard" in joined or "safety" in joined:
        labels.append("safety")
    if "qa" in joined:
        labels.append("QA")
    if "design" in joined:
        labels.append("design")
    if "deploy" in joined or "ship" in joined or "canary" in joined:
        labels.append("deploy")
    if "scrape" in joined or "extract" in joined or "search" in joined or "fetch" in joined:
        labels.append("retrieval")
    if "sql" in joined or "migration" in joined or "database" in joined:
        labels.append("database")
    if not labels:
        return ""
    if len(labels) == 1:
        return labels[0]
    return " and ".join(labels[:2])


def _summary_total(result: dict[str, Any]) -> int | None:
    summary = result.get("summary")
    if isinstance(summary, dict) and isinstance(summary.get("total"), int):
        return int(summary["total"])
    return None


def _summary_counts(result: dict[str, Any]) -> dict[str, int] | None:
    summary = result.get("summary")
    if not isinstance(summary, dict):
        return None
    total = summary.get("total")
    if not isinstance(total, int):
        return None
    passed = summary.get("passed_cases", 0)
    failed = summary.get("failed_cases", 0)
    errors = summary.get("errors", 0)
    return {
        "errors": int(errors) if isinstance(errors, int) else 0,
        "failed": int(failed) if isinstance(failed, int) else 0,
        "passed": int(passed) if isinstance(passed, int) else 0,
        "total": total,
    }


def _score(value: Any) -> float | None:
    if isinstance(value, dict):
        if value.get("score") is not None:
            return float(value["score"])
        summary = value.get("summary")
        if isinstance(summary, dict) and summary.get("score") is not None:
            return float(summary["score"])
    if isinstance(value, (float, int)):
        return float(value)
    return None


def _format_score(value: Any) -> str:
    if value is None:
        return "n/a"
    return f"{float(value):.3f}"


def _hash_json(value: dict[str, Any]) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _shell_arg(value: Any) -> str:
    return shlex.quote(str(value))
