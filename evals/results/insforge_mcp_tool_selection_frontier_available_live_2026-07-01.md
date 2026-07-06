# InsForge MCP Frontier Matrix Live Result - 2026-07-01

Passed: no
Live: yes

This retained frontier receipt runs the current available frontier profiles in this workspace: OpenAI `gpt-5.5` and Gemini `gemini-3.1-pro-preview-customtools`.

> [!NOTE]
> Anthropic frontier is tracked in separate Anthropic Opus receipts. The current MCP Opus receipts have 0 provider errors after the targeted Anthropic rerun; gstack skill routing remains a separate provider-state receipt. See [Frontier Stress Receipts](https://github.com/cfregly/agent-harness-opt/blob/main/docs/frontier-stress-2026-07-01.md).

## Matrix Summary

- total: 76
- passed_cases: 64
- failed_cases: 11
- errors: 1
- skipped: 0
- score: 0.842

## Profiles

- `anthropic-opus48-frontier`: `claude-opus-4-8`
- `openai-gpt55-frontier`: `gpt-5.5`
- `gemini-31-pro-customtools-frontier`: `gemini-3.1-pro-preview-customtools`

## Status By Profile

| Profile | Passed | Failed | Errors | Skipped |
|---|---:|---:|---:|---:|
| `gemini-31-pro-customtools-frontier` | 31 | 6 | 1 | 0 |
| `openai-gpt55-frontier` | 33 | 5 | 0 | 0 |

## Remaining Failure Clusters

- 3x `new project setup reads instructions`: status `failed`, chose `fetch-docs`
- 3x `client token uses anon key`: status `failed`, chose `get-anon-key`
- 2x `function logs use container logs`: status `failed`, chose `get-container-logs`
- 2x `relative deploy path avoids tool`: status `failed`, chose `create-deployment`
- 1x `client token uses anon key`: status `error`, chose `error: HTTP 503: {`
- 1x `prepared remote upload starts deployment`: status `failed`, chose `NO_OUTPUT`

## Machine-readable Receipt

[JSON receipt](https://github.com/cfregly/agent-harness-opt/blob/main/evals/results/insforge_mcp_tool_selection_frontier_available_live_2026-07-01.json)
