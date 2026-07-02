# gstack Skill Routing PR Packet

Share link: [gstack full PR/evidence bundle](https://github.com/cfregly/claude-agent-harness-opt/tree/main/evals/pr_packets/gstack_skill_routing_2026-06-25)

## Summary

| Exact change | Before | After | Result |
|---|---|---|---|
| Clarify browser alias and safety-mode skill routing boundaries. | `gstack_stock_skill_descriptions` scored 0.975. Baseline mistakes clustered on careful-mode, browser-headless. | The target surface states this routing/default/fallback behavior before the agent chooses tools. | `gstack_boundary_tuned_skill_descriptions` scored 0.992, a 0.017 gain. Add retained cases as regression coverage. |


## Result

Current frontier stress receipt: 496 current available-frontier cells, 484 passed, 8 failed, 4 errors on OpenAI `gpt-5.5` and Gemini `gemini-3.1-pro-preview-customtools`. Treat this as hill-descending coverage for the next tuning pass.

Anthropic Opus frontier receipt: 248 Anthropic Opus cells, 0 passed, 0 failed, 248 errors. The new key passed smoke testing, then later Anthropic calls hit credit exhaustion where shown in the receipt.

Confirmed improvement. This clears the adversarially-confirmed to add value bar.

The tuned gstack skill descriptions improved the 720-cell live matrix from 0.975 to 0.992, with
the remaining packet evidence preserved for reruns and upstream review.

## Why This Matters

- Value proposition: helps agents choose the intended gstack workflow instead of adjacent tools that look plausible.
- Proof: `gstack_boundary_tuned_skill_descriptions` scored 0.992, a 0.017 gain.
- Proof scope: 720 live matrix cells on the same tasks, providers, harnesses, and instruction variants.
- Baseline failure pattern: careful-mode, browser-headless.
- Downside avoided: plausible-but-wrong tool choices that waste time or return misleading results.

## Recommended Actions

- Apply exact change: Clarify browser alias and safety-mode skill routing boundaries.
- Add the selected cases below to repo CI or release-blocking regression coverage.
- Run the local-agent prompt below in your repo to identify exact files, patch locations, tests, and risks before editing.

## Run This In Your Repo

Replace `/path/to/repo` with the target team's local checkout. These commands ask for a plan only.

```bash
cat <<'PROMPT' | codex exec -C /path/to/repo --sandbox read-only -
Review this action-first finding:
https://github.com/cfregly/claude-agent-harness-opt/tree/main/docs/findings/gstack

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
https://github.com/cfregly/claude-agent-harness-opt/tree/main/docs/findings/gstack

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
https://github.com/cfregly/claude-agent-harness-opt/tree/main/docs/findings/gstack

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
| Anthropic | `gstack_stock_skill_descriptions` 118/120 passed, 2 failed, 0 errors. | `gstack_boundary_tuned_skill_descriptions` 119/120 passed, 1 failed, 0 errors. |
| Google Gemini | `gstack_stock_skill_descriptions` 117/120 passed, 3 failed, 0 errors. | `gstack_boundary_tuned_skill_descriptions` 120/120 passed. |
| OpenAI | `gstack_stock_skill_descriptions` 116/120 passed, 4 failed, 0 errors. | `gstack_boundary_tuned_skill_descriptions` 118/120 passed, 2 failed, 0 errors. |

Provider/model rows are evidence lanes. The target repo actions above are the only primary CTA.

## Evidence Bundle

- Public harness repo: [claude-agent-harness-opt](https://github.com/cfregly/claude-agent-harness-opt)
- Bundle folder: [gstack_skill_routing_2026-06-25](https://github.com/cfregly/claude-agent-harness-opt/tree/main/evals/pr_packets/gstack_skill_routing_2026-06-25)
- Matrix: [gstack_skill_selection_matrix.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/targets/gstack/gstack_skill_selection_matrix.json)
- Result artifact: [gstack_skill_matrix_live_2026-06-25.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/gstack_skill_matrix_live_2026-06-25.json)
- PR_TITLE.txt: [PR_TITLE.txt](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/gstack_skill_routing_2026-06-25/PR_TITLE.txt)
- PR_BODY.md: [PR_BODY.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/gstack_skill_routing_2026-06-25/PR_BODY.md)
- REPRODUCTION.md: [REPRODUCTION.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/gstack_skill_routing_2026-06-25/REPRODUCTION.md)
- evidence.json: [evidence.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/gstack_skill_routing_2026-06-25/evidence.json)
- Target repo: [gstack](https://github.com/garrytan/gstack)

<details>
<summary>LLM / Machine-readable details</summary>

## Reproduce

[REPRODUCTION.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/gstack_skill_routing_2026-06-25/REPRODUCTION.md)
contains the exact command and pinned matrix surface.

</details>
