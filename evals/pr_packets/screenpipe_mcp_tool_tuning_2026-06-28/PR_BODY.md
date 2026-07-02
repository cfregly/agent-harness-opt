Suggested title: Tighten Screenpipe MCP retrieval routing with live evals

> [!NOTE]
> This page starts with the founder handoff. Detailed eval, command, and machine-readable material is preserved below.

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

<details>
<summary>LLM / Machine-readable details</summary>

## Evidence

- Finding folder: [Screenpipe MCP Tool Tuning finding](https://github.com/cfregly/claude-agent-harness-opt/tree/main/docs/findings/screenpipe)
- Matrix: [screenpipe_mcp_tool_selection.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/model_matrix/screenpipe_mcp_tool_selection.json)
- Result artifact: [screenpipe_mcp_tool_selection_2026-06-28.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/screenpipe_mcp_tool_selection_2026-06-28.md)
- Evidence JSON: [evidence.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/screenpipe_mcp_tool_tuning_2026-06-28/evidence.json)

## Frontier Receipts

- Current frontier stress receipt: [screenpipe_mcp_tool_selection_frontier_available_live_2026-07-01.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/screenpipe_mcp_tool_selection_frontier_available_live_2026-07-01.md)
- Current frontier JSON receipt: [screenpipe_mcp_tool_selection_frontier_available_live_2026-07-01.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/screenpipe_mcp_tool_selection_frontier_available_live_2026-07-01.json)
- Anthropic Opus frontier receipt: [screenpipe_mcp_tool_selection_frontier_anthropic_live_2026-07-01.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/screenpipe_mcp_tool_selection_frontier_anthropic_live_2026-07-01.md)
- Anthropic Opus JSON receipt: [screenpipe_mcp_tool_selection_frontier_anthropic_live_2026-07-01.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/screenpipe_mcp_tool_selection_frontier_anthropic_live_2026-07-01.json)

## Result

- packet type: improvement
- promoted by value bar: yes
- baseline variant: readme_screenpipe_mcp
- candidate variant: source_tuned_screenpipe_mcp
- baseline score: 0.857
- candidate score: 1.000
- delta: 0.143
- minimum delta: 0.010

## Cases

- broad morning recap starts summary | expected: activity-summary | forbidden: search-content,keyword-search,search-elements,export-video,list-meetings
- exact keyword uses keyword search | expected: keyword-search | forbidden: activity-summary,search-elements,export-video,list-meetings
- speaker transcript uses content search | expected: search-content | forbidden: activity-summary,keyword-search,search-elements,export-video,list-meetings
- ui button lookup uses elements | expected: search-elements | forbidden: search-content,activity-summary,keyword-search,frame-context,export-video
- known frame detail uses frame context | expected: frame-context | forbidden: search-content,get-frame-elements,activity-summary,export-video,list-meetings
- create recurring automation uses pipe | expected: create-pipe | forbidden: run-pipe,pipe-logs,activity-summary
- verify pipe output uses logs | expected: pipe-logs | forbidden: create-pipe,run-pipe,activity-summary

## Reproduce

```bash
make optimize mcp=screenpipe OUT=evals/results/screenpipe_mcp_tool_selection_2026-06-28.md
```

</details>
