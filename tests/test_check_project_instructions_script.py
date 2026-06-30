from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap
import unittest

from scripts.check_project_instructions import check_project_instructions


ROOT = Path(__file__).resolve().parents[1]


class CheckProjectInstructionsScriptTests(unittest.TestCase):
    def test_script_passes_current_repo(self):
        result = subprocess.run(
            [sys.executable, "scripts/check_project_instructions.py"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("project instruction check passed", result.stdout)

    def test_rejects_missing_instruction_contracts(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            scripts = root / "scripts"
            scripts.mkdir()
            (scripts / "check_sample.py").write_text("#!/usr/bin/env python3\n", encoding="utf-8")
            (scripts / "deslop_check.py").write_text("#!/usr/bin/env python3\n", encoding="utf-8")
            (root / "AGENTS.md").write_text("# Agents\n\nNo delegation.\n", encoding="utf-8")
            (root / "CLAUDE.md").write_text(
                textwrap.dedent(
                    """
                    # Claude

                    Thin instructions.
                    """
                ),
                encoding="utf-8",
            )

            failures = check_project_instructions(root)

        joined = "\n".join(failures)
        self.assertIn("AGENTS.md: missing required instruction phrase: See [CLAUDE.md](CLAUDE.md)", joined)
        self.assertIn("CLAUDE.md: missing required instruction phrase: evals/model_matrix", joined)
        self.assertIn("CLAUDE.md: missing gate script reference scripts/check_sample.py", joined)

    def test_rejects_stale_repo_references(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            scripts = root / "scripts"
            scripts.mkdir()
            (root / "AGENTS.md").write_text(
                "# Agents\n\nSee [CLAUDE.md](CLAUDE.md).\nadversarially-confirmed to add value\n",
                encoding="utf-8",
            )
            (root / "CLAUDE.md").write_text(
                "# Claude\n\nclaude-agent-harness-optimization\n",
                encoding="utf-8",
            )

            failures = check_project_instructions(root)

        self.assertIn("CLAUDE.md: contains stale repository reference claude-agent-harness-optimization", failures)


if __name__ == "__main__":
    unittest.main()
