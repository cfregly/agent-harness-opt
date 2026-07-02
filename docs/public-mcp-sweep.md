# Public MCP Sweep

This sweep tests popular public MCP tool catalogs against the repo's
adversarially-confirmed to add value bar. A tuned description is not promoted just because it sounds
better. It has to beat the baseline on live model calls without introducing verifier tricks or
regressions.

> [!NOTE]
> This page starts with the human summary. Detailed eval, command, and machine-readable material is preserved below.

## Summary

| Target | Exact change | Before | After | Result |
|---|---|---|---|---|
| Firecrawl MCP | Use `firecrawl_scrape` for one known page with specific fields. Reserve `firecrawl_extract` for broader extraction. | `legacy_firecrawl_mcp` chose `firecrawl_extract` for one known URL plus structured fields. | The single-page request routes to `firecrawl_scrape`. | `tuned_firecrawl_mcp_boundaries` chose the intended tool. |
| Supabase MCP | Route schema-changing SQL to `apply_migration`. Keep `execute_sql` for ordinary SQL. | `terse_supabase_database_mcp` chose `execute_sql` for DDL and RLS changes. | Schema-changing SQL routes to `apply_migration`. | `tuned_supabase_database_boundaries` chose the intended tool. |
| Zymtrace MCP | Tighten default-project, resource-first, metrics-first, and bounded hot-trace routing. | `stock_zymtrace_mcp` missed default-project and bounded-drilldown arguments. | Agents see explicit defaults, resource fallbacks, metrics-first GPU flow, and bounded trace drilldown. | `tuned_zymtrace_mcp_boundaries` passed all retained held-out routing cases. |
| Screenpipe MCP | Route literal keyword or exact phrase lookup to `keyword-search`. | `readme_screenpipe_mcp` sent exact keyword lookup to `search-content`. | Exact keyword lookup routes to `keyword-search`. | `source_tuned_screenpipe_mcp` chose the intended tool. |
| InsForge MCP | Require absolute deployment paths before calling `create-deployment`. | `readme_insforge_mcp` called `create-deployment` for a relative source path. | Relative source paths are rejected before tool execution. | `source_tuned_insforge_mcp` chose `NO_TOOL`. |
| Humwork MCP | No wording change promoted from this slice. | README-level descriptions passed 7/7. | Keep current wording and retain the cases. | Skill-tuned descriptions also passed 7/7. Guardrail only. |
| OpenWork UI MCP | No wording change promoted from this slice. | Docs-level descriptions passed 7/7. | Keep current wording and retain the cases. | Source-tuned descriptions also passed 7/7. Guardrail only. |
| GitHub, Playwright, Slack, Filesystem, Postgres MCP Pro, Context7, ClickHouse | No wording change promoted from this slice. | Stock descriptions passed or the apparent miss was a verifier/transient issue. | Keep current wording and retain useful cases. | Tuned descriptions did not produce a confirmed baseline delta. |

## Targets Tested

The current sweep covers:

- GitHub MCP Server: repository content, code search, issues, pull requests, and Actions.
- Playwright MCP: browser navigation, snapshots, clicks, typing, screenshots, network, and console.
- Slack MCP: channels, posting, threads, history, reactions, users, and profiles.
- Filesystem MCP: read, multi-read, write, edit, list, tree, search, metadata, move, and roots.
- Postgres MCP Pro: schema discovery, object details, SQL execution, explain plans, workload
  tuning, query-specific index tuning, and health checks.
- Firecrawl MCP: scrape, batch scrape, map, search, crawl, extract, agent, interact, monitor, and
  status polling.
- Context7 MCP: library ID resolution and documentation queries.
- Supabase MCP: database metadata, migrations, SQL execution, extensions, and schema changes.
- ClickHouse MCP: database listing, table metadata, and read-only SELECT queries.
- Zymtrace MCP: MCP resources, project discovery, time-window normalization, top
  functions/entities, hot traces, flamegraphs, metrics discovery/query, recommendations, raw project
  event/stat APIs, and CPU/GPU optimization skill routing.
- Screenpipe MCP: local screen/audio search, UI element lookup, frame context, meetings, memories,
  and scheduled pipes.
- InsForge MCP: backend metadata, table schema, raw SQL, starter templates, bulk import, storage
  buckets, edge functions, deployments, logs, docs, and anon-token generation.
- Humwork MCP: expert consultation start, active chat lifecycle, closure, rating, and no-tool
  safety.
- OpenWork UI MCP: desktop bridge status, UI snapshot, available semantic actions, action execution,
  and no-tool boundaries.

