from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from scripts.check_secret_hygiene import check_secret_hygiene


ROOT = Path(__file__).resolve().parents[1]


class CheckSecretHygieneScriptTests(unittest.TestCase):
    def test_script_passes_current_repo(self):
        result = subprocess.run(
            [sys.executable, "scripts/check_secret_hygiene.py"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("secret hygiene check passed", result.stdout)

    def test_rejects_tracked_secret_patterns_without_echoing_secret(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            sample = root / ".env.example"
            sample.write_text("ANTHROPIC_API_KEY=\n", encoding="utf-8")
            leaked = root / "leak.txt"
            secret = "sk-ant-api03-" + "A" * 48
            leaked.write_text(f"token={secret}\n", encoding="utf-8")

            failures = check_secret_hygiene(root, tracked_paths=[sample, leaked])

        joined = "\n".join(failures)
        self.assertIn("possible tracked anthropic api key", joined)
        self.assertNotIn(secret, joined)

    def test_rejects_unsafe_env_sample_values_and_duplicates(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            sample = root / ".env.example"
            sample.write_text(
                "\n".join(
                    [
                        "OPENAI_API_KEY=sk-proj-" + "A" * 40,
                        "OPENAI_API_KEY=replace-with-openai-key",
                        "ZYMTRACE_LICENSE_KEY=replace-with-zymtrace-license-jwt",
                        "CLICKHOUSE_PORT=8443",
                    ]
                ),
                encoding="utf-8",
            )

            failures = check_secret_hygiene(root, tracked_paths=[sample])

        joined = "\n".join(failures)
        self.assertIn("possible tracked openai api key", joined)
        self.assertIn("credential-like key OPENAI_API_KEY must be blank or masked", joined)
        self.assertIn("duplicate env key OPENAI_API_KEY", joined)
        self.assertNotIn("CLICKHOUSE_PORT", joined)


if __name__ == "__main__":
    unittest.main()
