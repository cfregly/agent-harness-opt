Suggested title: Tighten InsForge MCP deploy routing with live evals

> [!NOTE]
> This page starts with the founder handoff. Detailed eval, command, and machine-readable material is preserved below.

## Summary

| Before | After | Result |
|---|---|---|
| `readme_insforge_mcp` scored 0.938. Baseline mistakes clustered on relative deploy path avoids tool. | Suggested change: Clarify that `create-deployment` requires an absolute `sourceDirectory` and must be avoided for relative paths, starter-template creation, deployment status lookup, or remote prepared-deployment triggering. | `source_tuned_insforge_mcp` scored 1.000, a 0.062 gain. Add retained cases as regression coverage. |

## Why This Matters

- Value proposition: helps agents choose the intended InsForge MCP workflow instead of adjacent tools that look plausible.
- Proof: `source_tuned_insforge_mcp` scored 1.000, a 0.062 gain.
- Evidence: 32 live matrix cells on the same tasks, providers, harnesses, and instruction variants.
- Baseline failure pattern: relative deploy path avoids tool.
- Downside avoided: plausible-but-wrong tool choices that waste time or return misleading results.

## Recommended Actions

- Apply this change: Clarify that `create-deployment` requires an absolute `sourceDirectory` and must be avoided for relative paths, starter-template creation, deployment status lookup, or remote prepared-deployment triggering.
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
- Founder handoff: [InsForge MCP](https://github.com/cfregly/claude-agent-harness-opt/tree/main/docs/findings/insforge)
- Packet folder: [insforge_mcp_tool_tuning_2026-06-28](https://github.com/cfregly/claude-agent-harness-opt/tree/main/evals/pr_packets/insforge_mcp_tool_tuning_2026-06-28)
- PR_TITLE.txt: [PR_TITLE.txt](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/insforge_mcp_tool_tuning_2026-06-28/PR_TITLE.txt)
- PR_BODY.md: [PR_BODY.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/insforge_mcp_tool_tuning_2026-06-28/PR_BODY.md)
- REPRODUCTION.md: [REPRODUCTION.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/insforge_mcp_tool_tuning_2026-06-28/REPRODUCTION.md)
- evidence.json: [evidence.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/insforge_mcp_tool_tuning_2026-06-28/evidence.json)
- Matrix: [insforge_mcp_tool_selection.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/model_matrix/insforge_mcp_tool_selection.json)
- Result artifact: [insforge_mcp_tool_selection_2026-06-28.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/insforge_mcp_tool_selection_2026-06-28.md)
- Target repo: [insforge-mcp](https://github.com/InsForge/insforge-mcp)

<details>
<summary>LLM / Machine-readable details</summary>

## Evidence

- Finding folder: [InsForge MCP Tool Tuning finding](https://github.com/cfregly/claude-agent-harness-opt/tree/main/docs/findings/insforge)
- Matrix: [insforge_mcp_tool_selection.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/model_matrix/insforge_mcp_tool_selection.json)
- Result artifact: [insforge_mcp_tool_selection_2026-06-28.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/insforge_mcp_tool_selection_2026-06-28.md)
- Evidence JSON: [evidence.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/insforge_mcp_tool_tuning_2026-06-28/evidence.json)

## Frontier Receipts

- Current frontier stress receipt: [insforge_mcp_tool_selection_frontier_available_live_2026-07-01.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/insforge_mcp_tool_selection_frontier_available_live_2026-07-01.md)
- Current frontier JSON receipt: [insforge_mcp_tool_selection_frontier_available_live_2026-07-01.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/insforge_mcp_tool_selection_frontier_available_live_2026-07-01.json)
- Anthropic Opus frontier receipt: [insforge_mcp_tool_selection_frontier_anthropic_live_2026-07-01.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/insforge_mcp_tool_selection_frontier_anthropic_live_2026-07-01.md)
- Anthropic Opus JSON receipt: [insforge_mcp_tool_selection_frontier_anthropic_live_2026-07-01.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/insforge_mcp_tool_selection_frontier_anthropic_live_2026-07-01.json)

## Result

- packet type: improvement
- promoted by value bar: yes
- baseline variant: readme_insforge_mcp
- candidate variant: source_tuned_insforge_mcp
- baseline score: 0.938
- candidate score: 1.000
- delta: 0.062
- minimum delta: 0.010

## Cases

- new project setup reads instructions | expected: fetch-docs | forbidden: download-template,get-backend-metadata,run-raw-sql,fetch-sdk-docs
- new app bootstrap uses template | expected: download-template | forbidden: fetch-docs,create-deployment,get-backend-metadata
- backend inventory uses metadata | expected: get-backend-metadata | forbidden: get-table-schema,run-raw-sql,list-buckets,get-anon-key
- known table details use schema | expected: get-table-schema | forbidden: get-backend-metadata,run-raw-sql
- explicit sql uses raw sql | expected: run-raw-sql | forbidden: get-table-schema,get-backend-metadata,bulk-upsert
- csv import uses bulk upsert | expected: bulk-upsert | forbidden: run-raw-sql,create-bucket
- storage inventory lists buckets | expected: list-buckets | forbidden: get-backend-metadata,create-bucket,delete-bucket
- create storage bucket uses create bucket | expected: create-bucket | forbidden: list-buckets,delete-bucket
- read function uses get function | expected: get-function | forbidden: create-function,update-function,delete-function,get-container-logs
- update function uses update function | expected: update-function | forbidden: create-function,get-function,delete-function
- function logs use container logs | expected: get-container-logs | forbidden: get-function,run-raw-sql
- sdk docs use sdk docs | expected: fetch-sdk-docs | forbidden: fetch-docs,list-buckets
- client token uses anon key | expected: get-anon-key | forbidden: fetch-docs,get-backend-metadata
- absolute source deploy uses create deployment | expected: create-deployment | forbidden: download-template,start-deployment
- prepared remote upload starts deployment | expected: start-deployment | forbidden: create-deployment,download-template
- relative deploy path avoids tool | expected:  | forbidden: create-deployment,start-deployment,download-template

## Reproduce

```bash
make optimize mcp=insforge OUT=evals/results/insforge_mcp_tool_selection_2026-06-28.md
```

</details>
