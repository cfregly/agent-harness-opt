Suggested title: Tighten Zymtrace MCP retrieval routing with live evals

> [!NOTE]
> This page starts with the human summary. Detailed eval, command, and machine-readable material is preserved below.


## Value Proposition

- Helps agents choose the intended Zymtrace MCP workflow instead of adjacent tools that look plausible.
- `tuned_zymtrace_mcp_boundaries` improved score from 0.583 to 1.000, a 0.417 gain over `stock_zymtrace_mcp`.
- The signal comes from 48 live matrix cells on a pinned source surface.
- Baseline mistakes clustered on default project metrics discovery skips search, gpu inference workflow starts with metrics, selected trace drilldown is bounded, hot trace discovery is bounded.
- The change clears the adversarially-confirmed value bar for this pinned evaluation.

## What Already Works

- The tested Zymtrace MCP surface is already strong: 38/48 live cells passed with 0 errors.
- The candidate score is 1.000, so this is a boundary tightening, not a broad rewrite.
- The packet keeps passing behavior visible so maintainers can see what does not need to change.

<details>
<summary>LLM / Machine-readable details</summary>

## How This Is Proven Useful

- The proof compares `stock_zymtrace_mcp` and `tuned_zymtrace_mcp_boundaries` on the same tasks, providers, harnesses, and instruction variants.
- The measured delta is 0.417 against a required minimum of 0.010.
- The run contains 48 matrix cells, with 10 failures preserved as evidence instead of hand-waved examples.
- The source pin, exact cases, reproduction command, and result artifact are included so the claim can be rerun or challenged.

## Current Frontier Coverage

- No current frontier profile metadata is present in this result.
- Treat this packet as historical or compatibility evidence until rerun on current latest/frontier models and harness versions.
- Older-model wins should not be the headline if the ambiguity is fixed by newer model or harness behavior.

## Downside If Not Changed

- Ambiguous descriptions let plausible adjacent tools win, so failures look reasonable in transcripts even when the selected workflow is wrong.
- Model or harness upgrades can reintroduce the same mistake unless the boundary is encoded in descriptions and regression cases.
- Routing ambiguity can make agents choose broader or higher-cost tool paths instead of the narrow workflow the user asked for.

## Proposed change for Zymtrace MCP

Clarify default-project, GPU metrics-first, resource-first, and bounded hot-traces routing.

## Why

This change is backed by a harness matrix result, not a prose-only review. The bar is adversarially-confirmed to add value.

## Pinned surface

- default project id: 00000000-0000-0000-0000-000000000000
- docs: https://docs.zymtrace.com/getting-started/, https://docs.zymtrace.com/category/model-context-protocol-mcp/
- local MCP server: zymtrace-mcp 26.6.1
- local mcp url: http://localhost:8080/mcp
- resource count: 3
- resources: flamegraph, topfunctions, topentities
- skills: configure-zymtrace-mcp, optimize-cpu-workloads, optimize-gpu-workloads, optimize-memory-allocation
- tool count: 25
- target repo: https://github.com/zystem-io/zymtrace

## Result

- promoted by value bar: yes
- baseline variant: stock_zymtrace_mcp
- candidate variant: tuned_zymtrace_mcp_boundaries
- baseline score: 0.583
- candidate score: 1.000
- delta: 0.417
- minimum delta: 0.010

## What We Learned

- `tuned_zymtrace_mcp_boundaries` beat `stock_zymtrace_mcp` by 0.417 against a minimum delta of 0.010.
- Baseline mistakes clustered on these cases: default project metrics discovery skips search, gpu inference workflow starts with metrics, selected trace drilldown is bounded, hot trace discovery is bounded.
- The suggested change clears the adversarially-confirmed value bar for this pinned surface.

## Run surfaces

- provider=anthropic, profile=anthropic-sonnet, tier=, model=claude-sonnet-4-5, harness=prompt_json, instruction=zymtrace_host_and_skill_rules
- provider=openai, profile=openai-default, tier=, model=gpt-4.1, harness=prompt_json, instruction=zymtrace_host_and_skill_rules
- provider=gemini, profile=gemini-default, tier=, model=gemini-2.5-pro, harness=prompt_json, instruction=zymtrace_host_and_skill_rules

## Cell summary

