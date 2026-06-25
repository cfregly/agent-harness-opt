import subprocess
import sys
import unittest

from claude_agent_harness_optimization.harness_checks import (
    load_check_catalog,
    render_check_catalog_markdown,
)


class HarnessCheckTests(unittest.TestCase):
    def test_catalog_contains_required_check_families(self):
        catalog = load_check_catalog()
        ids = {item["id"] for item in catalog["checks"]}
        self.assertIn("adjacent_tool_boundary", ids)
        self.assertIn("no_tool_safety", ids)
        self.assertIn("argument_quality", ids)
        self.assertIn("directed_thinking", ids)
        self.assertIn("harness_parity", ids)
        self.assertIn("model_migration_api", ids)
        self.assertIn("prompt_migration_eval", ids)
        self.assertIn("reproducibility", ids)
        self.assertIn("Harness Optimization Checks", render_check_catalog_markdown(catalog))

    def test_cli_harness_checks(self):
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "claude_agent_harness_optimization",
                "harness-checks",
                "--markdown",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("Adjacent tool boundary", result.stdout)


if __name__ == "__main__":
    unittest.main()
