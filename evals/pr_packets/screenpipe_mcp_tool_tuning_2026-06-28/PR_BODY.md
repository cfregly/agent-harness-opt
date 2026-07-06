Suggested title: Tighten Screenpipe MCP retrieval routing with live evals

> [!NOTE]
> This page starts with the founder handoff. Detailed eval, command, and machine-readable material is preserved below.

## Summary

### Exact Text To Apply

Copy the suggested replacement text into the target repo field named in the first column.

| Where to edit | Baseline text | Suggested replacement text |
|---|---|---|
| `search-content.purpose` | Search through recorded content with content type filtering. | Search screen text, audio transcriptions, input events, and memories. Returns timestamped results with app context. |
| `search-content.avoid_when` | No exact-keyword avoid_when boundary. | Avoid for broad questions like what was I doing; use activity-summary. Avoid for targeted UI controls; use search-elements. Avoid for fastest exact keyword lookup; use keyword-search. |
| `keyword-search.purpose` | Fast keyword search across OCR and audio. | Fast FTS5 keyword search across OCR plus audio combined. |
| `keyword-search.avoid_when` | No structured-filter avoid_when boundary. | Avoid for structured filtering by content type, speaker, window, or broad activity questions. |

### Baseline / Suggested Behavior
The table below is the exact handoff text. Baseline / before is the current behavior. Suggested / after is the proposed wording or behavior to implement.

| Suggested change | Baseline / before description | Suggested / after description | Result |
|---|---|---|---|
| Clarify that `keyword-search` is for literal terms and exact phrases. Reserve `search-content` for transcript lines, screen text, speaker or window filters, tags, memories, and broader content search. | Exact keyword or phrase lookup could be routed to broad `search-content` instead of the dedicated literal lookup tool. | Literal terms and exact phrases route to `keyword-search`. `search-content` stays for broader content, transcript, screen text, speaker, window, tag, and memory search. | `source_tuned_screenpipe_mcp` scored 1.000, a 0.143 gain. Add retained cases as regression coverage. |


## Result

- Confirmed improvement: `source_tuned_screenpipe_mcp` moved from 0.857 to 1.000, a 0.143 gain over `readme_screenpipe_mcp`.
- Value bar: cleared the 0.010 minimum delta.
- Proof scope: 14 live matrix cells, 13 passed, 1 failed, 0 errors.

## What Failed

- `readme_screenpipe_mcp` failed or chose the wrong boundary on: exact keyword uses keyword search.
- Those failures are the target-owned behavior to encode in descriptions, defaults, options, or regression tests.

## Why This Matters

- Value proposition: helps agents choose the intended Screenpipe MCP workflow instead of adjacent tools that look plausible.
- Proof: `source_tuned_screenpipe_mcp` scored 1.000, a 0.143 gain.
- Proof scope: 14 live matrix cells on the same tasks, providers, harnesses, and instruction variants.
- Baseline failure pattern: exact keyword uses keyword search.
- Downside avoided: plausible-but-wrong tool choices that waste time or return misleading results.

## Recommended Actions

- Apply suggested change: Clarify that `keyword-search` is for literal terms and exact phrases. Reserve `search-content` for transcript lines, screen text, speaker or window filters, tags, memories, and broader content search.
- Add the selected cases below to repo CI or release-blocking regression coverage.
- Run the local-agent prompt below in your repo to identify exact files, patch locations, tests, and risks before editing.

## Run This In Your Repo

Replace `/path/to/repo` with the target team's local checkout. These commands ask for a plan only.

```bash
cat <<'PROMPT' | codex exec -C /path/to/repo --sandbox read-only -
Review this action-first finding:
https://github.com/cfregly/agent-harness-opt/tree/main/docs/findings/screenpipe

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
https://github.com/cfregly/agent-harness-opt/tree/main/docs/findings/screenpipe

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
https://github.com/cfregly/agent-harness-opt/tree/main/docs/findings/screenpipe

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

- Public harness repo: [agent-harness-opt](https://github.com/cfregly/agent-harness-opt)
- Bundle folder: [screenpipe_mcp_tool_tuning_2026-06-28](https://github.com/cfregly/agent-harness-opt/tree/main/evals/pr_packets/screenpipe_mcp_tool_tuning_2026-06-28)
- Matrix: [screenpipe_mcp_tool_selection.json](https://github.com/cfregly/agent-harness-opt/blob/main/evals/model_matrix/screenpipe_mcp_tool_selection.json)
- Result artifact: [screenpipe_mcp_tool_selection_2026-06-28.md](https://github.com/cfregly/agent-harness-opt/blob/main/evals/results/screenpipe_mcp_tool_selection_2026-06-28.md)
- PR_TITLE.txt: [PR_TITLE.txt](https://github.com/cfregly/agent-harness-opt/blob/main/evals/pr_packets/screenpipe_mcp_tool_tuning_2026-06-28/PR_TITLE.txt)
- PR_BODY.md: [PR_BODY.md](https://github.com/cfregly/agent-harness-opt/blob/main/evals/pr_packets/screenpipe_mcp_tool_tuning_2026-06-28/PR_BODY.md)
- REPRODUCTION.md: [REPRODUCTION.md](https://github.com/cfregly/agent-harness-opt/blob/main/evals/pr_packets/screenpipe_mcp_tool_tuning_2026-06-28/REPRODUCTION.md)
- evidence.json: [evidence.json](https://github.com/cfregly/agent-harness-opt/blob/main/evals/pr_packets/screenpipe_mcp_tool_tuning_2026-06-28/evidence.json)
- Target repo: [screenpipe](https://github.com/screenpipe/screenpipe)

<details>
<summary>LLM / Machine-readable details</summary>

## Artifact Pointers

- Finding folder: [Screenpipe MCP Tool Tuning finding](https://github.com/cfregly/agent-harness-opt/tree/main/docs/findings/screenpipe)
- Matrix: [screenpipe_mcp_tool_selection.json](https://github.com/cfregly/agent-harness-opt/blob/main/evals/model_matrix/screenpipe_mcp_tool_selection.json)
- Result artifact: [screenpipe_mcp_tool_selection_2026-06-28.md](https://github.com/cfregly/agent-harness-opt/blob/main/evals/results/screenpipe_mcp_tool_selection_2026-06-28.md)
- Evidence JSON: [evidence.json](https://github.com/cfregly/agent-harness-opt/blob/main/evals/pr_packets/screenpipe_mcp_tool_tuning_2026-06-28/evidence.json)

## Frontier Receipts

- Current frontier stress receipt: [screenpipe_mcp_tool_selection_frontier_available_live_2026-07-01.md](https://github.com/cfregly/agent-harness-opt/blob/main/evals/results/screenpipe_mcp_tool_selection_frontier_available_live_2026-07-01.md)
- Current frontier JSON receipt: [screenpipe_mcp_tool_selection_frontier_available_live_2026-07-01.json](https://github.com/cfregly/agent-harness-opt/blob/main/evals/results/screenpipe_mcp_tool_selection_frontier_available_live_2026-07-01.json)
- Anthropic Opus frontier receipt: [screenpipe_mcp_tool_selection_frontier_anthropic_live_2026-07-01.md](https://github.com/cfregly/agent-harness-opt/blob/main/evals/results/screenpipe_mcp_tool_selection_frontier_anthropic_live_2026-07-01.md)
- Anthropic Opus JSON receipt: [screenpipe_mcp_tool_selection_frontier_anthropic_live_2026-07-01.json](https://github.com/cfregly/agent-harness-opt/blob/main/evals/results/screenpipe_mcp_tool_selection_frontier_anthropic_live_2026-07-01.json)

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
