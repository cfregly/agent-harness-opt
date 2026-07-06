# Firecrawl MCP Frontier Matrix Live Result - 2026-07-01

Passed: no
Live: yes

This retained frontier receipt runs the current available frontier profiles in this workspace: OpenAI `gpt-5.5` and Gemini `gemini-3.1-pro-preview-customtools`.

> [!NOTE]
> Anthropic frontier is tracked in separate Anthropic Opus receipts. The current MCP Opus receipts have 0 provider errors after the targeted Anthropic rerun; gstack skill routing remains a separate provider-state receipt. See [Frontier Stress Receipts](https://github.com/cfregly/agent-harness-opt/blob/main/docs/frontier-stress-2026-07-01.md).

## Matrix Summary

- total: 60
- passed_cases: 51
- failed_cases: 9
- errors: 0
- skipped: 0
- score: 0.85

## Profiles

- `anthropic-opus48-frontier`: `claude-opus-4-8`
- `openai-gpt55-frontier`: `gpt-5.5`
- `gemini-31-pro-customtools-frontier`: `gemini-3.1-pro-preview-customtools`

## Status By Profile

| Profile | Passed | Failed | Errors | Skipped |
|---|---:|---:|---:|---:|
| `gemini-31-pro-customtools-frontier` | 25 | 5 | 0 | 0 |
| `openai-gpt55-frontier` | 26 | 4 | 0 | 0 |

## Remaining Failure Clusters

- 4x `complex autonomous research`: status `failed`, chose `firecrawl_agent`
- 2x `single known page structured fields`: status `failed`, chose `firecrawl_extract`
- 2x `single page concise json avoids markdown`: status `failed`, chose `firecrawl_extract`
- 1x `url index before content fetch`: status `failed`, chose `firecrawl_map`

## Machine-readable Receipt

[JSON receipt](https://github.com/cfregly/agent-harness-opt/blob/main/evals/results/firecrawl_mcp_tool_selection_frontier_available_live_2026-07-01.json)
