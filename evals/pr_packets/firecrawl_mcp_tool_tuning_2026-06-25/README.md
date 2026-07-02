# Firecrawl MCP Tool Tuning PR Packet

Share link: [Firecrawl MCP Tool Tuning full PR/evidence bundle](https://github.com/cfregly/claude-agent-harness-opt/tree/main/evals/pr_packets/firecrawl_mcp_tool_tuning_2026-06-25)

## Summary

| Before | After | Result |
|---|---|---|
| `legacy_firecrawl_mcp` scored 0.000. Baseline mistakes clustered on single known page structured fields. | Suggested change: Clarify that `firecrawl_scrape` handles one known page, including structured JSON fields. Reserve `firecrawl_extract` for broader multi-page structured extraction jobs. | `tuned_firecrawl_mcp_boundaries` scored 1.000, a 1.000 gain. Add retained cases as regression coverage. |

## Why This Matters

- Value proposition: helps agents choose the intended Firecrawl MCP workflow instead of adjacent tools that look plausible.
- Proof: `tuned_firecrawl_mcp_boundaries` scored 1.000, a 1.000 gain.
- Evidence: 12 live matrix cells on the same tasks, providers, harnesses, and instruction variants.
- Baseline failure pattern: single known page structured fields.
- Downside avoided: plausible-but-wrong tool choices that waste time or return misleading results.

## Recommended Actions

- Apply this change: Clarify that `firecrawl_scrape` handles one known page, including structured JSON fields. Reserve `firecrawl_extract` for broader multi-page structured extraction jobs.
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
- Founder handoff: [Firecrawl MCP](https://github.com/cfregly/claude-agent-harness-opt/tree/main/docs/findings/firecrawl)
- Packet folder: [firecrawl_mcp_tool_tuning_2026-06-25](https://github.com/cfregly/claude-agent-harness-opt/tree/main/evals/pr_packets/firecrawl_mcp_tool_tuning_2026-06-25)
- PR_TITLE.txt: [PR_TITLE.txt](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/firecrawl_mcp_tool_tuning_2026-06-25/PR_TITLE.txt)
- PR_BODY.md: [PR_BODY.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/firecrawl_mcp_tool_tuning_2026-06-25/PR_BODY.md)
- REPRODUCTION.md: [REPRODUCTION.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/firecrawl_mcp_tool_tuning_2026-06-25/REPRODUCTION.md)
- evidence.json: [evidence.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/firecrawl_mcp_tool_tuning_2026-06-25/evidence.json)
- Matrix: [firecrawl_mcp_tool_selection.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/model_matrix/firecrawl_mcp_tool_selection.json)
- Result artifact: [firecrawl_mcp_single_page_live_2026-06-25.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/firecrawl_mcp_single_page_live_2026-06-25.md)
- Target repo: [firecrawl-mcp-server](https://github.com/firecrawl/firecrawl-mcp-server)

- Packet folder: [firecrawl_mcp_tool_tuning_2026-06-25](https://github.com/cfregly/claude-agent-harness-opt/tree/main/evals/pr_packets/firecrawl_mcp_tool_tuning_2026-06-25)

[Current frontier stress receipts](https://github.com/cfregly/claude-agent-harness-opt/blob/main/docs/frontier-stress-2026-07-01.md) tracks all retained current available-frontier receipts.

Bundle folder: [firecrawl_mcp_tool_tuning_2026-06-25](https://github.com/cfregly/claude-agent-harness-opt/tree/main/evals/pr_packets/firecrawl_mcp_tool_tuning_2026-06-25)

- Finding folder: [Firecrawl MCP Tool Tuning finding](https://github.com/cfregly/claude-agent-harness-opt/tree/main/docs/findings/firecrawl)
- PR title: [PR_TITLE.txt](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/firecrawl_mcp_tool_tuning_2026-06-25/PR_TITLE.txt)
- PR body: [PR_BODY.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/firecrawl_mcp_tool_tuning_2026-06-25/PR_BODY.md)
- Reproduction doc: [REPRODUCTION.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/firecrawl_mcp_tool_tuning_2026-06-25/REPRODUCTION.md)
- Evidence JSON: [evidence.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/firecrawl_mcp_tool_tuning_2026-06-25/evidence.json)
- Frontier stress receipt: [firecrawl_mcp_tool_selection_frontier_available_live_2026-07-01.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/firecrawl_mcp_tool_selection_frontier_available_live_2026-07-01.md)
- Frontier JSON receipt: [firecrawl_mcp_tool_selection_frontier_available_live_2026-07-01.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/firecrawl_mcp_tool_selection_frontier_available_live_2026-07-01.json)
- Anthropic Opus receipt: [firecrawl_mcp_tool_selection_frontier_anthropic_live_2026-07-01.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/firecrawl_mcp_tool_selection_frontier_anthropic_live_2026-07-01.md)
- Anthropic Opus JSON: [firecrawl_mcp_tool_selection_frontier_anthropic_live_2026-07-01.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/firecrawl_mcp_tool_selection_frontier_anthropic_live_2026-07-01.json)
- Live result: [firecrawl_mcp_single_page_live_2026-06-25.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/firecrawl_mcp_single_page_live_2026-06-25.md)
- Detailed note: [firecrawl-mcp-tool-tuning.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/docs/firecrawl-mcp-tool-tuning.md)

## Result

Current frontier stress receipt: 60 current available-frontier cells, 51 passed, 9 failed, 0 errors on OpenAI `gpt-5.5` and Gemini `gemini-3.1-pro-preview-customtools`. Treat this as hill-descending coverage for the next tuning pass.

Anthropic Opus frontier receipt: 30 Anthropic Opus cells, 26 passed, 4 failed, 0 errors on accessible `claude-opus-4-8`. Any failed cells are model-selection findings, not provider-credit blockers.

Confirmed improvement. This clears the adversarially-confirmed to add value bar.

The adversarial single-page structured-fields cell moved from 0/6 legacy passes to 6/6 tuned passes across Anthropic, OpenAI, Gemini, native tools, and prompt JSON.

## Evidence

- Source: [Firecrawl MCP server](https://github.com/firecrawl/firecrawl-mcp-server)
- Matrix: [firecrawl_mcp_tool_selection.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/model_matrix/firecrawl_mcp_tool_selection.json)
- Live result: [firecrawl_mcp_single_page_live_2026-06-25.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/firecrawl_mcp_single_page_live_2026-06-25.md)
- Detailed note: [firecrawl-mcp-tool-tuning.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/docs/firecrawl-mcp-tool-tuning.md)
- Ledger: [Confirmed Improvements](https://github.com/cfregly/claude-agent-harness-opt/blob/main/docs/confirmed-improvements.md)

## Reproduce

[REPRODUCTION.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/firecrawl_mcp_tool_tuning_2026-06-25/REPRODUCTION.md) contains the exact command and pinned matrix surface.
