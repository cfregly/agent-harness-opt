from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from scripts.check_makefile_surface import check_makefile_surface
from scripts.optimize_mcp import Target


ROOT = Path(__file__).resolve().parents[1]


class CheckMakefileSurfaceScriptTests(unittest.TestCase):
    def test_script_passes_current_repo(self):
        result = subprocess.run(
            [sys.executable, "scripts/check_makefile_surface.py"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("Makefile surface check passed", result.stdout)

    def test_accepts_minimal_makefile_contract(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "Makefile").write_text(_valid_makefile(), encoding="utf-8")

            failures = check_makefile_surface(root, [_target("sample")], run_help=False)

        self.assertEqual([], failures)

    def test_rejects_live_dry_and_registry_drift(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            text = _valid_makefile()
            text = text.replace("--live --require-live ", "", 1)
            text = text.replace("make optimize mcp=sample", "make optimize mcp=wrong")
            text = text.replace(
                'scripts/optimize_mcp.py "$(MCP_TARGET)" --markdown',
                'scripts/optimize_mcp.py "$(MCP_TARGET)" --live --markdown',
                1,
            )
            (root / "Makefile").write_text(text, encoding="utf-8")

            failures = check_makefile_surface(root, [_target("sample")], run_help=False)

        joined = "\n".join(failures)
        self.assertIn("Makefile: optimize must be live and require live credentials", joined)
        self.assertIn("Makefile: help missing optimize shortcut mcp=sample", joined)
        self.assertIn("Makefile: optimize-dry must stay keyless and non-live", joined)


def _target(primary: str) -> Target:
    return Target(
        inputs=(primary,),
        baseline_variant="baseline",
        default_providers="anthropic",
        default_harnesses="prompt_json",
        instruction_variants="rules",
        matrix="evals/model_matrix/sample.json",
        optimized_variants=("tuned",),
        variants="baseline,tuned",
    )


def _valid_makefile() -> str:
    return """PY ?= python3
mcp ?=
url ?=
MCP_TARGET = $(if $(mcp),$(mcp),$(url))
ENV_FILE ?= .env
PROVIDERS ?=
HARNESSES ?=
CONCURRENCY ?= 2
MAX_CASES ?=
OUT ?=

define require_mcp_target
\t@if [ -n "$(MCP)$(URL)" ]; then \\
\t\techo "Use lowercase selectors: make $@ mcp=<target> or make $@ url=<repo-url>"; \\
\t\texit 2; \\
\tfi
\t@if [ -z "$(MCP_TARGET)" ]; then \\
\t\techo "Missing target. Use: make $@ mcp=sample or make $@ url=https://github.com/<org>/<repo>"; \\
\t\texit 2; \\
\tfi
endef

.PHONY: help optimize optimize-dry optimize-grind

help:
\t@echo "make optimize mcp=sample                            live sample matrix"
\t@echo "make optimize url=https://github.com/example/sample"
\t@echo "make optimize-dry mcp=sample                        plan cells without provider calls"
\t@echo "make optimize-grind mcp=sample                      try one hill-climb candidate"

optimize:
\t$(call require_mcp_target)
\t$(PY) scripts/optimize_mcp.py "$(MCP_TARGET)" --env-file "$(ENV_FILE)" --live --require-live --markdown --concurrency "$(CONCURRENCY)" $(if $(PROVIDERS),--providers "$(PROVIDERS)",) $(if $(HARNESSES),--harnesses "$(HARNESSES)",) $(if $(MAX_CASES),--max-cases "$(MAX_CASES)",) $(if $(OUT),--out "$(OUT)",)

optimize-dry:
\t$(call require_mcp_target)
\t$(PY) scripts/optimize_mcp.py "$(MCP_TARGET)" --markdown --concurrency "$(CONCURRENCY)" $(if $(PROVIDERS),--providers "$(PROVIDERS)",) $(if $(HARNESSES),--harnesses "$(HARNESSES)",) $(if $(MAX_CASES),--max-cases "$(MAX_CASES)",) $(if $(OUT),--out "$(OUT)",)

optimize-grind:
\t$(call require_mcp_target)
\t$(PY) scripts/optimize_mcp.py "$(MCP_TARGET)" --env-file "$(ENV_FILE)" --live --require-live --grind --markdown --concurrency "$(CONCURRENCY)" $(if $(PROVIDERS),--providers "$(PROVIDERS)",) $(if $(HARNESSES),--harnesses "$(HARNESSES)",) $(if $(MAX_CASES),--max-cases "$(MAX_CASES)",) $(if $(OUT),--out "$(OUT)",)
"""


if __name__ == "__main__":
    unittest.main()
