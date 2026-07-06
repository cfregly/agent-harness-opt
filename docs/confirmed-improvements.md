# Confirmed Improvements

This ledger separates confirmed tuning wins from passing guardrails. A tool catalog can pass now and
still count as an improvement when the tuned variant beat a weaker baseline under the same eval.

Checked through 2026-07-01.

## Summary

The table below is the exact handoff text. Baseline / before is the current behavior. Suggested / after is the proposed wording or behavior to implement.

| Target | Suggested change | Baseline / before description | Suggested / after description | Result |
|---|---|---|---|---|
| Firecrawl MCP | Keep or add wording that sends one known page plus specific fields to `firecrawl_scrape`. Reserve `firecrawl_extract` for multi-page or broad extraction. | A request for one exact URL plus specific fields could be routed to `firecrawl_extract`, even though it is not a broad multi-page extraction job. | `firecrawl_scrape` handles the exact URL with structured JSON fields. `firecrawl_extract` stays reserved for broader multi-page extraction. | `tuned_firecrawl_mcp_boundaries` moved the focused adversarial slice to 12/12. |
| Supabase MCP | Route schema-changing SQL to `apply_migration`. Use `execute_sql` only for ordinary non-schema SQL. | Schema-changing SQL such as `CREATE TABLE`, `CREATE INDEX`, functions, triggers, extensions, and RLS policy changes could be routed to `execute_sql`. | DDL, schema changes, indexes, functions, triggers, extensions, and RLS changes route to `apply_migration`. `execute_sql` is reserved for non-schema SQL. | `tuned_supabase_database_boundaries` moved the full Anthropic run from 6/9 to 9/9. |
| Zymtrace MCP | Tighten default-project, resource-first, metrics-first, and bounded hot-trace routing. Add the retained cases to regression coverage. | Agents could skip resource-first lookup, use `project_id: "default"`, query GPU or inference metrics before discovery, or fetch full traces before selecting a `prefix_hash`. | Use MCP resources first for `topfunctions`, `topentities`, and `flamegraph`. Use the default project UUID unless another project is named. Discover metrics before GPU or inference queries. Rank CPU traces before full trace fetches. Fetch full trace only after a selected `prefix_hash`. | `tuned_zymtrace_mcp_boundaries` moved the held-out prompt-JSON slice from 14/24 stock passes to 24/24 tuned passes. |
| Screenpipe MCP | Send literal keyword or exact phrase lookup to `keyword-search`. Reserve `search-content` for broader content search. | Exact keyword or phrase lookup could be routed to broad `search-content` instead of the dedicated literal lookup tool. | Literal terms and exact phrases route to `keyword-search`. `search-content` stays for broader content, transcript, screen text, speaker, window, tag, and memory search. | `source_tuned_screenpipe_mcp` moved Anthropic prompt JSON from 6/7 to 7/7. |
| InsForge MCP | Require an absolute `sourceDirectory`. Reject relative deploy paths before calling `create-deployment`. | A relative path such as `.` could still lead the agent to call `create-deployment`, even though deployment requires an absolute `sourceDirectory`. | `create-deployment` requires an absolute `sourceDirectory`. Relative paths, starter-template creation, status lookup, and remote prepared-deployment triggering do not call it. | `source_tuned_insforge_mcp` chose `NO_TOOL` and moved Anthropic prompt JSON from 15/16 to 16/16. |
| gstack skills | Tighten browser alias and safety-mode routing. Keep the current frontier failures as the next regression targets. | Agents could confuse browser/headless aliases or careful-mode versus other safety-mode skills. | Clarify browser/headless aliases and safety or careful-mode skill boundaries before the agent selects a skill. | `gstack_boundary_tuned_skill_descriptions` scored 0.992, with current frontier receipts retained as descent evidence. |
| Humwork MCP | No wording change promoted from this slice. | The retained MCP surface already passed every tested tool-selection case. | No tool or wording change is promoted. Keep current behavior and retain the cases as regression coverage. | `skill_tuned_humwork_mcp` also passed 7/7. Guardrail only. |
| OpenWork UI MCP | No wording change promoted from this slice. | The retained MCP surface already passed every tested tool-selection case. | No tool or wording change is promoted. Keep current behavior and retain the cases as regression coverage. | `source_tuned_openwork_ui_mcp` also passed 7/7. Guardrail only. |

## Promotion Bar

A change is promoted only when it clears the repo bar:

- same task, same provider or harness cell, baseline versus candidate
- live model call, not only static review
- realistic prompt with a verifiable outcome
- no verifier trick, brittle exact-match dependency, or held-out regression
- value maps to a practical failure avoided before execution

## Cross-Target Lessons

What is working:

