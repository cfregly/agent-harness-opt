# Reproduction for Supabase MCP Database Tool Tuning

> [!NOTE]
> This is supporting evidence for the founder handoff. Start with `PR_BODY.md` for Summary, Recommended Actions, and Run This In Your Repo.

## Source Pin

- repo: https://github.com/supabase/mcp
- commit: 100565f26d7eec6d314a08597ded22da63045923
- package: @supabase/mcp-server-supabase
- version: 0.8.2
- database_tools: packages/mcp-server-supabase/src/tools/database-operation-tools.ts
- server_instructions: packages/mcp-server-supabase/src/server.ts
- docs: https://supabase.com/docs/guides/ai-tools/mcp

## Command

```bash
python scripts/optimize_mcp.py supabase --env-file .env --live --require-live --markdown --providers anthropic,openai,gemini --harnesses prompt_json,native_tools --cases "ddl create table uses migration,ddl create index uses migration,rls policy uses migration" --out /tmp/supabase-ddl-boundary.md
```

## Current Frontier Stress Receipt

- Summary: [supabase_mcp_database_tool_selection_frontier_available_live_2026-07-01.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/supabase_mcp_database_tool_selection_frontier_available_live_2026-07-01.md)
- JSON: [supabase_mcp_database_tool_selection_frontier_available_live_2026-07-01.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/supabase_mcp_database_tool_selection_frontier_available_live_2026-07-01.json)
- All retained available-frontier receipts: [frontier-stress-2026-07-01.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/docs/frontier-stress-2026-07-01.md)

The retained current available-frontier run uses OpenAI `gpt-5.5` and Gemini `gemini-3.1-pro-preview-customtools`. Anthropic Opus receipts are retained separately on accessible `claude-opus-4-8`; the current MCP Opus receipts have 0 provider errors, and remaining failed rows are model-selection findings.

- Anthropic Opus summary: [supabase_mcp_database_tool_selection_frontier_anthropic_live_2026-07-01.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/supabase_mcp_database_tool_selection_frontier_anthropic_live_2026-07-01.md)
- Anthropic Opus JSON: [supabase_mcp_database_tool_selection_frontier_anthropic_live_2026-07-01.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/supabase_mcp_database_tool_selection_frontier_anthropic_live_2026-07-01.json)

## Value Bar

- baseline: terse_supabase_database_mcp at 0.222
- candidate: tuned_supabase_database_boundaries at 1.000
- delta: 0.778
- minimum delta: 0.010
- promote: yes

## Cases

- ddl create table uses migration | expected selection: apply_migration | confusable alternatives checked: execute_sql,list_tables
- ddl create index uses migration | expected selection: apply_migration | confusable alternatives checked: execute_sql,list_tables
- rls policy uses migration | expected selection: apply_migration | confusable alternatives checked: execute_sql,list_tables
