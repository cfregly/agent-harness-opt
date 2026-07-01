Suggested title: Tighten gstack browser and safety routing with live evals

> [!NOTE]
> This page starts with the human summary. Detailed eval, command, and machine-readable material is preserved below.


## Value Proposition

- Helps agents choose the intended gstack workflow instead of adjacent tools that look plausible.
- `gstack_boundary_tuned_skill_descriptions` improved score from 0.975 to 0.992, a 0.017 gain over `gstack_stock_skill_descriptions`.
- The signal comes from 720 live matrix cells on a pinned source surface.
- Baseline mistakes clustered on careful-mode and browser-headless.
- The change clears the adversarially-confirmed value bar for this pinned evaluation.

## What Already Works

- The tested gstack surface is already strong: 708/720 live cells passed with 0 errors.
- The candidate score is 0.992, so this is a boundary tightening, not a broad rewrite.
- The packet keeps passing behavior visible so maintainers can see what does not need to change.

<details>
<summary>LLM / Machine-readable details</summary>

## How This Is Proven Useful

- The proof compares `gstack_stock_skill_descriptions` and `gstack_boundary_tuned_skill_descriptions` on the same tasks, providers, harnesses, and instruction variants.
- The measured delta is 0.017 against a required minimum of 0.010.
- The run contains 720 matrix cells, with 12 failures preserved as evidence instead of hand-waved examples.
- The source pin, exact cases, reproduction command, and result artifact are included so the claim can be rerun or challenged.

## Current Frontier Coverage

- This packet's 720-cell result is historical compatibility evidence, not a complete current frontier/latest sweep.
- Do not present older-model wins as the upstream headline if the same ambiguity no longer reproduces on current latest model and harness versions.
- The generated gstack matrix now includes `anthropic-fable-frontier`, `openai-gpt55-frontier`, and `gemini-31-pro-customtools-frontier`; use those cells for a stronger upstream-facing claim.
- Keep the older `claude-sonnet-4-5`, `gpt-4.1`, and `gemini-2.5-pro` cells as regression evidence.

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

## Result

- promoted by value bar: yes
- baseline variant: gstack_stock_skill_descriptions
- candidate variant: gstack_boundary_tuned_skill_descriptions
- baseline score: 0.975
- candidate score: 0.992
- delta: 0.017
- minimum delta: 0.010

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

## Evidence

- Public harness repo: [claude-agent-harness-opt](https://github.com/cfregly/claude-agent-harness-opt)
- Reproduction doc: [REPRODUCTION.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/gstack_skill_routing_2026-06-25/REPRODUCTION.md)
- Evidence JSON: [evidence.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/gstack_skill_routing_2026-06-25/evidence.json)
- Matrix: [gstack_skill_selection_matrix.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/targets/gstack/gstack_skill_selection_matrix.json)
- Result artifact: [gstack_skill_matrix_live_2026-06-25.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/gstack_skill_matrix_live_2026-06-25.json)

</details>
