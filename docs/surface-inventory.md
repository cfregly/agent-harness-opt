# Surface Inventory

This is the coverage contract for the repo. Each row names a surface family, the files or globs
that own it, the deterministic gates that protect it, and the retained material that lets the same
surface become an eval or regression case later.

When a new surface appears, add it here with an owner path, a gate, and retained material. If the
new surface is only scratch work, do not commit it. If it is useful enough to keep, make it testable.
The checker expands these patterns against tracked files, so a new committed file must match at
least one owner or retained-material pattern.

## Inventory

| Surface | Owned Paths | Required Gates | Regression Material |
|---|---|---|---|
| Project Instructions | `AGENTS.md`, `CLAUDE.md` | `python scripts/check_project_instructions.py` | `CLAUDE.md`, `AGENTS.md` |
| Package Metadata And Imports | `pyproject.toml`, `LICENSE`, `.gitignore`, `claude_agent_harness_opt/*.py` | `python scripts/check_package_surface.py`, `python -m compileall claude_agent_harness_opt scripts`, `python -m unittest discover -s tests -q` | `tests/test_check_package_surface_script.py`, `tests/test_cli.py` |
| CLI And Command Examples | `claude_agent_harness_opt/cli.py`, `README.md`, `docs/**/*.md`, `.github/workflows/ci.yml` | `python scripts/check_command_surfaces.py`, `python scripts/check_cli_coverage.py` | `tests/test_check_command_surfaces_script.py`, `tests/test_check_cli_coverage_script.py` |
| Prompt And Recipe Assets | `recipes/*.json`, `prompts/*.md` | `python scripts/check_prompt_recipe_surfaces.py` | `tests/test_check_prompt_recipe_surfaces_script.py`, `evals/examples/search_answer.json` |
| Project Skill Assets | `.claude/skills/agent-audit/SKILL.md`, `.claude/skills/agent-audit/agents/openai.yaml` | `python scripts/check_skill_surfaces.py` | `tests/test_check_skill_surfaces_script.py`, `evals/model_matrix/agent_audit_skill_selection.json` |
| Model Matrix Surfaces | `evals/model_matrix/*.json`, `evals/targets/**/*.json` | `python -m claude_agent_harness_opt matrix-coverage-suite`, `python scripts/check_finding_packets.py` | `evals/results/model_matrix_coverage_suite_2026-06-30.json`, `tests/test_matrix_coverage.py` |
| Eval Fixture Surfaces | `evals/examples/*`, `evals/e2e/*.json`, `evals/live_harnesses/*.json`, `evals/suites/*.json`, `evals/checks/*.json` | `python scripts/check_eval_surfaces.py`, `python scripts/check_local_config.py` | `tests/test_check_eval_surfaces_script.py`, `tests/test_check_local_config_script.py` |
| Result Receipts And PR Packets | `evals/results/*`, `evals/pr_packets/*/*`, `docs/findings/*/README.md` | `python scripts/check_finding_packets.py`, `python scripts/check_artifact_surfaces.py`, `python scripts/check_value_bar.py` | `evals/pr_packets/zymtrace_mcp_tool_tuning_2026-06-30/evidence.json`, `docs/confirmed-improvements.md` |
| Credential And Local Config | `.env.example`, `docs/setup.md`, `docs/credentialed-service-probes.md`, `scripts/probe_service_keys.py` | `python scripts/check_secret_hygiene.py`, `python scripts/check_local_config.py` | `evals/e2e/github_readonly.json`, `docs/credentialed-service-probes.md` |
| Docs Navigation And Sources | `README.md`, `docs/**/*.md`, `docs/source-map.md` | `python scripts/deslop_check.py`, `python scripts/check_docs_navigation.py`, `python scripts/check_source_map.py`, `python scripts/check_public_links.py` | `docs/source-map.md`, `docs/video-coverage-audit.md` |
| Shortcut Runner And Make Targets | `scripts/optimize_mcp.py`, `Makefile` | `python scripts/check_makefile_surface.py`, `python scripts/check_optimize_shortcuts.py`, `python scripts/check_docs_navigation.py` | `evals/model_matrix/zymtrace_mcp_tool_selection.json`, `tests/test_check_makefile_surface_script.py`, `tests/test_optimize_mcp_script.py` |
| CI Workflow | `.github/workflows/ci.yml` | `python scripts/check_ci_surface.py` | `tests/test_check_ci_surface_script.py` |
| Tracked Demo Artifact | `demo.gif`, `demo.tape`, `docs/tool_tuning_demo_sample.txt` | `python scripts/check_artifact_surfaces.py` | `demo.gif`, `tests/test_check_artifact_surfaces_script.py` |
| Generic Artifact Format | `**/*.json`, `**/*.jsonl`, `**/*.md`, `**/*.txt`, `**/*.yml`, `**/*.yaml`, `**/*.toml` | `python scripts/check_artifact_format.py` | `tests/test_check_artifact_format_script.py` |
| Value Bar Ledger | `docs/confirmed-improvements.md`, `evals/examples/agent_audit_bundle.json`, `evals/examples/agent_audit_missing_value_bar.json` | `python scripts/check_value_bar.py` | `tests/test_check_value_bar_script.py`, `evals/examples/agent_audit_missing_value_bar.json` |
| Surface Inventory | `docs/surface-inventory.md`, `scripts/check_surface_inventory.py` | `python scripts/check_surface_inventory.py` | `tests/test_check_surface_inventory_script.py` |
| Gate Scripts And Utilities | `scripts/*.py` | `python scripts/check_regression_ownership.py`, `python -m compileall claude_agent_harness_opt scripts`, `python -m unittest discover -s tests -q` | `tests/test_check_regression_ownership_script.py`, `tests/test_check_command_surfaces_script.py`, `tests/test_optimize_mcp_script.py` |
| Test Suite | `tests/*.py` | `python -m unittest discover -s tests -q` | `tests/test_check_surface_inventory_script.py`, `tests/test_cli.py` |

## Hill Descent Inputs

The failure discovery pass starts wider than skills. Use skills as one source of workflow rules, then
cross-check those rules against MCP `tools/list`, resource lists, generated schemas, source pins,
upstream docs, smoke-call output, existing traces, support reports, and host instructions.

The inventory above is the retention rule for that process. A discovered boundary is kept only when
it lands in a matrix, fixture, result receipt, PR packet, public finding, or deterministic checker.
That is what turns hill descent into reusable eval coverage instead of a one-time prompt sweep.
