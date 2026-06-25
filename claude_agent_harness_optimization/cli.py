"""Command line interface for the prompt kit."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from .adapters import claude_messages_to_trace, load_json, runtime_events_to_trace, supported_adapters
from .agent_audit import (
    render_agent_audit_markdown,
    review_agent_bundle,
)
from .claude_judge import (
    ClaudeJudgeError,
    judge_tool_selection_with_claude,
    judge_trace_with_claude,
)
from .evals import build_judge_prompt, evaluate_case, load_eval_case
from .e2e import E2EError, run_e2e_spec
from .import_run import import_run_export
from .model_matrix import (
    MatrixFilters,
    render_model_matrix_markdown,
    run_model_matrix,
)
from .harness_optimizer import (
    HarnessGrindOptions,
    render_harness_grind_markdown,
    run_harness_grind,
)
from .prompt_builder import lint_tools, load_recipe, render_prompt
from .reports import load_report_input, render_html_report, render_pr_comment, write_report
from .snapshots import build_surface_snapshot, write_surface_snapshot
from .suitability import score_use_case
from .tool_selection import render_tool_selection_markdown, review_tool_selection_bundle
from .trace_suite import render_suite_markdown, run_trace_suite
from .trace_review import build_trace_judge_prompt, load_trace, review_trace


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="claude-agent-harness-optimization")
    subparsers = parser.add_subparsers(dest="command", required=True)

    render_parser = subparsers.add_parser("render", help="render a system prompt from a recipe")
    render_parser.add_argument("recipe", type=Path)

    score_parser = subparsers.add_parser("score", help="score whether a recipe fits an agent loop")
    score_parser.add_argument("recipe", type=Path)

    lint_parser = subparsers.add_parser("lint-tools", help="lint tool names and descriptions")
    lint_parser.add_argument("recipe", type=Path)

    eval_parser = subparsers.add_parser("eval", help="run an offline eval case")
    eval_parser.add_argument("case", type=Path)

    judge_parser = subparsers.add_parser("judge-prompt", help="render an LLM judge prompt")
    judge_parser.add_argument("case", type=Path)

    trace_parser = subparsers.add_parser("review-trace", help="review an ordered agent trace")
    trace_parser.add_argument("trace", type=Path)
    trace_parser.add_argument(
        "--claude-judge",
        action="store_true",
        help="call Claude to semantically judge reasoning, tool outputs, and final grounding",
    )
    trace_parser.add_argument(
        "--model",
        help="Claude model for --claude-judge, default from CLAUDE_JUDGE_MODEL or claude-sonnet-4-5",
    )

    trace_judge_parser = subparsers.add_parser(
        "trace-judge-prompt",
        help="render an LLM judge prompt for an ordered agent trace",
    )
    trace_judge_parser.add_argument("trace", type=Path)

    normalize_parser = subparsers.add_parser(
        "normalize-claude",
        help="normalize Claude Messages API blocks into an agent trace",
    )
    normalize_parser.add_argument("messages", type=Path)

    normalize_runtime_parser = subparsers.add_parser(
        "normalize-runtime",
        help="normalize generic Agent SDK or IDE-agent events into an agent trace",
    )
    normalize_runtime_parser.add_argument("events", type=Path)

    import_parser = subparsers.add_parser(
        "import-run",
        help="import a harness export into the shared trace and audit-bundle contract",
    )
    import_parser.add_argument("run", type=Path)
    import_parser.add_argument("--adapter", choices=supported_adapters(), default="auto")
    import_parser.add_argument("--name", help="override imported run name")
    import_parser.add_argument("--out-dir", type=Path, help="directory for generated files")
    import_parser.add_argument("--task", help="override trace task")
    import_parser.add_argument("--tools", type=Path, help="JSON tool inventory to include")
    import_parser.add_argument("--value-bar", type=Path, help="JSON value_bar proof to include")

    snapshot_parser = subparsers.add_parser(
        "snapshot-surface",
        help="snapshot matrices, bundles, skills, and files under eval",
    )
    snapshot_parser.add_argument("--matrix", action="append", type=Path, default=[])
    snapshot_parser.add_argument("--bundle", action="append", type=Path, default=[])
    snapshot_parser.add_argument("--skill", action="append", type=Path, default=[])
    snapshot_parser.add_argument("--file", action="append", type=Path, default=[])
    snapshot_parser.add_argument("--out", type=Path, help="write snapshot JSON to a file")

    e2e_parser = subparsers.add_parser(
        "mcp-e2e",
        help="run read-oriented credentialed harness checks from a JSON spec",
    )
    e2e_parser.add_argument("spec", type=Path)
    e2e_parser.add_argument("--env-file", type=Path, help="dotenv file with service keys")
    e2e_parser.add_argument("--allow-mutation", action="store_true", help="allow mutation checks")
    e2e_parser.add_argument("--dry-run", action="store_true", help="validate without live calls")
    e2e_parser.add_argument("--out", type=Path, help="write JSON result to a file")

    report_parser = subparsers.add_parser("render-report", help="render JSON result as static HTML")
    report_parser.add_argument("result", type=Path)
    report_parser.add_argument("--title", default="Harness Report")
    report_parser.add_argument("--out", type=Path, help="write HTML report to a file")

    pr_parser = subparsers.add_parser("pr-comment", help="render JSON result as a PR comment")
    pr_parser.add_argument("result", type=Path)
    pr_parser.add_argument("--title", default="Harness Report")
    pr_parser.add_argument("--out", type=Path, help="write Markdown comment to a file")

    suite_parser = subparsers.add_parser("trace-suite", help="run a trace regression suite")
    suite_parser.add_argument("suite", type=Path)
    suite_parser.add_argument("--markdown", action="store_true", help="print a Markdown report")

    audit_parser = subparsers.add_parser(
        "audit-agent",
        help="review tools, traces, and adversarial value-bar proof",
    )
    audit_parser.add_argument("bundle", type=Path)
    audit_parser.add_argument("--markdown", action="store_true", help="print a Markdown report")
    audit_parser.add_argument(
        "--claude-judge",
        action="store_true",
        help="call Claude to semantically judge each representative trace",
    )
    audit_parser.add_argument(
        "--model",
        help="Claude model for --claude-judge, default from CLAUDE_JUDGE_MODEL or claude-sonnet-4-5",
    )

    optimize_parser = subparsers.add_parser(
        "optimize-tools",
        help="review tool descriptions, schemas, selection cases, and trace selection failures",
    )
    optimize_parser.add_argument("bundle", type=Path)
    optimize_parser.add_argument("--markdown", action="store_true", help="print a Markdown report")
    optimize_parser.add_argument(
        "--claude-judge",
        action="store_true",
        help="call Claude to semantically judge tool descriptions and selection cases",
    )
    optimize_parser.add_argument(
        "--model",
        help="Claude model for --claude-judge, default from CLAUDE_JUDGE_MODEL or claude-sonnet-4-5",
    )

    matrix_parser = subparsers.add_parser(
        "model-matrix",
        help="run tool-selection evals across model, harness, prompt, and tool variants",
    )
    matrix_parser.add_argument("matrix", type=Path)
    matrix_parser.add_argument("--env-file", type=Path, help="dotenv file with provider API keys")
    matrix_parser.add_argument("--live", action="store_true", help="call provider APIs")
    matrix_parser.add_argument(
        "--require-live",
        action="store_true",
        help="fail if any selected provider is missing a key or returns an error",
    )
    matrix_parser.add_argument("--providers", help="comma-separated provider or profile names")
    matrix_parser.add_argument("--harnesses", help="comma-separated harness names")
    matrix_parser.add_argument("--variants", help="comma-separated tool variant names")
    matrix_parser.add_argument(
        "--instruction-variants",
        help="comma-separated instruction variant names",
    )
    matrix_parser.add_argument("--cases", help="comma-separated case names")
    matrix_parser.add_argument("--max-cases", type=int, help="limit cases per selected cell")
    matrix_parser.add_argument(
        "--concurrency",
        type=int,
        default=1,
        help="parallel provider calls for live runs",
    )
    matrix_parser.add_argument("--markdown", action="store_true", help="print a Markdown report")
    matrix_parser.add_argument("--out", type=Path, help="write the JSON or Markdown report to a file")

    grind_parser = subparsers.add_parser(
        "grind-harness",
        help="hill-climb tool and harness descriptions from model-matrix failures",
    )
    grind_parser.add_argument("matrix", type=Path)
    grind_parser.add_argument("--env-file", type=Path, help="dotenv file with provider API keys")
    grind_parser.add_argument("--live", action="store_true", help="call provider APIs")
    grind_parser.add_argument(
        "--require-live",
        action="store_true",
        help="fail if a selected provider is missing a key or returns an error",
    )
    grind_parser.add_argument("--baseline-variant", default="baseline_short")
    grind_parser.add_argument("--providers", help="comma-separated provider or profile names")
    grind_parser.add_argument("--harnesses", help="comma-separated harness names")
    grind_parser.add_argument(
        "--heldout-cases",
        help="comma-separated cases used only to confirm the promoted candidate does not regress",
    )
    grind_parser.add_argument("--instruction-variants", help="comma-separated instruction variant names")
    grind_parser.add_argument("--cases", help="comma-separated case names")
    grind_parser.add_argument("--max-cases", type=int, help="limit cases per selected cell")
    grind_parser.add_argument("--max-iterations", type=int, default=1)
    grind_parser.add_argument("--max-live-calls", type=int, default=60)
    grind_parser.add_argument(
        "--min-improvement",
        type=float,
        default=0.01,
        help="minimum live score improvement required for promotion",
    )
    grind_parser.add_argument("--concurrency", type=int, default=1)
    grind_parser.add_argument("--markdown", action="store_true", help="print a Markdown report")
    grind_parser.add_argument("--out", type=Path, help="write the JSON or Markdown report to a file")

    args = parser.parse_args(argv)

    if args.command == "render":
        recipe = load_recipe(args.recipe)
        sys.stdout.write(render_prompt(recipe))
        return 0

    if args.command == "score":
        recipe = load_recipe(args.recipe)
        print(json.dumps(score_use_case(recipe.get("use_case", {})), indent=2, sort_keys=True))
        return 0

    if args.command == "lint-tools":
        recipe = load_recipe(args.recipe)
        issues = lint_tools(recipe)
        print(json.dumps({"passed": not issues, "issues": issues}, indent=2, sort_keys=True))
        return 1 if issues else 0

    if args.command == "eval":
        result = evaluate_case(load_eval_case(args.case))
        print(result.to_json())
        return 0 if result.passed else 1

    if args.command == "judge-prompt":
        sys.stdout.write(build_judge_prompt(load_eval_case(args.case)))
        return 0

    if args.command == "review-trace":
        trace = load_trace(args.trace)
        result = review_trace(trace)
        if not args.claude_judge:
            print(result.to_json())
            return 0 if result.passed else 1
        try:
            semantic = judge_trace_with_claude(trace, result, model=args.model)
        except ClaudeJudgeError as exc:
            print(json.dumps({"error": str(exc), "passed": False}, indent=2, sort_keys=True))
            return 1
        combined = {
            "claude_judge": semantic.to_dict(),
            "deterministic_review": result.to_dict(),
            "passed": result.passed and semantic.passed,
        }
        print(json.dumps(combined, indent=2, sort_keys=True))
        return 0 if combined["passed"] else 1

    if args.command == "trace-judge-prompt":
        sys.stdout.write(build_trace_judge_prompt(load_trace(args.trace)))
        return 0

    if args.command == "normalize-claude":
        trace = claude_messages_to_trace(load_json(args.messages))
        print(json.dumps(trace, indent=2, sort_keys=True))
        return 0

    if args.command == "normalize-runtime":
        trace = runtime_events_to_trace(load_json(args.events))
        print(json.dumps(trace, indent=2, sort_keys=True))
        return 0

    if args.command == "import-run":
        result = import_run_export(
            args.run,
            adapter=args.adapter,
            name=args.name,
            out_dir=args.out_dir,
            task=args.task,
            tool_inventory=args.tools,
            value_bar=args.value_bar,
        )
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0

    if args.command == "snapshot-surface":
        snapshot = build_surface_snapshot(
            matrices=args.matrix,
            bundles=args.bundle,
            skills=args.skill,
            files=args.file,
        )
        output = json.dumps(snapshot, indent=2, sort_keys=True)
        if args.out:
            write_surface_snapshot(snapshot, args.out)
        else:
            print(output)
        return 0 if snapshot["items"] else 1

    if args.command == "mcp-e2e":
        try:
            result = run_e2e_spec(
                args.spec,
                env_file=args.env_file,
                allow_mutation=args.allow_mutation,
                dry_run=args.dry_run,
            )
        except E2EError as exc:
            print(json.dumps({"error": str(exc), "passed": False}, indent=2, sort_keys=True))
            return 1
        output = json.dumps(result, indent=2, sort_keys=True)
        if args.out:
            args.out.write_text(output + "\n", encoding="utf-8")
        else:
            print(output)
        return 0 if result["passed"] else 1

    if args.command == "render-report":
        output = render_html_report(load_report_input(args.result), title=args.title)
        if args.out:
            write_report(output, args.out)
        else:
            sys.stdout.write(output)
        return 0

    if args.command == "pr-comment":
        output = render_pr_comment(load_report_input(args.result), title=args.title)
        if args.out:
            write_report(output, args.out)
        else:
            sys.stdout.write(output)
        return 0

    if args.command == "trace-suite":
        result = run_trace_suite(args.suite)
        if args.markdown:
            sys.stdout.write(render_suite_markdown(result))
        else:
            print(json.dumps(result, indent=2, sort_keys=True))
        return 0 if result["passed"] else 1

    if args.command == "audit-agent":
        try:
            result = review_agent_bundle(
                args.bundle,
                claude_judge=args.claude_judge,
                require_claude_judge=args.claude_judge,
                judge_model=args.model,
            )
        except ClaudeJudgeError as exc:
            print(json.dumps({"error": str(exc), "passed": False}, indent=2, sort_keys=True))
            return 1
        if args.markdown:
            sys.stdout.write(render_agent_audit_markdown(result))
        else:
            print(json.dumps(result, indent=2, sort_keys=True))
        return 0 if result["passed"] else 1

    if args.command == "optimize-tools":
        review = review_tool_selection_bundle(args.bundle)
        result = review.to_dict()
        if args.claude_judge:
            try:
                bundle = load_json(args.bundle)
                semantic = judge_tool_selection_with_claude(
                    bundle,
                    result,
                    model=args.model,
                )
            except ClaudeJudgeError as exc:
                print(json.dumps({"error": str(exc), "passed": False}, indent=2, sort_keys=True))
                return 1
            result = {
                "claude_judge": semantic.to_dict(),
                "deterministic_review": review.to_dict(),
                "passed": review.passed and semantic.passed,
            }
        if args.markdown and not args.claude_judge:
            sys.stdout.write(render_tool_selection_markdown(review))
        else:
            print(json.dumps(result, indent=2, sort_keys=True))
        return 0 if result["passed"] else 1

    if args.command == "model-matrix":
        result = run_model_matrix(
            args.matrix,
            live=args.live,
            env_file=args.env_file,
            require_live=args.require_live,
            filters=MatrixFilters(
                providers=_csv_set(args.providers),
                harnesses=_csv_set(args.harnesses),
                variants=_csv_set(args.variants),
                instruction_variants=_csv_set(args.instruction_variants),
                cases=_csv_set(args.cases),
            ),
            max_cases=args.max_cases,
            concurrency=max(1, args.concurrency),
        )
        output = (
            render_model_matrix_markdown(result)
            if args.markdown
            else json.dumps(result, indent=2, sort_keys=True)
        )
        if args.out:
            args.out.write_text(output, encoding="utf-8")
        else:
            sys.stdout.write(output)
            if not output.endswith("\n"):
                sys.stdout.write("\n")
        return 0 if result["passed"] else 1

    if args.command == "grind-harness":
        result = run_harness_grind(
            args.matrix,
            HarnessGrindOptions(
                baseline_variant=args.baseline_variant,
                concurrency=max(1, args.concurrency),
                env_file=args.env_file,
                filters=MatrixFilters(
                    providers=_csv_set(args.providers),
                    harnesses=_csv_set(args.harnesses),
                    instruction_variants=_csv_set(args.instruction_variants),
                    cases=_csv_set(args.cases),
                ),
                heldout_cases=_csv_set(args.heldout_cases),
                live=args.live,
                max_cases=args.max_cases,
                max_iterations=max(1, args.max_iterations),
                max_live_calls=max(1, args.max_live_calls),
                min_improvement=max(0.0, args.min_improvement),
                require_live=args.require_live,
            ),
        )
        output = (
            render_harness_grind_markdown(result)
            if args.markdown
            else json.dumps(result, indent=2, sort_keys=True)
        )
        if args.out:
            args.out.write_text(output, encoding="utf-8")
        else:
            sys.stdout.write(output)
            if not output.endswith("\n"):
                sys.stdout.write("\n")
        return 0 if result["passed"] else 1

    parser.error(f"unknown command: {args.command}")
    return 2


def _csv_set(value: str | None) -> set[str] | None:
    if not value:
        return None
    return {item.strip() for item in value.split(",") if item.strip()}
