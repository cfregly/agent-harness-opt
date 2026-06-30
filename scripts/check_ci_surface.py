#!/usr/bin/env python3
"""Validate GitHub Actions keeps the full CI safety surface."""

from __future__ import annotations

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
CI_WORKFLOW = Path(".github/workflows/ci.yml")
DISALLOWED_ACTION_REFS = ("@main", "@master", "@latest")
REQUIRED_SUBSTRINGS = (
    ("workflow name", "name: ci"),
    ("push and pull request triggers", "on:\n  push:\n  pull_request:"),
    ("read-only workflow permissions", "permissions:\n  contents: read"),
    ("ubuntu runner", "runs-on: ubuntu-latest"),
    ("checkout action", "uses: actions/checkout@v4"),
    ("python setup action", "uses: actions/setup-python@v5"),
    ("python version", 'python-version: "3.11"'),
    ("compile smoke", "python -m compileall claude_agent_harness_opt scripts"),
    ("unit test suite", "python -m unittest discover -s tests -q"),
    ("surface inventory gate", "python scripts/check_surface_inventory.py"),
    ("regression ownership gate", "python scripts/check_regression_ownership.py"),
    ("artifact format gate", "python scripts/check_artifact_format.py"),
    ("Makefile surface gate", "python scripts/check_makefile_surface.py"),
    (
        "strict matrix coverage suite",
        "python -m claude_agent_harness_opt matrix-coverage-suite "
        "evals/model_matrix evals/targets/gstack/gstack_skill_selection_matrix.json --strict",
    ),
    (
        "strict zymtrace coverage",
        "python -m claude_agent_harness_opt matrix-coverage "
        "evals/model_matrix/zymtrace_mcp_tool_selection.json --strict",
    ),
    (
        "trace fixture live adapter check",
        "python -m claude_agent_harness_opt model-matrix "
        "evals/model_matrix/harness_trace_adapters.json --live --require-live --providers trace_fixture",
    ),
    ("live Claude judge step", "name: Run live Claude semantic judge"),
    ("live Claude judge secret", "ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}"),
    ("live Claude judge secret assertion", 'test -n "$ANTHROPIC_API_KEY"'),
    (
        "live audit-agent judge",
        "python -m claude_agent_harness_opt audit-agent "
        "evals/examples/agent_audit_bundle.json --claude-judge",
    ),
    (
        "live optimize-tools judge",
        "python -m claude_agent_harness_opt optimize-tools "
        "evals/examples/agent_audit_bundle.json --claude-judge",
    ),
    (
        "live model matrix requires key",
        "python -m claude_agent_harness_opt model-matrix "
        "evals/model_matrix/coding_tool_selection.json --live --require-live",
    ),
    (
        "live grind requires key",
        "python -m claude_agent_harness_opt grind-harness "
        "evals/model_matrix/coding_tool_selection.json --live --require-live",
    ),
    (
        "negative missing value bar",
        "if python -m claude_agent_harness_opt audit-agent "
        "evals/examples/agent_audit_missing_value_bar.json; then exit 1; fi",
    ),
    (
        "negative no-key audit-agent",
        "if env -u ANTHROPIC_API_KEY python -m claude_agent_harness_opt audit-agent "
        "evals/examples/agent_audit_bundle.json --claude-judge; then exit 1; fi",
    ),
    (
        "negative no-key optimize-tools",
        "if env -u ANTHROPIC_API_KEY python -m claude_agent_harness_opt optimize-tools "
        "evals/examples/agent_audit_bundle.json --claude-judge; then exit 1; fi",
    ),
    (
        "negative no-key model matrix",
        "if env -u ANTHROPIC_API_KEY python -m claude_agent_harness_opt model-matrix "
        "evals/model_matrix/coding_tool_selection.json --live --require-live",
    ),
    (
        "negative no-key grind",
        "if env -u ANTHROPIC_API_KEY python -m claude_agent_harness_opt grind-harness "
        "evals/model_matrix/coding_tool_selection.json --live --require-live",
    ),
)


def main() -> int:
    failures = check_ci_surface()
    if failures:
        print("\n".join(sorted(failures)))
        return 1
    print("CI surface check passed")
    return 0


def check_ci_surface(root: Path = ROOT) -> list[str]:
    path = root / CI_WORKFLOW
    if not path.exists():
        return [f"{CI_WORKFLOW}: missing"]
    text = path.read_text(encoding="utf-8")
    failures = [
        f"{CI_WORKFLOW}: missing {label}"
        for label, needle in REQUIRED_SUBSTRINGS
        if needle not in text
    ]
    failures.extend(_check_action_refs(text))
    if "--env-file .env" in text:
        failures.append(f"{CI_WORKFLOW}: CI must not depend on local .env files")
    return failures


def _check_action_refs(text: str) -> list[str]:
    failures: list[str] = []
    for line in text.splitlines():
        match = re.search(r"uses:\s*([^#\s]+)", line)
        if not match:
            continue
        action = match.group(1)
        if "@" not in action:
            failures.append(f"{CI_WORKFLOW}: action is not pinned with a version: {action}")
            continue
        if any(action.endswith(ref) for ref in DISALLOWED_ACTION_REFS):
            failures.append(f"{CI_WORKFLOW}: action must not pin to a mutable ref: {action}")
    return failures


if __name__ == "__main__":
    raise SystemExit(main())
