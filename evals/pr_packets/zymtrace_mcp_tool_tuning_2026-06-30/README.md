# Zymtrace MCP Tool Tuning PR Packet

Share link: [Zymtrace full PR/evidence bundle](https://github.com/cfregly/claude-agent-harness-opt/tree/main/evals/pr_packets/zymtrace_mcp_tool_tuning_2026-06-30)

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

Current frontier stress receipt: 272 current available-frontier cells, 233 passed, 27 failed, 12 errors on OpenAI `gpt-5.5` and Gemini `gemini-3.1-pro-preview-customtools`. Treat this as hill-descending coverage for the next tuning pass.

Anthropic Opus frontier receipt: 136 Anthropic Opus cells, 118 passed, 18 failed, 0 errors on accessible `claude-opus-4-8`. Any failed cells are model-selection findings, not provider-credit blockers.

Confirmed improvement. This clears the adversarially-confirmed to add value bar.

The tuned Zymtrace MCP boundary rules moved the selected held-out prompt JSON cells from 14/24
stock passes to 24/24 tuned passes across Anthropic, OpenAI, and Gemini.

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
https://github.com/cfregly/claude-agent-harness-opt/tree/main/docs/findings/zymtrace

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
https://github.com/cfregly/claude-agent-harness-opt/tree/main/docs/findings/zymtrace

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
https://github.com/cfregly/claude-agent-harness-opt/tree/main/docs/findings/zymtrace

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

- Public harness repo: [claude-agent-harness-opt](https://github.com/cfregly/claude-agent-harness-opt)
- Bundle folder: [zymtrace_mcp_tool_tuning_2026-06-30](https://github.com/cfregly/claude-agent-harness-opt/tree/main/evals/pr_packets/zymtrace_mcp_tool_tuning_2026-06-30)
- Matrix: [zymtrace_mcp_tool_selection.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/model_matrix/zymtrace_mcp_tool_selection.json)
- Result artifact: [zymtrace_mcp_matrix_live_2026-06-30.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/zymtrace_mcp_matrix_live_2026-06-30.json)
- PR_TITLE.txt: [PR_TITLE.txt](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/zymtrace_mcp_tool_tuning_2026-06-30/PR_TITLE.txt)
- PR_BODY.md: [PR_BODY.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/zymtrace_mcp_tool_tuning_2026-06-30/PR_BODY.md)
- REPRODUCTION.md: [REPRODUCTION.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/zymtrace_mcp_tool_tuning_2026-06-30/REPRODUCTION.md)
- evidence.json: [evidence.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/zymtrace_mcp_tool_tuning_2026-06-30/evidence.json)
- Target repo: [zymtrace](https://github.com/zystem-io/zymtrace)

<details>
<summary>LLM / Machine-readable details</summary>

## Frontier Stress Result

The current frontier sweep was run after adding named frontier profiles to the Zymtrace matrix and
hardening the prompt-JSON parser for fenced, wrapped, and array-shaped model outputs.

OpenAI `gpt-5.5` and Gemini `gemini-3.1-pro-preview-customtools` completed 272 live cells with
233 passed, 27 failed, and 12 errors. Treat this as hill-descending evidence for the next tuning
round, not as a replacement for the confirmed 24/24 held-out improvement.

Anthropic `claude-fable-5` was not available to the provided key. The accessible `claude-opus-4-8` rerun completed 136 cells with 118 passed, 18 failed, and 0 errors.
The all-provider attempt is retained here:
[zymtrace_mcp_frontier_all_providers_attempt_2026-07-01.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/zymtrace_mcp_frontier_all_providers_attempt_2026-07-01.md).

## Reproduce

[REPRODUCTION.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/zymtrace_mcp_tool_tuning_2026-06-30/REPRODUCTION.md)
contains the exact live matrix command and retained source pins.

</details>
