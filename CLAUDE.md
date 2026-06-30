# CLAUDE.md

Conventions for any agent working on `claude-agent-harness-opt`. Read this first.

## What this is

This repo is a public, standalone prompt kit for Claude-style agents. It renders agent system
prompts from recipes, scores whether a task deserves an agent, lints tool descriptions, runs
deterministic evals over agent transcripts and final state, and uses a live Claude judge for
semantic trace audits. It also runs model matrix sweeps to tune tool descriptions, provider
harnesses, `CLAUDE.md` style instructions, and skills across model generations.

## Run it

    pip install -e .
    python -m claude_agent_harness_opt render recipes/agentic_search.json
    python -m claude_agent_harness_opt score recipes/agentic_search.json
    python -m claude_agent_harness_opt eval evals/examples/search_answer.json
    python -m claude_agent_harness_opt model-matrix evals/model_matrix/coding_tool_selection.json

## Rules

- Keep it standalone. Do not reference parent workspaces, private notes, or local-only files.
- Keep it generic. Do not add interview framing, employer-specific context, or individual names.
- Preserve user changes. Read local diffs before editing, keep unrelated dirty files intact, and
  never rewrite work you did not make.
- No destructive git cleanup. Do not use reset, checkout, clean, force push, or history rewrite
  commands unless the user explicitly asks for that exact operation.
- Track reasoning and tool use explicitly. Real audits must include visible reasoning summaries or
  decision notes, ordered tool calls, tool outputs, and final answers.
- Enforce directed thinking in traces and prompts. Before the first tool, visible reasoning must
  mention complexity, tool budget, and evidence or stop criteria. After tool results, visible
  reasoning must mention quality, verification, and the continue or stop decision.
- Apply the value bar everywhere. An audit, prompt change, tool change, or eval change passes only
  when it is adversarially-confirmed to add value: it must name the value claim, compare against a
  baseline, meet a minimum improvement threshold, and survive an adversarial check with no open
  objections.
- Source Claude and agent-prompting claims. If a factual claim changes, update
  `docs/source-map.md` with the public source used.
- Deterministic tests stay runnable without an API key. CI and real audits require the live Claude
  judge through `ANTHROPIC_API_KEY`. Cross-provider matrix sweeps use `.env` keys when supplied.
- Secrets never get committed. `.env` stays git-ignored.
- Prose is deslop-clean: no em-dashes, no en-dashes, no semicolons, and no buzzwords. Run
  `python scripts/deslop_check.py` before shipping.

## Coverage Workflow

Use `.claude/skills/agent-audit/SKILL.md` when reviewing agent traces, tool boundaries, skills, or
MCP surfaces. Treat skills as one input to the hill descent, not as the whole corpus. Also inventory
MCP `tools/list`, resource lists, generated schemas, source pins, upstream docs, support reports,
smoke-call output, existing transcripts, and README or `CLAUDE.md` host rules.

Retain useful cases as eval material. Store reusable matrices under `evals/model_matrix`, imported
or minimal transcripts under `evals/examples`, dated receipts under `evals/results`, upstream PR
packets under `evals/pr_packets`, and promoted public findings under `docs/findings`. Run
`matrix-coverage-suite` before claiming broad coverage, and use `grind-harness` when you need a
bounded baseline-to-candidate climb.

## Verification Gates

Run the relevant focused command first, then run the full gate set before shipping broad changes:

```bash
python scripts/deslop_check.py
python scripts/check_value_bar.py
python scripts/check_prompt_recipe_surfaces.py
python scripts/check_skill_surfaces.py
python scripts/check_command_surfaces.py
python scripts/check_secret_hygiene.py
python scripts/check_docs_navigation.py
python scripts/check_artifact_surfaces.py
python scripts/check_optimize_shortcuts.py
python scripts/check_cli_coverage.py
python scripts/check_project_instructions.py
python scripts/check_finding_packets.py
python scripts/check_eval_surfaces.py
python -m compileall claude_agent_harness_opt scripts
python -m unittest discover -s tests -q
```
