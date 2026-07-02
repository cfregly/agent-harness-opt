# Zymtrace MCP Tool Tuning PR Packet

Share link: [Zymtrace full PR/evidence bundle](https://github.com/cfregly/claude-agent-harness-opt/tree/main/evals/pr_packets/zymtrace_mcp_tool_tuning_2026-06-30)

## Summary

| Exact change | Before | After | Result |
|---|---|---|---|
| Clarify default-project, GPU metrics-first, resource-first, and bounded hot-traces routing. | `stock_zymtrace_mcp` scored 0.583. Baseline mistakes clustered on default project metrics discovery skips search, gpu inference workflow starts with metrics, selected trace drilldown is bounded, hot trace discovery is bounded. | The target surface states this routing/default/fallback behavior before the agent chooses tools. | `tuned_zymtrace_mcp_boundaries` scored 1.000, a 0.417 gain. Add retained cases as regression coverage. |
| Add an explicit idle-exclusion option or marker for optimization-oriented `hot_traces` discovery. | `stock_zymtrace_mcp` scored 0.583. Baseline mistakes clustered on default project metrics discovery skips search, gpu inference workflow starts with metrics, selected trace drilldown is bounded, hot trace discovery is bounded. | Optimization-oriented hot-trace discovery excludes or clearly marks idle traces before ranking work. | `tuned_zymtrace_mcp_boundaries` scored 1.000, a 0.417 gain. Add retained cases as regression coverage. |
| Add a server-side option or marker that keeps `zymtrace-profiler` from being presented as an optimization target in `topentities`. | `stock_zymtrace_mcp` scored 0.583. Baseline mistakes clustered on default project metrics discovery skips search, gpu inference workflow starts with metrics, selected trace drilldown is bounded, hot trace discovery is bounded. | Profiler self-noise is not presented as an application optimization target. | `tuned_zymtrace_mcp_boundaries` scored 1.000, a 0.417 gain. Add retained cases as regression coverage. |
| Add a small read-only GPU readiness resource that reports GPU support, GPU metric collection, detected GPU names, and CUDA library extraction state without exposing the license value. | `stock_zymtrace_mcp` scored 0.583. Baseline mistakes clustered on default project metrics discovery skips search, gpu inference workflow starts with metrics, selected trace drilldown is bounded, hot trace discovery is bounded. | Agents can read GPU readiness from one safe MCP surface before querying GPU metrics. | `tuned_zymtrace_mcp_boundaries` scored 1.000, a 0.417 gain. Add retained cases as regression coverage. |


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

- Apply exact change: Clarify default-project, GPU metrics-first, resource-first, and bounded hot-traces routing.
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
