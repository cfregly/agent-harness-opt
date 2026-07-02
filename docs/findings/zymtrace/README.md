# Zymtrace MCP Finding

Share link: [Zymtrace packet](https://github.com/cfregly/claude-agent-harness-opt/tree/main/docs/findings/zymtrace)

## Summary

| Before | After | Result |
|---|---|---|
| `stock_zymtrace_mcp` scored 0.583. Baseline mistakes clustered on default project metrics discovery skips search, gpu inference workflow starts with metrics, selected trace drilldown is bounded, hot trace discovery is bounded. | Suggested change: Clarify default-project, GPU metrics-first, resource-first, and bounded hot-traces routing.<br>Add an explicit idle-exclusion option or marker for optimization-oriented `hot_traces` discovery.<br>Add a server-side option or marker that keeps `zymtrace-profiler` from being presented as an optimization target in `topentities`.<br>Add a small read-only GPU readiness resource that reports GPU support, GPU metric collection, detected GPU names, and CUDA library extraction state without exposing the license value. | `tuned_zymtrace_mcp_boundaries` scored 1.000, a 0.417 gain. Add retained cases as regression coverage. |

## Why This Matters

- Value proposition: helps agents choose the intended Zymtrace MCP workflow instead of adjacent tools that look plausible.
- Proof: `tuned_zymtrace_mcp_boundaries` scored 1.000, a 0.417 gain.
- Evidence: 48 live matrix cells on the same tasks, providers, harnesses, and instruction variants.
- Baseline failure pattern: default project metrics discovery skips search, gpu inference workflow starts with metrics, selected trace drilldown is bounded, hot trace discovery is bounded.
- Downside avoided: plausible-but-wrong tool choices that waste time or return misleading results.

## Recommended Actions

- Apply this change: Clarify default-project, GPU metrics-first, resource-first, and bounded hot-traces routing.
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
- Founder handoff: [Zymtrace MCP](https://github.com/cfregly/claude-agent-harness-opt/tree/main/docs/findings/zymtrace)
- Packet folder: [zymtrace_mcp_tool_tuning_2026-06-30](https://github.com/cfregly/claude-agent-harness-opt/tree/main/evals/pr_packets/zymtrace_mcp_tool_tuning_2026-06-30)
- PR_TITLE.txt: [PR_TITLE.txt](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/zymtrace_mcp_tool_tuning_2026-06-30/PR_TITLE.txt)
- PR_BODY.md: [PR_BODY.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/zymtrace_mcp_tool_tuning_2026-06-30/PR_BODY.md)
- REPRODUCTION.md: [REPRODUCTION.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/zymtrace_mcp_tool_tuning_2026-06-30/REPRODUCTION.md)
- evidence.json: [evidence.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/zymtrace_mcp_tool_tuning_2026-06-30/evidence.json)
- Matrix: [zymtrace_mcp_tool_selection.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/model_matrix/zymtrace_mcp_tool_selection.json)
- Result artifact: [zymtrace_mcp_matrix_live_2026-06-30.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/zymtrace_mcp_matrix_live_2026-06-30.json)
- Target repo: [zymtrace](https://github.com/zystem-io/zymtrace)

Bundle folder: [Zymtrace full PR/evidence bundle](https://github.com/cfregly/claude-agent-harness-opt/tree/main/evals/pr_packets/zymtrace_mcp_tool_tuning_2026-06-30)

- Finding folder: [Zymtrace finding](https://github.com/cfregly/claude-agent-harness-opt/tree/main/docs/findings/zymtrace)
- Frontier stress receipt: [zymtrace_mcp_frontier_available_matrix_live_2026-07-01.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/zymtrace_mcp_frontier_available_matrix_live_2026-07-01.md)
- Frontier JSON receipt: [zymtrace_mcp_frontier_available_matrix_live_2026-07-01.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/zymtrace_mcp_frontier_available_matrix_live_2026-07-01.json)
- Anthropic Opus receipt: [zymtrace_mcp_tool_selection_frontier_anthropic_live_2026-07-01.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/zymtrace_mcp_tool_selection_frontier_anthropic_live_2026-07-01.md)
- Anthropic Opus JSON: [zymtrace_mcp_tool_selection_frontier_anthropic_live_2026-07-01.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/zymtrace_mcp_tool_selection_frontier_anthropic_live_2026-07-01.json)
- Coverage: [zymtrace_mcp_coverage_2026-06-30.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/zymtrace_mcp_coverage_2026-06-30.md)
- Live result: [zymtrace_mcp_matrix_live_2026-06-30.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/zymtrace_mcp_matrix_live_2026-06-30.json)
- Frontier stress result: [zymtrace_mcp_frontier_available_matrix_live_2026-07-01.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/zymtrace_mcp_frontier_available_matrix_live_2026-07-01.md)
- Frontier JSON receipt: [zymtrace_mcp_frontier_available_matrix_live_2026-07-01.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/zymtrace_mcp_frontier_available_matrix_live_2026-07-01.json)
- All-provider frontier attempt: [zymtrace_mcp_frontier_all_providers_attempt_2026-07-01.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/zymtrace_mcp_frontier_all_providers_attempt_2026-07-01.md)
- PR body: [PR_BODY.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/zymtrace_mcp_tool_tuning_2026-06-30/PR_BODY.md)
- Reproduction doc: [REPRODUCTION.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/zymtrace_mcp_tool_tuning_2026-06-30/REPRODUCTION.md)
- Evidence JSON: [evidence.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/zymtrace_mcp_tool_tuning_2026-06-30/evidence.json)

## Result

Confirmed improvement. This clears the adversarially-confirmed to add value bar.

Current frontier stress receipt: 272 current available-frontier cells, 233 passed, 27 failed, 12 errors on OpenAI `gpt-5.5` and Gemini `gemini-3.1-pro-preview-customtools`. Treat this as hill-descending coverage for the next tuning pass, not as a replacement for the promoted baseline-to-tuned result.

Anthropic Opus frontier receipt: 136 Anthropic Opus cells, 118 passed, 18 failed, 0 errors on accessible `claude-opus-4-8`. Any failed cells are model-selection findings, not provider-credit blockers.

The expanded held-out prompt JSON run moved from 4/8 to 8/8 on Anthropic, 5/8 to 8/8 on OpenAI, and
5/8 to 8/8 on Gemini. Across all three providers, stock passed 14/24 cells and tuned passed 24/24.

The new result is packaged here:

- Matrix result: [zymtrace_mcp_matrix_live_2026-06-30.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/zymtrace_mcp_matrix_live_2026-06-30.json)
- Coverage audit: [zymtrace_mcp_coverage_2026-06-30.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/zymtrace_mcp_coverage_2026-06-30.md)
- Frontier stress result: [zymtrace_mcp_frontier_available_matrix_live_2026-07-01.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/zymtrace_mcp_frontier_available_matrix_live_2026-07-01.md)
- All-provider frontier attempt: [zymtrace_mcp_frontier_all_providers_attempt_2026-07-01.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/zymtrace_mcp_frontier_all_providers_attempt_2026-07-01.md)
- Upstream PR packet: [zymtrace_mcp_tool_tuning_2026-06-30](https://github.com/cfregly/claude-agent-harness-opt/tree/main/evals/pr_packets/zymtrace_mcp_tool_tuning_2026-06-30)
- Generated title: `Tighten Zymtrace MCP retrieval routing with live evals`

After the first live result, `matrix-coverage` exposed untested generated REST helpers. The hardened
matrix now has 34 cases, 25 of 25 expected-tool coverage, 25 of 25 forbidden-tool coverage, 85
boundary pairs, argument checks for every argument-taking expected tool, and `check_family` labels
for every case.

## Frontier Stress Result

The 2026-07-01 frontier stress run used OpenAI `gpt-5.5` and Gemini
`gemini-3.1-pro-preview-customtools` across the full 34-case Zymtrace matrix, both tool variants,
and both instruction variants. It completed 272 live cells with 233 passed, 27 failed, and 12 errors.

This is descent evidence for the next tuning pass. It shows the latest frontier models still expose
edge cases around generated stats endpoints, JSON flamegraph-vs-rendered flamegraph boundaries, and
prompt-JSON output robustness.

Anthropic Opus coverage is retained separately in this packet. `claude-fable-5` remained unavailable to the provided key. The accessible `claude-opus-4-8` rerun completed 136 cells with 118 passed, 18 failed, and 0 errors.

## GPU Verification

The local single-host Docker Compose install was originally CPU-only in practice. The profiler had
GPU flags and NVML access, but the backend `ingest` and `web` services were started without
`ZYMTRACE_LICENSE_KEY`, so the profiler logs showed `SupportsGpu:false`.

After adding the commercial license to ignored `.env` files, recreating `ingest` and `web`, and
restarting the standalone profiler, live verification changed:

- backend ingest reported the license as valid through `2027-06-21 16:32:35 UTC`
- backend ingest reported license features `all`
- profiler reported `SupportsGpu:true`
- profiler detected `GPU device 0-0 (NVIDIA B200) supports GPM: true`
- profiler reported `Exporting GPU metrics`
- profiler extracted `libzymtracecudaprofiler.so` under `/var/lib/zymtrace/profiler`
- MCP metrics discovery found `hw.gpu.utilization`, memory, process memory, power, power limit,
  temperature, and clock-throttle metrics
- a PyTorch CUDA smoke process with `CUDA_INJECTION64_PATH` set logged `Intercepted zymtrace implant`

No license value is committed. The public sample only includes
`ZYMTRACE_LICENSE_KEY=replace-with-zymtrace-license-jwt`.

## What Failed

The stock descriptions usually picked the right broad tool, but missed required arguments and
workflow boundaries:

- default project metrics discovery used `project_id: "default"` instead of
  `00000000-0000-0000-0000-000000000000`
- GPU inference investigation selected metric discovery but missed required metric-discovery
  arguments
- selected hot-trace drilldown did not consistently bind full trace fetches to a selected
  `prefix_hash` with `limit=1`
- first-pass hot-trace discovery did not consistently keep `meta_only=true` with a small limit
- one Gemini stock cell chose `hot_traces` instead of the resource fallback tool `topfunctions`

## Additional Live Findings

Unfiltered `hot_traces` can rank idle first. In the live smoke check, the first unfiltered CPU
`hot_traces` response returned an `IDLE` trace, and the ratio text referenced global non-idle time in
a way that exceeded 1.0. That is easy for agents to misread during first-pass optimization discovery.

`topentities` can expose profiler self-noise. The CPU resource returned `zymtrace-profiler` in the
top container list. The skills correctly tell agents to exclude the profiler from optimization
targets, but the resource output still makes it look selectable.

GPU readiness is spread across logs and metrics. After enablement, MCP showed GPU hardware metrics,
but there is no single MCP status path that reports GPU support, GPU metric collection, detected GPU
names, and CUDA library extraction state without exposing the license value.

## Suggested Change

Encode the profiling workflow in the MCP tool and resource surface:

```text
Use MCP resources first for topfunctions, topentities, and flamegraph. Call same-named tools only as fallback.

Use the default project id unless the user names another project.

Use metrics discovery before querying GPU or inference metrics.

Use rank-first tools for CPU investigations, then drill into selected traces.

Use bounded hot-trace metadata first. Fetch a full trace only after a prefix hash is selected.
```

Consider these MCP behavior changes:

- exclude idle traces by default for optimization-oriented `hot_traces` discovery, or expose an
  explicit idle-exclusion argument
- add a server-side option or marker to exclude `zymtrace-profiler` from `topentities`
- expose a small read-only GPU readiness resource with `supports_gpu`, `gpu_metrics_enabled`,
  detected GPU names, and CUDA library extraction status

## Evidence

- Source: [Zymtrace MCP docs](https://docs.zymtrace.com/category/model-context-protocol-mcp/)
- Matrix: [zymtrace_mcp_tool_selection.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/model_matrix/zymtrace_mcp_tool_selection.json)
- Frontier stress receipt: [zymtrace_mcp_frontier_available_matrix_live_2026-07-01.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/zymtrace_mcp_frontier_available_matrix_live_2026-07-01.md)
- Coverage: [zymtrace_mcp_coverage_2026-06-30.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/zymtrace_mcp_coverage_2026-06-30.md)
- Result: [zymtrace_mcp_matrix_live_2026-06-30.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/zymtrace_mcp_matrix_live_2026-06-30.json)
- Frontier stress result: [zymtrace_mcp_frontier_available_matrix_live_2026-07-01.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/zymtrace_mcp_frontier_available_matrix_live_2026-07-01.md)
- All-provider frontier attempt: [zymtrace_mcp_frontier_all_providers_attempt_2026-07-01.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/zymtrace_mcp_frontier_all_providers_attempt_2026-07-01.md)
- PR packet: [zymtrace_mcp_tool_tuning_2026-06-30](https://github.com/cfregly/claude-agent-harness-opt/tree/main/evals/pr_packets/zymtrace_mcp_tool_tuning_2026-06-30)
- Ledger: [Confirmed Improvements](https://github.com/cfregly/claude-agent-harness-opt/blob/main/docs/confirmed-improvements.md)
- Sweep: [Public MCP Sweep](https://github.com/cfregly/claude-agent-harness-opt/blob/main/docs/public-mcp-sweep.md)

## Reproduce

```bash
python -m claude_agent_harness_opt matrix-coverage evals/model_matrix/zymtrace_mcp_tool_selection.json --strict --out /tmp/zymtrace-coverage.json

python -m claude_agent_harness_opt model-matrix evals/model_matrix/zymtrace_mcp_tool_selection.json \
  --env-file .env \
  --live \
  --require-live \
  --providers anthropic,openai,gemini \
  --harnesses prompt_json \
  --variants stock_zymtrace_mcp,tuned_zymtrace_mcp_boundaries \
  --instruction-variants zymtrace_host_and_skill_rules \
  --cases "default project metrics discovery skips search,cpu rank first containerized apps,gpu inference workflow starts with metrics,gpu call tree uses hot traces,selected trace drilldown is bounded,full trace error recovers to discovery,hot trace discovery is bounded,resource fallback hot functions" \
  --concurrency 3 \
  --out /tmp/zymtrace-live.json
```