Founder-facing packets live under
[Founder Findings](https://github.com/cfregly/claude-agent-harness-opt/tree/main/docs/findings).
Use those links when sending a result to a startup.

## What Cleared

GitHub, Playwright, Slack, Filesystem, Postgres MCP Pro, Context7, and ClickHouse did
not produce a confirmed tuning win on the current slices. Their stock descriptions either passed
outright or the apparent miss was an unfair verifier/transient issue.

Firecrawl produced a confirmed improvement:

- Legacy description: single known URL plus structured fields chose `firecrawl_extract`.
- Tuned description: the same task chose `firecrawl_scrape`.
- Rationale: current Firecrawl guidance says one known page with specific fields should use
  `firecrawl_scrape` with a focused JSON format. `firecrawl_extract` is better for multi-page or
  broader structured extraction jobs.
- Packet: [Firecrawl finding](https://github.com/cfregly/claude-agent-harness-opt/tree/main/docs/findings/firecrawl).

Supabase produced a confirmed improvement:

- Terse description: schema-changing SQL chose `execute_sql`.
- Tuned description: the same DDL and RLS policy tasks chose `apply_migration`.
- Rationale: Supabase schema changes should be tracked as migrations. `execute_sql` is for regular
  SQL that does not change schema.
- Packet: [Supabase finding](https://github.com/cfregly/claude-agent-harness-opt/tree/main/docs/findings/supabase).

Zymtrace produced a confirmed improvement:

- Stock descriptions with the Zymtrace skill rules chose the right tools for the held-out cases but
  missed required default-project and bounded-drilldown arguments.
- Tuned descriptions passed the same held-out default-project, GPU metrics-first, CPU rank-first,
  GPU call-tree, and selected-trace drilldown cases across Anthropic, OpenAI, and Gemini prompt JSON.
- Rationale: the live Zymtrace MCP server has resource-first/default-project rules, and the
  installed CPU/GPU skills add workflow constraints that must be present in the tool surface.
- Packet: [Zymtrace finding](https://github.com/cfregly/claude-agent-harness-opt/tree/main/docs/findings/zymtrace).

Screenpipe produced a confirmed improvement:

- README-level description: exact keyword lookup chose `search-content`.
- Source-level tuned description: the same task chose `keyword-search`.
- Rationale: Screenpipe has a dedicated keyword search tool for literal terms and exact phrases.
  Broader content search remains useful for transcript lines, screen text, speakers, windows, tags,
  and memories.
- Packet: [Screenpipe finding](https://github.com/cfregly/claude-agent-harness-opt/tree/main/docs/findings/screenpipe).

InsForge produced a confirmed improvement:

- README-level description: a relative source-directory deployment request chose
  `create-deployment`.
- Source-level tuned description: the same task chose `NO_TOOL`.
- Rationale: InsForge deployment requires an absolute `sourceDirectory`. Relative paths should be
  rejected before the deployment tool is called.
- Packet: [InsForge finding](https://github.com/cfregly/claude-agent-harness-opt/tree/main/docs/findings/insforge).

Humwork and OpenWork did not produce a confirmed tuning win on the current Anthropic slices. Their
public descriptions already routed the tested expert-consultation and UI-control cases correctly.
Packets: [Humwork guardrail](https://github.com/cfregly/claude-agent-harness-opt/tree/main/docs/findings/humwork)
and [OpenWork guardrail](https://github.com/cfregly/claude-agent-harness-opt/tree/main/docs/findings/openwork).

This is the useful pattern: do not broadly rewrite a tool catalog. Identify one ambiguous boundary,
write a realistic prompt that isolates it, and prove the tuned wording changes the next tool call.

The pinned improvement ledger lives in
[Confirmed Improvements](https://github.com/cfregly/claude-agent-harness-opt/blob/main/docs/confirmed-improvements.md).
Use that page when you need the exact upstream MCP version or commit attached to each result.

<details>
<summary>LLM / Machine-readable details</summary>

## Live Results

Firecrawl full Anthropic prompt-JSON run:

- `legacy_firecrawl_mcp`: 11/12
- `tuned_firecrawl_mcp_boundaries`: 12/12

Firecrawl adversarial single-case run across provider and harness cells:

- Anthropic native tools: legacy failed, tuned passed.
- Anthropic prompt JSON: legacy failed, tuned passed.
- OpenAI native tools: legacy failed, tuned passed.
- OpenAI prompt JSON: legacy failed, tuned passed.
- Gemini native tools: legacy failed, tuned passed.
- Gemini prompt JSON: legacy failed, tuned passed.

The current Firecrawl MCP server already contains much of this boundary guidance. Treat the matrix
as a regression and migration test for older/terse descriptions, not as a claim that the current
server is broken.

Supabase adversarial DDL run:

- Anthropic native tools: terse 0/3, tuned 3/3.
- Anthropic prompt JSON: terse 0/3, tuned 3/3.
- OpenAI native tools: terse 1/3, tuned 3/3.
- OpenAI prompt JSON: terse 3/3, tuned 3/3.
- Gemini native tools: terse 0/3, tuned 3/3.
- Gemini prompt JSON: terse 0/3, tuned 3/3.

Zymtrace held-out tool/skill boundary run:

- Anthropic prompt JSON: stock 2/5, tuned 5/5.
- OpenAI prompt JSON: stock 2/5, tuned 5/5.
- Gemini prompt JSON: stock 2/5, tuned 5/5.
- The stock failures were default project UUIDs on project metrics calls and missing
  `meta_only=false` on selected full-trace drilldown. Tuned descriptions passed all held-out cells.

Screenpipe YC S26 local-activity run:

- Anthropic prompt JSON: README-level 6/7, source-level tuned 7/7.
- The tested slice covered broad activity recap, exact keyword lookup, speaker transcript search, UI
  element lookup, known frame context, pipe creation, and pipe log verification.
- The README-level miss chose `search-content` for exact keyword lookup. The source-level tuned
  variant chose `keyword-search`.
- Receipt: `evals/results/screenpipe_mcp_tool_selection_2026-06-28.md`.

YC P2026 MCP run:

- InsForge Anthropic prompt JSON: README-level 15/16, source-level tuned 16/16.
- Humwork Anthropic prompt JSON: README-level 7/7, skill-tuned 7/7.
- OpenWork Anthropic prompt JSON: docs-level 7/7, source-level tuned 7/7.
- InsForge produced the confirmed delta. Humwork and OpenWork remain guardrails without promotion.
- Receipts: `evals/results/insforge_mcp_tool_selection_2026-06-28.md`,
  `evals/results/humwork_mcp_tool_selection_2026-06-28.md`, and
  `evals/results/openwork_ui_mcp_tool_selection_2026-06-28.md`.

Additional guardrail slices were added for the partial check families on 2026-06-25. These are
not promoted as new upstream improvements by themselves. They are live tuned-variant regression
cases for error recovery, output budget, resource or metadata-first routing, and no-tool safety.

- Firecrawl Anthropic prompt JSON tuned variant: 3/3. Cases cover concise JSON scrape, JavaScript
  scrape error recovery to `firecrawl_interact`, and URL index discovery with `firecrawl_map`.
- Supabase Anthropic prompt JSON tuned variant: 3/3. Cases cover unknown relation recovery to
  `list_tables`, concise non-verbose table inventory, and metadata before `SELECT *`.
- ClickHouse Anthropic prompt JSON tuned variant: 3/3. Cases cover unknown table recovery to
  `list_tables`, exploratory `LIMIT 5`, and metadata before analytical SQL.
- GitHub Anthropic prompt JSON tuned variant: 4/4. Cases cover 404 path recovery to `search_code`,
  `perPage=5` pull request listing, workflow metadata via `actions_get`, and destructive repository
  deletion as `NO_TOOL`.
- Zymtrace Anthropic prompt JSON tuned variant with skill rules: 3/3. Cases cover full-trace error
  recovery to metadata discovery, bounded `hot_traces`, and fallback `topfunctions` in the tool-only
  resource matrix.
- Context7 Anthropic prompt JSON tuned variant: 3/3. Cases cover invalid ID recovery to
  `resolve-library-id`, focused exact-ID docs query, and selected ID bypassing the resolver.

ClickHouse adds a safety-oriented prompt-JSON matrix:

- Standard read-only tasks route to `list_databases`, `list_tables`, or `run_select_query`.
- Mutation tasks route to `NO_TOOL` because the visible official catalog is read-only.
- Live Anthropic, OpenAI, and Gemini prompt-JSON cells passed 42/42 across stock and tuned
  descriptions. That means no tuned ClickHouse wording is promoted yet.
- This is not yet a credentialed database execution result. The ClickHouse Cloud API key proves
  control-plane access. End-to-end MCP query traces also need database host/user/password.

Zymtrace adds a profiling-analysis matrix against an inspected `zymtrace-mcp` 26.6.1 surface and
the installed Zymtrace optimization skills:

- The live MCP endpoint advertises 25 tools.
- The live MCP endpoint advertises 3 resources: `topfunctions`, `topentities`, and `flamegraph`.
- The rerun found a real tuning miss in the first Zymtrace matrix: the live server says to prefer
  resources before same-named tools, use default project
  `00000000-0000-0000-0000-000000000000` unless the user explicitly asks for another project, and
  reserve `projects_search` for project listing/search/switching.
- The installed Zymtrace CPU/GPU skills add workflow boundaries: CPU rank-first requests start with
  `topentities` or `topfunctions`. GPU and inference investigations start with metric discovery.
  Call-tree analysis prefers first-pass `hot_traces` with `meta_only=true`. Full trace drilldown
  requires a selected `prefix_hash`, `meta_only=false`, and `limit=1`.
- The tuned variant now encodes those boundaries plus metrics discovery before metrics query,
  high-level versus project JSON flamegraphs, recommendations, and raw event APIs only when
  explicitly requested.
- The inspected profiler is CPU/eBPF-ready. GPU profiling is not treated as available until the
  Zymtrace license reports GPU support.
- The 2026-06-30 rerun enabled the commercial Zymtrace license in the local Docker Compose install.
  The profiler changed from `SupportsGpu:false` to `SupportsGpu:true`, detected an NVIDIA B200, and
  exported hardware GPU metrics through the MCP.
- The expanded held-out live run promoted the tuned Zymtrace wording as a confirmed provider win:
  stock passed 14/24 cells, while tuned passed 24/24 across Anthropic, OpenAI, and Gemini prompt
  JSON cells. Evidence lives in
  `evals/results/zymtrace_mcp_matrix_live_2026-06-30.json` and
  `evals/pr_packets/zymtrace_mcp_tool_tuning_2026-06-30/`.
- Additional live findings are captured in `docs/findings/zymtrace/README.md`: unfiltered
  `hot_traces` can rank idle first, `topentities` can expose `zymtrace-profiler` as self-noise, and
  GPU readiness would benefit from a single MCP status path.

## Commands

Dry contract checks:

```bash
python -m claude_agent_harness_opt model-matrix evals/model_matrix/firecrawl_mcp_tool_selection.json \
  --providers anthropic \
  --harnesses prompt_json \
  --variants legacy_firecrawl_mcp,tuned_firecrawl_mcp_boundaries \
  --instruction-variants firecrawl_host_rules \
  --max-cases 2 \
  --markdown
```

Live Supabase DDL boundary check:

```bash
python -m claude_agent_harness_opt model-matrix evals/model_matrix/supabase_mcp_database_tool_selection.json \
  --env-file .env \
  --live \
  --require-live \
  --providers anthropic,openai,gemini \
  --harnesses prompt_json,native_tools \
  --variants terse_supabase_database_mcp,tuned_supabase_database_boundaries \
  --instruction-variants supabase_database_host_rules \
  --cases "ddl create table uses migration,ddl create index uses migration,rls policy uses migration" \
  --concurrency 3 \
  --markdown
```

Live ClickHouse read-only boundary check:

```bash
python -m claude_agent_harness_opt model-matrix evals/model_matrix/clickhouse_mcp_tool_selection.json \
  --env-file .env \
  --live \
  --require-live \
  --providers anthropic,openai,gemini \
  --harnesses prompt_json \
  --variants stock_clickhouse_mcp,tuned_clickhouse_readonly_boundaries \
  --instruction-variants clickhouse_host_rules \
  --concurrency 3 \
  --markdown
```

Dry Zymtrace boundary check:

```bash
python -m claude_agent_harness_opt model-matrix evals/model_matrix/zymtrace_mcp_tool_selection.json \
  --providers anthropic \
  --harnesses prompt_json \
  --variants tuned_zymtrace_mcp_boundaries \
  --instruction-variants zymtrace_host_and_skill_rules \
  --max-cases 2 \
  --markdown
```

Live Screenpipe YC S26 boundary check:

```bash
make optimize mcp=screenpipe
make optimize url=https://github.com/screenpipe/screenpipe
```

Equivalent direct command:

```bash
python -m claude_agent_harness_opt model-matrix evals/model_matrix/screenpipe_mcp_tool_selection.json \
  --env-file .env \
  --live \
  --require-live \
  --providers anthropic \
  --harnesses prompt_json \
  --variants readme_screenpipe_mcp,source_tuned_screenpipe_mcp \
  --instruction-variants screenpipe_host_rules \
  --concurrency 2 \
  --markdown
```

Dry Zymtrace held-out skill boundary check:

```bash
python -m claude_agent_harness_opt model-matrix evals/model_matrix/zymtrace_mcp_tool_selection.json \
  --providers anthropic \
  --harnesses prompt_json \
  --variants tuned_zymtrace_mcp_boundaries \
  --instruction-variants zymtrace_host_and_skill_rules \
  --cases "default project metrics discovery skips search,cpu rank first containerized apps,gpu inference workflow starts with metrics,gpu call tree uses hot traces,selected trace drilldown is bounded,full trace error recovers to discovery,hot trace discovery is bounded,resource fallback hot functions" \
  --markdown
```

Live Zymtrace cross-provider boundary check:

```bash
python -m claude_agent_harness_opt model-matrix evals/model_matrix/zymtrace_mcp_tool_selection.json \
  --env-file .env \
  --live \
  --require-live \
  --providers anthropic,openai,gemini \
  --harnesses prompt_json \
  --variants stock_zymtrace_mcp,tuned_zymtrace_mcp_boundaries \
  --instruction-variants zymtrace_host_and_skill_rules \
  --cases "default project metrics discovery skips search,cpu rank first containerized apps,gpu inference workflow starts with metrics,gpu call tree uses hot traces,selected trace drilldown is bounded,full trace error recovers to discovery,hot trace discovery is bounded,resource fallback hot functions" \
  --concurrency 3 \
  --markdown
```

This baseline-versus-candidate command is expected to exit nonzero while `stock_zymtrace_mcp`
fails. Use it to confirm the delta. Use the tuned-only command as the passing merge gate:

```bash
python -m claude_agent_harness_opt model-matrix evals/model_matrix/zymtrace_mcp_tool_selection.json \
  --env-file .env \
  --live \
  --require-live \
  --providers anthropic,openai,gemini \
  --harnesses prompt_json \
  --variants tuned_zymtrace_mcp_boundaries \
  --instruction-variants zymtrace_host_and_skill_rules \
  --cases "default project metrics discovery skips search,cpu rank first containerized apps,gpu inference workflow starts with metrics,gpu call tree uses hot traces,selected trace drilldown is bounded,full trace error recovers to discovery,hot trace discovery is bounded,resource fallback hot functions" \
  --concurrency 3 \
  --markdown
```

Live full Anthropic check:

```bash
python -m claude_agent_harness_opt model-matrix evals/model_matrix/firecrawl_mcp_tool_selection.json \
  --env-file .env \
  --live \
  --require-live \
  --providers anthropic \
  --harnesses prompt_json \
  --variants legacy_firecrawl_mcp,tuned_firecrawl_mcp_boundaries \
  --instruction-variants firecrawl_host_rules \
  --markdown
```

Live cross-provider adversarial case:

```bash
python -m claude_agent_harness_opt model-matrix evals/model_matrix/firecrawl_mcp_tool_selection.json \
  --env-file .env \
  --live \
  --require-live \
  --providers anthropic,openai,gemini \
  --harnesses prompt_json,native_tools \
  --variants legacy_firecrawl_mcp,tuned_firecrawl_mcp_boundaries \
  --instruction-variants firecrawl_host_rules \
  --cases "single known page structured fields" \
  --concurrency 3 \
  --markdown
```

## Sources

- `https://github.com/firecrawl/firecrawl-mcp-server`
- cloned commit `e744bba494c0e77086d66af838d7a64fab52f138`
- `src/legacy/index.md`
- `src/index.ts`
- `README.md#how-to-choose-a-tool`
- `https://github.com/crystaldba/postgres-mcp`
- `https://github.com/microsoft/playwright-mcp`
- `https://github.com/github/github-mcp-server`
- `https://github.com/upstash/context7`
- `https://github.com/supabase/mcp`
- `https://supabase.com/docs/guides/ai-tools/mcp`
- `https://github.com/clickhouse/mcp-clickhouse`
- `https://clickhouse.com/docs/use-cases/AI/MCP`
- `https://docs.zymtrace.com/getting-started/`
- `https://docs.zymtrace.com/category/model-context-protocol-mcp/`
- `zymtrace-mcp` 26.6.1 `initialize`, `resources/list`, `tools/list`, and `get_date_time` MCP
  responses from the inspected endpoint
- Zymtrace skills plugin 26.6.0 `optimize-cpu-workloads` and `optimize-gpu-workloads`
- `https://github.com/screenpipe/screenpipe`
- `screenpipe-mcp` 0.18.14 source file `packages/screenpipe-mcp/src/index.ts`

</details>
