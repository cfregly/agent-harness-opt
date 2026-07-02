Suggested title: Add data-backed OpenWork UI MCP tool-routing evidence

> [!NOTE]
> This page starts with the founder handoff. Detailed eval, command, and machine-readable material is preserved below.

## Summary

| Exact change | Before | After | Result |
|---|---|---|---|
| No wording change promoted from this slice. | `docs_openwork_ui_mcp` scored 1.000 on the retained slice. | Keep the current surface and retain the cases as regression coverage. | `source_tuned_openwork_ui_mcp` also scored 1.000. Keep the cases as regression coverage. |


## Result

- Guardrail: no upstream change is promoted because `docs_openwork_ui_mcp` and `source_tuned_openwork_ui_mcp` did not produce a qualifying delta.
- Value bar: 0.000 delta against a 0.010 minimum.
- Proof scope: 14 live matrix cells, 14 passed, 0 failed, 0 errors.

## Why This Matters

- Value proposition: avoid spending founder or engineering time on a wording change that did not beat the current surface.
- No promoted delta from this slice; both variants were already passing.
- The retained cases are still useful regression coverage for future changes.
- Downside avoided: shipping unproven wording changes while the current behavior is already passing.

## Recommended Actions

- No upstream change is promoted from this slice.
- Keep the selected cases below as regression coverage because both variants already passed.
- Run the local-agent prompt below to decide where those regression cases belong if this area changes.

## Run This In Your Repo

Replace `/path/to/repo` with the target team's local checkout. These commands ask for a plan only.

```bash
cat <<'PROMPT' | codex exec -C /path/to/repo --sandbox read-only -
Review this action-first finding:
https://github.com/cfregly/claude-agent-harness-opt/tree/main/docs/findings/openwork

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
https://github.com/cfregly/claude-agent-harness-opt/tree/main/docs/findings/openwork

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
https://github.com/cfregly/claude-agent-harness-opt/tree/main/docs/findings/openwork

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
| Anthropic | `docs_openwork_ui_mcp` 7/7 passed. | `source_tuned_openwork_ui_mcp` 7/7 passed. |

Provider/model rows are evidence lanes. The target repo actions above are the only primary CTA.

## Evidence Bundle

- Public harness repo: [claude-agent-harness-opt](https://github.com/cfregly/claude-agent-harness-opt)
- Bundle folder: [openwork_ui_mcp_guardrail_2026-06-28](https://github.com/cfregly/claude-agent-harness-opt/tree/main/evals/pr_packets/openwork_ui_mcp_guardrail_2026-06-28)
- Matrix: [openwork_ui_mcp_tool_selection.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/model_matrix/openwork_ui_mcp_tool_selection.json)
- Result artifact: [openwork_ui_mcp_tool_selection_2026-06-28.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/openwork_ui_mcp_tool_selection_2026-06-28.md)
- PR_TITLE.txt: [PR_TITLE.txt](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/openwork_ui_mcp_guardrail_2026-06-28/PR_TITLE.txt)
- PR_BODY.md: [PR_BODY.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/openwork_ui_mcp_guardrail_2026-06-28/PR_BODY.md)
- REPRODUCTION.md: [REPRODUCTION.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/openwork_ui_mcp_guardrail_2026-06-28/REPRODUCTION.md)
- evidence.json: [evidence.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/openwork_ui_mcp_guardrail_2026-06-28/evidence.json)
- Target repo: [openwork](https://github.com/different-ai/openwork)

<details>
<summary>LLM / Machine-readable details</summary>

## Artifact Pointers

- Finding folder: [OpenWork UI MCP Guardrail finding](https://github.com/cfregly/claude-agent-harness-opt/tree/main/docs/findings/openwork)
- Matrix: [openwork_ui_mcp_tool_selection.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/model_matrix/openwork_ui_mcp_tool_selection.json)
- Result artifact: [openwork_ui_mcp_tool_selection_2026-06-28.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/openwork_ui_mcp_tool_selection_2026-06-28.md)
- Evidence JSON: [evidence.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/openwork_ui_mcp_guardrail_2026-06-28/evidence.json)

## Frontier Receipts

- Current frontier stress receipt: [openwork_ui_mcp_tool_selection_frontier_available_live_2026-07-01.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/openwork_ui_mcp_tool_selection_frontier_available_live_2026-07-01.md)
- Current frontier JSON receipt: [openwork_ui_mcp_tool_selection_frontier_available_live_2026-07-01.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/openwork_ui_mcp_tool_selection_frontier_available_live_2026-07-01.json)
- Anthropic Opus frontier receipt: [openwork_ui_mcp_tool_selection_frontier_anthropic_live_2026-07-01.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/openwork_ui_mcp_tool_selection_frontier_anthropic_live_2026-07-01.md)
- Anthropic Opus JSON receipt: [openwork_ui_mcp_tool_selection_frontier_anthropic_live_2026-07-01.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/openwork_ui_mcp_tool_selection_frontier_anthropic_live_2026-07-01.json)

## Cases

- bridge check uses status | expected: ui_status | forbidden: ui_snapshot,ui_list_actions,ui_execute_action
- unknown current screen uses snapshot | expected: ui_snapshot | forbidden: ui_status,ui_list_actions,ui_execute_action
- action discovery uses list actions | expected: ui_list_actions | forbidden: ui_status,ui_snapshot,ui_execute_action
- known action id executes action | expected: ui_execute_action | forbidden: ui_status,ui_snapshot,ui_list_actions
- unknown action id lists actions first | expected: ui_list_actions | forbidden: ui_status,ui_execute_action
- coordinate click avoids semantic bridge | expected:  | forbidden: ui_status,ui_snapshot,ui_list_actions,ui_execute_action
- app maybe closed checks status before action | expected: ui_status | forbidden: ui_snapshot,ui_list_actions,ui_execute_action

## Reproduce

```bash
make optimize mcp=openwork OUT=evals/results/openwork_ui_mcp_tool_selection_2026-06-28.md
```

</details>
