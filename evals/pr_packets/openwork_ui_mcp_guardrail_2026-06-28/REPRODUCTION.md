# Reproduction for OpenWork UI MCP Guardrail

> [!NOTE]
> This is supporting evidence for the founder handoff. Start with `PR_BODY.md` for Summary, Recommended Actions, and Run This In Your Repo.

## Source Pin

- repo: https://github.com/different-ai/openwork
- commit: 3c06ab620f8f867b0cf08e88617131bcfe24fa53
- package: openwork-ui-mcp
- package_version: 0.1.0
- yc: OpenWork, YC P2026
- slice: UI status, snapshot, available actions, semantic action execution, and no-tool boundaries

## Command

```bash
make optimize mcp=openwork OUT=evals/results/openwork_ui_mcp_tool_selection_2026-06-28.md
```

## Current Frontier Stress Receipt

- Summary: [openwork_ui_mcp_tool_selection_frontier_available_live_2026-07-01.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/openwork_ui_mcp_tool_selection_frontier_available_live_2026-07-01.md)
- JSON: [openwork_ui_mcp_tool_selection_frontier_available_live_2026-07-01.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/openwork_ui_mcp_tool_selection_frontier_available_live_2026-07-01.json)
- All retained available-frontier receipts: [frontier-stress-2026-07-01.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/docs/frontier-stress-2026-07-01.md)

The retained current available-frontier run uses OpenAI `gpt-5.5` and Gemini `gemini-3.1-pro-preview-customtools`. Anthropic Opus receipts are retained separately on accessible `claude-opus-4-8`; the current MCP Opus receipts have 0 provider errors, and remaining failed rows are model-selection findings.

- Anthropic Opus summary: [openwork_ui_mcp_tool_selection_frontier_anthropic_live_2026-07-01.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/openwork_ui_mcp_tool_selection_frontier_anthropic_live_2026-07-01.md)
- Anthropic Opus JSON: [openwork_ui_mcp_tool_selection_frontier_anthropic_live_2026-07-01.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/openwork_ui_mcp_tool_selection_frontier_anthropic_live_2026-07-01.json)

## Value Bar

- baseline: docs_openwork_ui_mcp at 1.000
- candidate: source_tuned_openwork_ui_mcp at 1.000
- delta: 0.000
- minimum delta: 0.010
- promote: no

## Cases

- bridge check uses status | expected selection: ui_status | confusable alternatives checked: ui_snapshot,ui_list_actions,ui_execute_action
- unknown current screen uses snapshot | expected selection: ui_snapshot | confusable alternatives checked: ui_status,ui_list_actions,ui_execute_action
- action discovery uses list actions | expected selection: ui_list_actions | confusable alternatives checked: ui_status,ui_snapshot,ui_execute_action
- known action id executes action | expected selection: ui_execute_action | confusable alternatives checked: ui_status,ui_snapshot,ui_list_actions
- unknown action id lists actions first | expected selection: ui_list_actions | confusable alternatives checked: ui_status,ui_execute_action
- coordinate click avoids semantic bridge | expected selection:  | confusable alternatives checked: ui_status,ui_snapshot,ui_list_actions,ui_execute_action
- app maybe closed checks status before action | expected selection: ui_status | confusable alternatives checked: ui_snapshot,ui_list_actions,ui_execute_action
