# Zymtrace MCP Frontier Matrix Live Result - 2026-07-01

Passed: no
Live: yes

This retained frontier receipt runs the current available frontier profiles in this workspace: OpenAI `gpt-5.5` and Gemini `gemini-3.1-pro-preview-customtools`.

> [!NOTE]
> Anthropic frontier is tracked in separate Anthropic Opus receipts. The current MCP Opus receipts have 0 provider errors after the targeted Anthropic rerun; gstack skill routing remains a separate provider-state receipt. See [Frontier Stress Receipts](https://github.com/cfregly/agent-harness-opt/blob/main/docs/frontier-stress-2026-07-01.md).

## Matrix Summary

- total: 272
- passed_cases: 233
- failed_cases: 27
- errors: 12
- skipped: 0
- score: 0.857

## Profiles

- `anthropic-opus48-frontier`: `claude-opus-4-8`
- `openai-gpt55-frontier`: `gpt-5.5`
- `gemini-31-pro-customtools-frontier`: `gemini-3.1-pro-preview-customtools`

## Status By Profile

| Profile | Passed | Failed | Errors | Skipped |
|---|---:|---:|---:|---:|
| `gemini-31-pro-customtools-frontier` | 116 | 19 | 1 | 0 |
| `openai-gpt55-frontier` | 117 | 8 | 11 | 0 |

## Remaining Failure Clusters

- 3x `selected trace drilldown is bounded`: status `failed`, chose `hot_traces`
- 3x `hot trace discovery is bounded`: status `failed`, chose `hot_traces`
- 3x `project top hosts endpoint`: status `error`, chose `error: model did not return a JSON tool choice: `
- 2x `project top pods endpoint`: status `error`, chose `error: model did not return a JSON tool choice: `
- 2x `default project metrics discovery skips search`: status `failed`, chose `project_metrics_activity_aggr`
- 2x `default project raw sample skips search`: status `failed`, chose `project_events_raw`
- 2x `gpu inference workflow starts with metrics`: status `failed`, chose `project_metrics_activity_aggr`
- 2x `project json flamegraph stays project scoped`: status `failed`, chose `flamegraph`
- 2x `project top deployments endpoint`: status `error`, chose `error: model did not return a JSON tool choice: `
- 2x `project top executables endpoint`: status `failed`, chose `topentities`
- 2x `project top namespaces endpoint`: status `failed`, chose `topentities`
- 1x `high level flamegraph`: status `failed`, chose `project_flamegraph_json`

## Machine-readable Receipt

[JSON receipt](https://github.com/cfregly/agent-harness-opt/blob/main/evals/results/zymtrace_mcp_frontier_available_matrix_live_2026-07-01.json)
