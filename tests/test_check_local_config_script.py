from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap
import unittest

from scripts.check_local_config import check_local_config


ROOT = Path(__file__).resolve().parents[1]


class CheckLocalConfigScriptTests(unittest.TestCase):
    def test_script_passes_current_repo(self):
        result = subprocess.run(
            [sys.executable, "scripts/check_local_config.py"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("local config check passed", result.stdout)

    def test_accepts_minimal_valid_config_surface(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            _write_valid_config_repo(root)

            failures = check_local_config(root)

        self.assertEqual([], failures)

    def test_rejects_missing_spec_matrix_probe_and_doc_keys(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            _write_valid_config_repo(root)
            (root / ".env.example").write_text(
                "ANTHROPIC_API_KEY=\n"
                "FIRECRAWL_API_KEY=\n"
                "GITHUB_TOKEN=\n"
                "CLOUDFLARE_ACCOUNT_ID=\n"
                "CLOUDFLARE_API_TOKEN=\n"
                "CLOUDFLARE_R2_API_TOKEN=\n"
                "R2_ACCESS_KEY_ID=\n"
                "R2_SECRET_ACCESS_KEY=\n"
                "STRIPE_SECRET_KEY=\n",
                encoding="utf-8",
            )
            (root / "docs" / "setup.md").write_text("# setup\n", encoding="utf-8")
            (root / "docs" / "credentialed-service-probes.md").write_text(
                "# probes\nFirecrawl\nGitHub\nCloudflare\nStripe\n",
                encoding="utf-8",
            )

            failures = check_local_config(root)

        joined = "\n".join(failures)
        self.assertIn(".env.example: missing required local config key OPENAI_API_KEY", joined)
        self.assertIn("alias group missing from .env.example: CLICKHOUSE_CLOUD_KEY_ID, CLICKHOUSE_KEY_ID", joined)
        self.assertIn(".env.example: missing documented optional local config key ZYMTRACE_LICENSE_KEY", joined)
        self.assertIn("docs/setup.md: missing setup phrase 'cp .env.example .env'", joined)
        self.assertIn("docs/credentialed-service-probes.md: missing probe phrase 'ClickHouse'", joined)


def _write_valid_config_repo(root: Path) -> None:
    (root / "evals" / "e2e").mkdir(parents=True)
    (root / "evals" / "model_matrix").mkdir(parents=True)
    (root / "evals" / "targets").mkdir(parents=True)
    (root / "scripts").mkdir()
    (root / "docs").mkdir()
    (root / ".env.example").write_text(
        textwrap.dedent(
            """
            ANTHROPIC_API_KEY=
            OPENAI_API_KEY=
            FIRECRAWL_API_KEY=
            GITHUB_TOKEN=
            CLOUDFLARE_ACCOUNT_ID=
            CLOUDFLARE_API_TOKEN=
            CLOUDFLARE_R2_API_TOKEN=
            R2_ACCESS_KEY_ID=
            R2_SECRET_ACCESS_KEY=
            CLICKHOUSE_CLOUD_KEY_ID=
            CLICKHOUSE_CLOUD_KEY_SECRET=
            CLICKHOUSE_HOST=
            CLICKHOUSE_USER=
            CLICKHOUSE_PASSWORD=
            CLICKHOUSE_DATABASE=
            CLICKHOUSE_ALLOW_WRITE_ACCESS=false
            STRIPE_SECRET_KEY=
            ZYMTRACE_LICENSE_KEY=replace-with-zymtrace-license-jwt
            """
        ).lstrip(),
        encoding="utf-8",
    )
    (root / "evals" / "e2e" / "sample.json").write_text(
        '{"env":{"required":["FIRECRAWL_API_KEY"]},"checks":[{"headers":{"Authorization":"Bearer ${FIRECRAWL_API_KEY}"}}]}',
        encoding="utf-8",
    )
    (root / "evals" / "model_matrix" / "sample.json").write_text(
        '{"profiles":[{"api_key_env":"ANTHROPIC_API_KEY"},{"api_key_env":"OPENAI_API_KEY"}]}',
        encoding="utf-8",
    )
    (root / "scripts" / "probe_service_keys.py").write_text(
        'env.get("FIRECRAWL_API_KEY")\n'
        'env.get("CLICKHOUSE_CLOUD_KEY_ID") or env.get("CLICKHOUSE_KEY_ID")\n',
        encoding="utf-8",
    )
    (root / "docs" / "setup.md").write_text(
        "# setup\ncp .env.example .env\nDo not commit `.env`\nANTHROPIC_API_KEY\ngh secret set ANTHROPIC_API_KEY\n",
        encoding="utf-8",
    )
    (root / "docs" / "credentialed-service-probes.md").write_text(
        textwrap.dedent(
            """
            # probes

            python scripts/probe_service_keys.py --env-file .env
            python -m claude_agent_harness_opt mcp-e2e evals/e2e/github_readonly.json --env-file .env

            Firecrawl
            GitHub
            Cloudflare
            Cloudflare R2
            ClickHouse
            Stripe

            FIRECRAWL_API_KEY GITHUB_TOKEN CLOUDFLARE_ACCOUNT_ID CLOUDFLARE_API_TOKEN
            CLOUDFLARE_R2_API_TOKEN R2_ACCESS_KEY_ID R2_SECRET_ACCESS_KEY
            CLICKHOUSE_CLOUD_KEY_ID CLICKHOUSE_CLOUD_KEY_SECRET CLICKHOUSE_HOST
            CLICKHOUSE_USER CLICKHOUSE_PASSWORD CLICKHOUSE_DATABASE CLICKHOUSE_ALLOW_WRITE_ACCESS
            STRIPE_SECRET_KEY ZYMTRACE_LICENSE_KEY
            """
        ).lstrip(),
        encoding="utf-8",
    )


if __name__ == "__main__":
    unittest.main()
