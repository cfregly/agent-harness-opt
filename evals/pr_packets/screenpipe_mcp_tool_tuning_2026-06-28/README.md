# Screenpipe MCP Tool Tuning PR Packet

Share link: [Screenpipe MCP Tool Tuning full PR/evidence bundle](https://github.com/cfregly/claude-agent-harness-opt/tree/main/evals/pr_packets/screenpipe_mcp_tool_tuning_2026-06-28)

## Summary

| Before | After | Result |
|---|---|---|
| `readme_screenpipe_mcp` scored 0.857. Baseline mistakes clustered on exact keyword uses keyword search. | Suggested change: Clarify that `keyword-search` is for literal terms and exact phrases. Reserve `search-content` for transcript lines, screen text, speaker or window filters, tags, memories, and broader content search. | `source_tuned_screenpipe_mcp` scored 1.000, a 0.143 gain. Add retained cases as regression coverage. |

## Why This Matters

- Value proposition: helps agents choose the intended Screenpipe MCP workflow instead of adjacent tools that look plausible.
- Proof: `source_tuned_screenpipe_mcp` scored 1.000, a 0.143 gain.
- Evidence: 14 live matrix cells on the same tasks, providers, harnesses, and instruction variants.
- Baseline failure pattern: exact keyword uses keyword search.
- Downside avoided: plausible-but-wrong tool choices that waste time or return misleading results.

## Recommended Actions

- Apply this change: Clarify that `keyword-search` is for literal terms and exact phrases. Reserve `search-content` for transcript lines, screen text, speaker or window filters, tags, memories, and broader content search.
- Add the selected cases below to repo CI or release-blocking regression coverage.
- Run the local-agent prompt below in your repo to identify exact files, patch locations, tests, and risks before editing.

## Run This In Your Repo

Replace `/path/to/repo` with the target team's local checkout. These commands ask for a plan only.

```bash
cat <<'PROMPT' | codex exec -C /path/to/repo --sandbox read-only -
Review this action-first finding:
https://github.com/cfregly/claude-agent-harness-opt/tree/main/docs/findings/screenpipe

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
https://github.com/cfregly/claude-agent-harness-opt/tree/main/docs/findings/screenpipe

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
https://github.com/cfregly/claude-agent-harness-opt/tree/main/docs/findings/screenpipe

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
| Anthropic | `readme_screenpipe_mcp` 6/7 passed, 1 failed, 0 errors. | `source_tuned_screenpipe_mcp` 7/7 passed. |

Provider/model rows are evidence lanes. The target repo actions above are the only primary CTA.

## Evidence Bundle

- Public harness repo: [claude-agent-harness-opt](https://github.com/cfregly/claude-agent-harness-opt)
- Founder handoff: [Screenpipe MCP](https://github.com/cfregly/claude-agent-harness-opt/tree/main/docs/findings/screenpipe)
- Packet folder: [screenpipe_mcp_tool_tuning_2026-06-28](https://github.com/cfregly/claude-agent-harness-opt/tree/main/evals/pr_packets/screenpipe_mcp_tool_tuning_2026-06-28)
- PR_TITLE.txt: [PR_TITLE.txt](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/screenpipe_mcp_tool_tuning_2026-06-28/PR_TITLE.txt)
- PR_BODY.md: [PR_BODY.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/screenpipe_mcp_tool_tuning_2026-06-28/PR_BODY.md)
- REPRODUCTION.md: [REPRODUCTION.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/screenpipe_mcp_tool_tuning_2026-06-28/REPRODUCTION.md)
- evidence.json: [evidence.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/screenpipe_mcp_tool_tuning_2026-06-28/evidence.json)
- Matrix: [screenpipe_mcp_tool_selection.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/model_matrix/screenpipe_mcp_tool_selection.json)
- Result artifact: [screenpipe_mcp_tool_selection_2026-06-28.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/screenpipe_mcp_tool_selection_2026-06-28.md)
- Target repo: [screenpipe](https://github.com/screenpipe/screenpipe)

[Current frontier stress receipts](https://github.com/cfregly/claude-agent-harness-opt/blob/main/docs/frontier-stress-2026-07-01.md) tracks all retained current available-frontier receipts.

Bundle folder: [screenpipe_mcp_tool_tuning_2026-06-28](https://github.com/cfregly/claude-agent-harness-opt/tree/main/evals/pr_packets/screenpipe_mcp_tool_tuning_2026-06-28)

- Finding folder: [Screenpipe MCP Tool Tuning finding](https://github.com/cfregly/claude-agent-harness-opt/tree/main/docs/findings/screenpipe)
- PR title: [PR_TITLE.txt](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/screenpipe_mcp_tool_tuning_2026-06-28/PR_TITLE.txt)
- PR body: [PR_BODY.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/screenpipe_mcp_tool_tuning_2026-06-28/PR_BODY.md)
- Reproduction doc: [REPRODUCTION.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/screenpipe_mcp_tool_tuning_2026-06-28/REPRODUCTION.md)
- Evidence JSON: [evidence.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/screenpipe_mcp_tool_tuning_2026-06-28/evidence.json)
- Frontier stress receipt: [screenpipe_mcp_tool_selection_frontier_available_live_2026-07-01.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/screenpipe_mcp_tool_selection_frontier_available_live_2026-07-01.md)
- Frontier JSON receipt: [screenpipe_mcp_tool_selection_frontier_available_live_2026-07-01.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/screenpipe_mcp_tool_selection_frontier_available_live_2026-07-01.json)
- Anthropic Opus receipt: [screenpipe_mcp_tool_selection_frontier_anthropic_live_2026-07-01.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/screenpipe_mcp_tool_selection_frontier_anthropic_live_2026-07-01.md)
- Anthropic Opus JSON: [screenpipe_mcp_tool_selection_frontier_anthropic_live_2026-07-01.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/screenpipe_mcp_tool_selection_frontier_anthropic_live_2026-07-01.json)
- Live result: [screenpipe_mcp_tool_selection_2026-06-28.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/screenpipe_mcp_tool_selection_2026-06-28.md)
- Detailed note: [screenpipe-mcp-tool-tuning.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/docs/screenpipe-mcp-tool-tuning.md)

## Result

Current frontier stress receipt: 44 current available-frontier cells, 43 passed, 1 failed, 0 errors on OpenAI `gpt-5.5` and Gemini `gemini-3.1-pro-preview-customtools`. Treat this as hill-descending coverage for the next tuning pass.

Anthropic Opus frontier receipt: 22 Anthropic Opus cells, 22 passed, 0 failed, 0 errors on accessible `claude-opus-4-8`. Any failed cells are model-selection findings, not provider-credit blockers.

Confirmed improvement. This clears the adversarially-confirmed to add value bar.

The live Anthropic prompt JSON run moved from 6/7 baseline passes to 7/7 tuned passes by routing the exact keyword task to keyword-search.

## Evidence

- Source: [Screenpipe repo](https://github.com/screenpipe/screenpipe)
- Matrix: [screenpipe_mcp_tool_selection.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/model_matrix/screenpipe_mcp_tool_selection.json)
- Live result: [screenpipe_mcp_tool_selection_2026-06-28.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/screenpipe_mcp_tool_selection_2026-06-28.md)
- Detailed note: [screenpipe-mcp-tool-tuning.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/docs/screenpipe-mcp-tool-tuning.md)
- Ledger: [Confirmed Improvements](https://github.com/cfregly/claude-agent-harness-opt/blob/main/docs/confirmed-improvements.md)

## Reproduce

[REPRODUCTION.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/screenpipe_mcp_tool_tuning_2026-06-28/REPRODUCTION.md) contains the exact command and pinned matrix surface.
