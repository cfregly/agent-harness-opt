from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from scripts.check_artifact_surfaces import (
    _check_result_receipt_reachability,
    _parse_gif,
    check_artifact_surfaces,
)


ROOT = Path(__file__).resolve().parents[1]


class CheckArtifactSurfacesScriptTests(unittest.TestCase):
    def test_script_passes_current_repo(self):
        result = subprocess.run(
            [sys.executable, "scripts/check_artifact_surfaces.py"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("artifact surface check passed", result.stdout)

    def test_parse_gif_reads_demo_dimensions_and_frames(self):
        info = _parse_gif(ROOT / "demo.gif")

        self.assertEqual(1200, info.width)
        self.assertEqual(720, info.height)
        self.assertGreaterEqual(info.frames, 5)

    def test_demo_check_rejects_missing_reference_and_bad_tape_path(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "README.md").write_text("# sample\n", encoding="utf-8")
            (root / "demo.gif").write_bytes((ROOT / "demo.gif").read_bytes())
            (root / "demo.tape").write_text(
                "\n".join(
                    [
                        "# Regenerate from the repo root with: vhs demo.tape",
                        "Output demo.gif",
                        "Set Width 1200",
                        "Set Height 720",
                        'Type "sed -n 1,2p docs/missing.txt"',
                    ]
                ),
                encoding="utf-8",
            )

            failures = check_artifact_surfaces(root)

        joined = "\n".join(failures)
        self.assertIn("README.md: missing public reference to demo.gif", joined)
        self.assertIn("demo.tape: referenced path missing: docs/missing.txt", joined)

    def test_result_receipt_reachability_accepts_linked_markdown_sibling(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            results = root / "evals" / "results"
            docs = root / "docs"
            packets = root / "evals" / "pr_packets"
            results.mkdir(parents=True)
            docs.mkdir()
            packets.mkdir(parents=True)
            (root / "README.md").write_text("# sample\n", encoding="utf-8")
            (docs / "result.md").write_text("See `coverage.md`.\n", encoding="utf-8")
            (results / "coverage.json").write_text("{}", encoding="utf-8")
            (results / "coverage.md").write_text("# coverage\n", encoding="utf-8")
            (results / "orphan.json").write_text("{}", encoding="utf-8")

            failures = _check_result_receipt_reachability(root)

        joined = "\n".join(failures)
        self.assertNotIn("coverage.json", joined)
        self.assertIn("evals/results/orphan.json", joined)


if __name__ == "__main__":
    unittest.main()
