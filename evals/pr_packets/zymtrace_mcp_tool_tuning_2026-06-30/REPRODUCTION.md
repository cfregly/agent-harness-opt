# Reproduction for Zymtrace MCP

## Source Pin

- default project id: 00000000-0000-0000-0000-000000000000
- docs: https://docs.zymtrace.com/getting-started/, https://docs.zymtrace.com/category/model-context-protocol-mcp/
- local MCP server: zymtrace-mcp 26.6.1
- local mcp url: http://localhost:8080/mcp
- resource count: 3
- resources: flamegraph, topfunctions, topentities
- skills: configure-zymtrace-mcp, optimize-cpu-workloads, optimize-gpu-workloads, optimize-memory-allocation
- tool count: 25

## Command

```bash
python -m claude_agent_harness_opt model-matrix evals/model_matrix/zymtrace_mcp_tool_selection.json --env-file .env --live --require-live --providers anthropic,gemini,openai --harnesses prompt_json --instruction-variants zymtrace_host_and_skill_rules --cases 'cpu rank first containerized apps,default project metrics discovery skips search,full trace error recovers to discovery,gpu call tree uses hot traces,gpu inference workflow starts with metrics,hot trace discovery is bounded,resource fallback hot functions,selected trace drilldown is bounded' --variants stock_zymtrace_mcp,tuned_zymtrace_mcp_boundaries
```

## Value Bar

- baseline: stock_zymtrace_mcp at 0.583
- candidate: tuned_zymtrace_mcp_boundaries at 1.000
- delta: 0.417
- minimum delta: 0.010
- promote: yes

## Cases

- default project metrics discovery skips search | expected selection: project_metrics_activity_aggr | confusable alternatives checked: projects_search,project_metrics_query,topfunctions
  - task: For the default Zymtrace project, discover active GPU, CPU, model, service, token, and latency metric names between 2026-06-25T04:00:00+00:00 and 2026-06-25T05:00:00+00:00.
- cpu rank first containerized apps | expected selection: topentities | confusable alternatives checked: hot_traces,flamegraph,recommendations
  - task: Which containerized app should I optimize first by CPU cost from 2026-06-25T04:00:00+00:00 to 2026-06-25T05:00:00+00:00?
- gpu inference workflow starts with metrics | expected selection: project_metrics_activity_aggr | confusable alternatives checked: hot_traces,flamegraph,topfunctions
  - task: For the default Zymtrace project, start investigating why the vLLM inference workload has low GPU utilization between 2026-06-25T04:00:00+00:00 and 2026-06-25T05:00:00+00:00 by finding the relevant GPU, CPU, and framework metrics.
- gpu call tree uses hot traces | expected selection: hot_traces | confusable alternatives checked: flamegraph,topfunctions,project_flamegraph_json
  - task: Pull the GPU call tree for the vLLM workload from 2026-06-25T04:00:00+00:00 to 2026-06-25T05:00:00+00:00, but only do first-pass discovery.
- selected trace drilldown is bounded | expected selection: hot_traces | confusable alternatives checked: flamegraph,topfunctions,project_events_raw
  - task: Drill into hot trace prefix_hash 981237 and fetch exactly that full trace for the CPU profile from 2026-06-25T04:00:00+00:00 to 2026-06-25T05:00:00+00:00.
- full trace error recovers to discovery | expected selection: hot_traces | confusable alternatives checked: flamegraph,topfunctions,project_events_raw
  - task: The previous Zymtrace hot_traces call failed because meta_only=false was requested without a selected prefix_hash. Recover by doing first-pass CPU hot trace discovery for the default project between 2026-06-25T04:00:00+00:00 and 2026-06-25T05:00:00+00:00.
- hot trace discovery is bounded | expected selection: hot_traces | confusable alternatives checked: flamegraph,topfunctions,project_events_raw
  - task: Show only the top 3 hot trace candidates as metadata for CPU between 2026-06-25T04:00:00+00:00 and 2026-06-25T05:00:00+00:00. Do not return full stacks yet.
- resource fallback hot functions | expected selection: topfunctions | confusable alternatives checked: hot_traces,flamegraph,project_metrics_query
  - task: In this tool-only Zymtrace matrix, choose the fallback call for the topfunctions MCP resource to rank hottest CPU functions between 2026-06-25T04:00:00+00:00 and 2026-06-25T05:00:00+00:00.

## Summary Counts

- total: 48
- passed cases: 38
- failed cases: 10
- errors: 0
- score: 0.792
