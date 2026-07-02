Suggested title: Tighten gstack browser and safety routing with live evals

> [!NOTE]
> This page starts with the founder handoff. Detailed eval, command, and machine-readable material is preserved below.

## Summary

| Exact change | Before | After | Result |
|---|---|---|---|
| Clarify browser alias and safety-mode skill routing boundaries. | `gstack_stock_skill_descriptions` scored 0.975. Baseline mistakes clustered on careful-mode, browser-headless. | The target surface states this routing/default/fallback behavior before the agent chooses tools. | `gstack_boundary_tuned_skill_descriptions` scored 0.992, a 0.017 gain. Add retained cases as regression coverage. |


## Result

- Confirmed improvement: `gstack_boundary_tuned_skill_descriptions` moved from 0.975 to 0.992, a 0.017 gain over `gstack_stock_skill_descriptions`.
- Value bar: cleared the 0.010 minimum delta.
- Proof scope: 720 live matrix cells, 708 passed, 12 failed, 0 errors.

## What Failed

- `gstack_stock_skill_descriptions` failed or chose the wrong boundary on: careful-mode, browser-headless.
- Those failures are the target-owned behavior to encode in descriptions, defaults, options, or regression tests.

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

## Frontier Receipts

- Anthropic Opus frontier receipt: [gstack_skill_matrix_frontier_anthropic_attempt_2026-07-01.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/gstack_skill_matrix_frontier_anthropic_attempt_2026-07-01.md)
- Anthropic Opus JSON receipt: [gstack_skill_matrix_frontier_anthropic_attempt_2026-07-01.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/gstack_skill_matrix_frontier_anthropic_attempt_2026-07-01.json)
- Current frontier stress receipt: [gstack_skill_matrix_frontier_available_live_2026-07-01.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/gstack_skill_matrix_frontier_available_live_2026-07-01.md)
- Current frontier JSON receipt: [gstack_skill_matrix_frontier_available_live_2026-07-01.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/gstack_skill_matrix_frontier_available_live_2026-07-01.json)

## How This Is Proven Useful

- The proof compares `gstack_stock_skill_descriptions` and `gstack_boundary_tuned_skill_descriptions` on the same tasks, providers, harnesses, and instruction variants.
- The measured delta is 0.017 against a required minimum of 0.010.
- The run contains 720 matrix cells, with 12 failures preserved as evidence instead of hand-waved examples.
- The source pin, exact cases, reproduction command, and result artifact are included so the claim can be rerun or challenged.

## Current Frontier Coverage

- The packet now includes a current available-frontier sweep: [gstack_skill_matrix_frontier_available_live_2026-07-01.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/gstack_skill_matrix_frontier_available_live_2026-07-01.md).
- The available-frontier sweep completed 496 current available-frontier cells, 484 passed, 8 failed, 4 errors across OpenAI `gpt-5.5` and Gemini `gemini-3.1-pro-preview-customtools`.
- The older `claude-sonnet-4-5`, `gpt-4.1`, and `gemini-2.5-pro` cells remain regression evidence, while the 2026-07-01 receipt is the current hill-descending surface.
- Anthropic Opus is now retained in a separate receipt: the new key passed smoke testing, then later calls hit credit exhaustion where shown in the receipt.

## Downside If Not Changed

- Ambiguous descriptions let plausible adjacent tools win, so failures look reasonable in transcripts even when the selected workflow is wrong.
- Model or harness upgrades can reintroduce the same mistake unless the boundary is encoded in descriptions and regression cases.
- Browser ambiguity can route a request to a broad compatibility alias instead of the purpose-built browser-testing workflow.
- Safety ambiguity can escalate warning-only or directory-only requests into full guard mode, adding constraints the user did not ask for.

## Proposed change for gstack

Clarify browser alias and safety-mode skill routing boundaries.

## Why

This change is backed by a harness matrix result, not a prose-only review. The bar is adversarially-confirmed to add value.

## Pinned surface

