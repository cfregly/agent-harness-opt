# GitHub MCP Tool Tuning

This audit uses GitHub's official MCP Server as the public tool catalog under test. It is a common
target because it exposes repository content, code search, issues, pull requests, Actions, and
security workflows to MCP-compatible hosts.

Sources used for the first matrix:

- `https://github.com/github/github-mcp-server`
- `https://github.blog/ai-and-ml/generative-ai/a-practical-guide-on-how-to-use-the-github-mcp-server/`
- cloned source commit `9430064a2becb382644042ce9fe5752ace1d8409`
- generated tool snapshots under `pkg/github/__toolsnaps__`

## Tool Surface Tested

The matrix covers a compact, high-traffic developer workflow subset:

- `get_file_contents`
- `search_code`
- `search_issues`
- `issue_read`
- `create_issue`
- `add_issue_comment`
- `list_pull_requests`
- `search_pull_requests`
- `pull_request_read`
- `create_pull_request`
- `actions_get`
- `get_job_logs`

The matrix lives at:

```text
evals/model_matrix/github_mcp_tool_selection.json
```

It compares:

- `stock_github_mcp`: public snapshot descriptions and schemas
- `tuned_github_mcp_boundaries`: the same tool names and schemas with explicit `use_when`,
  `avoid_when`, and quality checks

## Live Result

Commands run:

```bash
python -m claude_agent_harness_optimization model-matrix evals/model_matrix/github_mcp_tool_selection.json \
  --env-file .env \
  --live \
  --require-live \
  --providers anthropic \
  --harnesses prompt_json,native_tools \
  --variants stock_github_mcp,tuned_github_mcp_boundaries \
  --instruction-variants github_mcp_host_rules \
  --markdown
```

```bash
python -m claude_agent_harness_optimization model-matrix evals/model_matrix/github_mcp_tool_selection.json \
  --env-file .env \
  --live \
  --require-live \
  --providers openai,gemini \
  --harnesses prompt_json,native_tools \
  --variants stock_github_mcp,tuned_github_mcp_boundaries \
  --instruction-variants github_mcp_host_rules \
  --concurrency 4 \
  --markdown
```

Observed result:

- Anthropic prompt-JSON: stock 12/12, tuned 12/12
- Anthropic native tools: stock 12/12, tuned 12/12
- OpenAI prompt-JSON: stock 12/12, tuned 12/12
- OpenAI native tools: stock 12/12, tuned 12/12
- Gemini prompt-JSON: stock 12/12, tuned 12/12
- Gemini native tools: stock 12/12, tuned 12/12

The tuned descriptions did not beat the stock descriptions on this slice. Under the repo's
adversarially-confirmed value bar, that means the tuned variant is not promoted as an improvement.
The official descriptions already route well for these basic repository, issue, PR, and Actions
tasks.

## Verifier Fix

The first run produced one apparent stock failure on `search_issues`. The selected tool was correct,
but the verifier required separate `owner` and `repo` arguments. The model instead used a valid
GitHub search query:

```text
repo:github/github-mcp-server fetch file contents
```

That is a valid alternate strategy, so the verifier was too strict. The case now checks the expected
tool and the `query` term only. This is a useful failure: evals should detect wrong tool choice, not
reject correct calls because of harmless argument-shape variation.

## Current Recommendation

Do not rewrite the GitHub MCP descriptions based on this first matrix. Keep the matrix as a
regression baseline and add harder held-out cases before proposing a catalog change.

The next useful cases should stress boundaries that are not covered yet:

- issue comments versus pull request review comments
- `actions_get` log URL versus `get_job_logs` actual content
- `list_pull_requests` simple filters versus `search_pull_requests` query filters
- `get_file_contents` known path versus `search_code` unknown path
- read-only mode, excluded tools, and minimal enabled toolsets
- large-catalog behavior when additional GitHub MCP toolsets are enabled

If repeated failures appear in those harder cases, use `grind-harness` to generate a candidate
description variant and promote it only if it improves the baseline without held-out regressions.
