# gstack Skill Routing Anthropic Frontier Live Result - 2026-07-01

Passed: no
Live: yes

This retained receipt uses the newly provided Anthropic key against the accessible `claude-opus-4-8` profile.

> [!NOTE]
> Anthropic sent billing-lockout notices on 2026-07-01 for the `FluxCapacitor` and `Stealth` organizations: API access was disabled because each organization was out of usage credits. The regenerated JSON receipt now fails closed at provider preflight and marks these rows as `provider_blocked`, not model-quality failures.

## Matrix Summary

- total: 248
- passed_cases: 0
- failed_cases: 0
- errors: 0
- provider_blocked: 248
- skipped: 0
- score: 0.0

## Profiles

- `anthropic-opus-high`: `claude-opus-4-8`

## Status By Profile

| Profile | Passed | Failed | Errors | Provider blocked | Skipped |
|---|---:|---:|---:|---:|---:|
| `anthropic-opus-high` | 0 | 0 | 0 | 248 | 0 |

## Provider-State Blocker

- 248 cells were blocked before live fanout by Anthropic billing or usage-credit state.
- The blocker reason is `anthropic_billing_or_usage_credits`.
- Remediation is to add Anthropic API credits or enable auto-reload, then rerun the Anthropic profile.
- No gstack tool-routing quality conclusion should be drawn from this Anthropic receipt until provider access is restored.

## Machine-readable Receipt

[JSON receipt](https://github.com/cfregly/agent-harness-opt/blob/main/evals/results/gstack_skill_matrix_frontier_anthropic_attempt_2026-07-01.json)
