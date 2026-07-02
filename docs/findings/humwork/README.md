# Humwork MCP Finding

Share link: [Humwork packet](https://github.com/cfregly/claude-agent-harness-opt/tree/main/docs/findings/humwork)

## Summary

| Exact change | Before | After | Result |
|---|---|---|---|
| No wording change promoted from this slice. | `readme_humwork_mcp` scored 1.000 on the retained slice. | Keep the current surface and retain the cases as regression coverage. | `skill_tuned_humwork_mcp` also scored 1.000. Keep the cases as regression coverage. |


## Result

Guardrail. No upstream change is promoted.

Current frontier stress receipt: 28 current available-frontier cells, 25 passed, 3 failed, 0 errors on OpenAI `gpt-5.5` and Gemini `gemini-3.1-pro-preview-customtools`. Treat this as hill-descending coverage for the next tuning pass, not as a replacement for the promoted baseline-to-tuned result.

Anthropic Opus frontier receipt: 14 Anthropic Opus cells, 14 passed, 0 failed, 0 errors on accessible `claude-opus-4-8`. Any failed cells are model-selection findings, not provider-credit blockers.

The README-level and skill-tuned variants both passed 7/7 on Anthropic prompt JSON. That means this
did not clear the adversarially-confirmed to add value bar as an improvement, because there was no
baseline failure to fix.

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
- Bundle folder: [humwork_mcp_guardrail_2026-06-28](https://github.com/cfregly/claude-agent-harness-opt/tree/main/evals/pr_packets/humwork_mcp_guardrail_2026-06-28)
- Matrix: [humwork_mcp_tool_selection.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/model_matrix/humwork_mcp_tool_selection.json)
- Result artifact: [humwork_mcp_tool_selection_2026-06-28.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/humwork_mcp_tool_selection_2026-06-28.md)
- PR_TITLE.txt: [PR_TITLE.txt](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/humwork_mcp_guardrail_2026-06-28/PR_TITLE.txt)
- PR_BODY.md: [PR_BODY.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/humwork_mcp_guardrail_2026-06-28/PR_BODY.md)
- REPRODUCTION.md: [REPRODUCTION.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/humwork_mcp_guardrail_2026-06-28/REPRODUCTION.md)
- evidence.json: [evidence.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/humwork_mcp_guardrail_2026-06-28/evidence.json)
- Target repo: [humwork-mcp](https://github.com/humworkai/humwork-mcp)

<details>
<summary>LLM / Machine-readable details</summary>

## What Was Tested

The slice covered:

- starting an expert consultation
- sending a follow-up to an active session
- reading expert replies
- closing a resolved chat
- rating a closed chat
- avoiding expert spend for a basic docs question
- avoiding external chat when secrets or customer exports would be shared

## Artifact Pointers

- Source: [Humwork MCP repo](https://github.com/humworkai/humwork-mcp)
- Matrix: [humwork_mcp_tool_selection.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/model_matrix/humwork_mcp_tool_selection.json)
- Frontier stress receipt: [humwork_mcp_tool_selection_frontier_available_live_2026-07-01.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/humwork_mcp_tool_selection_frontier_available_live_2026-07-01.md)
- Receipt: [humwork_mcp_tool_selection_2026-06-28.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/humwork_mcp_tool_selection_2026-06-28.md)
- Guardrail packet: [humwork_mcp_guardrail_2026-06-28](https://github.com/cfregly/claude-agent-harness-opt/tree/main/evals/pr_packets/humwork_mcp_guardrail_2026-06-28)
- YC sweep: [YC P2026 MCP Sweep](https://github.com/cfregly/claude-agent-harness-opt/blob/main/docs/yc-p2026-mcp-sweep.md)

## Reproduce

```bash
make optimize mcp=humwork
```

</details>