- provider=anthropic, harness=prompt_json, variant=stock_zymtrace_mcp, instruction=zymtrace_host_and_skill_rules, passed=4, failed=4, errors=0, score=0.5
- provider=anthropic, harness=prompt_json, variant=tuned_zymtrace_mcp_boundaries, instruction=zymtrace_host_and_skill_rules, passed=8, failed=0, errors=0, score=1.0
- provider=gemini, harness=prompt_json, variant=stock_zymtrace_mcp, instruction=zymtrace_host_and_skill_rules, passed=5, failed=3, errors=0, score=0.625
- provider=gemini, harness=prompt_json, variant=tuned_zymtrace_mcp_boundaries, instruction=zymtrace_host_and_skill_rules, passed=8, failed=0, errors=0, score=1.0
- provider=openai, harness=prompt_json, variant=stock_zymtrace_mcp, instruction=zymtrace_host_and_skill_rules, passed=5, failed=3, errors=0, score=0.625
- provider=openai, harness=prompt_json, variant=tuned_zymtrace_mcp_boundaries, instruction=zymtrace_host_and_skill_rules, passed=8, failed=0, errors=0, score=1.0

## Reproduce

```bash
python -m claude_agent_harness_opt model-matrix evals/model_matrix/zymtrace_mcp_tool_selection.json --env-file .env --live --require-live --providers anthropic,gemini,openai --harnesses prompt_json --instruction-variants zymtrace_host_and_skill_rules --cases 'cpu rank first containerized apps,default project metrics discovery skips search,full trace error recovers to discovery,gpu call tree uses hot traces,gpu inference workflow starts with metrics,hot trace discovery is bounded,resource fallback hot functions,selected trace drilldown is bounded' --variants stock_zymtrace_mcp,tuned_zymtrace_mcp_boundaries
```

## Examples used

- default project metrics discovery skips search | expected selection: project_metrics_activity_aggr | confusable alternatives checked: projects_search,project_metrics_query,topfunctions
- cpu rank first containerized apps | expected selection: topentities | confusable alternatives checked: hot_traces,flamegraph,recommendations
- gpu inference workflow starts with metrics | expected selection: project_metrics_activity_aggr | confusable alternatives checked: hot_traces,flamegraph,topfunctions
- gpu call tree uses hot traces | expected selection: hot_traces | confusable alternatives checked: flamegraph,topfunctions,project_flamegraph_json
- selected trace drilldown is bounded | expected selection: hot_traces | confusable alternatives checked: flamegraph,topfunctions,project_events_raw
- full trace error recovers to discovery | expected selection: hot_traces | confusable alternatives checked: flamegraph,topfunctions,project_events_raw
- hot trace discovery is bounded | expected selection: hot_traces | confusable alternatives checked: flamegraph,topfunctions,project_events_raw
- resource fallback hot functions | expected selection: topfunctions | confusable alternatives checked: hot_traces,flamegraph,project_metrics_query

## Baseline failures

- default project metrics discovery skips search chose project_metrics_activity_aggr
- gpu inference workflow starts with metrics chose project_metrics_activity_aggr
- selected trace drilldown is bounded chose hot_traces
- hot trace discovery is bounded chose hot_traces
- default project metrics discovery skips search chose project_metrics_activity_aggr
- gpu inference workflow starts with metrics chose project_metrics_activity_aggr
- selected trace drilldown is bounded chose hot_traces
- selected trace drilldown is bounded chose hot_traces

## Candidate passes

- default project metrics discovery skips search chose project_metrics_activity_aggr
- cpu rank first containerized apps chose topentities
- gpu inference workflow starts with metrics chose project_metrics_activity_aggr
- gpu call tree uses hot traces chose hot_traces
- selected trace drilldown is bounded chose hot_traces
- full trace error recovers to discovery chose hot_traces
- hot trace discovery is bounded chose hot_traces
- resource fallback hot functions chose topfunctions

## Evidence

- Public harness repo: [claude-agent-harness-opt](https://github.com/cfregly/claude-agent-harness-opt)
- Reproduction doc: [REPRODUCTION.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/zymtrace_mcp_tool_tuning_2026-06-30/REPRODUCTION.md)
- Evidence JSON: [evidence.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/zymtrace_mcp_tool_tuning_2026-06-30/evidence.json)
- Matrix: [zymtrace_mcp_tool_selection.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/model_matrix/zymtrace_mcp_tool_selection.json)
- Result artifact: [zymtrace_mcp_matrix_live_2026-06-30.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/zymtrace_mcp_matrix_live_2026-06-30.json)

</details>
