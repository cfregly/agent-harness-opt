#!/usr/bin/env python3
"""Validate the documented surface inventory crosswalk."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import subprocess


ROOT = Path(__file__).resolve().parents[1]
INVENTORY = Path("docs/surface-inventory.md")
README = Path("README.md")
CLAUDE = Path("CLAUDE.md")
CI_WORKFLOW = Path(".github/workflows/ci.yml")


@dataclass(frozen=True)
class SurfaceContract:
    name: str
    paths: tuple[str, ...]
    gates: tuple[str, ...]
    artifacts: tuple[str, ...]


REQUIRED_SURFACES = (
    SurfaceContract(
        name="Project Instructions",
        paths=("AGENTS.md", "CLAUDE.md"),
        gates=("python scripts/check_project_instructions.py",),
        artifacts=("CLAUDE.md", "AGENTS.md"),
    ),
    SurfaceContract(
        name="Package Metadata And Imports",
        paths=("pyproject.toml", "LICENSE", ".gitignore", "claude_agent_harness_opt/*.py"),
        gates=(
            "python scripts/check_package_surface.py",
            "python -m compileall claude_agent_harness_opt scripts",
            "python -m unittest discover -s tests -q",
        ),
        artifacts=("tests/test_check_package_surface_script.py", "tests/test_cli.py"),
    ),
    SurfaceContract(
        name="CLI And Command Examples",
        paths=(
            "claude_agent_harness_opt/cli.py",
            "README.md",
            "CLAUDE.md",
            "AGENTS.md",
            "docs/**/*.md",
            "evals/pr_packets/**/*.md",
            ".github/workflows/ci.yml",
        ),
        gates=("python scripts/check_command_surfaces.py", "python scripts/check_cli_coverage.py"),
        artifacts=("tests/test_check_command_surfaces_script.py", "tests/test_check_cli_coverage_script.py"),
    ),
    SurfaceContract(
        name="Prompt And Recipe Assets",
        paths=("recipes/*.json", "prompts/*.md"),
        gates=("python scripts/check_prompt_recipe_surfaces.py",),
        artifacts=("tests/test_check_prompt_recipe_surfaces_script.py", "evals/examples/search_answer.json"),
    ),
    SurfaceContract(
        name="Project Skill Assets",
        paths=(".claude/skills/agent-audit/SKILL.md", ".claude/skills/agent-audit/agents/openai.yaml"),
        gates=("python scripts/check_skill_surfaces.py",),
        artifacts=("tests/test_check_skill_surfaces_script.py", "evals/model_matrix/agent_audit_skill_selection.json"),
    ),
    SurfaceContract(
        name="Model Matrix Surfaces",
        paths=("evals/model_matrix/*.json", "evals/targets/**/*.json"),
        gates=(
            "python -m claude_agent_harness_opt matrix-coverage-suite",
            "python scripts/check_finding_packets.py",
        ),
        artifacts=(
            "evals/results/model_matrix_coverage_suite_2026-06-30.json",
            "tests/test_matrix_coverage.py",
        ),
    ),
    SurfaceContract(
        name="Eval Fixture Surfaces",
        paths=(
            "evals/examples/*",
            "evals/e2e/*.json",
            "evals/live_harnesses/*.json",
            "evals/suites/*.json",
            "evals/checks/*.json",
        ),
        gates=("python scripts/check_eval_surfaces.py", "python scripts/check_local_config.py"),
        artifacts=("tests/test_check_eval_surfaces_script.py", "tests/test_check_local_config_script.py"),
    ),
    SurfaceContract(
        name="Result Receipts And PR Packets",
        paths=("evals/results/*", "evals/pr_packets/*/*", "docs/findings/*/README.md"),
        gates=(
            "python scripts/check_finding_packets.py",
            "python scripts/check_artifact_surfaces.py",
            "python scripts/check_value_bar.py",
        ),
        artifacts=("evals/pr_packets/zymtrace_mcp_tool_tuning_2026-06-30/evidence.json", "docs/confirmed-improvements.md"),
    ),
    SurfaceContract(
        name="Credential And Local Config",
        paths=(".env.example", "docs/setup.md", "docs/credentialed-service-probes.md", "scripts/probe_service_keys.py"),
        gates=("python scripts/check_secret_hygiene.py", "python scripts/check_local_config.py"),
        artifacts=("evals/e2e/github_readonly.json", "docs/credentialed-service-probes.md"),
    ),
    SurfaceContract(
        name="Docs Navigation And Sources",
        paths=("README.md", "docs/**/*.md", "docs/source-map.md"),
        gates=(
            "python scripts/deslop_check.py",
            "python scripts/check_docs_navigation.py",
            "python scripts/check_source_map.py",
            "python scripts/check_public_links.py",
        ),
        artifacts=("docs/source-map.md", "docs/video-coverage-audit.md"),
    ),
    SurfaceContract(
        name="Shortcut Runner And Make Targets",
        paths=("scripts/optimize_mcp.py", "Makefile"),
        gates=(
            "python scripts/check_makefile_surface.py",
            "python scripts/check_optimize_shortcuts.py",
            "python scripts/check_docs_navigation.py",
        ),
        artifacts=(
            "evals/model_matrix/zymtrace_mcp_tool_selection.json",
            "tests/test_check_makefile_surface_script.py",
            "tests/test_optimize_mcp_script.py",
        ),
    ),
    SurfaceContract(
        name="CI Workflow",
        paths=(".github/workflows/ci.yml",),
        gates=("python scripts/check_ci_surface.py",),
        artifacts=("tests/test_check_ci_surface_script.py",),
    ),
    SurfaceContract(
        name="Tracked Demo Artifact",
        paths=("demo.gif", "demo.tape", "docs/tool_tuning_demo_sample.txt"),
        gates=("python scripts/check_artifact_surfaces.py",),
        artifacts=("demo.gif", "tests/test_check_artifact_surfaces_script.py"),
    ),
    SurfaceContract(
        name="Generic Artifact Format",
        paths=("**/*.json", "**/*.jsonl", "**/*.md", "**/*.txt", "**/*.yml", "**/*.yaml", "**/*.toml"),
        gates=("python scripts/check_artifact_format.py",),
        artifacts=("tests/test_check_artifact_format_script.py",),
    ),
    SurfaceContract(
        name="Value Bar Ledger",
        paths=(
            "docs/confirmed-improvements.md",
            "evals/examples/agent_audit_bundle.json",
            "evals/examples/agent_audit_missing_value_bar.json",
        ),
        gates=("python scripts/check_value_bar.py",),
        artifacts=("tests/test_check_value_bar_script.py", "evals/examples/agent_audit_missing_value_bar.json"),
    ),
    SurfaceContract(
        name="Surface Inventory",
        paths=("docs/surface-inventory.md", "scripts/check_surface_inventory.py"),
        gates=("python scripts/check_surface_inventory.py",),
        artifacts=("tests/test_check_surface_inventory_script.py",),
    ),
    SurfaceContract(
        name="Gate Scripts And Utilities",
        paths=("scripts/*.py",),
        gates=(
            "python scripts/check_regression_ownership.py",
            "python -m compileall claude_agent_harness_opt scripts",
            "python -m unittest discover -s tests -q",
        ),
        artifacts=(
            "tests/test_check_regression_ownership_script.py",
            "tests/test_check_command_surfaces_script.py",
            "tests/test_optimize_mcp_script.py",
        ),
    ),
    SurfaceContract(
        name="Test Suite",
        paths=("tests/*.py",),
        gates=("python -m unittest discover -s tests -q",),
        artifacts=("tests/test_check_surface_inventory_script.py", "tests/test_cli.py"),
    ),
)


TABLE_ROW_RE = re.compile(r"^\|(.+)\|$")


def main() -> int:
    failures = check_surface_inventory()
    if failures:
        print("\n".join(sorted(failures)))
        return 1
    print("surface inventory check passed")
    return 0


def check_surface_inventory(root: Path = ROOT) -> list[str]:
    inventory_path = root / INVENTORY
    if not inventory_path.exists():
        return [f"{INVENTORY}: missing"]

    text = inventory_path.read_text(encoding="utf-8")
    rows = _parse_surface_rows(text)
    failures: list[str] = []
    failures.extend(_check_inventory_doc_shape(root, text))
    failures.extend(_check_surface_rows(root, rows))
    failures.extend(_check_discovered_gate_scripts(root, text))
    failures.extend(_check_eval_roots(root, text))
    failures.extend(_check_gate_locations(root, _contract_gates()))
    failures.extend(_check_tracked_file_coverage(root))
    return failures


def _parse_surface_rows(text: str) -> dict[str, tuple[str, str, str]]:
    rows: dict[str, tuple[str, str, str]] = {}
    for line in text.splitlines():
        match = TABLE_ROW_RE.match(line.strip())
        if not match:
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 4:
            continue
        if cells[0].casefold() == "surface" or set(cells[0]) <= {"-", " "}:
            continue
        rows[cells[0]] = (cells[1], cells[2], cells[3])
    return rows


def _check_inventory_doc_shape(root: Path, text: str) -> list[str]:
    failures: list[str] = []
    if not text.startswith("# Surface Inventory\n"):
        failures.append(f"{INVENTORY}: first line must be '# Surface Inventory'")
    if "coverage contract" not in text.casefold():
        failures.append(f"{INVENTORY}: missing coverage contract section")
    readme = _read_text(root / README)
    if INVENTORY.as_posix() not in readme:
        failures.append(f"{README}: missing navigation link for {INVENTORY}")
    return failures


def _check_surface_rows(root: Path, rows: dict[str, tuple[str, str, str]]) -> list[str]:
    failures: list[str] = []
    required_names = {contract.name for contract in REQUIRED_SURFACES}
    seen_names = set(rows)
    for missing in sorted(required_names - seen_names):
        failures.append(f"{INVENTORY}: missing surface row {missing!r}")
    for extra in sorted(seen_names - required_names):
        failures.append(f"{INVENTORY}: unknown surface row {extra!r}")

    for contract in REQUIRED_SURFACES:
        row = rows.get(contract.name)
        if row is None:
            continue
        path_cell, gate_cell, artifact_cell = row
        failures.extend(_check_tokens(contract.name, "owned path", contract.paths, path_cell))
        failures.extend(_check_tokens(contract.name, "gate", contract.gates, gate_cell))
        failures.extend(_check_tokens(contract.name, "regression material", contract.artifacts, artifact_cell))
        failures.extend(_check_path_patterns(root, contract.name, contract.paths + contract.artifacts))
    return failures


def _check_tokens(surface: str, label: str, required: tuple[str, ...], cell: str) -> list[str]:
    tokens = set(_code_spans(cell))
    return [
        f"{INVENTORY}: {surface}: missing {label} token `{token}`"
        for token in required
        if token not in tokens
    ]


def _check_path_patterns(root: Path, surface: str, patterns: tuple[str, ...]) -> list[str]:
    failures: list[str] = []
    for pattern in patterns:
        if pattern.startswith("python "):
            continue
        matches = _matches(root, pattern)
        if not matches:
            failures.append(f"{INVENTORY}: {surface}: path pattern has no matches: {pattern}")
    return failures


def _check_discovered_gate_scripts(root: Path, text: str) -> list[str]:
    failures: list[str] = []
    scripts = [*sorted((root / "scripts").glob("check_*.py")), root / "scripts" / "deslop_check.py"]
    for script in scripts:
        if not script.exists():
            continue
        rel = script.relative_to(root).as_posix()
        command = f"python {rel}"
        if command not in text:
            failures.append(f"{INVENTORY}: missing discovered gate script `{command}`")
        if script.name.startswith("check_"):
            test_path = root / "tests" / f"test_{script.stem}_script.py"
            if not test_path.exists():
                failures.append(f"{rel}: missing inventory-enforced test file {test_path.relative_to(root)}")
    return failures


def _check_eval_roots(root: Path, text: str) -> list[str]:
    evals_dir = root / "evals"
    if not evals_dir.exists():
        return ["evals: missing"]
    failures: list[str] = []
    for child in sorted(path for path in evals_dir.iterdir() if path.is_dir()):
        rel = child.relative_to(root).as_posix()
        if rel not in text:
            failures.append(f"{INVENTORY}: missing eval root `{rel}`")
    return failures


def _check_gate_locations(root: Path, gates: set[str]) -> list[str]:
    files = {
        README: _read_text(root / README),
        CLAUDE: _read_text(root / CLAUDE),
        CI_WORKFLOW: _read_text(root / CI_WORKFLOW),
    }
    failures: list[str] = []
    for gate in sorted(gates):
        if gate.startswith("python scripts/"):
            script_path = root / gate.split()[1]
            if not script_path.exists():
                failures.append(f"{INVENTORY}: gate script missing: {gate}")
        for path, text in files.items():
            if gate not in text:
                failures.append(f"{path}: missing inventory gate command `{gate}`")
    return failures


def _check_tracked_file_coverage(root: Path) -> list[str]:
    covered = {path.as_posix() for path in _covered_paths(root)}
    failures: list[str] = []
    for path in _tracked_files(root):
        rel = path.as_posix()
        if rel not in covered:
            failures.append(f"{rel}: tracked file is not covered by {INVENTORY} owner or artifact patterns")
    return failures


def _contract_gates() -> set[str]:
    return {gate for contract in REQUIRED_SURFACES for gate in contract.gates}


def _covered_paths(root: Path) -> set[Path]:
    paths: set[Path] = set()
    for contract in REQUIRED_SURFACES:
        for pattern in contract.paths + contract.artifacts:
            if pattern.startswith("python "):
                continue
            for match in _matches(root, pattern):
                if match.is_file():
                    paths.add(match.relative_to(root))
    return paths


def _tracked_files(root: Path) -> list[Path]:
    if (root / ".git").exists():
        result = subprocess.run(
            ["git", "ls-files"],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return [Path(line) for line in result.stdout.splitlines() if line.strip()]

    files: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        if ".git" in rel.parts or "__pycache__" in rel.parts:
            continue
        files.append(rel)
    return sorted(files)


def _matches(root: Path, pattern: str) -> list[Path]:
    if any(marker in pattern for marker in "*?["):
        return sorted(root.glob(pattern))
    path = root / pattern
    return [path] if path.exists() else []


def _code_spans(text: str) -> list[str]:
    return re.findall(r"`([^`]+)`", text)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


if __name__ == "__main__":
    raise SystemExit(main())
