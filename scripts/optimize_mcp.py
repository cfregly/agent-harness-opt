#!/usr/bin/env python3
"""Run the stored MCP optimization matrix for a known target."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import re
import sys
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from claude_agent_harness_opt.harness_optimizer import (  # noqa: E402
    HarnessGrindOptions,
    render_harness_grind_markdown,
    run_harness_grind,
)
from claude_agent_harness_opt.model_matrix import (  # noqa: E402
    MatrixFilters,
    render_model_matrix_markdown,
    run_model_matrix,
)


@dataclass(frozen=True)
class Target:
    inputs: tuple[str, ...]
    baseline_variant: str
    default_providers: str
    default_harnesses: str
    instruction_variants: str
    matrix: str
    optimized_variants: tuple[str, ...]
    variants: str


TARGETS = (
    Target(
        inputs=("screenpipe", "screenpipe/screenpipe", "https://github.com/screenpipe/screenpipe"),
        baseline_variant="readme_screenpipe_mcp",
        default_providers="anthropic",
        default_harnesses="prompt_json",
        instruction_variants="screenpipe_host_rules",
        matrix="evals/model_matrix/screenpipe_mcp_tool_selection.json",
        optimized_variants=("source_tuned_screenpipe_mcp",),
        variants="readme_screenpipe_mcp,source_tuned_screenpipe_mcp",
    ),
    Target(
        inputs=(
            "humwork",
            "humworkai/humwork-mcp",
            "https://github.com/humworkai/humwork-mcp",
        ),
        baseline_variant="readme_humwork_mcp",
        default_providers="anthropic",
        default_harnesses="prompt_json",
        instruction_variants="humwork_host_rules",
        matrix="evals/model_matrix/humwork_mcp_tool_selection.json",
        optimized_variants=("skill_tuned_humwork_mcp",),
        variants="readme_humwork_mcp,skill_tuned_humwork_mcp",
    ),
    Target(
        inputs=(
            "openwork",
            "openwork-ui",
            "different-ai/openwork",
            "https://github.com/different-ai/openwork",
        ),
        baseline_variant="docs_openwork_ui_mcp",
        default_providers="anthropic",
        default_harnesses="prompt_json",
        instruction_variants="openwork_ui_host_rules",
        matrix="evals/model_matrix/openwork_ui_mcp_tool_selection.json",
        optimized_variants=("source_tuned_openwork_ui_mcp",),
        variants="docs_openwork_ui_mcp,source_tuned_openwork_ui_mcp",
    ),
    Target(
        inputs=(
            "insforge",
            "insforge/insforge-mcp",
            "https://github.com/InsForge/insforge-mcp",
        ),
        baseline_variant="readme_insforge_mcp",
        default_providers="anthropic",
        default_harnesses="prompt_json",
        instruction_variants="insforge_host_rules",
        matrix="evals/model_matrix/insforge_mcp_tool_selection.json",
        optimized_variants=("source_tuned_insforge_mcp",),
        variants="readme_insforge_mcp,source_tuned_insforge_mcp",
    ),
    Target(
        inputs=("supabase", "supabase/mcp", "https://github.com/supabase/mcp"),
        baseline_variant="terse_supabase_database_mcp",
        default_providers="anthropic,openai,gemini",
        default_harnesses="prompt_json,native_tools",
        instruction_variants="supabase_database_host_rules",
        matrix="evals/model_matrix/supabase_mcp_database_tool_selection.json",
        optimized_variants=("tuned_supabase_database_boundaries",),
        variants="terse_supabase_database_mcp,tuned_supabase_database_boundaries",
    ),
    Target(
        inputs=("firecrawl", "firecrawl/firecrawl-mcp-server", "https://github.com/firecrawl/firecrawl-mcp-server"),
        baseline_variant="legacy_firecrawl_mcp",
        default_providers="anthropic,openai,gemini",
        default_harnesses="prompt_json,native_tools",
        instruction_variants="firecrawl_host_rules",
        matrix="evals/model_matrix/firecrawl_mcp_tool_selection.json",
        optimized_variants=("tuned_firecrawl_mcp_boundaries",),
        variants="legacy_firecrawl_mcp,tuned_firecrawl_mcp_boundaries",
    ),
    Target(
        inputs=("zymtrace", "zymtrace-mcp"),
        baseline_variant="stock_zymtrace_mcp",
        default_providers="anthropic,openai,gemini",
        default_harnesses="prompt_json",
        instruction_variants="zymtrace_host_and_skill_rules",
        matrix="evals/model_matrix/zymtrace_mcp_tool_selection.json",
        optimized_variants=("tuned_zymtrace_mcp_boundaries",),
        variants="stock_zymtrace_mcp,tuned_zymtrace_mcp_boundaries",
    ),
    Target(
        inputs=("clickhouse", "clickhouse/mcp-clickhouse", "https://github.com/clickhouse/mcp-clickhouse"),
        baseline_variant="stock_clickhouse_mcp",
        default_providers="anthropic,openai,gemini",
        default_harnesses="prompt_json",
        instruction_variants="clickhouse_host_rules",
        matrix="evals/model_matrix/clickhouse_mcp_tool_selection.json",
        optimized_variants=("tuned_clickhouse_readonly_boundaries",),
        variants="stock_clickhouse_mcp,tuned_clickhouse_readonly_boundaries",
    ),
    Target(
        inputs=("github", "github/github-mcp-server", "https://github.com/github/github-mcp-server"),
        baseline_variant="stock_github_mcp",
        default_providers="anthropic",
        default_harnesses="prompt_json",
        instruction_variants="github_mcp_host_rules",
        matrix="evals/model_matrix/github_mcp_tool_selection.json",
        optimized_variants=("tuned_github_mcp_boundaries",),
        variants="stock_github_mcp,tuned_github_mcp_boundaries",
    ),
    Target(
        inputs=("context7", "upstash/context7", "https://github.com/upstash/context7"),
        baseline_variant="readme_context7_mcp",
        default_providers="anthropic,openai,gemini",
        default_harnesses="prompt_json,native_tools",
        instruction_variants="context7_host_rules",
        matrix="evals/model_matrix/context7_mcp_tool_selection.json",
        optimized_variants=("tuned_context7_mcp_boundaries",),
        variants="readme_context7_mcp,tuned_context7_mcp_boundaries",
    ),
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", help="known MCP name, repo URL, or path to a matrix JSON file")
    parser.add_argument("--cases", help="comma-separated case names")
    parser.add_argument("--concurrency", type=int, default=1)
    parser.add_argument("--env-file", type=Path, help="dotenv file with provider API keys")
    parser.add_argument("--grind", action="store_true", help="run grind-harness instead of the stored baseline/candidate comparison")
    parser.add_argument("--harnesses", help="comma-separated harness names")
    parser.add_argument("--instruction-variants", help="comma-separated instruction variant names")
    parser.add_argument("--live", action="store_true", help="call provider APIs")
    parser.add_argument("--markdown", action="store_true", help="write Markdown instead of JSON")
    parser.add_argument("--max-cases", type=int)
    parser.add_argument("--out", type=Path, help="write report to this path")
    parser.add_argument("--providers", help="comma-separated provider or profile names")
    parser.add_argument("--require-live", action="store_true", help="fail if live calls cannot run")
    parser.add_argument("--variants", help="comma-separated tool variant names")
    args = parser.parse_args(argv)

    try:
        target = resolve_target(args.target)
    except ValueError as exc:
        parser.error(str(exc))

    providers = args.providers or target.default_providers
    harnesses = args.harnesses or target.default_harnesses
    variants = args.variants or target.variants
    instruction_variants = args.instruction_variants or target.instruction_variants
    filters = MatrixFilters(
        cases=_csv_set(args.cases),
        harnesses=_csv_set(harnesses),
        instruction_variants=_csv_set(instruction_variants),
        providers=_csv_set(providers),
        variants={target.baseline_variant} if args.grind else _csv_set(variants),
    )

    if args.grind:
        if not target.baseline_variant:
            parser.error("--grind requires a known MCP target, not a raw matrix path")
        result = run_harness_grind(
            ROOT / target.matrix,
            HarnessGrindOptions(
                baseline_variant=target.baseline_variant,
                concurrency=args.concurrency,
                env_file=args.env_file,
                filters=filters,
                live=args.live,
                max_cases=args.max_cases,
                require_live=args.require_live,
            ),
        )
        output = render_harness_grind_markdown(result) if args.markdown else _json(result)
        passed = result.get("passed", False)
    else:
        result = run_model_matrix(
            ROOT / target.matrix,
            live=args.live,
            env_file=args.env_file,
            require_live=args.require_live,
            filters=filters,
            max_cases=args.max_cases,
            concurrency=args.concurrency,
        )
        gate = optimization_gate(result, target, _csv_set(variants) or set())
        if gate:
            result["optimization_gate"] = gate
        output = render_model_matrix_markdown(result) if args.markdown else _json(result)
        if args.markdown and gate:
            output = add_optimization_gate_to_markdown(output, gate)
        passed = gate["passed"] if gate else result["passed"]

    out_path = args.out or default_out_path(args.target, markdown=args.markdown)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(output if output.endswith("\n") else output + "\n", encoding="utf-8")
    print(f"wrote {out_path}")
    if args.markdown:
        print(output, end="" if output.endswith("\n") else "\n")
    return 0 if passed else 1


def resolve_target(raw: str) -> Target:
    path = Path(raw)
    candidate_path = path if path.is_absolute() else ROOT / path
    if candidate_path.exists():
        return Target(
            inputs=(raw,),
            baseline_variant="",
            default_providers="anthropic",
            default_harnesses="prompt_json",
            instruction_variants="",
            matrix=str(
                candidate_path.relative_to(ROOT)
                if candidate_path.is_relative_to(ROOT)
                else candidate_path
            ),
            optimized_variants=(),
            variants="",
        )
    normalized = _normalize_target(raw)
    for target in TARGETS:
        for selector in target.inputs:
            if normalized == _normalize_target(selector):
                return target
    known = ", ".join(target.inputs[0] for target in TARGETS)
    raise ValueError(
        f"unknown MCP target {raw!r}. Use one of: {known}. Or pass a path to an existing matrix JSON."
    )


def default_out_path(target: str, *, markdown: bool) -> Path:
    suffix = ".md" if markdown else ".json"
    slug = re.sub(r"[^a-zA-Z0-9._-]+", "-", target.strip().rstrip("/").removesuffix(".git")).strip("-")
    return Path("/tmp") / f"{slug or 'mcp'}-optimization{suffix}"


def _csv_set(value: str | None) -> set[str] | None:
    if not value:
        return None
    return {item.strip() for item in value.split(",") if item.strip()}


def optimization_gate(
    result: dict[str, object],
    target: Target,
    selected_variants: set[str],
) -> dict[str, object] | None:
    if not target.optimized_variants:
        return None
    optimized = set(target.optimized_variants) & selected_variants
    if not optimized:
        return None
    cells = result.get("cells", [])
    if not isinstance(cells, list):
        return None
    optimized_cells = [
        cell for cell in cells if isinstance(cell, dict) and cell.get("tool_variant") in optimized
    ]
    if not optimized_cells:
        return None
    optimized_failed = sum(int(cell.get("failed", 0)) for cell in optimized_cells)
    optimized_errors = sum(int(cell.get("errors", 0)) for cell in optimized_cells)
    optimized_provider_blocked = sum(int(cell.get("provider_blocked", 0)) for cell in optimized_cells)
    optimized_skipped = sum(int(cell.get("skipped", 0)) for cell in optimized_cells)
    live = bool(result.get("live"))
    passed = (
        optimized_failed == 0
        and optimized_errors == 0
        and optimized_provider_blocked == 0
        and optimized_skipped == 0
    )
    if live:
        passed = passed and sum(int(cell.get("passed", 0)) for cell in optimized_cells) > 0

    baseline_cells = [
        cell
        for cell in cells
        if isinstance(cell, dict) and cell.get("tool_variant") == target.baseline_variant
    ]
    baseline_failed = sum(int(cell.get("failed", 0)) for cell in baseline_cells)
    baseline_errors = sum(int(cell.get("errors", 0)) for cell in baseline_cells)
    baseline_provider_blocked = sum(int(cell.get("provider_blocked", 0)) for cell in baseline_cells)
    baseline_skipped = sum(int(cell.get("skipped", 0)) for cell in baseline_cells)
    return {
        "baseline_errors": baseline_errors,
        "baseline_failed": baseline_failed,
        "baseline_provider_blocked": baseline_provider_blocked,
        "baseline_score": _average_score(baseline_cells),
        "baseline_skipped": baseline_skipped,
        "baseline_variant": target.baseline_variant,
        "optimized_errors": optimized_errors,
        "optimized_failed": optimized_failed,
        "optimized_provider_blocked": optimized_provider_blocked,
        "optimized_score": _average_score(optimized_cells),
        "optimized_skipped": optimized_skipped,
        "optimized_variants": sorted(optimized),
        "passed": passed,
        "reason": (
            "optimized variants passed every selected cell"
            if passed
            else "at least one optimized variant cell failed, errored, provider-blocked, or skipped"
        ),
    }


def render_optimization_gate_markdown(gate: dict[str, object]) -> str:
    variants = ", ".join(f"`{item}`" for item in gate["optimized_variants"])
    return "\n".join(
        [
            "",
            "## Optimization Gate",
            "",
            f"Passed: {'yes' if gate['passed'] else 'no'}",
            f"Optimized variants: {variants}",
            f"Baseline variant: `{gate['baseline_variant']}`",
            f"Baseline score: {gate['baseline_score']:.3f}",
            f"Optimized score: {gate['optimized_score']:.3f}",
            f"Baseline failures: {gate['baseline_failed']}",
            f"Baseline errors: {gate['baseline_errors']}",
            f"Baseline provider blocked: {gate['baseline_provider_blocked']}",
            f"Baseline skipped: {gate['baseline_skipped']}",
            f"Optimized failures: {gate['optimized_failed']}",
            f"Optimized errors: {gate['optimized_errors']}",
            f"Optimized provider blocked: {gate['optimized_provider_blocked']}",
            f"Optimized skipped: {gate['optimized_skipped']}",
            "",
            str(gate["reason"]),
            "",
        ]
    )


def add_optimization_gate_to_markdown(output: str, gate: dict[str, object]) -> str:
    section = render_optimization_gate_markdown(gate).strip()
    marker = "\nLive: "
    if marker not in output:
        return f"{section}\n\n{output}"
    return output.replace(marker, f"\n\n{section}\n\n## Raw Matrix\n{marker}", 1)


def _average_score(cells: list[dict[str, object]]) -> float:
    if not cells:
        return 0.0
    return round(sum(float(cell.get("score", 0.0)) for cell in cells) / len(cells), 3)


def _normalize_target(raw: str) -> str:
    value = raw.strip().rstrip("/").removesuffix(".git").lower()
    parsed = urlparse(value)
    if parsed.scheme and parsed.netloc:
        path = parsed.path.strip("/")
        return f"{parsed.netloc}/{path}".rstrip("/")
    return value


def _json(data: object) -> str:
    import json

    return json.dumps(data, indent=2, sort_keys=True)


if __name__ == "__main__":
    raise SystemExit(main())
