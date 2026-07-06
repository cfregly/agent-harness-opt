# Supabase MCP Database Frontier Matrix Live Result - 2026-07-01

Passed: no
Live: yes

This retained frontier receipt runs the current available frontier profiles in this workspace: OpenAI `gpt-5.5` and Gemini `gemini-3.1-pro-preview-customtools`.

> [!NOTE]
> Anthropic frontier is tracked in separate Anthropic Opus receipts. The current MCP Opus receipts have 0 provider errors after the targeted Anthropic rerun; gstack skill routing remains a separate provider-state receipt. See [Frontier Stress Receipts](https://github.com/cfregly/agent-harness-opt/blob/main/docs/frontier-stress-2026-07-01.md).

## Matrix Summary

- total: 48
- passed_cases: 43
- failed_cases: 5
- errors: 0
- skipped: 0
- score: 0.896

## Profiles

- `anthropic-opus48-frontier`: `claude-opus-4-8`
- `openai-gpt55-frontier`: `gpt-5.5`
- `gemini-31-pro-customtools-frontier`: `gemini-3.1-pro-preview-customtools`

## Status By Profile

| Profile | Passed | Failed | Errors | Skipped |
|---|---:|---:|---:|---:|
| `gemini-31-pro-customtools-frontier` | 20 | 4 | 0 | 0 |
| `openai-gpt55-frontier` | 23 | 1 | 0 | 0 |

## Remaining Failure Clusters

- 2x `ddl create table uses migration`: status `failed`, chose `execute_sql`
- 1x `ddl alter table uses migration`: status `failed`, chose `execute_sql`
- 1x `ddl create index uses migration`: status `failed`, chose `execute_sql`
- 1x `rls policy uses migration`: status `failed`, chose `execute_sql`

## Machine-readable Receipt

[JSON receipt](https://github.com/cfregly/agent-harness-opt/blob/main/evals/results/supabase_mcp_database_tool_selection_frontier_available_live_2026-07-01.json)