- Most mature public MCP catalogs passed the current slices outright. GitHub, Playwright, Slack,
  Filesystem, Postgres MCP Pro, Context7, and ClickHouse are useful guardrails, not current
  description rewrites.
- gstack also looks strong. The original full run passed 708 of 720 live cells with zero errors, and
  the current available-frontier stress receipt completed 496 cells with 484 passed, 8 failed, and 4
  errors.
- The useful feedback is narrow. The wins came from adjacent-boundary confusion, not broad tool
  catalog failure.

What produced confirmed value:

- Firecrawl needed a sharper scrape-versus-extract boundary for one known URL with structured
  fields.
- Supabase needed schema-changing SQL to route to migrations, not ordinary SQL execution.
- Zymtrace needed resource-first/default-project rules, metrics-first GPU workflows, and bounded
  hot-trace drilldown arguments.
- Screenpipe needed exact keyword lookup to route to `keyword-search`, not broader content search.
- InsForge needed relative deployment paths to stop before `create-deployment`.
- gstack needed browser-alias and safety-mode routing tightened. The historical 720-cell run remains
  compatibility evidence, and the 2026-07-01 available-frontier receipt is the current
  hill-descending surface for OpenAI `gpt-5.5` and Gemini
  `gemini-3.1-pro-preview-customtools`.

How usefulness is proven:

- Each promoted suggestion compares baseline and candidate descriptions on the same realistic
  prompts, providers, harnesses, and instruction variants.
- The useful signal is a live model-call delta that changes the next tool call or required
  arguments in the ambiguous boundary case.
- Upstream-facing claims should be led by current frontier/latest model and harness results when
  those runs are available. When provider access or credits block a frontier run, retain the blocked
  attempt and label it plainly instead of implying complete coverage.
  Historical, high, balanced, or older-model cells are still useful regression coverage, but they
  should be labeled that way.
