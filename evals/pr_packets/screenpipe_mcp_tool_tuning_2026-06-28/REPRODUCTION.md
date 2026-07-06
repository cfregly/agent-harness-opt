# Reproduction for Screenpipe MCP Tool Tuning

> [!NOTE]
> This is supporting evidence for the founder handoff. Start with `PR_BODY.md` for Summary, Recommended Actions, and Run This In Your Repo.

## Source Pin

- repo: https://github.com/screenpipe/screenpipe
- commit: 2de07ff501a63d3d3f0f39a9a602640a833d151f
- package: screenpipe-mcp
- package_version: 0.18.14
- yc: Screenpipe, YC S26
- slice: local screen/audio search, UI element lookup, meeting workflows, and scheduled pipes

## Command

```bash
make optimize mcp=screenpipe OUT=evals/results/screenpipe_mcp_tool_selection_2026-06-28.md
```

## Current Frontier Stress Receipt

- Summary: [screenpipe_mcp_tool_selection_frontier_available_live_2026-07-01.md](https://github.com/cfregly/agent-harness-opt/blob/main/evals/results/screenpipe_mcp_tool_selection_frontier_available_live_2026-07-01.md)
- JSON: [screenpipe_mcp_tool_selection_frontier_available_live_2026-07-01.json](https://github.com/cfregly/agent-harness-opt/blob/main/evals/results/screenpipe_mcp_tool_selection_frontier_available_live_2026-07-01.json)
- All retained available-frontier receipts: [frontier-stress-2026-07-01.md](https://github.com/cfregly/agent-harness-opt/blob/main/docs/frontier-stress-2026-07-01.md)

The retained current available-frontier run uses OpenAI `gpt-5.5` and Gemini `gemini-3.1-pro-preview-customtools`. Anthropic Opus receipts are retained separately on accessible `claude-opus-4-8`; the current MCP Opus receipts have 0 provider errors, and remaining failed rows are model-selection findings.

- Anthropic Opus summary: [screenpipe_mcp_tool_selection_frontier_anthropic_live_2026-07-01.md](https://github.com/cfregly/agent-harness-opt/blob/main/evals/results/screenpipe_mcp_tool_selection_frontier_anthropic_live_2026-07-01.md)
- Anthropic Opus JSON: [screenpipe_mcp_tool_selection_frontier_anthropic_live_2026-07-01.json](https://github.com/cfregly/agent-harness-opt/blob/main/evals/results/screenpipe_mcp_tool_selection_frontier_anthropic_live_2026-07-01.json)

## Value Bar

- baseline: readme_screenpipe_mcp at 0.857
- candidate: source_tuned_screenpipe_mcp at 1.000
- delta: 0.143
- minimum delta: 0.010
- promote: yes

## Cases

- broad morning recap starts summary | expected selection: activity-summary | confusable alternatives checked: search-content,keyword-search,search-elements,export-video,list-meetings
- exact keyword uses keyword search | expected selection: keyword-search | confusable alternatives checked: activity-summary,search-elements,export-video,list-meetings
- speaker transcript uses content search | expected selection: search-content | confusable alternatives checked: activity-summary,keyword-search,search-elements,export-video,list-meetings
- ui button lookup uses elements | expected selection: search-elements | confusable alternatives checked: search-content,activity-summary,keyword-search,frame-context,export-video
- known frame detail uses frame context | expected selection: frame-context | confusable alternatives checked: search-content,get-frame-elements,activity-summary,export-video,list-meetings
- create recurring automation uses pipe | expected selection: create-pipe | confusable alternatives checked: run-pipe,pipe-logs,activity-summary
- verify pipe output uses logs | expected selection: pipe-logs | confusable alternatives checked: create-pipe,run-pipe,activity-summary
