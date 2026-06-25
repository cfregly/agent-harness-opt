# Reproduction for gstack

## Source Pin

- commit: cd66fc2f890982351e3178925be563681d0ab2c5
- generated surface hash: 68d60eeefdde254818b03ee310bf1c4c9aaf0efee8d6db35141fe9cb7da8ae12
- package name: gstack
- package version: 0.13.3.0
- remote: git@github.com:garrytan/gstack.git
- source path: /Users/admin/dev/gstack
- target surface: .agents/skills/*/SKILL.md generated skill files
- target surface dirty: False
- worktree dirty: True

## Command

```bash
python -m claude_agent_harness_optimization model-matrix evals/targets/gstack/gstack_skill_selection_matrix.json --env-file .env --live --require-live --cases browser-headless,qa-fix,qa-report-only,implemented-design-polish,design-plan-review,design-system,design-variants,product-brainstorm,spec-plus-browser-validation,ceo-scope-review,engineering-plan-review,auto-plan-review,pre-landing-review,root-cause-debug,security-audit,ship-pr,land-and-deploy,configure-deploy,post-deploy-monitor,performance-regression,docs-after-release,weekly-retro,real-chrome,auth-cookies,careful-mode,freeze-edits,full-guard-mode,unfreeze-edits,upgrade-gstack,no-tool-general-answer --variants gstack_stock_skill_descriptions,gstack_boundary_tuned_skill_descriptions
```

## Value Bar

- baseline: gstack_stock_skill_descriptions at 0.975
- candidate: gstack_boundary_tuned_skill_descriptions at 0.992
- delta: 0.017
- minimum delta: 0.010
- promote: yes

## Cases

- browser-headless | expected: gstack_browse | forbidden: gstack_gstack,gstack_connect_chrome,gstack_qa
  - task: Open http://localhost:3000, click through the signup flow, and capture screenshots of any bug evidence.
- qa-fix | expected: gstack_qa | forbidden: gstack_qa_only,gstack_browse
  - task: QA this staging site, fix the bugs you find, add regression tests, and commit each fix atomically.
- qa-report-only | expected: gstack_qa_only | forbidden: gstack_qa,gstack_browse
  - task: Test this app and give me a bug report with repro steps, but do not edit any files.
- implemented-design-polish | expected: gstack_design_review | forbidden: gstack_plan_design_review,gstack_design_consultation
  - task: Audit the implemented dashboard UI for spacing, hierarchy, and visual slop, then fix the issues.
- design-plan-review | expected: gstack_plan_design_review | forbidden: gstack_design_review,gstack_plan_eng_review
  - task: Review this UI plan before implementation and score the design dimensions with recommendations.
- design-system | expected: gstack_design_consultation | forbidden: gstack_design_shotgun,gstack_plan_design_review
  - task: Create a design system and DESIGN.md for a new B2B workflow product.
- design-variants | expected: gstack_design_shotgun | forbidden: gstack_design_consultation,gstack_design_review
  - task: Show me several visual directions for this feature and let me compare options before choosing.
- product-brainstorm | expected: gstack_office_hours | forbidden: gstack_spec_qa,gstack_plan_ceo_review
  - task: I have an idea for a restaurant waitlist tool. Help me pressure-test whether it is worth building.

## Summary Counts

- total: 720
- passed cases: 708
- failed cases: 12
- errors: 0
- score: 0.9833333333333333
