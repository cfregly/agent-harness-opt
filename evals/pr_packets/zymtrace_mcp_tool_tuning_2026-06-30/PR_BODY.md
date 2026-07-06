Suggested title: Tighten Zymtrace MCP retrieval routing with live evals

> [!NOTE]
> This page starts with the founder handoff. Detailed eval, command, and machine-readable material is preserved below.

## Summary

### Exact Text To Apply

Copy the suggested replacement text into the target repo field named in the first column.

| Where to edit | Baseline text | Suggested replacement text |
|---|---|---|
| `topfunctions.purpose` | Return list of GPU, CPU or allocation top functions. | Rank hottest functions for CPU, GPU, or allocation profiles. |
| `topentities.purpose` | Return list of GPU, CPU or allocation top entities. | Rank top runtime entities such as executables, scripts, hosts, threads, deployments, containers, namespaces, pods, apps, services, or workloads. |
| `flamegraph.purpose` | Return profiling data as flamegraph. | Return a high-level rendered flamegraph fallback for a time window and optional runtime filters. |
| `hot_traces.purpose` | Find hot CPU/GPU profiling stack traces. | Discover hot stack traces/call trees and drill into one selected trace. |
| `hot_traces.avoid_when` | No first-full-stack-fetch avoid_when boundary. | Avoid as a first full-stack fetch. Use meta_only=true and a small limit before requesting a selected prefix_hash. |
| `hot_traces.input_schema.properties.meta_only` | Discovery mode | Use true for discovery; false only after selecting a prefix_hash or when full stacks are explicit |
| `hot_traces.input_schema.properties.limit` | No limit argument in baseline schema. | Small result limit |
| `project_metrics_activity_aggr.purpose` | Retrieve metrics activity aggregations for a project. | Discover active metric names and useful attributes for a project, including GPU, CPU, model, service, token, latency, and framework metrics. |
| `project_metrics_activity_aggr.avoid_when` | No known-metric-name avoid_when boundary. | Avoid when the metric name is already known and the user asks for values; use project_metrics_query then. |
| `project_metrics_query.purpose` | Query metrics for a project with custom filters. | Query metric time-series values for known metric names and dimensions. |
| `project_metrics_query.avoid_when` | No metric-discovery avoid_when boundary. | Avoid before discovering metric names when the user is unsure what metrics exist. |
| `projects_search.avoid_when` | No default-project avoid_when boundary. | Avoid for the normal default-project path. Do not search just because a project-scoped tool needs a project_id; use default project_id 00000000-0000-0000-0000-000000000000 unless the user explicitly asks otherwise. |
| New MCP resource `gpu_readiness` | No single MCP resource reports GPU readiness without checking logs and metric surfaces. | Expose a read-only resource with supports_gpu, gpu_metrics_enabled, detected GPU names, and CUDA library extraction status. Do not expose the license value. |

### Baseline / Suggested Behavior
The table below is the exact handoff text. Baseline / before is the current behavior. Suggested / after is the proposed wording or behavior to implement.

