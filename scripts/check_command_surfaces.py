#!/usr/bin/env python3
"""Validate CLI, CI, and documented command surfaces stay in sync."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import shlex
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
CI_WORKFLOW = ROOT / ".github" / "workflows" / "ci.yml"

CLI_COMMAND_RE = re.compile(r"python\s+-m\s+claude_agent_harness_opt\s+([a-z0-9][a-z0-9-]*)")
SCRIPT_COMMAND_RE = re.compile(r"python\s+(scripts/[A-Za-z0-9_./-]+\.py)")
HELP_COMMANDS_RE = re.compile(r"\{([^}]+)\}")

DOC_COMMAND_PATHS = (
    ROOT / "README.md",
    ROOT / ".github" / "workflows" / "ci.yml",
    ROOT / ".claude" / "skills",
    ROOT / "docs",
)

PATH_SUFFIXES = (
    ".html",
    ".json",
    ".jsonl",
    ".md",
    ".py",
    ".txt",
    ".yaml",
    ".yml",
)

SKIP_PATH_PREFIXES = (
    "/dev/",
    "/tmp/",
    "http://",
    "https://",
    "path/to/",
)

SKIP_PATH_VALUES = {
    ".env",
    "-",
}


@dataclass(frozen=True)
class Invocation:
    source: Path
    line: int
    raw: str
    command: str
    tokens: tuple[str, ...]


def main() -> int:
    failures = check_command_surfaces()
    if failures:
        print("\n".join(sorted(failures)))
        return 1
    print("command surface check passed")
    return 0


def check_command_surfaces(root: Path = ROOT, cli_commands: set[str] | None = None) -> list[str]:
    failures: list[str] = []
    commands = cli_commands or _load_cli_commands(root)
    readme = (root / "README.md").read_text(encoding="utf-8") if (root / "README.md").exists() else ""
    ci = (
        (root / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
        if (root / ".github" / "workflows" / "ci.yml").exists()
        else ""
    )

    failures.extend(_check_gate_scripts(root, readme, ci))

    invocations = _collect_invocations(root)
    failures.extend(_check_cli_invocations(root, invocations, commands))
    failures.extend(_check_cli_command_documentation(commands, invocations))
    failures.extend(_check_script_invocations(root, _collect_script_invocations(root)))
    return failures


def _load_cli_commands(root: Path = ROOT) -> set[str]:
    result = subprocess.run(
        [sys.executable, "-m", "claude_agent_harness_opt", "--help"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    match = HELP_COMMANDS_RE.search(result.stdout)
    if not match:
        raise RuntimeError("could not parse CLI command list from --help")
    return {command.strip() for command in match.group(1).split(",") if command.strip()}


def _check_gate_scripts(root: Path, readme: str, ci: str) -> list[str]:
    failures: list[str] = []
    gate_scripts = [
        *sorted((root / "scripts").glob("check_*.py")),
        root / "scripts" / "deslop_check.py",
    ]
    existing_gate_scripts = [path for path in gate_scripts if path.exists()]
    if not existing_gate_scripts:
        return ["scripts: no check gate scripts found"]

    for path in existing_gate_scripts:
        rel = path.relative_to(root).as_posix()
        command = f"python {rel}"
        if command not in ci:
            failures.append(f"{rel}: missing from .github/workflows/ci.yml")
        if command not in readme:
            failures.append(f"{rel}: missing from README Verify it commands")
        if path.name.startswith("check_"):
            test_path = root / "tests" / f"test_{path.stem}_script.py"
            if not test_path.exists():
                failures.append(f"{rel}: missing test file {test_path.relative_to(root)}")
    return failures


def _collect_invocations(root: Path = ROOT) -> list[Invocation]:
    invocations: list[Invocation] = []
    for path in _command_surface_files(root):
        text = path.read_text(encoding="utf-8")
        invocations.extend(_extract_cli_invocations(path, text))
    return invocations


def _collect_script_invocations(root: Path = ROOT) -> list[Invocation]:
    invocations: list[Invocation] = []
    for path in _command_surface_files(root):
        text = path.read_text(encoding="utf-8")
        invocations.extend(_extract_script_invocations(path, text))
    return invocations


def _command_surface_files(root: Path = ROOT) -> list[Path]:
    paths: list[Path] = []
    for source in DOC_COMMAND_PATHS:
        path = root / source.relative_to(ROOT) if source.is_absolute() else root / source
        if not path.exists():
            continue
        if path.is_file():
            paths.append(path)
        else:
            paths.extend(sorted(path.rglob("*.md")))
            paths.extend(sorted(path.rglob("*.yml")))
            paths.extend(sorted(path.rglob("*.yaml")))
    return sorted(set(paths))


def _extract_cli_invocations(source: Path, text: str) -> list[Invocation]:
    normalized = re.sub(r"\\\n\s*", " ", text)
    invocations: list[Invocation] = []
    for line_number, line in enumerate(normalized.splitlines(), start=1):
        if "python -m claude_agent_harness_opt" not in line:
            continue
        for match in CLI_COMMAND_RE.finditer(line):
            raw = line[match.start() :].strip()
            command = match.group(1)
            tokens = _safe_split(raw)
            invocations.append(
                Invocation(
                    source=source,
                    line=line_number,
                    raw=raw,
                    command=command,
                    tokens=tuple(tokens),
                )
            )
    return invocations


def _extract_script_invocations(source: Path, text: str) -> list[Invocation]:
    normalized = re.sub(r"\\\n\s*", " ", text)
    invocations: list[Invocation] = []
    for line_number, line in enumerate(normalized.splitlines(), start=1):
        if "python scripts/" not in line:
            continue
        for match in SCRIPT_COMMAND_RE.finditer(line):
            raw = line[match.start() :].strip()
            script = match.group(1)
            tokens = _safe_split(raw)
            invocations.append(
                Invocation(
                    source=source,
                    line=line_number,
                    raw=raw,
                    command=script,
                    tokens=tuple(tokens),
                )
            )
    return invocations


def _safe_split(raw: str) -> list[str]:
    command_text = raw
    if "`" in command_text:
        command_text = command_text.split("`", 1)[0]
    for separator in (" || ", " && ", "; then", "; fi"):
        command_text = command_text.split(separator, 1)[0]
    try:
        return shlex.split(command_text)
    except ValueError:
        return command_text.split()


def _check_cli_invocations(
    root: Path,
    invocations: list[Invocation],
    commands: set[str],
) -> list[str]:
    failures: list[str] = []
    for invocation in invocations:
        prefix = f"{_rel(invocation.source, root)}:{invocation.line}"
        if invocation.command not in commands:
            failures.append(f"{prefix}: unknown CLI command {invocation.command!r}")
        failures.extend(_check_invocation_paths(root, invocation, prefix, argument_start=4))
    return failures


def _check_script_invocations(root: Path, invocations: list[Invocation]) -> list[str]:
    failures: list[str] = []
    for invocation in invocations:
        prefix = f"{_rel(invocation.source, root)}:{invocation.line}"
        script_path = root / invocation.command
        if not script_path.is_file():
            failures.append(f"{prefix}: documented script missing: {invocation.command}")
        failures.extend(_check_invocation_paths(root, invocation, prefix, argument_start=2))
    return failures


def _check_invocation_paths(
    root: Path,
    invocation: Invocation,
    prefix: str,
    *,
    argument_start: int,
) -> list[str]:
    failures: list[str] = []
    for token in _argument_tokens(invocation.tokens, argument_start=argument_start):
        if not _looks_like_repo_path(token):
            continue
        if _should_skip_path_token(token):
            continue
        path = root / token
        if not path.exists():
            failures.append(f"{prefix}: command references missing local path {token!r}")
    return failures


def _argument_tokens(tokens: tuple[str, ...], *, argument_start: int) -> list[str]:
    if len(tokens) <= argument_start:
        return []
    args = list(tokens[argument_start:])
    result: list[str] = []
    skip_next = False
    for token in args:
        if skip_next:
            skip_next = False
            continue
        if token in {">", "1>", "2>", "|"}:
            skip_next = token != "|"
            continue
        result.append(token)
    return result


def _looks_like_repo_path(token: str) -> bool:
    cleaned = token.strip().strip("'\"")
    if "/" in cleaned:
        return True
    if cleaned.startswith("."):
        return True
    return cleaned.endswith(PATH_SUFFIXES)


def _should_skip_path_token(token: str) -> bool:
    cleaned = token.strip().strip("'\"")
    if cleaned in SKIP_PATH_VALUES:
        return True
    if Path(cleaned).is_absolute():
        return True
    if any(cleaned.startswith(prefix) for prefix in SKIP_PATH_PREFIXES):
        return True
    if any(marker in cleaned for marker in ("<", ">", "{", "}", "$", "*", "(", ")")):
        return True
    if "," in cleaned:
        return True
    return False


def _check_cli_command_documentation(
    commands: set[str],
    invocations: list[Invocation],
) -> list[str]:
    documented = {invocation.command for invocation in invocations}
    missing = sorted(commands - documented)
    return [f"CLI command lacks a documented invocation: {command}" for command in missing]


def _rel(path: Path, root: Path = ROOT) -> Path:
    try:
        return path.relative_to(root)
    except ValueError:
        return path


if __name__ == "__main__":
    raise SystemExit(main())
