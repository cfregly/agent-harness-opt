# Confirmed Improvements

This ledger separates confirmed tuning wins from passing guardrails. A tool catalog can pass now and
still count as an improvement when the tuned variant beat a weaker baseline under the same eval.

Checked on 2026-06-25.

## Promotion Bar

A change is promoted only when it clears the repo bar:

- same task, same provider or harness cell, baseline versus candidate
- live model call, not only static review
- realistic prompt with a verifiable outcome
- no verifier trick, brittle exact-match dependency, or held-out regression
- value maps to a practical failure avoided before execution

## Wins

| Target | Upstream Pin | Baseline | Candidate | Signal | Promoted Pattern |
|---|---|---|---|---|---|
| Firecrawl MCP | `firecrawl-mcp` 3.22.0, `firecrawl/firecrawl-mcp-server` commit `e744bba494c0e77086d66af838d7a64fab52f138` | `legacy_firecrawl_mcp` | `tuned_firecrawl_mcp_boundaries` | Anthropic full run moved from 11/12 to 12/12. The adversarial single-page structured-fields case failed on legacy and passed on tuned across Anthropic, OpenAI, Gemini, native tools, and prompt JSON. | For one exact URL plus specific fields, use `firecrawl_scrape` with JSON format. Reserve `firecrawl_extract` for multi-page or broader extraction jobs. |
| Supabase MCP database tools | `@supabase/mcp-server-supabase` 0.8.2, `supabase/mcp` commit `100565f26d7eec6d314a08597ded22da63045923` | `terse_supabase_database_mcp` | `tuned_supabase_database_boundaries` | Anthropic full run moved from 6/9 to 9/9. Cross-provider DDL/RLS cells moved failing native and prompt-JSON cells to 3/3, with no regression in the OpenAI prompt-JSON cell that already passed. | Route schema-changing SQL to `apply_migration`. Use `execute_sql` only for regular non-schema SQL. |
| Zymtrace MCP | `zymtrace-mcp` 26.6.1 endpoint inspection and Zymtrace skills plugin 26.6.0 | `stock_zymtrace_mcp` + `zymtrace_host_and_skill_rules` | `tuned_zymtrace_mcp_boundaries` + `zymtrace_host_and_skill_rules` | Held-out prompt-JSON run moved from 2/5 to 5/5 on Anthropic, 2/5 to 5/5 on OpenAI, and 2/5 to 5/5 on Gemini. Stock missed default project UUIDs and bounded full-trace drilldown arguments. Tuned passed all held-out tool/skill boundary cases. | Prefer resource-first fallbacks, default project `00000000-0000-0000-0000-000000000000`, metrics-first GPU/inference workflows, rank-first CPU workflows, and bounded `hot_traces` drilldown with `prefix_hash`, `meta_only=false`, and `limit=1`. |

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

## How The Signals Were Found

The repo uses matrix files under `evals/model_matrix/`. Each matrix defines:

- provider profiles
- harnesses such as native tools or prompt JSON
- baseline and candidate tool-description variants
- realistic cases with expected and forbidden tools
- optional argument checks that avoid overfitting valid alternatives

The useful signal is a live baseline-to-candidate delta. Firecrawl, Supabase, and Zymtrace changed
the next tool call or required arguments in exactly the ambiguous boundary case. ClickHouse,
Context7, GitHub, Playwright, Postgres, Slack, and Filesystem did not show that delta, so their
matrices stay as regression coverage.

## Skill Pin

The project-local agent audit skill lives at `.claude/skills/agent-audit/SKILL.md`. It is versioned
with this repository rather than an external package. The skill-selection matrix is
`evals/model_matrix/agent_audit_skill_selection.json`, and the current public pin before this ledger
was repo commit `f307a8684222e88420b6dc538d77d311af388d02`.
