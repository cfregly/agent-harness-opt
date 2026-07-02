Suggested title: Tighten Supabase MCP database routing with live evals

> [!NOTE]
> This page starts with the founder handoff. Detailed eval, command, and machine-readable material is preserved below.

## Summary

| Exact change | Before | After | Result |
|---|---|---|---|
| Clarify that `apply_migration` is required for DDL, schema changes, indexes, functions, triggers, extension enablement, and RLS policy changes. Reserve `execute_sql` for non-schema-changing SQL. | Schema-changing SQL such as `CREATE TABLE`, `CREATE INDEX`, functions, triggers, extensions, and RLS policy changes could be routed to `execute_sql`. | DDL, schema changes, indexes, functions, triggers, extensions, and RLS changes route to `apply_migration`. `execute_sql` is reserved for non-schema SQL. | `tuned_supabase_database_boundaries` scored 1.000, a 0.778 gain. Add retained cases as regression coverage. |


## Result

- Confirmed improvement: `tuned_supabase_database_boundaries` moved from 0.222 to 1.000, a 0.778 gain over `terse_supabase_database_mcp`.
- Value bar: cleared the 0.010 minimum delta.
- Proof scope: 36 live matrix cells, 22 passed, 14 failed, 0 errors.

## What Failed

- `terse_supabase_database_mcp` failed or chose the wrong boundary on: ddl create table uses migration, ddl create index uses migration, rls policy uses migration.
- Those failures are the target-owned behavior to encode in descriptions, defaults, options, or regression tests.

## Why This Matters

- Value proposition: helps agents choose the intended Supabase MCP workflow instead of adjacent tools that look plausible.
- Proof: `tuned_supabase_database_boundaries` scored 1.000, a 0.778 gain.
- Proof scope: 36 live matrix cells on the same tasks, providers, harnesses, and instruction variants.
- Baseline failure pattern: ddl create table uses migration, ddl create index uses migration, rls policy uses migration.
- Downside avoided: plausible-but-wrong tool choices that waste time or return misleading results.

## Recommended Actions

- Apply exact change: Clarify that `apply_migration` is required for DDL, schema changes, indexes, functions, triggers, extension enablement, and RLS policy changes. Reserve `execute_sql` for non-schema-changing SQL.
- Add the selected cases below to repo CI or release-blocking regression coverage.
- Run the local-agent prompt below in your repo to identify exact files, patch locations, tests, and risks before editing.

## Run This In Your Repo

Replace `/path/to/repo` with the target team's local checkout. These commands ask for a plan only.

```bash
cat <<'PROMPT' | codex exec -C /path/to/repo --sandbox read-only -
Review this action-first finding:
https://github.com/cfregly/claude-agent-harness-opt/tree/main/docs/findings/supabase

Then inspect this local repo and tell us exactly what to change.

Return:
- Executive summary
- Before / after
- Recommended repo changes
- Suggested patch locations
- Regression tests to add
- Risks or open questions

Do not edit files yet.
PROMPT
```

```bash
claude -p --permission-mode plan "$(cat <<'PROMPT'
Review this action-first finding:
https://github.com/cfregly/claude-agent-harness-opt/tree/main/docs/findings/supabase

Then inspect this local repo and tell us exactly what to change.

Return:
- Executive summary
- Before / after
- Recommended repo changes
- Suggested patch locations
- Regression tests to add
- Risks or open questions

Do not edit files yet.
PROMPT
)"
```

```bash
gemini --approval-mode plan --output-format text -p "$(cat <<'PROMPT'
Review this action-first finding:
https://github.com/cfregly/claude-agent-harness-opt/tree/main/docs/findings/supabase

Then inspect this local repo and tell us exactly what to change.

Return:
- Executive summary
- Before / after
- Recommended repo changes
- Suggested patch locations
- Regression tests to add
- Risks or open questions

Do not edit files yet.
PROMPT
)"
```

## Model Coverage

