# Humwork MCP Guardrail PR Packet

Share link: [Humwork MCP Guardrail full PR/evidence bundle](https://github.com/cfregly/claude-agent-harness-opt/tree/main/evals/pr_packets/humwork_mcp_guardrail_2026-06-28)

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

[Current frontier stress receipts](https://github.com/cfregly/claude-agent-harness-opt/blob/main/docs/frontier-stress-2026-07-01.md) tracks all retained current available-frontier receipts.

Bundle folder: [humwork_mcp_guardrail_2026-06-28](https://github.com/cfregly/claude-agent-harness-opt/tree/main/evals/pr_packets/humwork_mcp_guardrail_2026-06-28)

- Finding folder: [Humwork MCP Guardrail finding](https://github.com/cfregly/claude-agent-harness-opt/tree/main/docs/findings/humwork)
- PR title: [PR_TITLE.txt](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/humwork_mcp_guardrail_2026-06-28/PR_TITLE.txt)
- PR body: [PR_BODY.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/humwork_mcp_guardrail_2026-06-28/PR_BODY.md)
- Reproduction doc: [REPRODUCTION.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/humwork_mcp_guardrail_2026-06-28/REPRODUCTION.md)
- Evidence JSON: [evidence.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/humwork_mcp_guardrail_2026-06-28/evidence.json)
- Frontier stress receipt: [humwork_mcp_tool_selection_frontier_available_live_2026-07-01.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/humwork_mcp_tool_selection_frontier_available_live_2026-07-01.md)
- Frontier JSON receipt: [humwork_mcp_tool_selection_frontier_available_live_2026-07-01.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/humwork_mcp_tool_selection_frontier_available_live_2026-07-01.json)
- Anthropic Opus receipt: [humwork_mcp_tool_selection_frontier_anthropic_live_2026-07-01.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/humwork_mcp_tool_selection_frontier_anthropic_live_2026-07-01.md)
- Anthropic Opus JSON: [humwork_mcp_tool_selection_frontier_anthropic_live_2026-07-01.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/humwork_mcp_tool_selection_frontier_anthropic_live_2026-07-01.json)
- Live result: [humwork_mcp_tool_selection_2026-06-28.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/humwork_mcp_tool_selection_2026-06-28.md)
- Detailed note: [yc-p2026-mcp-sweep.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/docs/yc-p2026-mcp-sweep.md)

## Result

Current frontier stress receipt: 28 current available-frontier cells, 25 passed, 3 failed, 0 errors on OpenAI `gpt-5.5` and Gemini `gemini-3.1-pro-preview-customtools`. Treat this as hill-descending coverage for the next tuning pass.

Anthropic Opus frontier receipt: 14 Anthropic Opus cells, 14 passed, 0 failed, 0 errors on accessible `claude-opus-4-8`. Any failed cells are model-selection findings, not provider-credit blockers.

Guardrail. No upstream change is promoted because the baseline already passed the tested slice.

The live Anthropic prompt JSON run kept both README-level and skill-tuned variants at 7/7, so the packet is guardrail evidence rather than a promoted change.

## Evidence

- Source: [Humwork MCP repo](https://github.com/humworkai/humwork-mcp)
- Matrix: [humwork_mcp_tool_selection.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/model_matrix/humwork_mcp_tool_selection.json)
- Live result: [humwork_mcp_tool_selection_2026-06-28.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/humwork_mcp_tool_selection_2026-06-28.md)
- Detailed note: [yc-p2026-mcp-sweep.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/docs/yc-p2026-mcp-sweep.md)
- Ledger: [Confirmed Improvements](https://github.com/cfregly/claude-agent-harness-opt/blob/main/docs/confirmed-improvements.md)

## Reproduce

[REPRODUCTION.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/humwork_mcp_guardrail_2026-06-28/REPRODUCTION.md) contains the exact command and pinned matrix surface.
