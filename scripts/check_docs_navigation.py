#!/usr/bin/env python3
"""Validate public documentation, navigation, and package entry points."""

from __future__ import annotations

from pathlib import Path
import importlib
import re
import sys
import tomllib


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
README = ROOT / "README.md"
MAKEFILE = ROOT / "Makefile"
PYPROJECT = ROOT / "pyproject.toml"
PUBLIC_REPO_NAME = "agent-harness-opt"
REPO_URL_RE = re.compile(
    r"https://github\.com/cfregly/agent-harness-opt/(blob|tree)/main/([^)\s#]+)"
)
OLD_REPO_SLUGS = (
    "claude-agent-harness-optimization",
    "ai-performance-engineering",
)


def main() -> int:
    failures = check_docs_navigation()
    if failures:
        print("\n".join(sorted(failures)))
        return 1
    print("docs/navigation check passed")
    return 0


def check_docs_navigation(root: Path = ROOT) -> list[str]:
    failures: list[str] = []
    failures.extend(_check_markdown_docs(root))
    failures.extend(_check_repo_links(root))
    failures.extend(_check_readme_docs_index(root))
    failures.extend(_check_readme_layout(root))
    failures.extend(_check_makefile_help(root))
    failures.extend(_check_pyproject_entry_points(root))
    return failures


def _check_markdown_docs(root: Path = ROOT) -> list[str]:
    failures: list[str] = []
    paths = [root / "README.md", *sorted((root / "docs").rglob("*.md"))]
    for path in paths:
        rel = _rel(path, root)
        lines = path.read_text(encoding="utf-8").splitlines()
        first_nonempty = next((line.strip() for line in lines if line.strip()), "")
        if not first_nonempty.startswith("# "):
            failures.append(f"{rel}: first nonempty line must be an H1")
        text = "\n".join(lines)
        for slug in OLD_REPO_SLUGS:
            if slug in text:
                failures.append(f"{rel}: contains stale repository reference {slug}")
    return failures


def _check_repo_links(root: Path = ROOT) -> list[str]:
    failures: list[str] = []
    paths = [root / "README.md", *sorted((root / "docs").rglob("*.md"))]
    for path in paths:
        rel = _rel(path, root)
        text = path.read_text(encoding="utf-8")
        for match in REPO_URL_RE.finditer(text):
            kind, target = match.groups()
            target_path = root / target.rstrip("/")
            if kind == "blob" and not target_path.is_file():
                failures.append(f"{rel}: GitHub blob link target missing file: {target}")
            if kind == "tree" and not target_path.exists():
                failures.append(f"{rel}: GitHub tree link target missing path: {target}")
    return failures


def _check_readme_docs_index(root: Path = ROOT) -> list[str]:
    readme = (root / "README.md").read_text(encoding="utf-8")
    failures: list[str] = []
    for path in sorted((root / "docs").rglob("*.md")):
        rel = path.relative_to(root).as_posix()
        accepted_targets = _accepted_readme_targets(path, root)
        if not any(target in readme for target in accepted_targets):
            failures.append(f"README.md: missing navigation link for {rel}")
    return failures


def _accepted_readme_targets(path: Path, root: Path = ROOT) -> set[str]:
    rel = path.relative_to(root).as_posix()
    targets = {rel}
    if path.name == "README.md":
        targets.add(path.parent.relative_to(root).as_posix())
    return targets


def _check_readme_layout(root: Path = ROOT) -> list[str]:
    readme = (root / "README.md").read_text(encoding="utf-8")
    block = _extract_layout_block(readme)
    if not block:
        return ["README.md: missing Layout code block"]

    failures: list[str] = []
    current_dir: Path | None = None
    for raw_line in block.splitlines():
        stripped = raw_line.strip()
        if not stripped:
            continue
        entry = stripped.split("#", 1)[0].strip()
        if not entry:
            continue
        if entry.endswith("/"):
            current_dir = Path(entry.rstrip("/"))
            if not (root / current_dir).is_dir():
                failures.append(f"README.md: layout directory missing: {entry}")
            continue
        if entry.endswith(".py"):
            path = (root / current_dir / entry) if current_dir else root / entry
            if not path.is_file():
                failures.append(f"README.md: layout file missing: {path.relative_to(root)}")
            continue
        current_dir = None
    return failures


def _extract_layout_block(readme: str) -> str:
    match = re.search(r"## Layout\s+```(?:text)?\n(.*?)\n```", readme, flags=re.DOTALL)
    return match.group(1) if match else ""


def _check_makefile_help(root: Path = ROOT) -> list[str]:
    path = root / "Makefile"
    if not path.exists():
        return ["Makefile: missing"]
    text = path.read_text(encoding="utf-8")
    phony_match = re.search(r"^\.PHONY:\s*(.+)$", text, flags=re.MULTILINE)
    if not phony_match:
        return ["Makefile: missing .PHONY targets"]
    targets = [target for target in phony_match.group(1).split() if target != "help"]
    failures: list[str] = []
    for target in targets:
        if f"make {target}" not in text:
            failures.append(f"Makefile: help output missing target {target}")
        if not re.search(rf"^{re.escape(target)}:", text, flags=re.MULTILINE):
            failures.append(f"Makefile: .PHONY target has no recipe: {target}")
    return failures


def _check_pyproject_entry_points(root: Path = ROOT) -> list[str]:
    path = root / "pyproject.toml"
    if not path.exists():
        return ["pyproject.toml: missing"]
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    project = data.get("project", {})
    readme_h1 = _readme_h1(root / "README.md")
    failures: list[str] = []
    if readme_h1 != PUBLIC_REPO_NAME:
        failures.append(f"README.md: H1 must be public repo name {PUBLIC_REPO_NAME}")
    scripts = project.get("scripts", {})
    for name, target in scripts.items():
        try:
            module_name, function_name = str(target).split(":", 1)
            module = importlib.import_module(module_name)
            if not callable(getattr(module, function_name)):
                failures.append(f"pyproject.toml: script {name} target is not callable")
        except (ImportError, AttributeError, ValueError) as exc:
            failures.append(f"pyproject.toml: script {name} target invalid: {exc}")
    return failures


def _readme_h1(path: Path) -> str:
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    return ""


def _rel(path: Path, root: Path = ROOT) -> Path:
    try:
        return path.relative_to(root)
    except ValueError:
        return path


if __name__ == "__main__":
    raise SystemExit(main())
