from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from scripts.check_command_surfaces import (
    Invocation,
    ScriptContract,
    _check_cli_parse_contract,
    _check_script_choices,
    _check_script_required_args,
    _check_script_value_types,
    _extract_cli_invocations,
    _extract_script_contract,
    _extract_script_options,
    _extract_script_invocations,
    _parse_only_args,
    check_command_surfaces,
)


ROOT = Path(__file__).resolve().parents[1]


class CheckCommandSurfacesScriptTests(unittest.TestCase):
    def test_script_passes_current_repo(self):
        result = subprocess.run(
            [sys.executable, "scripts/check_command_surfaces.py"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("command surface check passed", result.stdout)

    def test_command_surface_check_rejects_drift(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "scripts").mkdir()
            (root / ".github" / "workflows").mkdir(parents=True)
            (root / "fixtures").mkdir()
            (root / "fixtures" / "known.json").write_text("{}", encoding="utf-8")
            (root / "scripts" / "check_example.py").write_text("print('ok')\n", encoding="utf-8")
            (root / "scripts" / "known_helper.py").write_text(
                "import argparse\n"
                "parser = argparse.ArgumentParser()\n"
                "parser.add_argument('--known-script-flag', action='store_true')\n",
                encoding="utf-8",
            )
            (root / "README.md").write_text(
                "\n".join(
                    [
                        "python -m claude_agent_harness_opt known-command --known-flag fixtures/known.json",
                        "python -m claude_agent_harness_opt known-command --stale-flag fixtures/known.json",
                        "python -m claude_agent_harness_opt stale-command fixtures/missing.json",
                        "python scripts/known_helper.py --known-script-flag fixtures/known.json",
                        "python scripts/known_helper.py --stale-script-flag fixtures/known.json",
                        "python scripts/known_helper.py > fixtures/result_$(date +%F).json",
                        "python scripts/missing_helper.py fixtures/known.json",
                        "python scripts/known_helper.py fixtures/missing.json",
                    ]
                ),
                encoding="utf-8",
            )
            (root / ".github" / "workflows" / "ci.yml").write_text(
                "steps:\n  - run: python scripts/check_example.py\n",
                encoding="utf-8",
            )

            failures = check_command_surfaces(
                root,
                cli_commands={"known-command"},
                cli_options={"known-command": {"--known-flag"}},
            )

        joined = "\n".join(failures)
        self.assertIn("scripts/check_example.py: missing from README Verify it commands", joined)
        self.assertIn("scripts/check_example.py: missing test file", joined)
        self.assertIn("unknown CLI command 'stale-command'", joined)
        self.assertIn("known-command' has unknown option '--stale-flag'", joined)
        self.assertIn("missing local path 'fixtures/missing.json'", joined)
        self.assertIn("known_helper.py' has unknown option '--stale-script-flag'", joined)
        self.assertIn("documented script missing: scripts/missing_helper.py", joined)

    def test_command_surface_check_scans_project_instruction_commands(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "scripts").mkdir()
            (root / "tests").mkdir()
            (root / ".github" / "workflows").mkdir(parents=True)
            (root / "scripts" / "check_example.py").write_text("print('ok')\n", encoding="utf-8")
            (root / "tests" / "test_check_example_script.py").write_text(
                "def test_sample():\n    assert True\n",
                encoding="utf-8",
            )
            (root / "README.md").write_text(
                "python scripts/check_example.py\n"
                "python -m claude_agent_harness_opt known-command\n",
                encoding="utf-8",
            )
            (root / "CLAUDE.md").write_text(
                "python -m claude_agent_harness_opt stale-project-command\n",
                encoding="utf-8",
            )
            (root / ".github" / "workflows" / "ci.yml").write_text(
                "steps:\n  - run: python scripts/check_example.py\n",
                encoding="utf-8",
            )

            failures = check_command_surfaces(
                root,
                cli_commands={"known-command"},
                cli_options={"known-command": set()},
            )

        joined = "\n".join(failures)
        self.assertIn("CLAUDE.md:1", joined)
        self.assertIn("unknown CLI command 'stale-project-command'", joined)

    def test_command_surface_check_scans_pr_packet_reproduction_commands(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "scripts").mkdir()
            (root / "tests").mkdir()
            (root / ".github" / "workflows").mkdir(parents=True)
            (root / "evals" / "pr_packets" / "sample").mkdir(parents=True)
            (root / "scripts" / "check_example.py").write_text("print('ok')\n", encoding="utf-8")
            (root / "tests" / "test_check_example_script.py").write_text(
                "def test_sample():\n    assert True\n",
                encoding="utf-8",
            )
            (root / "README.md").write_text(
                "python scripts/check_example.py\n"
                "python -m claude_agent_harness_opt known-command\n",
                encoding="utf-8",
            )
            (root / "evals" / "pr_packets" / "sample" / "REPRODUCTION.md").write_text(
                "python -m claude_agent_harness_opt stale-packet-command\n",
                encoding="utf-8",
            )
            (root / ".github" / "workflows" / "ci.yml").write_text(
                "steps:\n  - run: python scripts/check_example.py\n",
                encoding="utf-8",
            )

            failures = check_command_surfaces(
                root,
                cli_commands={"known-command"},
                cli_options={"known-command": set()},
            )

        joined = "\n".join(failures)
        self.assertIn("evals/pr_packets/sample/REPRODUCTION.md:1", joined)
        self.assertIn("unknown CLI command 'stale-packet-command'", joined)

    def test_extract_cli_invocations_handles_multiline_commands(self):
        invocations = _extract_cli_invocations(
            Path("README.md"),
            """python -m claude_agent_harness_opt model-matrix \\
  evals/model_matrix/coding_tool_selection.json \\
  --providers anthropic
""",
        )

        self.assertEqual(1, len(invocations))
        self.assertEqual("model-matrix", invocations[0].command)
        self.assertIn("evals/model_matrix/coding_tool_selection.json", invocations[0].tokens)

    def test_cli_parse_contract_rejects_missing_required_arguments(self):
        invocations = [
            Invocation(
                source=Path("README.md"),
                line=1,
                raw="python -m claude_agent_harness_opt render recipes/agentic_search.json",
                command="render",
                tokens=(
                    "python",
                    "-m",
                    "claude_agent_harness_opt",
                    "render",
                    "recipes/agentic_search.json",
                ),
            ),
            Invocation(
                source=Path("README.md"),
                line=2,
                raw="python -m claude_agent_harness_opt upstream-pr-packet result.json",
                command="upstream-pr-packet",
                tokens=(
                    "python",
                    "-m",
                    "claude_agent_harness_opt",
                    "upstream-pr-packet",
                    "result.json",
                ),
            ),
        ]

        failures = _check_cli_parse_contract(invocations)

        self.assertEqual(1, len(failures))
        self.assertIn("README.md:2", failures[0])
        self.assertIn("does not parse", failures[0])

    def test_cli_parse_contract_ignores_inline_reference_tokens(self):
        invocations = [
            Invocation(
                source=Path("docs/surface-inventory.md"),
                line=21,
                raw="python -m claude_agent_harness_opt matrix-coverage-suite`, `python scripts/check.py`",
                command="matrix-coverage-suite",
                tokens=("python", "-m", "claude_agent_harness_opt", "matrix-coverage-suite"),
            )
        ]

        self.assertEqual([], _check_cli_parse_contract(invocations))

    def test_parse_only_args_strip_shell_redirects(self):
        args = _parse_only_args(
            (
                "python",
                "-m",
                "claude_agent_harness_opt",
                "judge-prompt",
                "evals/examples/search_answer.json",
                ">",
                "/tmp/judge-prompt.txt",
            ),
            argument_start=3,
        )

        self.assertEqual(["judge-prompt", "evals/examples/search_answer.json"], args)

    def test_extract_script_invocations_handles_multiline_commands(self):
        invocations = _extract_script_invocations(
            Path("docs/example.md"),
            """python scripts/known_helper.py \\
  fixtures/known.json \\
  --out /tmp/result.json
""",
        )

        self.assertEqual(1, len(invocations))
        self.assertEqual("scripts/known_helper.py", invocations[0].command)
        self.assertIn("fixtures/known.json", invocations[0].tokens)

    def test_extract_script_options_reads_argparse_flags(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "helper.py"
            path.write_text(
                "import argparse\n"
                "parser = argparse.ArgumentParser()\n"
                "parser.add_argument('target', choices=('alpha', 'beta'))\n"
                "parser.add_argument('retries', type=int, nargs='?')\n"
                "parser.add_argument('--required-flag', required=True)\n"
                "parser.add_argument('--known-flag', choices=('fast', 'slow'))\n"
                "parser.add_argument('--count', type=int)\n"
                "parser.add_argument('--boolean-flag', action='store_true')\n"
                "parser.add_argument('-s', '--second-flag')\n",
                encoding="utf-8",
            )

            options = _extract_script_options(path)
            contract = _extract_script_contract(path)

        self.assertEqual(
            {"--boolean-flag", "--count", "--known-flag", "--required-flag", "--second-flag"},
            options,
        )
        self.assertEqual(1, contract.required_positionals)
        self.assertEqual(frozenset({"--required-flag"}), contract.required_options)
        self.assertEqual(
            frozenset({"--count", "--known-flag", "--required-flag", "--second-flag"}),
            contract.value_options,
        )
        self.assertEqual({"--count": "int"}, contract.option_types)
        self.assertEqual({"--known-flag": frozenset({"fast", "slow"})}, contract.option_choices)
        self.assertEqual((frozenset({"alpha", "beta"}), frozenset()), contract.positional_choices)
        self.assertEqual(("", "int"), contract.positional_types)

    def test_script_required_args_rejects_missing_positionals_and_options(self):
        invocation = Invocation(
            source=Path("README.md"),
            line=3,
            raw="python scripts/known_helper.py --known-flag",
            command="scripts/known_helper.py",
            tokens=("python", "scripts/known_helper.py", "--known-flag"),
        )
        contract = ScriptContract(
            options=frozenset({"--known-flag", "--required-flag"}),
            required_options=frozenset({"--required-flag"}),
            required_positionals=1,
        )

        failures = _check_script_required_args("README.md:3", invocation, contract)

        joined = "\n".join(failures)
        self.assertIn("missing required option '--required-flag'", joined)
        self.assertIn("has 0 positional argument(s), expected at least 1", joined)

    def test_script_required_args_keeps_positionals_after_boolean_flags(self):
        invocation = Invocation(
            source=Path("README.md"),
            line=4,
            raw="python scripts/known_helper.py --boolean-flag target-name",
            command="scripts/known_helper.py",
            tokens=("python", "scripts/known_helper.py", "--boolean-flag", "target-name"),
        )
        contract = ScriptContract(
            options=frozenset({"--boolean-flag"}),
            required_options=frozenset(),
            required_positionals=1,
            value_options=frozenset(),
        )

        self.assertEqual([], _check_script_required_args("README.md:4", invocation, contract))

    def test_script_choices_reject_invalid_documented_values(self):
        invocation = Invocation(
            source=Path("README.md"),
            line=5,
            raw="python scripts/known_helper.py --mode turbo gamma",
            command="scripts/known_helper.py",
            tokens=("python", "scripts/known_helper.py", "--mode", "turbo", "gamma"),
        )
        contract = ScriptContract(
            options=frozenset({"--mode"}),
            required_options=frozenset(),
            required_positionals=1,
            value_options=frozenset({"--mode"}),
            option_choices={"--mode": frozenset({"fast", "slow"})},
            positional_choices=(frozenset({"alpha", "beta"}),),
        )

        failures = _check_script_choices("README.md:5", invocation, contract)

        joined = "\n".join(failures)
        self.assertIn("option '--mode' has invalid choice 'turbo'", joined)
        self.assertIn("positional 1 has invalid choice 'gamma'", joined)

    def test_script_value_types_reject_invalid_documented_values(self):
        invocation = Invocation(
            source=Path("README.md"),
            line=6,
            raw="python scripts/known_helper.py --count lots target-name nope",
            command="scripts/known_helper.py",
            tokens=(
                "python",
                "scripts/known_helper.py",
                "--count",
                "lots",
                "target-name",
                "nope",
            ),
        )
        contract = ScriptContract(
            options=frozenset({"--count"}),
            required_options=frozenset(),
            required_positionals=1,
            value_options=frozenset({"--count"}),
            option_types={"--count": "int"},
            positional_types=("", "int"),
        )

        failures = _check_script_value_types("README.md:6", invocation, contract)

        joined = "\n".join(failures)
        self.assertIn("option '--count' expects int, got 'lots'", joined)
        self.assertIn("positional 2 expects int, got 'nope'", joined)

    def test_extract_cli_invocations_stops_at_inline_code_span(self):
        invocations = _extract_cli_invocations(
            Path("docs/surface-inventory.md"),
            "| Surface | Gate | Artifact |\n"
            "|---|---|---|\n"
            "| Matrix | `python -m claude_agent_harness_opt matrix-coverage-suite`, "
            "`python scripts/check_finding_packets.py` | `tests/test_matrix_coverage.py` |\n",
        )

        self.assertEqual(1, len(invocations))
        self.assertEqual("matrix-coverage-suite", invocations[0].command)
        self.assertEqual(
            ["python", "-m", "claude_agent_harness_opt", "matrix-coverage-suite"],
            list(invocations[0].tokens),
        )


if __name__ == "__main__":
    unittest.main()