| Suggested change | Baseline / before description | Suggested / after description | Result |
|---|---|---|---|
| Encode the profiling workflow: prefer MCP resources for `topfunctions`, `topentities`, and `flamegraph`. Use project UUID `00000000-0000-0000-0000-000000000000` unless the user names another project. Discover metrics before GPU or inference metric queries. Use rank-first CPU tools. Fetch full traces only after a selected `prefix_hash`. | Agents could skip resource-first lookup, use `project_id: "default"`, query GPU or inference metrics before discovery, or fetch full traces before selecting a `prefix_hash`. | Use MCP resources first for `topfunctions`, `topentities`, and `flamegraph`. Use the default project UUID unless another project is named. Discover metrics before GPU or inference queries. Rank CPU traces before full trace fetches. Fetch full trace only after a selected `prefix_hash`. | `tuned_zymtrace_mcp_boundaries` scored 1.000, a 0.417 gain. Add retained cases as regression coverage. |
| Add an explicit idle-exclusion option or marker for optimization-oriented `hot_traces` discovery. | `hot_traces` can rank an `IDLE` trace first for optimization-oriented discovery. | Add idle exclusion or an explicit idle marker for optimization-oriented `hot_traces` discovery before traces are ranked. | `tuned_zymtrace_mcp_boundaries` scored 1.000, a 0.417 gain. Add retained cases as regression coverage. |
| Add a server-side option or marker that keeps `zymtrace-profiler` from being presented as an optimization target in `topentities`. | `topentities` can expose `zymtrace-profiler` as if it were an application optimization target. | Filter or mark `zymtrace-profiler` in `topentities` so profiler self-noise is not presented as an application optimization target. | `tuned_zymtrace_mcp_boundaries` scored 1.000, a 0.417 gain. Add retained cases as regression coverage. |
| Add a small read-only GPU readiness resource that reports GPU support, GPU metric collection, detected GPU names, and CUDA library extraction state without exposing the license value. | GPU support, GPU metric collection, detected GPU names, and CUDA library extraction state are scattered across logs and metric surfaces. | Expose one read-only GPU readiness resource with `supports_gpu`, `gpu_metrics_enabled`, detected GPU names, and CUDA library extraction status without exposing the license value. | `tuned_zymtrace_mcp_boundaries` scored 1.000, a 0.417 gain. Add retained cases as regression coverage. |


## Result

- Confirmed improvement: `tuned_zymtrace_mcp_boundaries` moved from 0.583 to 1.000, a 0.417 gain over `stock_zymtrace_mcp`.
- Value bar: cleared the 0.010 minimum delta.
- Proof scope: 48 live matrix cells, 38 passed, 10 failed, 0 errors.

## What Failed

- `stock_zymtrace_mcp` failed or chose the wrong boundary on: default project metrics discovery skips search, gpu inference workflow starts with metrics, selected trace drilldown is bounded, hot trace discovery is bounded.
- Those failures are the target-owned behavior to encode in descriptions, defaults, options, or regression tests.

## Why This Matters

- Value proposition: helps agents choose the intended Zymtrace MCP workflow instead of adjacent tools that look plausible.
- Proof: `tuned_zymtrace_mcp_boundaries` scored 1.000, a 0.417 gain.
- Proof scope: 48 live matrix cells on the same tasks, providers, harnesses, and instruction variants.
- Baseline failure pattern: default project metrics discovery skips search, gpu inference workflow starts with metrics, selected trace drilldown is bounded, hot trace discovery is bounded.
- Downside avoided: plausible-but-wrong tool choices that waste time or return misleading results.

## Recommended Actions

- Apply suggested change: Encode the profiling workflow: prefer MCP resources for `topfunctions`, `topentities`, and `flamegraph`. Use project UUID `00000000-0000-0000-0000-000000000000` unless the user names another project. Discover metrics before GPU or inference metric queries. Use rank-first CPU tools. Fetch full traces only after a selected `prefix_hash`.
- Add an explicit idle-exclusion option or marker for optimization-oriented `hot_traces` discovery.
- Add a server-side option or marker that keeps `zymtrace-profiler` from being presented as an optimization target in `topentities`.
- Add a small read-only GPU readiness resource that reports GPU support, GPU metric collection, detected GPU names, and CUDA library extraction state without exposing the license value.
- Add the selected cases below to repo CI or release-blocking regression coverage.
- Run the local-agent prompt below in your repo to identify exact files, patch locations, tests, and risks before editing.

## Run This In Your Repo

Replace `/path/to/repo` with the target team's local checkout. These commands ask for a plan only.

