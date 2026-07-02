# Supabase MCP Finding

Share link: [Supabase packet](https://github.com/cfregly/claude-agent-harness-opt/tree/main/docs/findings/supabase)

## Summary

### Exact Text To Apply

Copy the suggested replacement text into the target repo field named in the first column.

| Where to edit | Baseline text | Suggested replacement text |
|---|---|---|
| `execute_sql.purpose` | Executes raw SQL in the database. | Run regular SQL that does not change the database schema. |
| `execute_sql.avoid_when` | No DDL/schema-change avoid_when boundary. | Avoid for DDL or schema changes such as CREATE TABLE, ALTER TABLE, DROP TABLE, CREATE INDEX, policies, triggers, functions, or extension enablement. Use apply_migration for those. |
| `execute_sql.input_schema.properties.query.description` | SQL query to execute. | Regular SQL query that does not change schema. |
| `apply_migration.purpose` | Applies a SQL migration to the database. | Apply DDL or schema-changing SQL as a tracked Supabase migration. |
| `apply_migration.avoid_when` | No SELECT/ad-hoc-read avoid_when boundary. | Avoid for SELECT queries, ad hoc reads, reports, or non-schema SQL. Use execute_sql for regular queries that do not change schema. |
| `apply_migration.input_schema.properties.query.description` | SQL query to apply. | DDL or schema-changing SQL to track as a migration. |

### Baseline / Suggested Behavior
The table below is the exact handoff text. Baseline / before is the current behavior. Suggested / after is the proposed wording or behavior to implement.

| Suggested change | Baseline / before description | Suggested / after description | Result |
|---|---|---|---|
| Clarify that `apply_migration` is required for DDL, schema changes, indexes, functions, triggers, extension enablement, and RLS policy changes. Reserve `execute_sql` for non-schema-changing SQL. | Schema-changing SQL such as `CREATE TABLE`, `CREATE INDEX`, functions, triggers, extensions, and RLS policy changes could be routed to `execute_sql`. | DDL, schema changes, indexes, functions, triggers, extensions, and RLS changes route to `apply_migration`. `execute_sql` is reserved for non-schema SQL. | `tuned_supabase_database_boundaries` scored 1.000, a 0.778 gain. Add retained cases as regression coverage. |


## Result

Confirmed improvement. This clears the adversarially-confirmed to add value bar.

Current frontier stress receipt: 48 current available-frontier cells, 43 passed, 5 failed, 0 errors on OpenAI `gpt-5.5` and Gemini `gemini-3.1-pro-preview-customtools`. Treat this as hill-descending coverage for the next tuning pass, not as a replacement for the promoted baseline-to-tuned result.

Anthropic Opus frontier receipt: 24 Anthropic Opus cells, 24 passed, 0 failed, 0 errors on accessible `claude-opus-4-8`. Any failed cells are model-selection findings, not provider-credit blockers.

The full Anthropic prompt JSON run moved from 6/9 to 9/9. The DDL and RLS boundary improved across
Anthropic, OpenAI, Gemini, native tools, and prompt JSON without regressing the passing cell.

## What Failed

The baseline chose `execute_sql` for schema-changing SQL:

- `CREATE TABLE`
- `CREATE INDEX`
- RLS policy creation

Those should route to `apply_migration`.

## Why This Matters

- Value proposition: helps agents choose the intended Supabase MCP workflow instead of adjacent tools that look plausible.
- Proof: `tuned_supabase_database_boundaries` scored 1.000, a 0.778 gain.
- Proof scope: 36 live matrix cells on the same tasks, providers, harnesses, and instruction variants.
- Baseline failure pattern: ddl create table uses migration, ddl create index uses migration, rls policy uses migration.
- Downside avoided: plausible-but-wrong tool choices that waste time or return misleading results.

## Recommended Actions

- Apply suggested change: Clarify that `apply_migration` is required for DDL, schema changes, indexes, functions, triggers, extension enablement, and RLS policy changes. Reserve `execute_sql` for non-schema-changing SQL.
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

- Source: [Supabase MCP repo](https://github.com/supabase/mcp)
- Matrix: [supabase_mcp_database_tool_selection.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/model_matrix/supabase_mcp_database_tool_selection.json)
- Frontier stress receipt: [supabase_mcp_database_tool_selection_frontier_available_live_2026-07-01.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/supabase_mcp_database_tool_selection_frontier_available_live_2026-07-01.md)
- Live result: [supabase_mcp_ddl_boundary_live_2026-06-25.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/supabase_mcp_ddl_boundary_live_2026-06-25.md)
- PR packet: [supabase_mcp_database_tool_tuning_2026-06-25](https://github.com/cfregly/claude-agent-harness-opt/tree/main/evals/pr_packets/supabase_mcp_database_tool_tuning_2026-06-25)
- Detailed note: [Supabase MCP Tool Tuning](https://github.com/cfregly/claude-agent-harness-opt/blob/main/docs/supabase-mcp-tool-tuning.md)
- Ledger: [Confirmed Improvements](https://github.com/cfregly/claude-agent-harness-opt/blob/main/docs/confirmed-improvements.md)

## Reproduce

```bash
make optimize mcp=supabase
```

</details>
