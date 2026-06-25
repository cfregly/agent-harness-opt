# gstack Skill Routing Audit

Checked on 2026-06-25.

## Target

This audit treats the generated `gstack` Codex-compatible skills as a skills-as-tools catalog.

| Field | Value |
|---|---|
| Package | `gstack` |
| Version | `0.13.3.0` |
| Commit | `cd66fc2f890982351e3178925be563681d0ab2c5` |
| Evaluated surface | `.agents/skills/*/SKILL.md` generated skill files |
| Surface hash | `68d60eeefdde254818b03ee310bf1c4c9aaf0efee8d6db35141fe9cb7da8ae12` |
| Target surface dirty | `false` |
| Worktree dirty | `true`, from unrelated local files outside the evaluated generated skill surface |

## Commands

```bash
python scripts/build_gstack_skill_target.py \
  --gstack-root /Users/admin/dev/gstack \
  --out-dir evals/targets/gstack

python -m claude_agent_harness_optimization optimize-tools \
  evals/targets/gstack/gstack_agent_audit_bundle.json --markdown

python -m claude_agent_harness_optimization audit-agent \
  evals/targets/gstack/gstack_agent_audit_bundle.json --markdown

python -m claude_agent_harness_optimization model-matrix \
  evals/targets/gstack/gstack_skill_selection_matrix.json \
  --env-file .env --live --require-live --concurrency 8 \
  --out /tmp/gstack-skill-matrix-live-full.json

python -m claude_agent_harness_optimization model-matrix \
  evals/targets/gstack/gstack_skill_selection_matrix.json \
  --env-file .env --live --require-live --providers gemini --concurrency 6 \
  --out /tmp/gstack-skill-matrix-live-gemini-rerun.json
```

Gemini was rerun after increasing its matrix `max_tokens` to `4096`. The first full run showed
Gemini truncating prompt-JSON responses because internal thinking consumed the default output budget.

## Results

Deterministic checks:

| Check | Result |
|---|---|
| `optimize-tools` | pass, score `1.000` |
| `audit-agent` | pass, score `1.000` |
| Surface snapshot | pass, hash `ec3752895c47b5f0...` |

Live matrix:

| Metric | Value |
|---|---:|
| Total live cells | 720 |
| Passed | 708 |
| Failed | 12 |
| Errors | 0 |
| Score | 0.983 |

Variant comparison from the generated PR packet:

| Variant | Score |
|---|---:|
| `gstack_stock_skill_descriptions` | 0.97525 |
| `gstack_boundary_tuned_skill_descriptions` | 0.99175 |
| Delta | +0.01650 |
| Promote threshold | 0.01000 |
| Promotion | yes |

## Signals

Browser alias boundary:

- Failing case: `browser-headless`
- Expected: `gstack_browse`
- Observed wrong choice: `gstack_gstack`
- Affected cells: OpenAI native stock, OpenAI prompt-JSON stock and tuned, Gemini stock native and prompt-JSON.
- Interpretation: the broad generated `gstack` browser alias competes with the narrower `gstack-browse` skill. Boundary-tuned descriptions fix Anthropic and Gemini, but OpenAI prompt-JSON still chooses the alias.

Suggested upstream change:

- Do not expose the broad `gstack` alias as a normal selectable workflow skill when `gstack-browse` is also present, or mark it as a compatibility alias only.
- Add an explicit line to the alias description: "Do not select this for browser testing. Select `/browse` instead."

Safety-mode boundary:

- Failing cases: `careful-mode`, `freeze-edits`
- Expected: `gstack_careful` for destructive-command warnings, `gstack_freeze` for edit-scope locking.
- Observed wrong choice: `gstack_guard`.
- Interpretation: `/guard` is attractive because it includes both safety behaviors. The skill descriptions should say `/guard` is only for requests that explicitly ask for both destructive-command warnings and directory-scoped edit locking.

Suggested upstream change:

- Add examples to `/careful`, `/freeze`, and `/guard`.
- `/careful`: "Be careful while touching prod" means warnings only.
- `/freeze`: "Only edit this directory" means edit lock only.
- `/guard`: "Warn before destructive commands and lock edits to this directory" means both.

Gemini harness budget:

- First full run: Gemini prompt-JSON returned truncated JSON and empty native outputs in many cells.
- Probe result: `finishReason=MAX_TOKENS`, with most budget consumed by internal thinking.
- Fix: set Gemini matrix `max_tokens` to `4096`.
- Rerun result: 237/240 Gemini cells passed, 0 errors.

## Artifacts

- Matrix: `evals/targets/gstack/gstack_skill_selection_matrix.json`
- Bundle: `evals/targets/gstack/gstack_agent_audit_bundle.json`
- Combined live result: `evals/results/gstack_skill_matrix_live_2026-06-25.json`
- Gemini rerun result: `evals/results/gstack_skill_matrix_live_gemini_rerun_2026-06-25.json`
- Surface snapshot: `evals/results/gstack_surface_snapshot_2026-06-25.json`
- Upstream PR packet: `evals/pr_packets/gstack_skill_routing_2026-06-25/`
