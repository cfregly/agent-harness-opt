#!/usr/bin/env python3
"""Reject tracked secrets and unsafe environment samples."""

from __future__ import annotations

from pathlib import Path
import re
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
ENV_SAMPLE = ".env.example"

SECRET_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("private key block", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("anthropic api key", re.compile(r"sk-ant-api[0-9A-Za-z_-]{20,}")),
    ("openai api key", re.compile(r"sk-proj-[0-9A-Za-z_-]{20,}|sk-[A-Za-z0-9]{32,}")),
    ("google api key", re.compile(r"AIza[0-9A-Za-z_-]{30,}")),
    ("github token", re.compile(r"ghp_[0-9A-Za-z_]{30,}|github_pat_[0-9A-Za-z_]{40,}")),
    ("slack token", re.compile(r"xox[baprs]-[0-9A-Za-z-]{20,}")),
    ("stripe secret key", re.compile(r"(?:sk|rk)_live_[0-9A-Za-z]{20,}")),
    ("statsig secret", re.compile(r"secret-[0-9A-Za-z]{20,}")),
    ("jwt-like secret", re.compile(r"[A-Za-z0-9_-]{24,}\.[A-Za-z0-9_-]{24,}\.[A-Za-z0-9_-]{24,}")),
)

SECRET_ENV_RE = re.compile(
    r"(?:API_KEY|TOKEN|SECRET|PASSWORD|LICENSE|PRIVATE_KEY|ACCESS_KEY|CLIENT_SECRET|CREDENTIAL)"
)

PLACEHOLDER_VALUES = {
    "",
    "***",
    "xxxx",
    "xxxxx",
    "placeholder",
    "redacted",
    "dummy",
    "example",
}

PLACEHOLDER_PREFIXES = (
    "replace-with-",
    "your-",
    "example-",
    "dummy-",
    "test-",
    "<",
)

ALLOWED_NONSECRET_ENV_VALUES = {
    "ANTHROPIC_MATRIX_MODEL",
    "OPENAI_MATRIX_MODEL",
    "GEMINI_MATRIX_MODEL",
    "CLICKHOUSE_PORT",
    "CLICKHOUSE_SECURE",
    "CLICKHOUSE_ALLOW_WRITE_ACCESS",
}


def main() -> int:
    failures = check_secret_hygiene()
    if failures:
        print("\n".join(sorted(failures)))
        return 1
    print("secret hygiene check passed")
    return 0


def check_secret_hygiene(
    root: Path = ROOT,
    tracked_paths: list[Path] | None = None,
) -> list[str]:
    failures: list[str] = []
    tracked = tracked_paths or _git_tracked_paths(root)
    tracked_rel = {_rel(path, root).as_posix() for path in tracked}

    if ".env" in tracked_rel:
        failures.append(".env: local secret file must not be tracked")
    if ENV_SAMPLE not in tracked_rel:
        failures.append(f"{ENV_SAMPLE}: missing tracked masked environment sample")

    if tracked_paths is None:
        failures.extend(_check_env_is_ignored(root))
    failures.extend(_scan_tracked_files(root, tracked))
    failures.extend(_check_env_sample(root / ENV_SAMPLE, root))
    return failures


def _git_tracked_paths(root: Path = ROOT) -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=root,
        check=True,
        capture_output=True,
    )
    return [root / item.decode("utf-8") for item in result.stdout.split(b"\0") if item]


def _check_env_is_ignored(root: Path = ROOT) -> list[str]:
    if not (root / ".git").exists():
        return []
    result = subprocess.run(
        ["git", "check-ignore", "-q", ".env"],
        cwd=root,
        check=False,
    )
    if result.returncode == 0:
        return []
    return [".gitignore: .env must be ignored"]


def _scan_tracked_files(root: Path, paths: list[Path]) -> list[str]:
    failures: list[str] = []
    for path in paths:
        if _is_binary(path):
            continue
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue
        rel = _rel(path, root)
        for line_number, line in enumerate(lines, start=1):
            for label, pattern in SECRET_PATTERNS:
                if pattern.search(line):
                    failures.append(f"{rel}:{line_number}: possible tracked {label}")
    return failures


def _check_env_sample(path: Path, root: Path = ROOT) -> list[str]:
    failures: list[str] = []
    rel = _rel(path, root)
    if not path.exists():
        return [f"{rel}: missing"]

    seen: dict[str, int] = {}
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'\"")
        if key in seen:
            failures.append(f"{rel}:{line_number}: duplicate env key {key}")
        seen[key] = line_number
        if key in ALLOWED_NONSECRET_ENV_VALUES:
            continue
        if SECRET_ENV_RE.search(key) and not _is_placeholder(value):
            failures.append(f"{rel}:{line_number}: credential-like key {key} must be blank or masked")
    return failures


def _is_placeholder(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized in PLACEHOLDER_VALUES:
        return True
    return any(normalized.startswith(prefix) for prefix in PLACEHOLDER_PREFIXES)


def _is_binary(path: Path) -> bool:
    try:
        chunk = path.read_bytes()[:1024]
    except OSError:
        return True
    return b"\0" in chunk


def _rel(path: Path, root: Path = ROOT) -> Path:
    try:
        return path.relative_to(root)
    except ValueError:
        return path


if __name__ == "__main__":
    raise SystemExit(main())
