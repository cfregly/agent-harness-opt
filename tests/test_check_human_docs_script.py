from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from scripts.check_human_docs import check_human_docs


ROOT = Path(__file__).resolve().parents[1]


class CheckHumanDocsScriptTests(unittest.TestCase):
    def test_script_passes_current_repo(self):
        result = subprocess.run(
            [sys.executable, "scripts/check_human_docs.py"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("human docs check passed", result.stdout)

    def test_rejects_root_machine_sections_above_llm_details(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            _write_readme(
                root,
                extra_before_details="## Layout\n\n```text\npython scripts/check_example.py\n```\n",
            )

            failures = check_human_docs(root)

        joined = "\n".join(failures)
        self.assertIn("README.md: machine section ## Layout appears before LLM details", joined)
        self.assertIn("README.md: checker inventory appears above LLM details", joined)

    def test_rejects_machine_heavy_doc_without_llm_details(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            _write_readme(root)
            docs = root / "docs"
            docs.mkdir()
            (docs / "machine.md").write_text(
                "# Machine Doc\n\n"
                + "\n".join("python scripts/check_example.py" for _ in range(20))
                + "\n",
                encoding="utf-8",
            )

            failures = check_human_docs(root)

        joined = "\n".join(failures)
        self.assertIn("docs/machine.md: machine-heavy doc must end with LLM / Machine-readable details", joined)

    def test_rejects_sendable_packet_without_why_this_matters(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            _write_readme(root)
            finding = root / "docs" / "findings" / "sample"
            finding.mkdir(parents=True)
            (finding / "README.md").write_text(
                "# Sample Finding\n\n"
                "Share link: [Sample](https://github.com/cfregly/claude-agent-harness-opt/tree/main/docs/findings/sample)\n\n"
                "## Evidence Bundle\n\n"
                "Bundle folder: [Sample](https://github.com/cfregly/claude-agent-harness-opt/tree/main/docs/findings/sample)\n",
                encoding="utf-8",
            )

            failures = check_human_docs(root)

        joined = "\n".join(failures)
        self.assertIn("docs/findings/sample/README.md: missing founder-handoff section ## Why This Matters", joined)

    def test_rejects_sendable_packet_without_local_agent_cta(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            _write_readme(root)
            finding = root / "docs" / "findings" / "sample"
            finding.mkdir(parents=True)
            (finding / "README.md").write_text(
                "# Sample Finding\n\n"
                "Share link: [Sample](https://github.com/cfregly/claude-agent-harness-opt/tree/main/docs/findings/sample)\n\n"
                "## Summary\n\n"
                "| Exact change | Before | After | Result |\n|---|---|---|---|\n| Update routing. | Before. | After. | Result. |\n\n"
                "## Why This Matters\n\n"
                "- Value proposition: useful.\n\n"
                "## Recommended Actions\n\n"
                "- Apply exact change.\n\n"
                "## Run This In Your Repo\n\n"
                "Run a local agent.\n\n"
                "## Model Coverage\n\n"
                "- Coverage.\n\n"
                "## Evidence Bundle\n\n"
                "Bundle folder: [Sample](https://github.com/cfregly/claude-agent-harness-opt/tree/main/evals/pr_packets/sample)\n",
                encoding="utf-8",
            )

            failures = check_human_docs(root)

        joined = "\n".join(failures)
        self.assertIn(
            "docs/findings/sample/README.md: missing local-agent CTA marker codex exec -C /path/to/repo --sandbox read-only -",
            joined,
        )
        self.assertIn(
            "docs/findings/sample/README.md: missing local-agent CTA marker claude -p --permission-mode plan",
            joined,
        )
        self.assertIn(
            "docs/findings/sample/README.md: missing local-agent CTA marker gemini --approval-mode plan --output-format text",
            joined,
        )

    def test_rejects_evidence_bundle_before_recommended_actions(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            _write_readme(root)
            packet = root / "evals" / "pr_packets" / "sample"
            packet.mkdir(parents=True)
            (packet / "PR_BODY.md").write_text(
                "Suggested title: Sample\n\n"
                "## Summary\n\n"
                "| Exact change | Before | After | Result |\n|---|---|---|---|\n| Update routing. | Before. | After. | Result. |\n\n"
                "## Evidence Bundle\n\n"
                "Evidence.\n\n"
                "## Why This Matters\n\n"
                "- Value proposition: useful.\n\n"
                "## Recommended Actions\n\n"
                "- Apply exact change.\n\n"
                "## Model Coverage\n\n"
                "- Coverage.\n\n"
                "## Run This In Your Repo\n\n"
                "codex exec -C /path/to/repo --sandbox read-only -\n"
                "claude -p --permission-mode plan\n"
                "gemini --approval-mode plan --output-format text\n"
                "Review this action-first finding:\n"
                "Do not edit files yet.\n",
                encoding="utf-8",
            )

            failures = check_human_docs(root)

        joined = "\n".join(failures)
        self.assertIn("evals/pr_packets/sample/PR_BODY.md: founder-handoff sections are out of order", joined)
        self.assertIn("evals/pr_packets/sample/PR_BODY.md: Evidence Bundle must appear after Run This In Your Repo", joined)

    def test_rejects_pr_body_that_puts_founder_sections_inside_details(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            _write_readme(root)
            packet = root / "evals" / "pr_packets" / "sample"
            packet.mkdir(parents=True)
            (packet / "PR_BODY.md").write_text(
                "Suggested title: Sample\n\n"
                "<details>\n"
                "<summary>LLM / Machine-readable details</summary>\n\n"
                "## Summary\n\n"
                "## Why This Matters\n\n"
                "## Recommended Actions\n\n"
                "## Run This In Your Repo\n\n"
                "## Model Coverage\n\n"
                "## Evidence Bundle\n\n"
                "</details>\n",
                encoding="utf-8",
            )

            failures = check_human_docs(root)

        joined = "\n".join(failures)
        self.assertIn("evals/pr_packets/sample/PR_BODY.md: ## Summary must appear before LLM details", joined)

    def test_rejects_provider_actions_above_target_actions(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            _write_readme(root)
            packet = root / "evals" / "pr_packets" / "sample"
            packet.mkdir(parents=True)
            (packet / "PR_BODY.md").write_text(
                "Suggested title: Sample\n\n"
                "## Summary\n\n"
                "| Exact change | Before | After | Result |\n|---|---|---|---|\n| Update routing. | Before. | After. | Result. |\n\n"
                "## Why This Matters\n\n"
                "- Value proposition: useful.\n\n"
                "## Recommended Actions\n\n"
                "### Anthropic\n\n"
                "- Add provider cases.\n\n"
                "## Run This In Your Repo\n\n"
                "codex exec -C /path/to/repo --sandbox read-only -\n"
                "claude -p --permission-mode plan\n"
                "gemini --approval-mode plan --output-format text\n"
                "Review this action-first finding:\n"
                "Do not edit files yet.\n\n"
                "## Model Coverage\n\n"
                "- Coverage.\n\n"
                "## Evidence Bundle\n\n"
                "Evidence.\n",
                encoding="utf-8",
            )

            failures = check_human_docs(root)

        joined = "\n".join(failures)
        self.assertIn(
            "evals/pr_packets/sample/PR_BODY.md: provider-specific action sections must not appear above target-owned actions",
            joined,
        )

    def test_rejects_duplicate_founder_sections(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            _write_readme(root)
            packet = root / "evals" / "pr_packets" / "sample"
            packet.mkdir(parents=True)
            (packet / "PR_BODY.md").write_text(
                "Suggested title: Sample\n\n"
                "## Summary\n\n"
                "| Exact change | Before | After | Result |\n|---|---|---|---|\n| Update routing. | Before. | After. | Result. |\n\n"
                "## Why This Matters\n\n"
                "- Value proposition: useful.\n\n"
                "## Recommended Actions\n\n"
                "- Apply exact change.\n\n"
                "## Run This In Your Repo\n\n"
                "codex exec -C /path/to/repo --sandbox read-only -\n"
                "claude -p --permission-mode plan\n"
                "gemini --approval-mode plan --output-format text\n"
                "Review this action-first finding:\n"
                "Do not edit files yet.\n\n"
                "## Model Coverage\n\n"
                "- Coverage.\n\n"
                "## Model Coverage\n\n"
                "- Duplicate coverage.\n\n"
                "## Evidence Bundle\n\n"
                "Evidence.\n",
                encoding="utf-8",
            )

            failures = check_human_docs(root)

        joined = "\n".join(failures)
        self.assertIn("evals/pr_packets/sample/PR_BODY.md: duplicate founder-handoff section ## Model Coverage", joined)

    def test_rejects_duplicate_lower_change_and_evidence_sections(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            _write_readme(root)
            packet = root / "evals" / "pr_packets" / "sample"
            packet.mkdir(parents=True)
            (packet / "PR_BODY.md").write_text(
                "Suggested title: Sample\n\n"
                "## Summary\n\n"
                "| Exact change | Before | After | Result |\n|---|---|---|---|\n| Update routing. | Before. | After. | Result. |\n\n"
                "## Why This Matters\n\n"
                "- Value proposition: useful.\n\n"
                "## Recommended Actions\n\n"
                "- Apply exact change.\n\n"
                "## Run This In Your Repo\n\n"
                "codex exec -C /path/to/repo --sandbox read-only -\n"
                "claude -p --permission-mode plan\n"
                "gemini --approval-mode plan --output-format text\n"
                "Review this action-first finding:\n"
                "Do not edit files yet.\n\n"
                "## Model Coverage\n\n"
                "- Coverage.\n\n"
                "## Evidence Bundle\n\n"
                "Bundle.\n\n"
                "## Suggested Change\n\n"
                "Old duplicate.\n\n"
                "## Evidence\n\n"
                "Old duplicate.\n",
                encoding="utf-8",
            )

            failures = check_human_docs(root)

        joined = "\n".join(failures)
        self.assertIn(
            "evals/pr_packets/sample/PR_BODY.md: move ## Suggested Change into the top Summary table or remove the duplicate section",
            joined,
        )
        self.assertIn(
            "evals/pr_packets/sample/PR_BODY.md: use one founder-facing ## Evidence Bundle section, not a second ## Evidence section",
            joined,
        )

    def test_rejects_pr_reproduction_without_supporting_evidence_note(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            _write_readme(root)
            packet = root / "evals" / "pr_packets" / "sample"
            packet.mkdir(parents=True)
            (packet / "REPRODUCTION.md").write_text(
                "# Reproduction\n\n"
                "## Command\n\n"
                "```bash\n"
                "python -m claude_agent_harness_opt model-matrix evals/model_matrix/sample.json\n"
                "```\n",
                encoding="utf-8",
            )

            failures = check_human_docs(root)

        joined = "\n".join(failures)
        self.assertIn(
            "evals/pr_packets/sample/REPRODUCTION.md: supporting evidence doc must say so in the first 24 lines",
            joined,
        )
        self.assertIn(
            "evals/pr_packets/sample/REPRODUCTION.md: supporting evidence doc must point readers to the action-first doc",
            joined,
        )
        self.assertIn(
            "evals/pr_packets/sample/REPRODUCTION.md: supporting evidence doc must name the action-first entrypoint (PR_BODY.md)",
            joined,
        )

    def test_rejects_company_summary_doc_without_action_table(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            _write_readme(root)
            docs = root / "docs"
            docs.mkdir()
            (docs / "confirmed-improvements.md").write_text(
                "# Confirmed Improvements\n\n"
                "## Finding Summaries\n\n"
                "| Target | Finding |\n"
                "|---|---|\n"
                "| Sample | Link |\n",
                encoding="utf-8",
            )

            failures = check_human_docs(root)

        joined = "\n".join(failures)
        self.assertIn("docs/confirmed-improvements.md: missing ## Summary", joined)

    def test_rejects_company_summary_doc_without_exact_change_column(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            _write_readme(root)
            docs = root / "docs"
            docs.mkdir()
            (docs / "confirmed-improvements.md").write_text(
                "# Confirmed Improvements\n\n"
                "## Summary\n\n"
                "| Target | Before | After | Result |\n"
                "|---|---|---|---|\n"
                "| Sample | Baseline failed. | Candidate passed. | Add tests. |\n",
                encoding="utf-8",
            )

            failures = check_human_docs(root)

        joined = "\n".join(failures)
        self.assertIn(
            "docs/confirmed-improvements.md: action summary table must include Exact change, Before, After, and Result columns",
            joined,
        )

    def test_allows_findings_index_shareable_bundle_table_before_llm_details(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            _write_readme(root)
            findings = root / "docs" / "findings"
            findings.mkdir(parents=True)
            (findings / "README.md").write_text(
                "# Founder Findings\n\n"
                "These folders are share links.\n\n"
                "## Shareable Bundles\n\n"
                "| Target | Full bundle | Matrix | Result / coverage |\n"
                "|---|---|---|---|\n"
                + "\n".join(
                    "| Sample | "
                    "[Bundle](https://github.com/cfregly/claude-agent-harness-opt/tree/main/evals/pr_packets/sample) | "
                    "[Matrix](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/model_matrix/sample.json) | "
                    "[Receipt](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/sample.md) |"
                    for _ in range(12)
                )
                + "\n\n"
                "<details>\n"
                "<summary>LLM / Machine-readable details</summary>\n\n"
                "`scripts/check_finding_packets.py` enforces retained PR packets.\n\n"
                "</details>\n",
                encoding="utf-8",
            )

            failures = check_human_docs(root)

        self.assertEqual([], failures)


def _write_readme(root: Path, *, extra_before_details: str = "") -> None:
    root.mkdir(parents=True, exist_ok=True)
    (root / "README.md").write_text(
        "# claude-agent-harness-opt\n\n"
        "A human-first project page.\n\n"
        "## Demo\n\n"
        "Demo text.\n\n"
        "## Share This\n\n"
        "| Audience | Send this |\n|---|---|\n| maintainer | [bundle](https://github.com/cfregly/claude-agent-harness-opt/tree/main/docs/findings/sample) |\n\n"
        "## Quickstart\n\n"
        "Run it.\n\n"
        "## What it implements\n\n"
        "Tools.\n\n"
        "## How It Works\n\n"
        "Steps.\n\n"
        "## Start Here\n\n"
        "Links.\n\n"
        "## Shareable Bundles\n\n"
        "Bundles.\n\n"
        f"{extra_before_details}"
        "<details>\n"
        "<summary>LLM / Machine-readable details</summary>\n\n"
        "## Verify it\n\n"
        "python scripts/check_human_docs.py\n\n"
        "</details>\n\n"
        "## License\n\n"
        "MIT.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    unittest.main()
