# Repeatable Harness Lab

This repo is a lab for tuning agent harnesses, not only tool descriptions. A harness can be a
provider native tool API, a prompt JSON wrapper, an Agent SDK loop, an IDE agent, or a hosted MCP
workflow. The useful artifact is a trace that shows visible decision notes, tool calls, tool
outputs, and final answers.

The promotion bar is still adversarially-confirmed to add value. A candidate change needs a
baseline, metric, minimum improvement, and adversarial check before it should be kept.

## Import A Run

Export the raw run from the harness, then normalize it:

```bash
python -m claude_agent_harness_optimization import-run path/to/run.json \
  --adapter cursor \
  --out-dir /tmp/imported-run
```

Supported adapter names include:

- `claude_messages`
- `cursor`
- `openai_agents`
- `agent_sdk`
- `langgraph`
- `langsmith`
- `runtime_events`

The importer writes:

- a normalized `*.trace.json`
- an `agent_audit_bundle.json`

If the raw export or a separate file includes `value_bar`, the bundle keeps it. The importer does
not invent a passing value proof.

## Audit The Run

Run deterministic checks first:

```bash
python -m claude_agent_harness_optimization review-trace /tmp/imported-run/*.trace.json
python -m claude_agent_harness_optimization audit-agent /tmp/imported-run/agent_audit_bundle.json
python -m claude_agent_harness_optimization optimize-tools /tmp/imported-run/agent_audit_bundle.json
```

For a real audit, call Claude:

```bash
python -m claude_agent_harness_optimization audit-agent /tmp/imported-run/agent_audit_bundle.json --claude-judge
```

The judge can review visible reasoning summaries, provider reasoning blocks when exposed, tool
calls, tool outputs, and final grounding. It does not claim hidden chain-of-thought access.

## Pin The Tested Surface

Snapshot the exact files and tool catalogs under test:

```bash
python -m claude_agent_harness_optimization snapshot-surface \
  --matrix evals/model_matrix/harness_trace_adapters.json \
  --bundle /tmp/imported-run/agent_audit_bundle.json \
  --skill .claude/skills/agent-audit/SKILL.md \
  --out /tmp/surface-snapshot.json
```

The snapshot records content hashes for matrices, tool variants, tool schemas, instruction
variants, skills, and files. Use it when reporting which version of an MCP server, skill, or
`CLAUDE.md` style instruction was evaluated.

## Add The Harness To A Matrix

Once an adapter emits the trace contract, add it as a named harness through the `trace_fixture`
provider:

```bash
python -m claude_agent_harness_optimization model-matrix evals/model_matrix/harness_trace_adapters.json \
  --live \
  --require-live \
  --providers trace_fixture \
  --harnesses agent_sdk_trace,cursor_trace \
  --variants exported_trace_tools \
  --instruction-variants exported_trace \
  --markdown
```

This checks whether the exported harness chose the expected tool and passed the expected arguments.
For provider APIs, run the same matrix with `.env` and `--live`.

## Check Credentialed Services

Use `mcp-e2e` for read-oriented service checks:

```bash
python -m claude_agent_harness_optimization mcp-e2e evals/e2e/github_readonly.json --env-file .env
python -m claude_agent_harness_optimization mcp-e2e evals/e2e/firecrawl_readonly.json --env-file .env
python -m claude_agent_harness_optimization mcp-e2e evals/e2e/cloudflare_readonly.json --env-file .env
python -m claude_agent_harness_optimization mcp-e2e evals/e2e/cloudflare_r2_readonly.json --env-file .env
python -m claude_agent_harness_optimization mcp-e2e evals/e2e/clickhouse_cloud_readonly.json --env-file .env
python -m claude_agent_harness_optimization mcp-e2e evals/e2e/stripe_readonly.json --env-file .env
```

CI runs these specs with `--dry-run`, so it validates shape without needing secrets. Local runs use
keys from `.env`. Specs should stay read-only unless the task explicitly requires a mutation.

## Report Results

Write a JSON result first:

```bash
python -m claude_agent_harness_optimization model-matrix evals/model_matrix/harness_trace_adapters.json \
  --providers trace_fixture \
  --harnesses agent_sdk_trace \
  --max-cases 1 \
  --out /tmp/harness-matrix.json
```

Then render review artifacts:

```bash
python -m claude_agent_harness_optimization render-report /tmp/harness-matrix.json --out /tmp/harness-matrix.html
python -m claude_agent_harness_optimization pr-comment /tmp/harness-matrix.json --out /tmp/harness-matrix.md
```

Use the HTML report for local review. Use the PR comment output when another agent opens a pull
request with new matrix results or tool-description changes.

## What To Optimize

Optimize the smallest surface that explains the failure:

- tool description
- tool schema
- provider native tool schema
- prompt JSON wrapper
- Agent SDK loop rule
- IDE harness instruction
- `CLAUDE.md` style rule
- skill instruction
- trace capture

Run `grind-harness` only after the baseline failure is repeated and visible:

```bash
python -m claude_agent_harness_optimization grind-harness evals/model_matrix/coding_tool_selection.json \
  --env-file .env \
  --live \
  --require-live \
  --heldout-cases "find python files,read known file" \
  --min-improvement 0.05 \
  --markdown
```

Keep the candidate only when it clears the configured improvement threshold and held-out checks.
