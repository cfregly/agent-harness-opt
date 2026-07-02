# Reproduction for Firecrawl MCP Tool Tuning

> [!NOTE]
> This is supporting evidence for the founder handoff. Start with `PR_BODY.md` for Summary, Recommended Actions, and Run This In Your Repo.

## Source Pin

- repo: https://github.com/firecrawl/firecrawl-mcp-server
- commit: e744bba494c0e77086d66af838d7a64fab52f138
- package: firecrawl-mcp
- version: 3.22.0
- legacy_descriptions: src/legacy/index.md
- current_descriptions: src/index.ts
- docs: README.md#how-to-choose-a-tool

## Command

```bash
python scripts/optimize_mcp.py firecrawl --env-file .env --live --require-live --markdown --providers anthropic,openai,gemini --harnesses prompt_json,native_tools --cases "single known page structured fields" --out /tmp/firecrawl-single-page.md
```

## Current Frontier Stress Receipt

- Summary: [firecrawl_mcp_tool_selection_frontier_available_live_2026-07-01.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/firecrawl_mcp_tool_selection_frontier_available_live_2026-07-01.md)
- JSON: [firecrawl_mcp_tool_selection_frontier_available_live_2026-07-01.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/firecrawl_mcp_tool_selection_frontier_available_live_2026-07-01.json)
- All retained available-frontier receipts: [frontier-stress-2026-07-01.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/docs/frontier-stress-2026-07-01.md)

The retained current available-frontier run uses OpenAI `gpt-5.5` and Gemini `gemini-3.1-pro-preview-customtools`. Anthropic Opus receipts are retained separately on accessible `claude-opus-4-8`; the current MCP Opus receipts have 0 provider errors, and remaining failed rows are model-selection findings.

- Anthropic Opus summary: [firecrawl_mcp_tool_selection_frontier_anthropic_live_2026-07-01.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/firecrawl_mcp_tool_selection_frontier_anthropic_live_2026-07-01.md)
- Anthropic Opus JSON: [firecrawl_mcp_tool_selection_frontier_anthropic_live_2026-07-01.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/firecrawl_mcp_tool_selection_frontier_anthropic_live_2026-07-01.json)

## Value Bar

- baseline: legacy_firecrawl_mcp at 0.000
- candidate: tuned_firecrawl_mcp_boundaries at 1.000
- delta: 1.000
- minimum delta: 0.010
- promote: yes

## Cases

- single known page structured fields | expected selection: firecrawl_scrape | confusable alternatives checked: firecrawl_extract,firecrawl_batch_scrape,firecrawl_interact,firecrawl_monitor_create