```bash
cat <<'PROMPT' | codex exec -C /path/to/repo --sandbox read-only -
Review this action-first finding:
https://github.com/cfregly/agent-harness-opt/tree/main/docs/findings/zymtrace

Then inspect this local repo and tell us exactly what to change.

Return:
- Executive summary
- Before / after
- Recommended repo changes
- Suggested patch locations
- Regression tests to add
- Risks or open questions

Do not edit files yet.
PROMPT
```

```bash
claude -p --permission-mode plan "$(cat <<'PROMPT'
Review this action-first finding:
https://github.com/cfregly/agent-harness-opt/tree/main/docs/findings/zymtrace

Then inspect this local repo and tell us exactly what to change.

Return:
- Executive summary
- Before / after
- Recommended repo changes
- Suggested patch locations
- Regression tests to add
- Risks or open questions

Do not edit files yet.
PROMPT
)"
```

```bash
gemini --approval-mode plan --output-format text -p "$(cat <<'PROMPT'
Review this action-first finding:
https://github.com/cfregly/agent-harness-opt/tree/main/docs/findings/zymtrace

Then inspect this local repo and tell us exactly what to change.

Return:
- Executive summary
- Before / after
- Recommended repo changes
- Suggested patch locations
- Regression tests to add
- Risks or open questions

Do not edit files yet.
PROMPT
)"
```

## Model Coverage

| Evidence lane | Baseline | Candidate |
|---|---|---|
| Anthropic | `stock_zymtrace_mcp` 4/8 passed, 4 failed, 0 errors. | `tuned_zymtrace_mcp_boundaries` 8/8 passed. |
| Google Gemini | `stock_zymtrace_mcp` 5/8 passed, 3 failed, 0 errors. | `tuned_zymtrace_mcp_boundaries` 8/8 passed. |
| OpenAI | `stock_zymtrace_mcp` 5/8 passed, 3 failed, 0 errors. | `tuned_zymtrace_mcp_boundaries` 8/8 passed. |

Provider/model rows are evidence lanes. The target repo actions above are the only primary CTA.

## Evidence Bundle

