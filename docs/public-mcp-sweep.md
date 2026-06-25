# Public MCP Sweep

This sweep tests popular public MCP tool catalogs against the repo's
adversarially-confirmed to add value bar. A tuned description is not promoted just because it sounds
better. It has to beat the baseline on live model calls without introducing verifier tricks or
regressions.

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

## What Cleared

GitHub, Playwright, Slack, Filesystem, and Postgres MCP Pro did not produce a confirmed tuning win
on the current slices. Their stock descriptions either passed outright or the apparent miss was an
unfair verifier/transient issue.

Firecrawl produced a confirmed improvement:

- Legacy description: single known URL plus structured fields chose `firecrawl_extract`.
- Tuned description: the same task chose `firecrawl_scrape`.
- Rationale: current Firecrawl guidance says one known page with specific fields should use
  `firecrawl_scrape` with a focused JSON format. `firecrawl_extract` is better for multi-page or
  broader structured extraction jobs.

This is the useful pattern: do not broadly rewrite a tool catalog. Identify one ambiguous boundary,
write a realistic prompt that isolates it, and prove the tuned wording changes the next tool call.

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

## Commands

Dry contract checks:

```bash
python -m claude_agent_harness_optimization model-matrix evals/model_matrix/firecrawl_mcp_tool_selection.json \
  --providers anthropic \
  --harnesses prompt_json \
  --variants legacy_firecrawl_mcp,tuned_firecrawl_mcp_boundaries \
  --instruction-variants firecrawl_host_rules \
  --max-cases 2 \
  --markdown
```

Live full Anthropic check:

```bash
python -m claude_agent_harness_optimization model-matrix evals/model_matrix/firecrawl_mcp_tool_selection.json \
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
python -m claude_agent_harness_optimization model-matrix evals/model_matrix/firecrawl_mcp_tool_selection.json \
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
