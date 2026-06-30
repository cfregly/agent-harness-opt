#!/usr/bin/env python3
"""Validate retained project-local skill surfaces."""

from __future__ import annotations

from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / ".claude" / "skills"
VALUE_PHRASE = "adversarially-confirmed to add value"

ALLOWED_CLI_COMMANDS = {
    "audit-agent",
    "eval",
    "grind-harness",
    "harness-checks",
    "import-run",
    "judge-prompt",
    "lint-tools",
    "live-harness",
    "matrix-coverage",
    "matrix-coverage-suite",
    "mcp-e2e",
    "model-matrix",
    "normalize-claude",
    "normalize-runtime",
    "optimize-tools",
    "pr-comment",
    "render",
    "render-report",
    "review-trace",
    "score",
    "snapshot-surface",
    "trace-judge-prompt",
    "trace-suite",
    "upstream-pr-packet",
}

REQUIRED_AGENT_AUDIT_COMMANDS = {
    "audit-agent",
    "grind-harness",
    "harness-checks",
    "model-matrix",
    "normalize-claude",
    "normalize-runtime",
    "optimize-tools",
    "review-trace",
    "trace-judge-prompt",
    "trace-suite",
    "upstream-pr-packet",
}

REQUIRED_AGENT_AUDIT_HEADINGS = (
    "## Decision Tree",
    "## Commands",
    "## Review Method",
    "## What To Look For",
    "## Reporting",
)

REQUIRED_LOOK_FOR_CATEGORIES = (
    "Tools",
    "Tool calls",
    "Metrics",
    "Selection cases",
    "Model matrix",
    "Skills",
    "Harness grind",
    "Tool outputs",
    "Reasoning",
    "Final answer",
    "Value bar",
    "Upstream PR packet",
)

CLI_COMMAND_RE = re.compile(r"python -m claude_agent_harness_opt\s+([a-z][a-z-]+)")


def main() -> int:
    failures = check_skill_surfaces()
    if failures:
        print("\n".join(sorted(failures)))
        return 1
    print("skill surface check passed")
    return 0


def check_skill_surfaces(skills_dir: Path = SKILLS_DIR) -> list[str]:
    failures: list[str] = []
    if not skills_dir.exists():
        return [f"{skills_dir.relative_to(ROOT)}: missing skills directory"]

    skill_paths = sorted(skills_dir.glob("*/SKILL.md"))
    if not skill_paths:
        return [f"{skills_dir.relative_to(ROOT)}: no project-local skills found"]

    for path in skill_paths:
        failures.extend(_check_skill(path))
        failures.extend(_check_agent_metadata(path.parent))

    return failures


def _check_skill(path: Path) -> list[str]:
    failures: list[str] = []
    rel = _rel(path)
    text = path.read_text(encoding="utf-8")
    frontmatter, body = _parse_frontmatter(text)

    if not frontmatter:
        failures.append(f"{rel}: missing frontmatter")
    else:
        if frontmatter.get("name") != path.parent.name:
            failures.append(f"{rel}: frontmatter name must match skill directory")
        description = frontmatter.get("description", "")
        if len(description.split()) < 20:
            failures.append(f"{rel}: description is too thin for skill selection")
        if "Use when" not in description:
            failures.append(f"{rel}: description must include trigger guidance")
        if VALUE_PHRASE not in description:
            failures.append(f"{rel}: description missing '{VALUE_PHRASE}'")

    for banned in ("TODO", "TBD", "FIXME"):
        if banned in text:
            failures.append(f"{rel}: contains unresolved marker {banned}")

    if path.parent.name == "agent-audit":
        failures.extend(_check_agent_audit_skill(rel, body))

    return failures


def _check_agent_audit_skill(rel: Path, body: str) -> list[str]:
    failures: list[str] = []
    for heading in REQUIRED_AGENT_AUDIT_HEADINGS:
        if heading not in body:
            failures.append(f"{rel}: missing heading {heading}")

    decision_items = re.findall(r"^\d+\.\s+", body, flags=re.MULTILINE)
    if len(decision_items) < 10:
        failures.append(f"{rel}: decision tree must cover at least 10 routes")

    command_names = set(CLI_COMMAND_RE.findall(body))
    unknown_commands = sorted(command_names - ALLOWED_CLI_COMMANDS)
    for command in unknown_commands:
        failures.append(f"{rel}: unknown CLI command referenced: {command}")
    for command in sorted(REQUIRED_AGENT_AUDIT_COMMANDS - command_names):
        failures.append(f"{rel}: missing required CLI command reference: {command}")

    for category in REQUIRED_LOOK_FOR_CATEGORIES:
        if f"- {category}:" not in body:
            failures.append(f"{rel}: missing What To Look For category: {category}")

    for phrase in ("Backing data:", "Commands run:", "Do not claim hidden reasoning exists"):
        if phrase not in body:
            failures.append(f"{rel}: missing reporting phrase: {phrase}")

    if VALUE_PHRASE not in body:
        failures.append(f"{rel}: body missing '{VALUE_PHRASE}'")

    return failures


def _check_agent_metadata(skill_dir: Path) -> list[str]:
    failures: list[str] = []
    agents_dir = skill_dir / "agents"
    if not agents_dir.exists():
        return failures

    metadata_paths = sorted(agents_dir.glob("*.yaml"))
    if not metadata_paths:
        failures.append(f"{_rel(agents_dir)}: agents directory has no metadata files")
        return failures

    for path in metadata_paths:
        rel = _rel(path)
        text = path.read_text(encoding="utf-8")
        if "interface:" not in text:
            failures.append(f"{rel}: missing interface block")
        metadata = _parse_simple_yaml(text)
        for key in ("display_name", "short_description", "default_prompt"):
            if not metadata.get(key):
                failures.append(f"{rel}: missing interface.{key}")
        if "value-bar" not in text:
            failures.append(f"{rel}: missing value-bar routing language")
        for banned in ("TODO", "TBD", "FIXME"):
            if banned in text:
                failures.append(f"{rel}: contains unresolved marker {banned}")

    return failures


def _parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---", 4)
    if end == -1:
        return {}, text
    raw_frontmatter = text[4:end]
    body = text[end + len("\n---") :].lstrip("\n")
    return _parse_simple_yaml(raw_frontmatter), body


def _parse_simple_yaml(text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.endswith(":") or ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        values[key.strip()] = value.strip().strip('"')
    return values


def _rel(path: Path) -> Path:
    try:
        return path.relative_to(ROOT)
    except ValueError:
        return path


if __name__ == "__main__":
    raise SystemExit(main())
