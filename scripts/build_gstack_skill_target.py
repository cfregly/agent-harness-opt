#!/usr/bin/env python3
"""Build a skills-as-tools target bundle and matrix for a pinned gstack checkout."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any


BOUNDARY_NOTES = {
    "gstack_gstack": "Compatibility browser alias. Prefer gstack_browse for explicit browser testing and QA navigation requests.",
    "gstack_browse": "Browser operation only. Do not choose for full QA with code fixes, report-only QA, or real Chrome side-panel setup.",
    "gstack_qa": "Use only when the user wants testing plus code fixes. For bug reports without edits, choose gstack_qa_only.",
    "gstack_qa_only": "Use only when the user wants a report without code changes. For fix-and-verify loops, choose gstack_qa.",
    "gstack_design_review": "Use for live or implemented UI visual audit and fixes. For pre-implementation design-plan review, choose gstack_plan_design_review.",
    "gstack_plan_design_review": "Use for plan-mode UI or UX critique before implementation. For implemented UI fixes, choose gstack_design_review.",
    "gstack_design_consultation": "Use for creating a design system or DESIGN.md. For choosing among multiple concrete variants, choose gstack_design_shotgun.",
    "gstack_design_shotgun": "Use for generating and comparing multiple design variants. For a durable design system, choose gstack_design_consultation.",
    "gstack_review": "Use for pre-landing code review. For root-cause debugging, choose gstack_investigate; for security threat modeling, choose gstack_cso.",
    "gstack_investigate": "Use for debugging and root-cause analysis. Do not choose for general PR review or security audit.",
    "gstack_cso": "Use for security audits, threat models, OWASP, STRIDE, dependency and secrets checks. Do not choose for ordinary code review.",
    "gstack_ship": "Use to prepare/push/create a PR. For merging an existing PR and verifying deploy, choose gstack_land_and_deploy.",
    "gstack_land_and_deploy": "Use after a PR is ready to merge and deploy. For one-time deploy config, choose gstack_setup_deploy.",
    "gstack_setup_deploy": "Use for one-time deployment configuration. Do not choose for actual merge/deploy execution.",
    "gstack_canary": "Use after deployment to monitor production health. For performance baselines, choose gstack_benchmark.",
    "gstack_benchmark": "Use for performance and Core Web Vitals baselines or regressions. Do not choose for general QA.",
    "gstack_careful": "Use for destructive-command warnings. For edit directory locking, choose gstack_freeze; for both, choose gstack_guard.",
    "gstack_freeze": "Use to restrict edits to a directory. For destructive-command warnings, choose gstack_careful; for both, choose gstack_guard.",
    "gstack_guard": "Use when the user explicitly wants both destructive-command warnings and directory-scoped edits.",
    "gstack_unfreeze": "Use only to clear an existing freeze boundary.",
    "gstack_connect_chrome": "Use to launch a visible Chrome with side panel control. For headless browser testing, choose gstack_browse.",
    "gstack_setup_browser_cookies": "Use to import browser cookies before authenticated browser testing. Do not choose for ordinary browser navigation.",
    "gstack_office_hours": "Use for early product/startup brainstorming. For turning an idea into a concrete spec plus browser validation, choose gstack_spec_qa.",
    "gstack_spec_qa": "Use for feature shaping plus browser validation. For pure brainstorming without validation, choose gstack_office_hours.",
    "gstack_autoplan": "Use when the user wants CEO, design, and engineering plan reviews run automatically.",
    "gstack_plan_ceo_review": "Use for ambition, scope, and product strategy review.",
    "gstack_plan_eng_review": "Use for architecture, data flow, edge cases, and test-plan review.",
    "gstack_document_release": "Use after shipping to update docs to match the change. For weekly team retrospectives, choose gstack_retro.",
    "gstack_retro": "Use for weekly or sprint retrospective over commits and work patterns.",
    "gstack_upgrade": "Use only to update the gstack installation itself.",
}


CASES = [
    ("browser-headless", "Open http://localhost:3000, click through the signup flow, and capture screenshots of any bug evidence.", "gstack_browse", ["gstack_gstack", "gstack_connect_chrome", "gstack_qa"]),
    ("qa-fix", "QA this staging site, fix the bugs you find, add regression tests, and commit each fix atomically.", "gstack_qa", ["gstack_qa_only", "gstack_browse"]),
    ("qa-report-only", "Test this app and give me a bug report with repro steps, but do not edit any files.", "gstack_qa_only", ["gstack_qa", "gstack_browse"]),
    ("implemented-design-polish", "Audit the implemented dashboard UI for spacing, hierarchy, and visual slop, then fix the issues.", "gstack_design_review", ["gstack_plan_design_review", "gstack_design_consultation"]),
    ("design-plan-review", "Review this UI plan before implementation and score the design dimensions with recommendations.", "gstack_plan_design_review", ["gstack_design_review", "gstack_plan_eng_review"]),
    ("design-system", "Create a design system and DESIGN.md for a new B2B workflow product.", "gstack_design_consultation", ["gstack_design_shotgun", "gstack_plan_design_review"]),
    ("design-variants", "Show me several visual directions for this feature and let me compare options before choosing.", "gstack_design_shotgun", ["gstack_design_consultation", "gstack_design_review"]),
    ("product-brainstorm", "I have an idea for a restaurant waitlist tool. Help me pressure-test whether it is worth building.", "gstack_office_hours", ["gstack_spec_qa", "gstack_plan_ceo_review"]),
    ("spec-plus-browser-validation", "Turn this rough feature request into a spec, pressure-test it, then validate the critical path in the browser.", "gstack_spec_qa", ["gstack_office_hours", "gstack_qa"]),
    ("ceo-scope-review", "Rethink this plan from a founder perspective and tell me whether the scope is ambitious enough.", "gstack_plan_ceo_review", ["gstack_plan_eng_review", "gstack_autoplan"]),
    ("engineering-plan-review", "Review the architecture, data flow, edge cases, and test plan before implementation.", "gstack_plan_eng_review", ["gstack_plan_ceo_review", "gstack_review"]),
    ("auto-plan-review", "Run CEO, design, and engineering plan reviews automatically and surface only the key decisions.", "gstack_autoplan", ["gstack_plan_ceo_review", "gstack_plan_eng_review"]),
    ("pre-landing-review", "Review this PR before merge for SQL safety, trust boundaries, and production bugs.", "gstack_review", ["gstack_cso", "gstack_investigate"]),
    ("root-cause-debug", "Debug why this job started failing and do not patch anything until you find the root cause.", "gstack_investigate", ["gstack_review", "gstack_cso"]),
    ("security-audit", "Run an infrastructure-first security audit with secrets, dependency supply chain, OWASP, and STRIDE coverage.", "gstack_cso", ["gstack_review", "gstack_careful"]),
    ("ship-pr", "Sync main, run tests, update changelog, push this branch, and create a PR.", "gstack_ship", ["gstack_land_and_deploy", "gstack_setup_deploy"]),
    ("land-and-deploy", "Merge the approved PR, wait for CI and deploy, then verify production health.", "gstack_land_and_deploy", ["gstack_ship", "gstack_canary"]),
    ("configure-deploy", "Detect our deploy platform and write the production URL, health checks, and deploy commands into project docs.", "gstack_setup_deploy", ["gstack_land_and_deploy", "gstack_ship"]),
    ("post-deploy-monitor", "Watch the live app after deploy for console errors, page failures, and regressions.", "gstack_canary", ["gstack_benchmark", "gstack_qa"]),
    ("performance-regression", "Establish a page-load and Core Web Vitals baseline and compare this PR against it.", "gstack_benchmark", ["gstack_canary", "gstack_qa"]),
    ("docs-after-release", "Update README, architecture docs, and changelog to match what just shipped.", "gstack_document_release", ["gstack_retro", "gstack_ship"]),
    ("weekly-retro", "Summarize what shipped this week across commits, tests, and team work patterns.", "gstack_retro", ["gstack_document_release", "gstack_review"]),
    ("real-chrome", "Launch my real Chrome with the side panel so I can watch the agent operate in the browser.", "gstack_connect_chrome", ["gstack_browse", "gstack_setup_browser_cookies"]),
    ("auth-cookies", "Import cookies from my real browser so the headless browser can test authenticated pages.", "gstack_setup_browser_cookies", ["gstack_connect_chrome", "gstack_browse"]),
    ("careful-mode", "Be careful while touching production and warn me before destructive shell commands.", "gstack_careful", ["gstack_freeze", "gstack_guard"]),
    ("freeze-edits", "Only edit files under packages/api while debugging this issue.", "gstack_freeze", ["gstack_careful", "gstack_guard"]),
    ("full-guard-mode", "Lock edits to this directory and warn before destructive commands.", "gstack_guard", ["gstack_careful", "gstack_freeze"]),
    ("unfreeze-edits", "Remove the edit restriction so changes can touch the whole repo again.", "gstack_unfreeze", ["gstack_freeze", "gstack_guard"]),
    ("upgrade-gstack", "Upgrade gstack to the latest version and show me what changed.", "gstack_upgrade", ["gstack_ship", "gstack_setup_deploy"]),
    ("no-tool-general-answer", "Explain what a monorepo is in two paragraphs. Do not run a workflow.", "NO_TOOL", []),
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gstack-root", default="/Users/admin/dev/gstack")
    parser.add_argument("--out-dir", default="evals/targets/gstack")
    args = parser.parse_args()

    root = Path(args.gstack_root)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    source = _source_metadata(root)
    tools = _load_tools(root)
    matrix = _build_matrix(tools, source)
    bundle = _build_bundle(tools, source)

    matrix_path = out_dir / "gstack_skill_selection_matrix.json"
    bundle_path = out_dir / "gstack_agent_audit_bundle.json"
    matrix_path.write_text(json.dumps(matrix, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    bundle_path.write_text(json.dumps(bundle, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"bundle": str(bundle_path), "matrix": str(matrix_path), "tool_count": len(tools)}, indent=2, sort_keys=True))
    return 0


def _source_metadata(root: Path) -> dict[str, Any]:
    package = _load_package(root)
    skills_root = root / ".agents" / "skills"
    return {
        "commit": _git(root, "rev-parse", "HEAD"),
        "generated_surface_hash": _surface_hash(skills_root),
        "target_surface_dirty": bool(_git(root, "status", "--short", "--", ".agents/skills")),
        "worktree_dirty": bool(_git(root, "status", "--short")),
        "package_name": package.get("name", "gstack"),
        "package_version": package.get("version", ""),
        "remote": _git(root, "remote", "get-url", "origin"),
        "source_path": str(root),
        "target_surface": ".agents/skills/*/SKILL.md generated skill files",
    }


def _load_package(root: Path) -> dict[str, Any]:
    path = root / "package.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def _load_tools(root: Path) -> list[dict[str, Any]]:
    skills_root = root / ".agents" / "skills"
    tools = []
    for skill_path in sorted(skills_root.glob("*/SKILL.md")):
        text = skill_path.read_text(encoding="utf-8")
        frontmatter = _frontmatter(text)
        raw_name = str(frontmatter.get("name") or skill_path.parent.name)
        tool_name = _tool_name(skill_path.parent.name, raw_name)
        description = _clean_description(str(frontmatter.get("description", "")))
        boundary = BOUNDARY_NOTES.get(tool_name, "")
        tools.append(
            {
                "avoid_when": boundary or "Avoid when another gstack skill better matches the requested workflow.",
                "context_controls": ["target path or URL", "mutation intent", "review mode", "stop criteria"],
                "error_guidance": "If required context is missing, ask for the missing URL, path, PR, deployment target, or allowed mutation scope before running the workflow.",
                "input_schema": {
                    "properties": {
                        "request": {
                            "description": "The user's workflow request, including target URL, file, PR, or scope when available.",
                            "type": "string",
                        }
                    },
                    "required": ["request"],
                    "type": "object",
                },
                "name": tool_name,
                "output_schema": {
                    "result": "The selected gstack skill should execute its documented workflow and report evidence, changes, or next steps."
                },
                "path": str(skill_path),
                "purpose": f"Run the {raw_name} gstack workflow: {description}",
                "quality_checks": [
                    "Confirm the request matches this skill's phase of work.",
                    "Check adjacent gstack skills before selecting this one.",
                    "Preserve no-edit and safety boundaries from the user request.",
                ],
                "source_hash": _hash_text(text),
                "source_skill_name": raw_name,
                "use_when": description,
            }
        )
    return [*tools, _no_tool()]


def _no_tool() -> dict[str, Any]:
    return {
        "avoid_when": "Avoid when one of the gstack workflow skills should actually run.",
        "context_controls": ["workflow necessity", "user intent"],
        "error_guidance": "If the user asks a general question or explicitly says not to run a workflow, choose this pseudo-skill.",
        "input_schema": {
            "properties": {
                "rationale": {
                    "description": "Why no gstack workflow should be selected.",
                    "type": "string",
                }
            },
            "required": ["rationale"],
            "type": "object",
        },
        "name": "NO_TOOL",
        "output_schema": {"result": "A short explanation that no gstack workflow should run."},
        "path": "",
        "purpose": "Represent the safe decision to run no gstack workflow.",
        "quality_checks": [
            "Use only when the user request is general, unsupported, or explicitly says not to run a workflow."
        ],
        "source_hash": "",
        "source_skill_name": "NO_TOOL",
        "use_when": "Use when no gstack workflow skill should be selected for the user request.",
    }


def _tool_name(directory_name: str, raw_name: str) -> str:
    suffix = directory_name.removeprefix("gstack-")
    if directory_name == "gstack":
        suffix = "gstack"
    if raw_name == "gstack-upgrade" or suffix == "upgrade":
        suffix = "upgrade"
    return "gstack_" + re.sub(r"[^a-zA-Z0-9_]", "_", suffix).strip("_")


def _build_matrix(tools: list[dict[str, Any]], source: dict[str, Any]) -> dict[str, Any]:
    tool_names = [tool["name"] for tool in tools if tool["name"] != "NO_TOOL"]
    cases = [_case(name, task, expected, forbidden, tool_names) for name, task, expected, forbidden in CASES]
    return {
        "cases": cases,
        "description": "Cross-provider skill-routing matrix for the pinned gstack Codex-compatible skill catalog.",
        "instruction_variants": [
            {
                "instructions": "Choose the gstack skill that best matches the user request. Treat each skill as a workflow tool. Do not answer the task directly.",
                "name": "baseline_skill_routing",
            },
            {
                "instructions": (
                    "Choose exactly one gstack skill. First separate phase of work: ideation, plan review, code review, debugging, browser testing, QA with fixes, report-only QA, ship, deploy, post-deploy monitoring, documentation, retrospective, safety mode, or setup. "
                    "Respect no-edit requests. Prefer narrow skills over broad aliases. If no gstack workflow should run, choose NO_TOOL."
                ),
                "name": "boundary_routing_rules",
            },
        ],
        "name": "gstack skill-routing matrix",
        "profiles": [
            {
                "api_key_env": "ANTHROPIC_API_KEY",
                "harnesses": ["native_tools", "prompt_json"],
                "model": "claude-sonnet-4-5",
                "model_env": "ANTHROPIC_MATRIX_MODEL",
                "name": "anthropic-sonnet",
                "provider": "anthropic",
            },
            {
                "api_key_env": "OPENAI_API_KEY",
                "harnesses": ["native_tools", "prompt_json"],
                "model": "gpt-4.1",
                "model_env": "OPENAI_MATRIX_MODEL",
                "name": "openai-gpt",
                "provider": "openai",
            },
            {
                "api_key_env": "GEMINI_API_KEY",
                "harnesses": ["native_tools", "prompt_json"],
                "max_tokens": 4096,
                "model": "gemini-2.5-pro",
                "model_env": "GEMINI_MATRIX_MODEL",
                "name": "gemini-pro",
                "provider": "gemini",
            },
        ],
        "source": source,
        "tool_variants": [
            {"name": "gstack_stock_skill_descriptions", "tools": [_stock_tool(tool) for tool in tools]},
            {"name": "gstack_boundary_tuned_skill_descriptions", "tools": tools},
        ],
        "value_bar": {
            "adversarial_check": "Adjacent gstack skills must not be interchangeable: qa versus qa-only, browse versus connect-chrome, review versus cso, ship versus land-and-deploy, and careful versus freeze versus guard.",
            "baseline": "Unvalidated skill catalogs can route requests to broad aliases or adjacent workflows.",
            "claim": "The matrix adds value if it exposes or confirms skill-routing boundaries across providers and harnesses for a pinned gstack version.",
            "minimum_improvement": "Boundary-tuned descriptions should match or outperform stock descriptions without masking NO_TOOL safety cases.",
        },
    }


def _stock_tool(tool: dict[str, Any]) -> dict[str, Any]:
    copied = dict(tool)
    copied["avoid_when"] = "Avoid when another gstack skill clearly matches the request better."
    copied["quality_checks"] = ["Confirm the request matches this skill's documented trigger."]
    return copied


def _build_bundle(tools: list[dict[str, Any]], source: dict[str, Any]) -> dict[str, Any]:
    return {
        "heldout_tool_selection_cases": [
            {
                "expected_tools": ["gstack_qa_only"],
                "forbidden_tools": ["gstack_qa"],
                "name": "authenticated qa report only",
                "rationale": "Authenticated browser setup can be a prerequisite, but the final requested workflow is still report-only QA.",
                "task": "Use my logged-in session if needed and produce a QA report, but do not edit files.",
                "valid_tool_paths": [["gstack_setup_browser_cookies", "gstack_qa_only"], ["gstack_qa_only"]],
                "verifier": {
                    "must_include_any": [["gstack_qa_only"]],
                    "type": "flexible_text",
                },
            }
        ],
        "name": "gstack skill-routing audit bundle",
        "source": source,
        "tool_metrics": {
            "avg_runtime_ms": 0,
            "avg_tool_calls": 1,
            "source_skill_count": len(tools),
            "source_version": source.get("package_version", ""),
            "token_count": 0,
            "tool_error_rate": 0,
        },
        "tool_selection_cases": [
            _case(name, task, expected, forbidden, tool_names=[tool["name"] for tool in tools if tool["name"] != "NO_TOOL"])
            for name, task, expected, forbidden in CASES
        ],
        "tools": tools,
        "traces": [],
        "value_bar": {
            "adversarial_review": {
                "challenge": "The bundle must include adjacent-boundary cases and a NO_TOOL case so broad aliases cannot pass by being merely plausible.",
                "failed_to_disprove": True,
                "open_objections": [],
                "reviewer": "gstack skills-as-tools matrix",
            },
            "baseline": {"score": 0.0, "source": "unmeasured before this generated target"},
            "candidate": {"score": 1.0, "source": "generated matrix must be run live before claiming routing quality"},
            "claim": "A pinned gstack skill catalog can be audited as a skills-as-tools routing target with adjacent-boundary and no-tool checks.",
            "metric": "model_matrix.score",
            "minimum_delta": 0.01,
        },
    }


def _case(name: str, task: str, expected: str, forbidden: list[str], tool_names: list[str]) -> dict[str, Any]:
    forbidden_tools = [item for item in forbidden if item in tool_names or item == "NO_TOOL"]
    if expected == "NO_TOOL":
        forbidden_tools = tool_names
    return {
        "expected_outcome": f"The selected tool is {expected}.",
        "expected_tools": [expected],
        "forbidden_tools": forbidden_tools,
        "name": name,
        "rationale": f"The request should route to {expected}.",
        "task": task,
        "verifier": {
            "must_include_any": [[expected]],
            "type": "flexible_text",
        },
    }


def _frontmatter(text: str) -> dict[str, Any]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    data: dict[str, Any] = {}
    key = None
    buf: list[str] = []
    for raw in lines[1:]:
        line = raw.rstrip()
        if line.strip() == "---":
            if key:
                data[key] = "\n".join(buf).strip()
            return data
        if re.match(r"^[A-Za-z0-9_-]+:", line):
            if key:
                data[key] = "\n".join(buf).strip()
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()
            if value == "|":
                buf = []
            else:
                data[key] = value.strip("'\"")
                key = None
                buf = []
        elif key:
            buf.append(line.strip())
    return data


def _clean_description(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _git(root: Path, *args: str) -> str:
    completed = subprocess.run(["git", *args], cwd=root, check=False, capture_output=True, text=True)
    return completed.stdout.strip()


def _surface_hash(skills_root: Path) -> str:
    payload = []
    for path in sorted(skills_root.glob("*/SKILL.md")):
        payload.append({"path": str(path.relative_to(skills_root)), "sha256": _hash_text(path.read_text(encoding="utf-8"))})
    return _hash_text(json.dumps(payload, sort_keys=True, separators=(",", ":")))


def _hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


if __name__ == "__main__":
    raise SystemExit(main())
