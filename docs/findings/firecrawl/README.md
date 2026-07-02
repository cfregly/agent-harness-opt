# Firecrawl MCP Finding

Share link: [Firecrawl packet](https://github.com/cfregly/claude-agent-harness-opt/tree/main/docs/findings/firecrawl)

## Summary

| Exact change | Before | After | Result |
|---|---|---|---|
| Clarify that `firecrawl_scrape` handles one known page, including structured JSON fields. Reserve `firecrawl_extract` for broader multi-page structured extraction jobs. | `legacy_firecrawl_mcp` scored 0.000. Baseline mistakes clustered on single known page structured fields. | The target surface states this routing/default/fallback behavior before the agent chooses tools. | `tuned_firecrawl_mcp_boundaries` scored 1.000, a 1.000 gain. Add retained cases as regression coverage. |


## Result

Confirmed improvement. This clears the adversarially-confirmed to add value bar.

Current frontier stress receipt: 60 current available-frontier cells, 51 passed, 9 failed, 0 errors on OpenAI `gpt-5.5` and Gemini `gemini-3.1-pro-preview-customtools`. Treat this as hill-descending coverage for the next tuning pass, not as a replacement for the promoted baseline-to-tuned result.

Anthropic Opus frontier receipt: 30 Anthropic Opus cells, 26 passed, 4 failed, 0 errors on accessible `claude-opus-4-8`. Any failed cells are model-selection findings, not provider-credit blockers.

The full Anthropic prompt JSON run moved from 11/12 to 12/12. The adversarial single-case run also
passed across Anthropic, OpenAI, Gemini, native tools, and prompt JSON after tuning.

## What Failed

The baseline chose `firecrawl_extract` for one exact product URL with specific fields.

That should be `firecrawl_scrape` with JSON format. `firecrawl_extract` is better for broader
multi-page extraction jobs.

## Why This Matters

- Value proposition: helps agents choose the intended Firecrawl MCP workflow instead of adjacent tools that look plausible.
- Proof: `tuned_firecrawl_mcp_boundaries` scored 1.000, a 1.000 gain.
- Proof scope: 12 live matrix cells on the same tasks, providers, harnesses, and instruction variants.
- Baseline failure pattern: single known page structured fields.
- Downside avoided: plausible-but-wrong tool choices that waste time or return misleading results.

## Recommended Actions

- Apply exact change: Clarify that `firecrawl_scrape` handles one known page, including structured JSON fields. Reserve `firecrawl_extract` for broader multi-page structured extraction jobs.
- Add the selected cases below to repo CI or release-blocking regression coverage.
- Run the local-agent prompt below in your repo to identify exact files, patch locations, tests, and risks before editing.

## Run This In Your Repo

Replace `/path/to/repo` with the target team's local checkout. These commands ask for a plan only.

```bash
cat <<'PROMPT' | codex exec -C /path/to/repo --sandbox read-only -
Review this action-first finding:
https://github.com/cfregly/claude-agent-harness-opt/tree/main/docs/findings/firecrawl

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
https://github.com/cfregly/claude-agent-harness-opt/tree/main/docs/findings/firecrawl

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
https://github.com/cfregly/claude-agent-harness-opt/tree/main/docs/findings/firecrawl

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
| Anthropic | `legacy_firecrawl_mcp` 0/2 passed, 2 failed, 0 errors. | `tuned_firecrawl_mcp_boundaries` 2/2 passed. |
| Google Gemini | `legacy_firecrawl_mcp` 0/2 passed, 2 failed, 0 errors. | `tuned_firecrawl_mcp_boundaries` 2/2 passed. |
| OpenAI | `legacy_firecrawl_mcp` 0/2 passed, 2 failed, 0 errors. | `tuned_firecrawl_mcp_boundaries` 2/2 passed. |

Provider/model rows are evidence lanes. The target repo actions above are the only primary CTA.

## Evidence Bundle

- Public harness repo: [claude-agent-harness-opt](https://github.com/cfregly/claude-agent-harness-opt)
- Bundle folder: [firecrawl_mcp_tool_tuning_2026-06-25](https://github.com/cfregly/claude-agent-harness-opt/tree/main/evals/pr_packets/firecrawl_mcp_tool_tuning_2026-06-25)
- Matrix: [firecrawl_mcp_tool_selection.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/model_matrix/firecrawl_mcp_tool_selection.json)
- Result artifact: [firecrawl_mcp_single_page_live_2026-06-25.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/firecrawl_mcp_single_page_live_2026-06-25.md)
- PR_TITLE.txt: [PR_TITLE.txt](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/firecrawl_mcp_tool_tuning_2026-06-25/PR_TITLE.txt)
- PR_BODY.md: [PR_BODY.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/firecrawl_mcp_tool_tuning_2026-06-25/PR_BODY.md)
- REPRODUCTION.md: [REPRODUCTION.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/firecrawl_mcp_tool_tuning_2026-06-25/REPRODUCTION.md)
- evidence.json: [evidence.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/firecrawl_mcp_tool_tuning_2026-06-25/evidence.json)
- Target repo: [firecrawl-mcp-server](https://github.com/firecrawl/firecrawl-mcp-server)

<details>
<summary>LLM / Machine-readable details</summary>

## Artifact Pointers

- Source: [Firecrawl MCP server](https://github.com/firecrawl/firecrawl-mcp-server)
- Matrix: [firecrawl_mcp_tool_selection.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/model_matrix/firecrawl_mcp_tool_selection.json)
- Frontier stress receipt: [firecrawl_mcp_tool_selection_frontier_available_live_2026-07-01.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/firecrawl_mcp_tool_selection_frontier_available_live_2026-07-01.md)
- Live result: [firecrawl_mcp_single_page_live_2026-06-25.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/firecrawl_mcp_single_page_live_2026-06-25.md)
- PR packet: [firecrawl_mcp_tool_tuning_2026-06-25](https://github.com/cfregly/claude-agent-harness-opt/tree/main/evals/pr_packets/firecrawl_mcp_tool_tuning_2026-06-25)
- Detailed note: [Firecrawl MCP Tool Tuning](https://github.com/cfregly/claude-agent-harness-opt/blob/main/docs/firecrawl-mcp-tool-tuning.md)
- Ledger: [Confirmed Improvements](https://github.com/cfregly/claude-agent-harness-opt/blob/main/docs/confirmed-improvements.md)

## Reproduce

```bash
make optimize mcp=firecrawl
```

</details>
