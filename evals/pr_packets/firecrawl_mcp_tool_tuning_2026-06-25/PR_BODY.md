Suggested title: Improve Firecrawl MCP tool routing with live eval evidence

> [!NOTE]
> This page starts with the founder handoff. Detailed eval, command, and machine-readable material is preserved below.

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

<details>
<summary>LLM / Machine-readable details</summary>

## Evidence

- Finding folder: [Firecrawl MCP Tool Tuning finding](https://github.com/cfregly/claude-agent-harness-opt/tree/main/docs/findings/firecrawl)
- Matrix: [firecrawl_mcp_tool_selection.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/model_matrix/firecrawl_mcp_tool_selection.json)
- Result artifact: [firecrawl_mcp_single_page_live_2026-06-25.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/firecrawl_mcp_single_page_live_2026-06-25.md)
- Evidence JSON: [evidence.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/firecrawl_mcp_tool_tuning_2026-06-25/evidence.json)

## Frontier Receipts

- Current frontier stress receipt: [firecrawl_mcp_tool_selection_frontier_available_live_2026-07-01.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/firecrawl_mcp_tool_selection_frontier_available_live_2026-07-01.md)
- Current frontier JSON receipt: [firecrawl_mcp_tool_selection_frontier_available_live_2026-07-01.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/firecrawl_mcp_tool_selection_frontier_available_live_2026-07-01.json)
- Anthropic Opus frontier receipt: [firecrawl_mcp_tool_selection_frontier_anthropic_live_2026-07-01.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/firecrawl_mcp_tool_selection_frontier_anthropic_live_2026-07-01.md)
- Anthropic Opus JSON receipt: [firecrawl_mcp_tool_selection_frontier_anthropic_live_2026-07-01.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/firecrawl_mcp_tool_selection_frontier_anthropic_live_2026-07-01.json)

## Result

- packet type: improvement
- promoted by value bar: yes
- baseline variant: legacy_firecrawl_mcp
- candidate variant: tuned_firecrawl_mcp_boundaries
- baseline score: 0.000
- candidate score: 1.000
- delta: 1.000
- minimum delta: 0.010

## Cases

- single known page structured fields | expected: firecrawl_scrape | forbidden: firecrawl_extract,firecrawl_batch_scrape,firecrawl_interact,firecrawl_monitor_create

## Reproduce

```bash
python scripts/optimize_mcp.py firecrawl --env-file .env --live --require-live --markdown --providers anthropic,openai,gemini --harnesses prompt_json,native_tools --cases "single known page structured fields" --out /tmp/firecrawl-single-page.md
```

</details>