| Evidence lane | Baseline | Candidate |
|---|---|---|
| Anthropic | `terse_supabase_database_mcp` 0/6 passed, 6 failed, 0 errors. | `tuned_supabase_database_boundaries` 6/6 passed. |
| Google Gemini | `terse_supabase_database_mcp` 0/6 passed, 6 failed, 0 errors. | `tuned_supabase_database_boundaries` 6/6 passed. |
| OpenAI | `terse_supabase_database_mcp` 4/6 passed, 2 failed, 0 errors. | `tuned_supabase_database_boundaries` 6/6 passed. |

Provider/model rows are evidence lanes. The target repo actions above are the only primary CTA.

## Evidence Bundle

- Public harness repo: [claude-agent-harness-opt](https://github.com/cfregly/claude-agent-harness-opt)
- Bundle folder: [supabase_mcp_database_tool_tuning_2026-06-25](https://github.com/cfregly/claude-agent-harness-opt/tree/main/evals/pr_packets/supabase_mcp_database_tool_tuning_2026-06-25)
- Matrix: [supabase_mcp_database_tool_selection.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/model_matrix/supabase_mcp_database_tool_selection.json)
- Result artifact: [supabase_mcp_ddl_boundary_live_2026-06-25.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/supabase_mcp_ddl_boundary_live_2026-06-25.md)
- PR_TITLE.txt: [PR_TITLE.txt](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/supabase_mcp_database_tool_tuning_2026-06-25/PR_TITLE.txt)
- PR_BODY.md: [PR_BODY.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/supabase_mcp_database_tool_tuning_2026-06-25/PR_BODY.md)
- REPRODUCTION.md: [REPRODUCTION.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/supabase_mcp_database_tool_tuning_2026-06-25/REPRODUCTION.md)
- evidence.json: [evidence.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/supabase_mcp_database_tool_tuning_2026-06-25/evidence.json)
- Target repo: [mcp](https://github.com/supabase/mcp)

<details>
<summary>LLM / Machine-readable details</summary>

## Artifact Pointers

- Finding folder: [Supabase MCP Database Tool Tuning finding](https://github.com/cfregly/claude-agent-harness-opt/tree/main/docs/findings/supabase)
- Matrix: [supabase_mcp_database_tool_selection.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/model_matrix/supabase_mcp_database_tool_selection.json)
- Result artifact: [supabase_mcp_ddl_boundary_live_2026-06-25.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/supabase_mcp_ddl_boundary_live_2026-06-25.md)
- Evidence JSON: [evidence.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/supabase_mcp_database_tool_tuning_2026-06-25/evidence.json)

## Frontier Receipts

- Current frontier stress receipt: [supabase_mcp_database_tool_selection_frontier_available_live_2026-07-01.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/supabase_mcp_database_tool_selection_frontier_available_live_2026-07-01.md)
- Current frontier JSON receipt: [supabase_mcp_database_tool_selection_frontier_available_live_2026-07-01.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/supabase_mcp_database_tool_selection_frontier_available_live_2026-07-01.json)
- Anthropic Opus frontier receipt: [supabase_mcp_database_tool_selection_frontier_anthropic_live_2026-07-01.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/supabase_mcp_database_tool_selection_frontier_anthropic_live_2026-07-01.md)
- Anthropic Opus JSON receipt: [supabase_mcp_database_tool_selection_frontier_anthropic_live_2026-07-01.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/supabase_mcp_database_tool_selection_frontier_anthropic_live_2026-07-01.json)

## Cases

- ddl create table uses migration | expected: apply_migration | forbidden: execute_sql,list_tables
- ddl create index uses migration | expected: apply_migration | forbidden: execute_sql,list_tables
- rls policy uses migration | expected: apply_migration | forbidden: execute_sql,list_tables

## Reproduce

```bash
python scripts/optimize_mcp.py supabase --env-file .env --live --require-live --markdown --providers anthropic,openai,gemini --harnesses prompt_json,native_tools --cases "ddl create table uses migration,ddl create index uses migration,rls policy uses migration" --out /tmp/supabase-ddl-boundary.md
```

</details>
