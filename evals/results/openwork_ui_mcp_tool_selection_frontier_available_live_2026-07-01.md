# OpenWork UI MCP Frontier Matrix Live Result - 2026-07-01

Passed: no
Live: yes

This retained frontier receipt runs the current available frontier profiles in this workspace: OpenAI `gpt-5.5` and Gemini `gemini-3.1-pro-preview-customtools`.

> [!NOTE]
> Anthropic frontier is tracked in separate Anthropic Opus receipts. The current MCP Opus receipts have 0 provider errors after the targeted Anthropic rerun; gstack skill routing remains a separate provider-state receipt. See [Frontier Stress Receipts](https://github.com/cfregly/agent-harness-opt/blob/main/docs/frontier-stress-2026-07-01.md).

## Matrix Summary

- total: 28
- passed_cases: 27
- failed_cases: 0
- errors: 1
- skipped: 0
- score: 0.964

## Profiles

- `anthropic-opus48-frontier`: `claude-opus-4-8`
- `openai-gpt55-frontier`: `gpt-5.5`
- `gemini-31-pro-customtools-frontier`: `gemini-3.1-pro-preview-customtools`

## Status By Profile

| Profile | Passed | Failed | Errors | Skipped |
|---|---:|---:|---:|---:|
| `gemini-31-pro-customtools-frontier` | 13 | 0 | 1 | 0 |
| `openai-gpt55-frontier` | 14 | 0 | 0 | 0 |

## Remaining Failure Clusters

- 1x `bridge check uses status`: status `error`, chose `error: HTTP 503: {`

## Machine-readable Receipt

[JSON receipt](https://github.com/cfregly/agent-harness-opt/blob/main/evals/results/openwork_ui_mcp_tool_selection_frontier_available_live_2026-07-01.json)
