from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap
import unittest

from scripts.check_docs_navigation import (
    _check_markdown_docs,
    _check_pyproject_entry_points,
    _check_readme_layout,
    _check_repo_links,
)


ROOT = Path(__file__).resolve().parents[1]


class CheckDocsNavigationScriptTests(unittest.TestCase):
    def test_script_passes_current_repo(self):
        result = subprocess.run(
            [sys.executable, "scripts/check_docs_navigation.py"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("docs/navigation check passed", result.stdout)

    def test_repo_links_reject_missing_local_targets(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            docs = root / "docs"
            docs.mkdir()
            (root / "README.md").write_text(
                "# sample\n\n"
                "[Bad](https://github.com/cfregly/agent-harness-opt/blob/main/docs/missing.md)\n"
                "[Bad tree](https://github.com/cfregly/agent-harness-opt/tree/main/docs/missing)\n",
                encoding="utf-8",
            )

            failures = _check_repo_links(root)

        joined = "\n".join(failures)
        self.assertIn("GitHub blob link target missing file: docs/missing.md", joined)
        self.assertIn("GitHub tree link target missing path: docs/missing", joined)

    def test_markdown_docs_reject_missing_h1_and_stale_repo_slug(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            docs = root / "docs"
            docs.mkdir()
            (root / "README.md").write_text(
                "No H1\nclaude-agent-harness-optimization\n",
                encoding="utf-8",
            )

            failures = _check_markdown_docs(root)

        joined = "\n".join(failures)
        self.assertIn("first nonempty line must be an H1", joined)
        self.assertIn("stale repository reference claude-agent-harness-optimization", joined)

    def test_layout_rejects_missing_readme_layout_paths(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "README.md").write_text(
                textwrap.dedent(
                    """
                    # sample

                    ## Layout

                    ```
                    missing_dir/
                      missing.py # should exist
                    ```
                    """
                ),
                encoding="utf-8",
            )

            failures = _check_readme_layout(root)

        joined = "\n".join(failures)
        self.assertIn("layout directory missing: missing_dir/", joined)
        self.assertIn("layout file missing: missing_dir/missing.py", joined)

    def test_pyproject_entry_points_reject_mismatched_name(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "README.md").write_text("# readme-name\n", encoding="utf-8")
            (root / "pyproject.toml").write_text(
                textwrap.dedent(
                    """
                    [project]
                    name = "package-name"
                    [project.scripts]
                    bad = "missing_module:main"
                    """
                ),
                encoding="utf-8",
            )

            failures = _check_pyproject_entry_points(root)

        joined = "\n".join(failures)
        self.assertIn("project.name must match README H1", joined)
        self.assertIn("script bad target invalid", joined)


if __name__ == "__main__":
    unittest.main()
