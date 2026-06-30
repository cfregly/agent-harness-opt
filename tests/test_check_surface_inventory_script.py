from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from scripts.check_surface_inventory import (
    REQUIRED_SURFACES,
    check_surface_inventory,
)


ROOT = Path(__file__).resolve().parents[1]


class CheckSurfaceInventoryScriptTests(unittest.TestCase):
    def test_script_passes_current_repo(self):
        result = subprocess.run(
            [sys.executable, "scripts/check_surface_inventory.py"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("surface inventory check passed", result.stdout)

    def test_accepts_minimal_valid_inventory(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            _write_minimal_repo(root)

            failures = check_surface_inventory(root)

        self.assertEqual([], failures)

    def test_rejects_missing_surface_gate_path_and_eval_root(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            _write_minimal_repo(root)
            inventory = root / "docs" / "surface-inventory.md"
            text = inventory.read_text(encoding="utf-8")
            text = text.replace("`python scripts/check_package_surface.py`, ", "")
            text = text.replace("`claude_agent_harness_opt/*.py`", "")
            text = "\n".join(
                line
                for line in text.splitlines()
                if not line.startswith("| Surface Inventory |")
            )
            inventory.write_text(text, encoding="utf-8")
            (root / "evals" / "new_root").mkdir(parents=True)

            failures = check_surface_inventory(root)

        joined = "\n".join(failures)
        self.assertIn("missing surface row 'Surface Inventory'", joined)
        self.assertIn("Package Metadata And Imports: missing owned path token `claude_agent_harness_opt/*.py`", joined)
        self.assertIn("Package Metadata And Imports: missing gate token `python scripts/check_package_surface.py`", joined)
        self.assertIn("missing eval root `evals/new_root`", joined)

    def test_rejects_file_outside_inventory_patterns(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            _write_minimal_repo(root)
            _touch(root / "unowned" / "surface.bin")

            failures = check_surface_inventory(root)

        joined = "\n".join(failures)
        self.assertIn(
            "unowned/surface.bin: tracked file is not covered by docs/surface-inventory.md",
            joined,
        )


def _write_minimal_repo(root: Path) -> None:
    all_paths: set[str] = set()
    all_gates: set[str] = set()
    for contract in REQUIRED_SURFACES:
        all_paths.update(contract.paths)
        all_paths.update(contract.artifacts)
        all_gates.update(contract.gates)

    for rel in sorted(all_paths):
        _touch_sample_path(root, rel)

    for gate in sorted(all_gates):
        if gate.startswith("python scripts/"):
            script = root / gate.split()[1]
            _touch(script)
            if script.name.startswith("check_"):
                _touch(root / "tests" / f"test_{script.stem}_script.py")

    eval_roots = {
        "checks",
        "e2e",
        "examples",
        "live_harnesses",
        "model_matrix",
        "pr_packets",
        "results",
        "suites",
        "targets",
    }
    for name in eval_roots:
        (root / "evals" / name).mkdir(parents=True, exist_ok=True)

    inventory = _render_inventory_doc()
    (root / "docs").mkdir(parents=True, exist_ok=True)
    (root / "docs" / "surface-inventory.md").write_text(inventory, encoding="utf-8")

    gate_text = "\n".join(sorted(all_gates))
    (root / "README.md").write_text(
        f"# claude-agent-harness-opt\n\ndocs/surface-inventory.md\n\n{gate_text}\n",
        encoding="utf-8",
    )
    (root / "CLAUDE.md").write_text(f"# CLAUDE.md\n\n{gate_text}\n", encoding="utf-8")
    _touch(root / ".github" / "workflows" / "ci.yml")
    (root / ".github" / "workflows" / "ci.yml").write_text(gate_text, encoding="utf-8")


def _render_inventory_doc() -> str:
    lines = [
        "# Surface Inventory",
        "",
        "This is the coverage contract.",
        "",
        "## Inventory",
        "",
        "| Surface | Owned Paths | Required Gates | Regression Material |",
        "|---|---|---|---|",
    ]
    for contract in REQUIRED_SURFACES:
        paths = ", ".join(f"`{item}`" for item in contract.paths)
        gates = ", ".join(f"`{item}`" for item in contract.gates)
        artifacts = ", ".join(f"`{item}`" for item in contract.artifacts)
        lines.append(f"| {contract.name} | {paths} | {gates} | {artifacts} |")
    return "\n".join(lines) + "\n"


def _touch_sample_path(root: Path, pattern: str) -> None:
    if "*" not in pattern:
        _touch(root / pattern)
        return
    sample = pattern
    sample = sample.replace("**/*.json", "sample/sample.json")
    sample = sample.replace("**/*.md", "sample/sample.md")
    sample = sample.replace("*/README.md", "sample/README.md")
    sample = sample.replace("*/*", "sample/file.txt")
    sample = sample.replace("*.json", "sample.json")
    sample = sample.replace("*.md", "sample.md")
    sample = sample.replace("*.py", "sample.py")
    sample = sample.replace("*", "sample")
    _touch(root / sample)


def _touch(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text("sample\n", encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
