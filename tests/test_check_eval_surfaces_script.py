from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

from scripts.check_eval_surfaces import (
    DisappearedDuringCheck,
    ROOT,
    _check_e2e_specs,
    _check_example_fixtures,
    _check_live_harness_specs,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


class CheckEvalSurfacesScriptTests(unittest.TestCase):
    def test_script_passes_current_repo(self):
        result = subprocess.run(
            [sys.executable, "scripts/check_eval_surfaces.py"],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("eval surface check passed", result.stdout)

    def test_e2e_surface_check_rejects_mutating_or_assertionless_specs(self):
        path = ROOT / "evals" / "e2e" / "temporary_bad_e2e.json"
        path.write_text(
            """
{
  "name": "bad e2e",
  "env": {"required": ["TOKEN"]},
  "checks": [
    {
      "method": "POST",
      "name": "mutating call",
      "read_only": false,
      "type": "http_json",
      "url": "https://example.test/mutate"
    }
  ]
}
""",
            encoding="utf-8",
        )
        try:
            failures = _check_e2e_specs()
        finally:
            path.unlink()

        joined = "\n".join(failures)
        self.assertIn("temporary_bad_e2e.json", joined)
        self.assertIn("method must be GET or HEAD", joined)
        self.assertIn("read_only must be true", joined)
        self.assertIn("missing JSON expectation", joined)

    def test_example_surface_check_rejects_unclassified_fixtures(self):
        path = ROOT / "evals" / "examples" / "temporary_unclassified.json"
        path.write_text('{"name": "unclassified"}\n', encoding="utf-8")
        try:
            failures = _check_example_fixtures()
        finally:
            path.unlink()

        joined = "\n".join(failures)
        self.assertIn("temporary_unclassified.json", joined)
        self.assertIn("unclassified example fixture shape", joined)

    def test_live_harness_surface_check_rejects_missing_prompt_and_adapter(self):
        path = ROOT / "evals" / "live_harnesses" / "temporary_bad_live.json"
        path.write_text(
            """
{
  "name": "bad live harness",
  "value_bar": {"claim": "Bad spec."},
  "cases": [{"name": "case without prompt"}],
  "harnesses": [
    {
      "name": "missing adapter",
      "command": ["python", "scripts/missing_live_helper.py"],
      "version_command": ["python", "scripts/missing_live_helper.py", "--version"]
    }
  ]
}
""",
            encoding="utf-8",
        )
        try:
            failures = _check_live_harness_specs()
        finally:
            path.unlink()

        joined = "\n".join(failures)
        self.assertIn("temporary_bad_live.json", joined)
        self.assertIn("value_bar.adversarial_check must be present", joined)
        self.assertIn("cases[0] missing prompt_template", joined)
        self.assertIn("harnesses[0] missing adapter", joined)
        self.assertIn("harnesses[0] missing marker", joined)
        self.assertIn("harnesses[0] missing expected_tool", joined)
        self.assertIn("harnesses[0] expected_args_contains must be a nonempty object", joined)
        self.assertIn("harnesses[0].command[1] local path missing", joined)
        self.assertIn("harnesses[0].version_command[1] local path missing", joined)

    def test_live_harness_surface_skips_disappearing_glob_results(self):
        with patch(
            "scripts.check_eval_surfaces._load_object",
            side_effect=DisappearedDuringCheck("gone"),
        ):
            failures = _check_live_harness_specs()

        self.assertEqual([], failures)


if __name__ == "__main__":
    unittest.main()
