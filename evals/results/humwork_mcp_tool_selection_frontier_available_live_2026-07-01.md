# Humwork MCP Frontier Matrix Live Result - 2026-07-01

Passed: no
Live: yes

This retained frontier receipt runs the current available frontier profiles in this workspace: OpenAI `gpt-5.5` and Gemini `gemini-3.1-pro-preview-customtools`.

> [!NOTE]
> Anthropic frontier is tracked in separate Anthropic Opus receipts. The current MCP Opus receipts have 0 provider errors after the targeted Anthropic rerun; gstack skill routing remains a separate provider-state receipt. See [Frontier Stress Receipts](https://github.com/cfregly/agent-harness-opt/blob/main/docs/frontier-stress-2026-07-01.md).

## Matrix Summary

- total: 28
- passed_cases: 25
- failed_cases: 3
- errors: 0
- skipped: 0
- score: 0.893

## Profiles

- `anthropic-opus48-frontier`: `claude-opus-4-8`
- `openai-gpt55-frontier`: `gpt-5.5`
- `gemini-31-pro-customtools-frontier`: `gemini-3.1-pro-preview-customtools`

## Status By Profile

| Profile | Passed | Failed | Errors | Skipped |
|---|---:|---:|---:|---:|
| `gemini-31-pro-customtools-frontier` | 12 | 2 | 0 | 0 |
| `openai-gpt55-frontier` | 13 | 1 | 0 | 0 |

## Remaining Failure Clusters

- 2x `active expert session sends focused follow-up`: status `failed`, chose `send_chat_message`
- 1x `secrets request avoids external chat`: status `failed`, chose `consult_expert`

## Machine-readable Receipt

[JSON receipt](https://github.com/cfregly/agent-harness-opt/blob/main/evals/results/humwork_mcp_tool_selection_frontier_available_live_2026-07-01.json)