- Public harness repo: [agent-harness-opt](https://github.com/cfregly/agent-harness-opt)
- Bundle folder: [zymtrace_mcp_tool_tuning_2026-06-30](https://github.com/cfregly/agent-harness-opt/tree/main/evals/pr_packets/zymtrace_mcp_tool_tuning_2026-06-30)
- Matrix: [zymtrace_mcp_tool_selection.json](https://github.com/cfregly/agent-harness-opt/blob/main/evals/model_matrix/zymtrace_mcp_tool_selection.json)
- Result artifact: [zymtrace_mcp_matrix_live_2026-06-30.json](https://github.com/cfregly/agent-harness-opt/blob/main/evals/results/zymtrace_mcp_matrix_live_2026-06-30.json)
- PR_TITLE.txt: [PR_TITLE.txt](https://github.com/cfregly/agent-harness-opt/blob/main/evals/pr_packets/zymtrace_mcp_tool_tuning_2026-06-30/PR_TITLE.txt)
- PR_BODY.md: [PR_BODY.md](https://github.com/cfregly/agent-harness-opt/blob/main/evals/pr_packets/zymtrace_mcp_tool_tuning_2026-06-30/PR_BODY.md)
- REPRODUCTION.md: [REPRODUCTION.md](https://github.com/cfregly/agent-harness-opt/blob/main/evals/pr_packets/zymtrace_mcp_tool_tuning_2026-06-30/REPRODUCTION.md)
- evidence.json: [evidence.json](https://github.com/cfregly/agent-harness-opt/blob/main/evals/pr_packets/zymtrace_mcp_tool_tuning_2026-06-30/evidence.json)
- Target repo: [zymtrace](https://github.com/zystem-io/zymtrace)

<details>
<summary>LLM / Machine-readable details</summary>

## Frontier Receipts

- Anthropic Opus frontier receipt: [zymtrace_mcp_tool_selection_frontier_anthropic_live_2026-07-01.md](https://github.com/cfregly/agent-harness-opt/blob/main/evals/results/zymtrace_mcp_tool_selection_frontier_anthropic_live_2026-07-01.md)
- Anthropic Opus JSON receipt: [zymtrace_mcp_tool_selection_frontier_anthropic_live_2026-07-01.json](https://github.com/cfregly/agent-harness-opt/blob/main/evals/results/zymtrace_mcp_tool_selection_frontier_anthropic_live_2026-07-01.json)
- Current frontier stress receipt: [zymtrace_mcp_frontier_available_matrix_live_2026-07-01.md](https://github.com/cfregly/agent-harness-opt/blob/main/evals/results/zymtrace_mcp_frontier_available_matrix_live_2026-07-01.md)
- Current frontier JSON receipt: [zymtrace_mcp_frontier_available_matrix_live_2026-07-01.json](https://github.com/cfregly/agent-harness-opt/blob/main/evals/results/zymtrace_mcp_frontier_available_matrix_live_2026-07-01.json)

## How This Is Proven Useful

- The proof compares `stock_zymtrace_mcp` and `tuned_zymtrace_mcp_boundaries` on the same tasks, providers, harnesses, and instruction variants.
- The measured delta is 0.417 against a required minimum of 0.010.
- The run contains 48 matrix cells, with 10 failures preserved as evidence instead of hand-waved examples.
- The source pin, exact cases, reproduction command, and result artifact are included so the claim can be rerun or challenged.

## Current Frontier Coverage

- The packet now includes a 2026-07-01 frontier stress/descent run for OpenAI `gpt-5.5` and Gemini `gemini-3.1-pro-preview-customtools`.
- The frontier run completed 272 live cells with 233 passed, 27 failed, and 12 errors across both stock/tuned tool variants and both instruction variants.
- Treat the 24/24 held-out default-profile result as the confirmed improvement, and treat the frontier receipt as the next failure-discovery surface.
- Anthropic Opus coverage is retained separately: `claude-fable-5` remained unavailable, and the accessible `claude-opus-4-8` rerun completed 136 cells with 118 passed, 18 failed, and 0 errors.

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

## Artifact Pointers

- Public harness repo: [agent-harness-opt](https://github.com/cfregly/agent-harness-opt)
- Reproduction doc: [REPRODUCTION.md](https://github.com/cfregly/agent-harness-opt/blob/main/evals/pr_packets/zymtrace_mcp_tool_tuning_2026-06-30/REPRODUCTION.md)
- Evidence JSON: [evidence.json](https://github.com/cfregly/agent-harness-opt/blob/main/evals/pr_packets/zymtrace_mcp_tool_tuning_2026-06-30/evidence.json)
- Matrix: [zymtrace_mcp_tool_selection.json](https://github.com/cfregly/agent-harness-opt/blob/main/evals/model_matrix/zymtrace_mcp_tool_selection.json)
- Result artifact: [zymtrace_mcp_matrix_live_2026-06-30.json](https://github.com/cfregly/agent-harness-opt/blob/main/evals/results/zymtrace_mcp_matrix_live_2026-06-30.json)
- Frontier stress result: [zymtrace_mcp_frontier_available_matrix_live_2026-07-01.md](https://github.com/cfregly/agent-harness-opt/blob/main/evals/results/zymtrace_mcp_frontier_available_matrix_live_2026-07-01.md)
- Frontier JSON receipt: [zymtrace_mcp_frontier_available_matrix_live_2026-07-01.json](https://github.com/cfregly/agent-harness-opt/blob/main/evals/results/zymtrace_mcp_frontier_available_matrix_live_2026-07-01.json)
- All-provider frontier attempt: [zymtrace_mcp_frontier_all_providers_attempt_2026-07-01.md](https://github.com/cfregly/agent-harness-opt/blob/main/evals/results/zymtrace_mcp_frontier_all_providers_attempt_2026-07-01.md)

</details>
