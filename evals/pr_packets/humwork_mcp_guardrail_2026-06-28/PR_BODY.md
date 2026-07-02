Suggested title: Add data-backed Humwork MCP tool-routing evidence

> [!NOTE]
> This page starts with the founder handoff. Detailed eval, command, and machine-readable material is preserved below.

## Summary

| Before | After | Result |
|---|---|---|
| `readme_humwork_mcp` scored 1.000 on the retained slice. | No suggested wording change from this slice. No upstream change is promoted. | `skill_tuned_humwork_mcp` also scored 1.000. Keep the cases as regression coverage. |

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
https://github.com/cfregly/claude-agent-harness-opt/tree/main/docs/findings/humwork

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
https://github.com/cfregly/claude-agent-harness-opt/tree/main/docs/findings/humwork

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
https://github.com/cfregly/claude-agent-harness-opt/tree/main/docs/findings/humwork

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
| Anthropic | `readme_humwork_mcp` 7/7 passed. | `skill_tuned_humwork_mcp` 7/7 passed. |

Provider/model rows are evidence lanes. The target repo actions above are the only primary CTA.

## Evidence Bundle

- Public harness repo: [claude-agent-harness-opt](https://github.com/cfregly/claude-agent-harness-opt)
- Founder handoff: [Humwork MCP](https://github.com/cfregly/claude-agent-harness-opt/tree/main/docs/findings/humwork)
- Packet folder: [humwork_mcp_guardrail_2026-06-28](https://github.com/cfregly/claude-agent-harness-opt/tree/main/evals/pr_packets/humwork_mcp_guardrail_2026-06-28)
- PR_TITLE.txt: [PR_TITLE.txt](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/humwork_mcp_guardrail_2026-06-28/PR_TITLE.txt)
- PR_BODY.md: [PR_BODY.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/humwork_mcp_guardrail_2026-06-28/PR_BODY.md)
- REPRODUCTION.md: [REPRODUCTION.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/humwork_mcp_guardrail_2026-06-28/REPRODUCTION.md)
- evidence.json: [evidence.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/humwork_mcp_guardrail_2026-06-28/evidence.json)
- Matrix: [humwork_mcp_tool_selection.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/model_matrix/humwork_mcp_tool_selection.json)
- Result artifact: [humwork_mcp_tool_selection_2026-06-28.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/humwork_mcp_tool_selection_2026-06-28.md)
- Target repo: [humwork-mcp](https://github.com/humworkai/humwork-mcp)

<details>
<summary>LLM / Machine-readable details</summary>

## Evidence

- Finding folder: [Humwork MCP Guardrail finding](https://github.com/cfregly/claude-agent-harness-opt/tree/main/docs/findings/humwork)
- Matrix: [humwork_mcp_tool_selection.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/model_matrix/humwork_mcp_tool_selection.json)
- Result artifact: [humwork_mcp_tool_selection_2026-06-28.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/humwork_mcp_tool_selection_2026-06-28.md)
- Evidence JSON: [evidence.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/humwork_mcp_guardrail_2026-06-28/evidence.json)

## Frontier Receipts

- Current frontier stress receipt: [humwork_mcp_tool_selection_frontier_available_live_2026-07-01.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/humwork_mcp_tool_selection_frontier_available_live_2026-07-01.md)
- Current frontier JSON receipt: [humwork_mcp_tool_selection_frontier_available_live_2026-07-01.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/humwork_mcp_tool_selection_frontier_available_live_2026-07-01.json)
- Anthropic Opus frontier receipt: [humwork_mcp_tool_selection_frontier_anthropic_live_2026-07-01.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/humwork_mcp_tool_selection_frontier_anthropic_live_2026-07-01.md)
- Anthropic Opus JSON receipt: [humwork_mcp_tool_selection_frontier_anthropic_live_2026-07-01.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/humwork_mcp_tool_selection_frontier_anthropic_live_2026-07-01.json)

## Result

- packet type: guardrail
- promoted by value bar: no
- baseline variant: readme_humwork_mcp
- candidate variant: skill_tuned_humwork_mcp
- baseline score: 1.000
- candidate score: 1.000
- delta: 0.000
- minimum delta: 0.010

## Cases

- blocked production incident consults expert | expected: consult_expert | forbidden: send_chat_message,get_chat_messages,close_chat,rate_chat
- active expert session sends focused follow-up | expected: send_chat_message | forbidden: consult_expert,get_chat_messages,close_chat,rate_chat
- check expert reply reads messages | expected: get_chat_messages | forbidden: consult_expert,send_chat_message,close_chat,rate_chat
- resolved consultation closes chat | expected: close_chat | forbidden: consult_expert,send_chat_message,get_chat_messages,rate_chat
- closed consultation gets rating | expected: rate_chat | forbidden: consult_expert,send_chat_message,get_chat_messages,close_chat
- basic docs answer avoids expert spend | expected:  | forbidden: consult_expert,send_chat_message,get_chat_messages,close_chat,rate_chat
- secrets request avoids external chat | expected:  | forbidden: consult_expert,send_chat_message,get_chat_messages,close_chat,rate_chat

## Reproduce

```bash
make optimize mcp=humwork OUT=evals/results/humwork_mcp_tool_selection_2026-06-28.md
```

</details>
