from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap
import unittest

from scripts.check_ci_surface import check_ci_surface


ROOT = Path(__file__).resolve().parents[1]


class CheckCiSurfaceScriptTests(unittest.TestCase):
    def test_script_passes_current_repo(self):
        result = subprocess.run(
            [sys.executable, "scripts/check_ci_surface.py"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("CI surface check passed", result.stdout)

    def test_accepts_minimal_valid_ci_surface(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            workflow = root / ".github" / "workflows"
            workflow.mkdir(parents=True)
            (workflow / "ci.yml").write_text(_valid_ci(), encoding="utf-8")

            failures = check_ci_surface(root)

        self.assertEqual([], failures)

    def test_rejects_missing_critical_ci_invariants(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            workflow = root / ".github" / "workflows"
            workflow.mkdir(parents=True)
            (workflow / "ci.yml").write_text(
                textwrap.dedent(
                    """
                    name: ci

                    on:
                      push:

                    jobs:
                      test:
                        runs-on: ubuntu-latest
                        steps:
                          - uses: actions/checkout@main
                          - uses: ./local-action
                          - run: python -m unittest discover -s tests -q --env-file .env
                    """
                ).lstrip(),
                encoding="utf-8",
            )

            failures = check_ci_surface(root)

        joined = "\n".join(failures)
        self.assertIn("missing push and pull request triggers", joined)
        self.assertIn("missing read-only workflow permissions", joined)
        self.assertIn("missing strict matrix coverage suite", joined)
        self.assertIn("missing live Claude judge secret", joined)
        self.assertIn("action must not pin to a mutable ref: actions/checkout@main", joined)
        self.assertIn("action is not pinned with a version: ./local-action", joined)
        self.assertIn("CI must not depend on local .env files", joined)


def _valid_ci() -> str:
    return textwrap.dedent(
        """
        name: ci

        on:
          push:
          pull_request:

        permissions:
          contents: read

        jobs:
          test:
            runs-on: ubuntu-latest
            steps:
              - uses: actions/checkout@v4
              - uses: actions/setup-python@v5
                with:
                  python-version: "3.11"
              - run: python scripts/check_ci_surface.py
              - run: python scripts/check_surface_inventory.py
              - run: python scripts/check_regression_ownership.py
              - run: python scripts/check_artifact_format.py
              - run: python -m compileall claude_agent_harness_opt scripts
              - run: python -m unittest discover -s tests -q
              - run: python -m claude_agent_harness_opt matrix-coverage-suite evals/model_matrix evals/targets/gstack/gstack_skill_selection_matrix.json --strict --out /tmp/model-matrix-coverage-suite.json
              - run: python -m claude_agent_harness_opt matrix-coverage evals/model_matrix/zymtrace_mcp_tool_selection.json --strict --out /tmp/zymtrace-coverage.json
              - run: python -m claude_agent_harness_opt model-matrix evals/model_matrix/harness_trace_adapters.json --live --require-live --providers trace_fixture
              - name: Run live Claude semantic judge
                env:
                  ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
                run: |
                  test -n "$ANTHROPIC_API_KEY"
                  python -m claude_agent_harness_opt audit-agent evals/examples/agent_audit_bundle.json --claude-judge
                  python -m claude_agent_harness_opt optimize-tools evals/examples/agent_audit_bundle.json --claude-judge
                  python -m claude_agent_harness_opt model-matrix evals/model_matrix/coding_tool_selection.json --live --require-live
                  python -m claude_agent_harness_opt grind-harness evals/model_matrix/coding_tool_selection.json --live --require-live
              - run: if python -m claude_agent_harness_opt audit-agent evals/examples/agent_audit_missing_value_bar.json; then exit 1; fi
              - run: if env -u ANTHROPIC_API_KEY python -m claude_agent_harness_opt audit-agent evals/examples/agent_audit_bundle.json --claude-judge; then exit 1; fi
              - run: if env -u ANTHROPIC_API_KEY python -m claude_agent_harness_opt optimize-tools evals/examples/agent_audit_bundle.json --claude-judge; then exit 1; fi
              - run: if env -u ANTHROPIC_API_KEY python -m claude_agent_harness_opt model-matrix evals/model_matrix/coding_tool_selection.json --live --require-live; then exit 1; fi
              - run: if env -u ANTHROPIC_API_KEY python -m claude_agent_harness_opt grind-harness evals/model_matrix/coding_tool_selection.json --live --require-live; then exit 1; fi
        """
    ).lstrip()


if __name__ == "__main__":
    unittest.main()