- Current available-frontier receipts across MCP matrices and gstack are indexed in
  [Frontier Stress Receipts](https://github.com/cfregly/agent-harness-opt/blob/main/docs/frontier-stress-2026-07-01.md).
- The packet includes source pins, exact cases, reproduction commands, and result artifacts so an
  upstream maintainer can rerun or challenge the claim.

Downside of ignoring confirmed suggestions:

- Plausible adjacent tools keep winning, which makes bad routing hard to notice in transcripts.
- Model and harness upgrades can reintroduce the same mistake unless the boundary is encoded as a
  regression case.
- Wrong tool choice can increase cost, choose a broader workflow than requested, skip migration
  safety, or apply safety constraints the user did not ask for.

## Finding Summaries

| Target | Finding page |
|---|---|
| gstack | [gstack finding](https://github.com/cfregly/agent-harness-opt/tree/main/docs/findings/gstack) |
| Firecrawl | [Firecrawl finding](https://github.com/cfregly/agent-harness-opt/tree/main/docs/findings/firecrawl) |
| Supabase | [Supabase finding](https://github.com/cfregly/agent-harness-opt/tree/main/docs/findings/supabase) |
| Zymtrace | [Zymtrace finding](https://github.com/cfregly/agent-harness-opt/tree/main/docs/findings/zymtrace) |
| Screenpipe | [Screenpipe finding](https://github.com/cfregly/agent-harness-opt/tree/main/docs/findings/screenpipe) |
| InsForge | [InsForge finding](https://github.com/cfregly/agent-harness-opt/tree/main/docs/findings/insforge) |
| Humwork | [Humwork finding](https://github.com/cfregly/agent-harness-opt/tree/main/docs/findings/humwork) |
| OpenWork | [OpenWork finding](https://github.com/cfregly/agent-harness-opt/tree/main/docs/findings/openwork) |

<details>
<summary>LLM / Machine-readable details</summary>

## Wins

| Target | Upstream Pin | Baseline | Candidate | Signal | Promoted Pattern |
|---|---|---|---|---|---|
| Firecrawl MCP | `firecrawl-mcp` 3.22.0, `firecrawl/firecrawl-mcp-server` commit `e744bba494c0e77086d66af838d7a64fab52f138` | `legacy_firecrawl_mcp` | `tuned_firecrawl_mcp_boundaries` | Anthropic full run moved from 11/12 to 12/12. The adversarial single-page structured-fields case failed on legacy and passed on tuned across Anthropic, OpenAI, Gemini, native tools, and prompt JSON. | [Firecrawl packet](https://github.com/cfregly/agent-harness-opt/tree/main/evals/pr_packets/firecrawl_mcp_tool_tuning_2026-06-25): for one exact URL plus specific fields, use `firecrawl_scrape` with JSON format. Reserve `firecrawl_extract` for multi-page or broader extraction jobs. |
| Supabase MCP database tools | `@supabase/mcp-server-supabase` 0.8.2, `supabase/mcp` commit `100565f26d7eec6d314a08597ded22da63045923` | `terse_supabase_database_mcp` | `tuned_supabase_database_boundaries` | Anthropic full run moved from 6/9 to 9/9. Cross-provider DDL/RLS cells moved failing native and prompt-JSON cells to 3/3, with no regression in the OpenAI prompt-JSON cell that already passed. | [Supabase packet](https://github.com/cfregly/agent-harness-opt/tree/main/evals/pr_packets/supabase_mcp_database_tool_tuning_2026-06-25): route schema-changing SQL to `apply_migration`. Use `execute_sql` only for regular non-schema SQL. |
| Zymtrace MCP | `zymtrace-mcp` 26.6.1 endpoint inspection, Zymtrace skills plugin 26.6.0, local GPU-enabled profiler verification on 2026-06-30, and frontier stress run on 2026-07-01 | `stock_zymtrace_mcp` + `zymtrace_host_and_skill_rules` | `tuned_zymtrace_mcp_boundaries` + `zymtrace_host_and_skill_rules` | Expanded held-out prompt-JSON run moved from 4/8 to 8/8 on Anthropic, 5/8 to 8/8 on OpenAI, and 5/8 to 8/8 on Gemini. Stock missed default project UUIDs, metric-discovery arguments, bounded full-trace drilldown arguments, and one resource fallback. Tuned passed all held-out tool/skill boundary cases. The current frontier stress receipt on OpenAI `gpt-5.5` and Gemini `gemini-3.1-pro-preview-customtools` completed 272 cells with 233 passed, 27 failed, and 12 errors. Anthropic Opus was retried on accessible `claude-opus-4-8` and completed 136 cells with 118 passed, 18 failed, and 0 errors. | [Zymtrace packet](https://github.com/cfregly/agent-harness-opt/tree/main/evals/pr_packets/zymtrace_mcp_tool_tuning_2026-06-30): prefer resource-first fallbacks, default project `00000000-0000-0000-0000-000000000000`, metrics-first GPU/inference workflows, rank-first CPU workflows, and bounded `hot_traces` drilldown with `prefix_hash`, `meta_only=false`, and `limit=1`. Frontier stress receipt: [2026-07-01](https://github.com/cfregly/agent-harness-opt/blob/main/evals/results/zymtrace_mcp_frontier_available_matrix_live_2026-07-01.md). |
| gstack skills | `gstack` 0.13.3.0, `garrytan/gstack` commit `cd66fc2f890982351e3178925be563681d0ab2c5`, generated skill surface hash `68d60eeefdde254818b03ee310bf1c4c9aaf0efee8d6db35141fe9cb7da8ae12` | `gstack_stock_skill_descriptions` | `gstack_boundary_tuned_skill_descriptions` | Original full run moved from 0.975 to 0.992 across 720 live cells. The current available-frontier stress receipt on OpenAI `gpt-5.5` and Gemini `gemini-3.1-pro-preview-customtools` completed 496 cells with 484 passed, 8 failed, and 4 errors. Anthropic Opus skill-routing coverage remains a separate provider-state blocker with 248 `provider_blocked` cells and 0 model-quality errors after billing-lockout classification. | [gstack finding](https://github.com/cfregly/agent-harness-opt/tree/main/docs/findings/gstack): tighten browser alias and safety-mode skill boundaries. Frontier stress receipt: [2026-07-01](https://github.com/cfregly/agent-harness-opt/blob/main/evals/results/gstack_skill_matrix_frontier_available_live_2026-07-01.md). |
| Screenpipe MCP | `screenpipe-mcp` 0.18.14, `screenpipe/screenpipe` commit `2de07ff501a63d3d3f0f39a9a602640a833d151f` | `readme_screenpipe_mcp` | `source_tuned_screenpipe_mcp` | Anthropic prompt-JSON run moved from 6/7 to 7/7. README-level descriptions routed exact keyword lookup to `search-content`. Source-level tuned descriptions routed it to `keyword-search`. | [Screenpipe packet](https://github.com/cfregly/agent-harness-opt/tree/main/evals/pr_packets/screenpipe_mcp_tool_tuning_2026-06-28): route literal keyword or exact phrase lookup to `keyword-search`. Reserve `search-content` for broader content search. |
| InsForge MCP | `@insforge/mcp` 1.2.10, `InsForge/insforge-mcp` commit `dad794d445d05e7df2efcb8280dba59682b97a87` | `readme_insforge_mcp` | `source_tuned_insforge_mcp` | Anthropic prompt-JSON run moved from 15/16 to 16/16. README-level descriptions routed a relative source-directory deployment request to `create-deployment`. Source-level tuned descriptions routed it to `NO_TOOL`. | [InsForge packet](https://github.com/cfregly/agent-harness-opt/tree/main/evals/pr_packets/insforge_mcp_tool_tuning_2026-06-28): require an absolute `sourceDirectory` before calling `create-deployment`. Reject relative deploy paths before tool call. |

## Guardrails Without Promotion

| Target | Upstream Pin | Result | Why Not Promoted |
|---|---|---|---|
| ClickHouse MCP | `mcp-clickhouse` 0.4.0, `clickhouse/mcp-clickhouse` commit `ccef141dbd4e482111c8b8803962339b1f3bf1d7` | Stock and tuned both passed 42/42 across Anthropic, OpenAI, and Gemini prompt-JSON cells. Mutation prompts correctly returned `NO_TOOL` for the read-only visible catalog. | No baseline delta. Keep the matrix as a safety and regression guardrail. |
| Context7 MCP | `@upstash/context7` 1.0.0, `upstash/context7` commit `a914a8693488f1a7b37581de176ad1f19def8e64` | README-style and tuned descriptions both passed the tested library-resolution boundary. | No baseline delta. |
| GitHub MCP Server | `github/github-mcp-server` commit `9430064a2becb382644042ce9fe5752ace1d8409` | Stock and tuned variants both passed the tested repository, issue, pull request, and Actions cases. | No baseline delta. |
| Playwright MCP | `microsoft/playwright-mcp` commit `511320db60d6774557243a32b2ff201f14ca4188` | Stock and tuned variants both passed after an unfair verifier was corrected. | The apparent miss was verifier quality, not tool wording. |
| Postgres MCP Pro | `crystaldba/postgres-mcp` public docs and repo reference checked from the matrix source | Stock and tuned variants both passed the tested schema, SQL, explain, workload, index, and health cases. | No baseline delta. |
| Slack MCP | Slack official MCP docs and Docker MCP reference checked from the matrix source | Stock and tuned variants both passed the tested channel, thread, message, reaction, and user cases. | No baseline delta. |
| Filesystem MCP | Model Context Protocol filesystem registry and Docker MCP reference checked from the matrix source | Stock and tuned variants both passed after an isolated rerun. | The apparent miss was transient, not a stable description gap. |
| Humwork MCP | `humwork-mcp` 1.1.1, `humworkai/humwork-mcp` commit `278bc96500d6b04a780fcf5ca04d190ab6adb85b` | README-level and skill-tuned variants both passed 7/7 on Anthropic prompt JSON. | No baseline delta. Keep the [Humwork guardrail packet](https://github.com/cfregly/agent-harness-opt/tree/main/evals/pr_packets/humwork_mcp_guardrail_2026-06-28) as retained evidence. |
| OpenWork UI MCP | `openwork-ui-mcp` 0.1.0, `different-ai/openwork` commit `3c06ab620f8f867b0cf08e88617131bcfe24fa53` | Docs-level and source-tuned variants both passed 7/7 on Anthropic prompt JSON. | No baseline delta. Keep the [OpenWork guardrail packet](https://github.com/cfregly/agent-harness-opt/tree/main/evals/pr_packets/openwork_ui_mcp_guardrail_2026-06-28) as retained evidence. |

## How The Signals Were Found

The repo uses matrix files under `evals/model_matrix/`. Each matrix defines:

- provider profiles
- harnesses such as native tools or prompt JSON
- baseline and candidate tool-description variants
- realistic cases with expected tools and confusable alternatives
- optional argument checks that avoid overfitting valid alternatives

The useful signal is a live baseline-to-candidate delta. Firecrawl, Supabase, Zymtrace, and
Screenpipe and InsForge changed the next tool call or required arguments in exactly the ambiguous
boundary case. ClickHouse, Context7, GitHub, Playwright, Postgres, Slack, Filesystem, Humwork, and
OpenWork did not show that delta, so their matrices stay as regression coverage.

## Skill Pin

The project-local agent audit skill lives at `.claude/skills/agent-audit/SKILL.md`. It is versioned
with this repository rather than an external package. The skill-selection matrix is
`evals/model_matrix/agent_audit_skill_selection.json`, and the current public pin before this ledger
was repo commit `f307a8684222e88420b6dc538d77d311af388d02`.

This ledger is intentionally redundant with the retained finding folders and PR packets. The
machine-readable source of truth for each promoted or guardrail packet remains the linked matrix,
result receipt, reproduction document, and `evidence.json` bundle.

The public gates that protect this ledger include `scripts/check_public_links.py`,
`scripts/check_docs_navigation.py`, `scripts/check_finding_packets.py`, and
`scripts/check_human_docs.py`.

</details>
