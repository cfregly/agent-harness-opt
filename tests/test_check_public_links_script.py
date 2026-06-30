from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap
import unittest

from scripts.check_public_links import check_public_links


ROOT = Path(__file__).resolve().parents[1]


class CheckPublicLinksScriptTests(unittest.TestCase):
    def test_script_passes_current_repo(self):
        result = subprocess.run(
            [sys.executable, "scripts/check_public_links.py"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("public link check passed", result.stdout)

    def test_rejects_local_and_empty_public_links(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            docs = root / "docs"
            docs.mkdir()
            (root / "README.md").write_text(
                textwrap.dedent(
                    """
                    # sample

                    [Local](docs/setup.md)
                    [Empty]()
                    ![Local image](demo.gif)
                    [Mail](mailto:test@example.com)
                    [Remote](https://example.com)

                    ```markdown
                    [Allowed in code](docs/internal.md)
                    ```
                    """
                ),
                encoding="utf-8",
            )
            (docs / "setup.md").write_text("# setup\n", encoding="utf-8")

            failures = check_public_links(root)

        joined = "\n".join(failures)
        self.assertIn("local link target is not shareable: docs/setup.md", joined)
        self.assertIn("empty link target", joined)
        self.assertIn("local image target is not shareable: demo.gif", joined)
        self.assertNotIn("docs/internal.md", joined)

    def test_accepts_angle_bracket_urls_and_fragments(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "README.md").write_text(
                "# sample\n\n[Fragment](#section)\n[Remote](<https://example.com/a-b>)\n",
                encoding="utf-8",
            )

            failures = check_public_links(root)

        self.assertEqual([], failures)

    def test_checks_wrapped_image_link_target(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "README.md").write_text(
                "# sample\n\n[![badge](https://example.com/badge.svg)](docs/local.md)\n",
                encoding="utf-8",
            )

            failures = check_public_links(root)

        self.assertIn("local link target is not shareable: docs/local.md", "\n".join(failures))

    def test_checks_reference_style_links(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "README.md").write_text(
                textwrap.dedent(
                    """
                    # sample

                    [Good][remote]
                    [Bad][local]
                    [Missing][missing]

                    [remote]: https://example.com
                    [local]: docs/local.md
                    """
                ),
                encoding="utf-8",
            )

            failures = check_public_links(root)

        joined = "\n".join(failures)
        self.assertIn("local link target is not shareable: docs/local.md", joined)
        self.assertIn("empty link target", joined)


if __name__ == "__main__":
    unittest.main()
