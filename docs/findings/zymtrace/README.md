# Zymtrace MCP Finding

Share link: [Zymtrace packet](https://github.com/cfregly/claude-agent-harness-opt/tree/main/docs/findings/zymtrace)

## Result

Confirmed improvement. This clears the adversarially-confirmed to add value bar.

The expanded held-out prompt JSON run moved from 4/8 to 8/8 on Anthropic, 5/8 to 8/8 on OpenAI, and
5/8 to 8/8 on Gemini. Across all three providers, stock passed 14/24 cells and tuned passed 24/24.

The new result is packaged here:

- matrix result: `evals/results/zymtrace_mcp_matrix_live_2026-06-30.json`
- upstream PR packet: `evals/pr_packets/zymtrace_mcp_tool_tuning_2026-06-30/`
- generated title: `Tighten Zymtrace MCP retrieval routing with live evals`

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
- Result: [zymtrace_mcp_matrix_live_2026-06-30.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/zymtrace_mcp_matrix_live_2026-06-30.json)
- PR packet: [zymtrace_mcp_tool_tuning_2026-06-30](https://github.com/cfregly/claude-agent-harness-opt/tree/main/evals/pr_packets/zymtrace_mcp_tool_tuning_2026-06-30)
- Ledger: [Confirmed Improvements](https://github.com/cfregly/claude-agent-harness-opt/blob/main/docs/confirmed-improvements.md)
- Sweep: [Public MCP Sweep](https://github.com/cfregly/claude-agent-harness-opt/blob/main/docs/public-mcp-sweep.md)

## Reproduce

```bash
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
