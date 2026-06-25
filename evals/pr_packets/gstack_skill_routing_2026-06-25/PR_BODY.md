Suggested title: Tighten gstack browser and safety routing with live evals

## Value Proposition

- Helps agents choose the intended gstack workflow instead of adjacent tools that look plausible.
- `gstack_boundary_tuned_skill_descriptions` improved score from 0.975 to 0.992, a 0.017 gain over `gstack_stock_skill_descriptions`.
- The signal comes from 720 live matrix cells on a pinned source surface.
- Baseline mistakes clustered on careful-mode and browser-headless.
- The change clears the adversarially-confirmed value bar for this pinned evaluation.

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
python -m claude_agent_harness_optimization model-matrix evals/targets/gstack/gstack_skill_selection_matrix.json --env-file .env --live --require-live --cases browser-headless,qa-fix,qa-report-only,implemented-design-polish,design-plan-review,design-system,design-variants,product-brainstorm,spec-plus-browser-validation,ceo-scope-review,engineering-plan-review,auto-plan-review,pre-landing-review,root-cause-debug,security-audit,ship-pr,land-and-deploy,configure-deploy,post-deploy-monitor,performance-regression,docs-after-release,weekly-retro,real-chrome,auth-cookies,careful-mode,freeze-edits,full-guard-mode,unfreeze-edits,upgrade-gstack,no-tool-general-answer --variants gstack_stock_skill_descriptions,gstack_boundary_tuned_skill_descriptions
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

- public harness repo: https://github.com/cfregly/claude-agent-harness-optimization
- `REPRODUCTION.md` contains the full local reproduction path.
- `evidence.json` contains the matrix result, selected cases, comparison, and source pins.
- reproducible result artifact: https://github.com/cfregly/claude-agent-harness-optimization/tree/main/evals/results/gstack_skill_matrix_live_2026-06-25.json