- commit: cd66fc2f890982351e3178925be563681d0ab2c5
- generated surface hash: 68d60eeefdde254818b03ee310bf1c4c9aaf0efee8d6db35141fe9cb7da8ae12
- package name: gstack
- package version: 0.13.3.0
- remote: git@github.com:garrytan/gstack.git
- source path: /Users/admin/dev/gstack
- target surface: .agents/skills/*/SKILL.md generated skill files
- target surface dirty: False
- worktree dirty: True
- target repo: https://github.com/garrytan/gstack

## What We Learned

- `gstack_boundary_tuned_skill_descriptions` beat `gstack_stock_skill_descriptions` by 0.017 against a minimum delta of 0.010.
- Baseline mistakes clustered on these cases: careful-mode, browser-headless.
- The suggested change clears the adversarially-confirmed value bar for this pinned surface.

## Run surfaces

- provider=anthropic, model=claude-sonnet-4-5, harness=native_tools, instruction=baseline_skill_routing
- provider=anthropic, model=claude-sonnet-4-5, harness=native_tools, instruction=boundary_routing_rules
- provider=anthropic, model=claude-sonnet-4-5, harness=prompt_json, instruction=baseline_skill_routing
- provider=anthropic, model=claude-sonnet-4-5, harness=prompt_json, instruction=boundary_routing_rules
- provider=openai, model=gpt-4.1, harness=native_tools, instruction=baseline_skill_routing
- provider=openai, model=gpt-4.1, harness=native_tools, instruction=boundary_routing_rules
- provider=openai, model=gpt-4.1, harness=prompt_json, instruction=baseline_skill_routing
- provider=openai, model=gpt-4.1, harness=prompt_json, instruction=boundary_routing_rules
- provider=gemini, model=gemini-2.5-pro, harness=native_tools, instruction=baseline_skill_routing
- provider=gemini, model=gemini-2.5-pro, harness=native_tools, instruction=boundary_routing_rules
- provider=gemini, model=gemini-2.5-pro, harness=prompt_json, instruction=baseline_skill_routing
- provider=gemini, model=gemini-2.5-pro, harness=prompt_json, instruction=boundary_routing_rules

## Cell summary

- provider=anthropic, harness=native_tools, variant=gstack_boundary_tuned_skill_descriptions, instruction=baseline_skill_routing, passed=30, failed=0, errors=0, score=1.0
- provider=anthropic, harness=native_tools, variant=gstack_boundary_tuned_skill_descriptions, instruction=boundary_routing_rules, passed=29, failed=1, errors=0, score=0.967
- provider=anthropic, harness=native_tools, variant=gstack_stock_skill_descriptions, instruction=baseline_skill_routing, passed=30, failed=0, errors=0, score=1.0
- provider=anthropic, harness=native_tools, variant=gstack_stock_skill_descriptions, instruction=boundary_routing_rules, passed=30, failed=0, errors=0, score=1.0
- provider=anthropic, harness=prompt_json, variant=gstack_boundary_tuned_skill_descriptions, instruction=baseline_skill_routing, passed=30, failed=0, errors=0, score=1.0
- provider=anthropic, harness=prompt_json, variant=gstack_boundary_tuned_skill_descriptions, instruction=boundary_routing_rules, passed=30, failed=0, errors=0, score=1.0
- provider=anthropic, harness=prompt_json, variant=gstack_stock_skill_descriptions, instruction=baseline_skill_routing, passed=29, failed=1, errors=0, score=0.967
- provider=anthropic, harness=prompt_json, variant=gstack_stock_skill_descriptions, instruction=boundary_routing_rules, passed=29, failed=1, errors=0, score=0.967
- provider=gemini, harness=native_tools, variant=gstack_boundary_tuned_skill_descriptions, instruction=baseline_skill_routing, passed=30, failed=0, errors=0, score=1.0
- provider=gemini, harness=native_tools, variant=gstack_boundary_tuned_skill_descriptions, instruction=boundary_routing_rules, passed=30, failed=0, errors=0, score=1.0
- provider=gemini, harness=native_tools, variant=gstack_stock_skill_descriptions, instruction=baseline_skill_routing, passed=29, failed=1, errors=0, score=0.967
- provider=gemini, harness=native_tools, variant=gstack_stock_skill_descriptions, instruction=boundary_routing_rules, passed=30, failed=0, errors=0, score=1.0

## Reproduce

```bash
python -m claude_agent_harness_opt model-matrix evals/targets/gstack/gstack_skill_selection_matrix.json --env-file .env --live --require-live --cases browser-headless,qa-fix,qa-report-only,implemented-design-polish,design-plan-review,design-system,design-variants,product-brainstorm,spec-plus-browser-validation,ceo-scope-review,engineering-plan-review,auto-plan-review,pre-landing-review,root-cause-debug,security-audit,ship-pr,land-and-deploy,configure-deploy,post-deploy-monitor,performance-regression,docs-after-release,weekly-retro,real-chrome,auth-cookies,careful-mode,freeze-edits,full-guard-mode,unfreeze-edits,upgrade-gstack,no-tool-general-answer --variants gstack_stock_skill_descriptions,gstack_boundary_tuned_skill_descriptions
```

## Examples used

- browser-headless | expected selection: gstack_browse | confusable alternatives checked: gstack_gstack,gstack_connect_chrome,gstack_qa
- qa-fix | expected selection: gstack_qa | confusable alternatives checked: gstack_qa_only,gstack_browse
- qa-report-only | expected selection: gstack_qa_only | confusable alternatives checked: gstack_qa,gstack_browse
- implemented-design-polish | expected selection: gstack_design_review | confusable alternatives checked: gstack_plan_design_review,gstack_design_consultation
- design-plan-review | expected selection: gstack_plan_design_review | confusable alternatives checked: gstack_design_review,gstack_plan_eng_review
- design-system | expected selection: gstack_design_consultation | confusable alternatives checked: gstack_design_shotgun,gstack_plan_design_review
- design-variants | expected selection: gstack_design_shotgun | confusable alternatives checked: gstack_design_consultation,gstack_design_review
- product-brainstorm | expected selection: gstack_office_hours | confusable alternatives checked: gstack_spec_qa,gstack_plan_ceo_review

## Baseline failures

- careful-mode chose gstack_guard
- careful-mode chose gstack_guard
- browser-headless chose gstack_gstack
- browser-headless chose gstack_gstack
- browser-headless chose gstack_gstack
- browser-headless chose gstack_gstack
- browser-headless chose gstack_gstack
- browser-headless chose gstack_gstack

## Candidate passes

- browser-headless chose gstack_browse
- qa-fix chose gstack_qa
- qa-report-only chose gstack_qa_only
- implemented-design-polish chose gstack_design_review
- design-plan-review chose gstack_plan_design_review
- design-system chose gstack_design_consultation
- design-variants chose gstack_design_shotgun
- product-brainstorm chose gstack_office_hours

## Artifact Pointers

- Public harness repo: [claude-agent-harness-opt](https://github.com/cfregly/claude-agent-harness-opt)
- Reproduction doc: [REPRODUCTION.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/gstack_skill_routing_2026-06-25/REPRODUCTION.md)
- Evidence JSON: [evidence.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/gstack_skill_routing_2026-06-25/evidence.json)
- Matrix: [gstack_skill_selection_matrix.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/targets/gstack/gstack_skill_selection_matrix.json)
- Result artifact: [gstack_skill_matrix_live_2026-06-25.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/gstack_skill_matrix_live_2026-06-25.json)

</details>
