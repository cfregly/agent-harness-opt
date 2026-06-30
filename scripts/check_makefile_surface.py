#!/usr/bin/env python3
"""Validate the public Makefile shortcut surface."""

from __future__ import annotations

from pathlib import Path
import re
import subprocess
import sys
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.optimize_mcp import TARGETS, Target  # noqa: E402


EXPECTED_PHONY_TARGETS = ("help", "optimize", "optimize-dry", "optimize-grind")
PASSTHROUGH_FLAGS = (
    ('$(if $(PROVIDERS),--providers "$(PROVIDERS)",)', "PROVIDERS"),
    ('$(if $(HARNESSES),--harnesses "$(HARNESSES)",)', "HARNESSES"),
    ('$(if $(MAX_CASES),--max-cases "$(MAX_CASES)",)', "MAX_CASES"),
    ('$(if $(OUT),--out "$(OUT)",)', "OUT"),
)


def main() -> int:
    failures = check_makefile_surface()
    if failures:
        print("\n".join(sorted(failures)))
        return 1
    print("Makefile surface check passed")
    return 0


def check_makefile_surface(
    root: Path = ROOT,
    targets: Iterable[Target] = TARGETS,
    *,
    run_help: bool = True,
) -> list[str]:
    path = root / "Makefile"
    if not path.exists():
        return ["Makefile: missing"]

    text = path.read_text(encoding="utf-8")
    failures: list[str] = []
    failures.extend(_check_phony_targets(text))
    failures.extend(_check_selector_contract(text))
    failures.extend(_check_recipe_contract(text))
    failures.extend(_check_target_shortcuts(text, list(targets)))
    if run_help:
        failures.extend(_check_help_smoke(root, text))
    return failures


def _check_phony_targets(text: str) -> list[str]:
    match = re.search(r"^\.PHONY:\s*(.+)$", text, flags=re.MULTILINE)
    if not match:
        return ["Makefile: missing .PHONY targets"]

    phony = tuple(match.group(1).split())
    failures: list[str] = []
    for target in EXPECTED_PHONY_TARGETS:
        if target not in phony:
            failures.append(f"Makefile: missing .PHONY target {target}")
        if not re.search(rf"^{re.escape(target)}:", text, flags=re.MULTILINE):
            failures.append(f"Makefile: target {target} has no recipe")

    for target in phony:
        if target == "help":
            continue
        if f"make {target}" not in text:
            failures.append(f"Makefile: help text missing public target {target}")
    return failures


def _check_selector_contract(text: str) -> list[str]:
    required = {
        "lowercase selector guard": "Use lowercase selectors",
        "mcp selector": "mcp=<target>",
        "url selector": "url=https://github.com/<org>/<repo>",
        "missing target guard": "Missing target",
        "combined target resolver": "MCP_TARGET = $(if $(mcp),$(mcp),$(url))",
    }
    return [f"Makefile: missing {label}" for label, needle in required.items() if needle not in text]


def _check_recipe_contract(text: str) -> list[str]:
    failures: list[str] = []
    recipes = {target: _recipe_for(text, target) for target in EXPECTED_PHONY_TARGETS}

    live = recipes.get("optimize", "")
    dry = recipes.get("optimize-dry", "")
    grind = recipes.get("optimize-grind", "")

    for target, recipe in recipes.items():
        if not recipe:
            continue
        if target.startswith("optimize") and "$(call require_mcp_target)" not in recipe:
            failures.append(f"Makefile: {target} must require an explicit mcp/url target")
        if target.startswith("optimize") and 'scripts/optimize_mcp.py "$(MCP_TARGET)"' not in recipe:
            failures.append(f"Makefile: {target} must call scripts/optimize_mcp.py with MCP_TARGET")
        for flag, variable in PASSTHROUGH_FLAGS:
            if target.startswith("optimize") and flag not in recipe:
                failures.append(f"Makefile: {target} missing {variable} passthrough")
        if target.startswith("optimize") and '--concurrency "$(CONCURRENCY)"' not in recipe:
            failures.append(f"Makefile: {target} missing CONCURRENCY passthrough")
        if target.startswith("optimize") and "--markdown" not in recipe:
            failures.append(f"Makefile: {target} must write markdown by default")

    if "--live" not in live or "--require-live" not in live:
        failures.append("Makefile: optimize must be live and require live credentials")
    if "--env-file" not in live:
        failures.append("Makefile: optimize must pass ENV_FILE")
    if "--grind" in live:
        failures.append("Makefile: optimize must not enable grind mode")

    if "--live" in dry or "--require-live" in dry or "--env-file" in dry:
        failures.append("Makefile: optimize-dry must stay keyless and non-live")
    if "--grind" in dry:
        failures.append("Makefile: optimize-dry must not enable grind mode")

    if "--live" not in grind or "--require-live" not in grind:
        failures.append("Makefile: optimize-grind must be live and require live credentials")
    if "--env-file" not in grind:
        failures.append("Makefile: optimize-grind must pass ENV_FILE")
    if "--grind" not in grind:
        failures.append("Makefile: optimize-grind must enable grind mode")
    return failures


def _check_target_shortcuts(text: str, targets: list[Target]) -> list[str]:
    failures: list[str] = []
    if not targets:
        return ["scripts.optimize_mcp: no shortcut targets registered"]

    for target in targets:
        primary = target.inputs[0]
        if f"make optimize mcp={primary}" not in text:
            failures.append(f"Makefile: help missing optimize shortcut mcp={primary}")
    if "make optimize url=https://github.com/" not in text:
        failures.append("Makefile: help missing URL optimization shortcut")
    if "make optimize-dry mcp=" not in text:
        failures.append("Makefile: help missing dry-run shortcut")
    if "make optimize-grind mcp=" not in text:
        failures.append("Makefile: help missing grind shortcut")
    return failures


def _check_help_smoke(root: Path, text: str) -> list[str]:
    result = subprocess.run(
        ["make", "help"],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return [f"Makefile: make help failed with exit {result.returncode}: {result.stderr.strip()}"]

    failures: list[str] = []
    for target in EXPECTED_PHONY_TARGETS:
        if target == "help":
            continue
        if f"make {target}" not in result.stdout:
            failures.append(f"Makefile: make help output missing {target}")
    for line in _help_echo_lines(text):
        expected = _unquote_echo(line)
        if expected and expected not in result.stdout:
            failures.append(f"Makefile: help recipe line not emitted: {expected}")
    return failures


def _recipe_for(text: str, target: str) -> str:
    match = re.search(
        rf"^{re.escape(target)}:\n(?P<body>(?:\t.*(?:\n|$))*)",
        text,
        flags=re.MULTILINE,
    )
    return match.group("body") if match else ""


def _help_echo_lines(text: str) -> list[str]:
    recipe = _recipe_for(text, "help")
    lines: list[str] = []
    for line in recipe.splitlines():
        stripped = line.strip()
        if stripped.startswith('@echo "'):
            lines.append(stripped.removeprefix("@echo ").strip())
    return lines


def _unquote_echo(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] == '"':
        return value[1:-1]
    return value


if __name__ == "__main__":
    raise SystemExit(main())
