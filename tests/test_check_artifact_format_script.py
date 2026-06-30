from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from scripts.check_artifact_format import check_artifact_format


ROOT = Path(__file__).resolve().parents[1]


class CheckArtifactFormatScriptTests(unittest.TestCase):
    def test_script_passes_current_repo(self):
        result = subprocess.run(
            [sys.executable, "scripts/check_artifact_format.py"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("artifact format check passed", result.stdout)

    def test_accepts_valid_json_jsonl_and_text_artifacts(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            _write(root / "fixture.json", '{"ok": true}\n')
            _write(root / "events.jsonl", '{"type": "one"}\n{"type": "two"}\n')
            _write(root / "README.md", "# Title\n")

            failures = check_artifact_format(
                root,
                tracked_paths=["fixture.json", "events.jsonl", "README.md"],
            )

        self.assertEqual([], failures)

    def test_rejects_invalid_jsonl_newlines_crlf_and_empty_text(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            _write(root / "bad.json", '{"missing": true\n')
            _write(root / "bad.jsonl", '{"ok": true}\n\nnot-json\n')
            (root / "missing_newline.md").write_bytes(b"# Title")
            (root / "crlf.txt").write_bytes(b"line\r\n")
            _write(root / "empty.py", "")

            failures = check_artifact_format(
                root,
                tracked_paths=[
                    "bad.json",
                    "bad.jsonl",
                    "missing_newline.md",
                    "crlf.txt",
                    "empty.py",
                ],
            )

        joined = "\n".join(failures)
        self.assertIn("bad.json: invalid JSON", joined)
        self.assertIn("bad.jsonl:2: blank JSONL line", joined)
        self.assertIn("bad.jsonl:3: invalid JSONL", joined)
        self.assertIn("missing_newline.md: missing trailing newline", joined)
        self.assertIn("crlf.txt: contains CRLF line endings", joined)
        self.assertIn("empty.py: tracked text artifact must not be empty", joined)


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
