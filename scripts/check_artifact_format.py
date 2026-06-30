#!/usr/bin/env python3
"""Validate generic tracked artifact formatting."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {
    ".example",
    ".json",
    ".jsonl",
    ".md",
    ".py",
    ".tape",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}
TEXT_FILENAMES = {
    ".gitignore",
    "AGENTS.md",
    "CLAUDE.md",
    "LICENSE",
    "Makefile",
    "README.md",
}


def main() -> int:
    failures = check_artifact_format()
    if failures:
        print("\n".join(sorted(failures)))
        return 1
    print("artifact format check passed")
    return 0


def check_artifact_format(root: Path = ROOT, tracked_paths: list[str] | None = None) -> list[str]:
    paths = tracked_paths if tracked_paths is not None else _tracked_paths(root)
    failures: list[str] = []
    for rel in paths:
        path = root / rel
        if not path.is_file():
            continue
        if _is_text_artifact(rel):
            failures.extend(_check_text_artifact(path, rel))
        if path.suffix == ".json":
            failures.extend(_check_json_file(path, rel))
        if path.suffix == ".jsonl":
            failures.extend(_check_jsonl_file(path, rel))
    return failures


def _check_text_artifact(path: Path, rel: str) -> list[str]:
    data = path.read_bytes()
    failures: list[str] = []
    if not data:
        failures.append(f"{rel}: tracked text artifact must not be empty")
        return failures
    if not data.endswith(b"\n"):
        failures.append(f"{rel}: missing trailing newline")
    if b"\r\n" in data:
        failures.append(f"{rel}: contains CRLF line endings")
    if b"\x00" in data:
        failures.append(f"{rel}: contains NUL bytes")
    try:
        data.decode("utf-8")
    except UnicodeDecodeError as exc:
        failures.append(f"{rel}: not valid UTF-8: {exc}")
    return failures


def _check_json_file(path: Path, rel: str) -> list[str]:
    try:
        json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"{rel}: invalid JSON: {exc}"]
    return []


def _check_jsonl_file(path: Path, rel: str) -> list[str]:
    failures: list[str] = []
    for line_number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not raw.strip():
            failures.append(f"{rel}:{line_number}: blank JSONL line")
            continue
        try:
            json.loads(raw)
        except json.JSONDecodeError as exc:
            failures.append(f"{rel}:{line_number}: invalid JSONL: {exc}")
    return failures


def _is_text_artifact(rel: str) -> bool:
    path = Path(rel)
    return path.suffix in TEXT_SUFFIXES or path.name in TEXT_FILENAMES


def _tracked_paths(root: Path = ROOT) -> list[str]:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    return [line for line in result.stdout.splitlines() if line.strip()]


if __name__ == "__main__":
    raise SystemExit(main())
