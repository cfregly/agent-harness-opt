#!/usr/bin/env python3
"""Validate agent-facing project instructions cover the optimization workflow."""

from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
AGENTS = ROOT / "AGENTS.md"
CLAUDE = ROOT / "CLAUDE.md"
OLD_REPO_SLUGS = (
    "claude-agent-harness-optimization",
    "ai-performance-engineering",
)

AGENTS_REQUIRED_PHRASES = (
    "See [CLAUDE.md](CLAUDE.md)",
    "adversarially-confirmed to add value",
)

CLAUDE_REQUIRED_PHRASES = (
    "adversarially-confirmed to add value",
    ".claude/skills/agent-audit/SKILL.md",
    "evals/model_matrix",
    "evals/results",
    "evals/pr_packets",
    "docs/findings",
    "matrix-coverage-suite",
    "grind-harness",
    "Preserve user changes",
    "No destructive git cleanup",
    "Secrets never get committed",
    "`.env` stays git-ignored",
)


def main() -> int:
    failures = check_project_instructions()
    if failures:
        print("\n".join(sorted(failures)))
        return 1
    print("project instruction check passed")
    return 0


def check_project_instructions(root: Path = ROOT) -> list[str]:
    failures: list[str] = []
    agents = root / "AGENTS.md"
    claude = root / "CLAUDE.md"

    failures.extend(_check_markdown_file(agents, root))
    failures.extend(_check_markdown_file(claude, root))
    if agents.exists():
        failures.extend(_check_required_phrases(agents, AGENTS_REQUIRED_PHRASES, root))
    if claude.exists():
        failures.extend(_check_required_phrases(claude, CLAUDE_REQUIRED_PHRASES, root))
        failures.extend(_check_gate_scripts(claude, root))
    return failures


def _check_markdown_file(path: Path, root: Path = ROOT) -> list[str]:
    rel = _rel(path, root)
    if not path.exists():
        return [f"{rel}: missing"]

    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    first_nonempty = next((line.strip() for line in lines if line.strip()), "")
    failures: list[str] = []
    if not first_nonempty.startswith("# "):
        failures.append(f"{rel}: first nonempty line must be an H1")
    for slug in OLD_REPO_SLUGS:
        if slug in text:
            failures.append(f"{rel}: contains stale repository reference {slug}")
    return failures


def _check_required_phrases(path: Path, phrases: tuple[str, ...], root: Path = ROOT) -> list[str]:
    text = path.read_text(encoding="utf-8")
    rel = _rel(path, root)
    return [f"{rel}: missing required instruction phrase: {phrase}" for phrase in phrases if phrase not in text]


def _check_gate_scripts(path: Path, root: Path = ROOT) -> list[str]:
    text = path.read_text(encoding="utf-8")
    rel = _rel(path, root)
    gate_scripts = [
        *sorted((root / "scripts").glob("check_*.py")),
        root / "scripts" / "deslop_check.py",
    ]
    failures: list[str] = []
    for script in gate_scripts:
        if not script.exists():
            continue
        script_rel = script.relative_to(root).as_posix()
        if script_rel not in text:
            failures.append(f"{rel}: missing gate script reference {script_rel}")
    return failures


def _rel(path: Path, root: Path = ROOT) -> Path:
    try:
        return path.relative_to(root)
    except ValueError:
        return path


if __name__ == "__main__":
    raise SystemExit(main())
