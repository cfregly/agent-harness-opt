# InsForge MCP Tool Tuning PR Packet

Share link: [InsForge MCP Tool Tuning full PR/evidence bundle](https://github.com/cfregly/claude-agent-harness-opt/tree/main/evals/pr_packets/insforge_mcp_tool_tuning_2026-06-28)

## Summary

| Exact change | Before | After | Result |
|---|---|---|---|
| Clarify that `create-deployment` requires an absolute `sourceDirectory` and must be avoided for relative paths, starter-template creation, deployment status lookup, or remote prepared-deployment triggering. | `readme_insforge_mcp` scored 0.938. Baseline mistakes clustered on relative deploy path avoids tool. | The target surface states this routing/default/fallback behavior before the agent chooses tools. | `source_tuned_insforge_mcp` scored 1.000, a 0.062 gain. Add retained cases as regression coverage. |


## Result

Current frontier stress receipt: 76 current available-frontier cells, 64 passed, 11 failed, 1 error on OpenAI `gpt-5.5` and Gemini `gemini-3.1-pro-preview-customtools`. Treat this as hill-descending coverage for the next tuning pass.

Anthropic Opus frontier receipt: 38 Anthropic Opus cells, 34 passed, 4 failed, 0 errors on accessible `claude-opus-4-8`. Any failed cells are model-selection findings, not provider-credit blockers.

Confirmed improvement. This clears the adversarially-confirmed to add value bar.

The live Anthropic prompt JSON run moved from 15/16 baseline passes to 16/16 tuned passes by routing the relative-path deployment request to NO_TOOL.

## Why This Matters

- Value proposition: helps agents choose the intended InsForge MCP workflow instead of adjacent tools that look plausible.
- Proof: `source_tuned_insforge_mcp` scored 1.000, a 0.062 gain.
- Proof scope: 32 live matrix cells on the same tasks, providers, harnesses, and instruction variants.
- Baseline failure pattern: relative deploy path avoids tool.
- Downside avoided: plausible-but-wrong tool choices that waste time or return misleading results.

## Recommended Actions

- Apply exact change: Clarify that `create-deployment` requires an absolute `sourceDirectory` and must be avoided for relative paths, starter-template creation, deployment status lookup, or remote prepared-deployment triggering.
- Add the selected cases below to repo CI or release-blocking regression coverage.
- Run the local-agent prompt below in your repo to identify exact files, patch locations, tests, and risks before editing.

## Run This In Your Repo

Replace `/path/to/repo` with the target team's local checkout. These commands ask for a plan only.

```bash
cat <<'PROMPT' | codex exec -C /path/to/repo --sandbox read-only -
Review this action-first finding:
https://github.com/cfregly/claude-agent-harness-opt/tree/main/docs/findings/insforge

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
https://github.com/cfregly/claude-agent-harness-opt/tree/main/docs/findings/insforge

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
https://github.com/cfregly/claude-agent-harness-opt/tree/main/docs/findings/insforge

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
| Anthropic | `readme_insforge_mcp` 15/16 passed, 1 failed, 0 errors. | `source_tuned_insforge_mcp` 16/16 passed. |

Provider/model rows are evidence lanes. The target repo actions above are the only primary CTA.

## Evidence Bundle

- Public harness repo: [claude-agent-harness-opt](https://github.com/cfregly/claude-agent-harness-opt)
- Bundle folder: [insforge_mcp_tool_tuning_2026-06-28](https://github.com/cfregly/claude-agent-harness-opt/tree/main/evals/pr_packets/insforge_mcp_tool_tuning_2026-06-28)
- Matrix: [insforge_mcp_tool_selection.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/model_matrix/insforge_mcp_tool_selection.json)
- Result artifact: [insforge_mcp_tool_selection_2026-06-28.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/insforge_mcp_tool_selection_2026-06-28.md)
- PR_TITLE.txt: [PR_TITLE.txt](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/insforge_mcp_tool_tuning_2026-06-28/PR_TITLE.txt)
- PR_BODY.md: [PR_BODY.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/insforge_mcp_tool_tuning_2026-06-28/PR_BODY.md)
- REPRODUCTION.md: [REPRODUCTION.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/insforge_mcp_tool_tuning_2026-06-28/REPRODUCTION.md)
- evidence.json: [evidence.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/insforge_mcp_tool_tuning_2026-06-28/evidence.json)
- Target repo: [insforge-mcp](https://github.com/InsForge/insforge-mcp)

<details>
<summary>LLM / Machine-readable details</summary>

## Artifact Pointers

- Source: [InsForge MCP repo](https://github.com/InsForge/insforge-mcp)
- Matrix: [insforge_mcp_tool_selection.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/model_matrix/insforge_mcp_tool_selection.json)
- Live result: [insforge_mcp_tool_selection_2026-06-28.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/insforge_mcp_tool_selection_2026-06-28.md)
- Detailed note: [insforge-mcp-tool-tuning.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/docs/insforge-mcp-tool-tuning.md)
- Ledger: [Confirmed Improvements](https://github.com/cfregly/claude-agent-harness-opt/blob/main/docs/confirmed-improvements.md)

## Reproduce

[REPRODUCTION.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/insforge_mcp_tool_tuning_2026-06-28/REPRODUCTION.md) contains the exact command and pinned matrix surface.

</details>
