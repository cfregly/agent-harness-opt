#!/usr/bin/env python3
"""CI gate for the adversarial value bar."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from claude_agent_prompting.agent_audit import review_agent_bundle  # noqa: E402


VALUE_PHRASE = "adversarially-confirmed to add value"

REQUIRED_VALUE_PHRASE_FILES = (
    "AGENTS.md",
    "CLAUDE.md",
    "README.md",
    "docs/techniques.md",
    "docs/trace-review.md",
    "docs/video-coverage-audit.md",
    "prompts/agent_system_template.md",
    ".claude/skills/agent-audit/SKILL.md",
)

REQUIRED_VALUE_BAR_FILES = (
    "prompts/llm_judge.md",
    ".github/workflows/ci.yml",
)


def main() -> int:
    failures: list[str] = []
    failures.extend(_check_required_text())
    failures.extend(_check_recipes())
    failures.extend(_check_agent_audit_bundles())

    if failures:
        print("\n".join(sorted(failures)))
        return 1
    print("value-bar check passed")
    return 0


def _check_required_text() -> list[str]:
    failures: list[str] = []
    for rel_path in REQUIRED_VALUE_PHRASE_FILES:
        path = ROOT / rel_path
        if not path.exists():
            failures.append(f"{rel_path}: missing required value-bar surface")
            continue
        if VALUE_PHRASE not in path.read_text(encoding="utf-8"):
            failures.append(f"{rel_path}: missing '{VALUE_PHRASE}'")

    for rel_path in REQUIRED_VALUE_BAR_FILES:
        path = ROOT / rel_path
        if not path.exists():
            failures.append(f"{rel_path}: missing required value-bar surface")
            continue
        text = path.read_text(encoding="utf-8")
        if "value_bar" not in text and "check_value_bar.py" not in text:
            failures.append(f"{rel_path}: missing value_bar/check_value_bar enforcement")
    return failures


def _check_recipes() -> list[str]:
    failures: list[str] = []
    for path in sorted((ROOT / "recipes").glob("*.json")):
        data = _load_json(path)
        text = json.dumps(data, sort_keys=True)
        if VALUE_PHRASE not in text:
            failures.append(f"{path.relative_to(ROOT)}: missing '{VALUE_PHRASE}'")
    return failures


def _check_agent_audit_bundles() -> list[str]:
    failures: list[str] = []
    bundle_paths = [
        path
        for path in sorted((ROOT / "evals").rglob("*.json"))
        if _is_agent_audit_bundle(_load_json(path))
    ]
    if not bundle_paths:
        return ["evals: no agent audit bundles found"]

    negative_controls = 0
    for path in bundle_paths:
        result = review_agent_bundle(path)
        rel = path.relative_to(ROOT)
        if "missing_value_bar" in path.stem:
            negative_controls += 1
            if result["passed"] or result["value_bar"]["passed"]:
                failures.append(f"{rel}: negative value-bar control unexpectedly passed")
            continue
        if not result["value_bar"]["passed"]:
            failures.append(f"{rel}: value_bar failed")
        if not result["passed"]:
            failures.append(f"{rel}: audit bundle failed")

    if negative_controls == 0:
        failures.append("evals: missing negative control for absent value_bar")
    return failures


def _is_agent_audit_bundle(data: Any) -> bool:
    return isinstance(data, dict) and isinstance(data.get("tools"), list) and isinstance(
        data.get("traces"), list
    )


def _load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


if __name__ == "__main__":
    raise SystemExit(main())
