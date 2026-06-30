# claude-agent-harness-opt

[![ci](https://github.com/cfregly/claude-agent-harness-opt/actions/workflows/ci.yml/badge.svg)](https://github.com/cfregly/claude-agent-harness-opt/actions/workflows/ci.yml)
[![license: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/cfregly/claude-agent-harness-opt/blob/main/LICENSE)

A runnable workbench for Claude-style agent harnesses. It helps you decide whether a task deserves
an agent, render a structured system prompt, lint tool contracts, run local transcript evals, import
external agent traces, and ask Claude to judge trace quality when a live key is available.

Use it when an agent is failing for boring reasons: fuzzy tool names, broad schemas, weak stop
criteria, missing held-out cases, unclear reasoning summaries, or no baseline. The repo turns those
failure modes into repeatable checks.

The value bar is adversarially-confirmed to add value. A prompt, tool, harness, or matrix result is
promoted only when it names the value claim, compares against a baseline, clears the threshold, and
survives an adversarial check with no open objections.

## Quickstart

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e .

python -m claude_agent_harness_opt render recipes/agentic_search.json
python -m claude_agent_harness_opt score recipes/agentic_search.json
python -m claude_agent_harness_opt lint-tools recipes/agentic_search.json
python -m claude_agent_harness_opt eval evals/examples/search_answer.json
python -m claude_agent_harness_opt review-trace evals/examples/agent_trace_good.json
```

Those commands are keyless except for live Claude judging and cross-provider sweeps. For the wider
surface, start with [Setup](https://github.com/cfregly/claude-agent-harness-opt/blob/main/docs/setup.md)
and [Techniques](https://github.com/cfregly/claude-agent-harness-opt/blob/main/docs/techniques.md).

## What it implements

The kit covers four jobs:

- **Prompt and tool design:** task-fit scoring, prompt rendering, tool-description linting, tool
  budget checks, stop criteria, fallback behavior, and destructive-action guardrails.
- **Trace and eval review:** answer evals, tool-use evals, final-state evals, trace suites, audit
  bundles, and optional Claude judging over visible reasoning summaries and tool outputs.
- **Harness import and comparison:** adapters for Claude Messages, Agent SDK exports, IDE-agent
  events, live harness CLI runs, model matrices, and surface snapshots.
- **Tool-contract optimization:** baseline matrices, candidate tool-description variants, held-out
  checks, reports, and upstream PR packets that promote only measured improvements.

## Layout

```
claude_agent_harness_opt/
  prompt_builder.py  # recipe validation and system prompt rendering
  suitability.py     # agent task-fit scoring
  evals.py           # offline answer, tool-use, and final-state evals
  trace_review.py    # ordered trace review for tools and reasoning
  trace_suite.py     # regression suites for repeated trace review
  agent_audit.py     # review tools and traces in one bundle
  claude_judge.py    # optional Claude Messages API judge for semantic trace review
  model_matrix.py    # live provider matrix for tool and instruction tuning
  harness_optimizer.py # hill-climb candidate tool descriptions from matrix failures
  import_run.py       # convert external harness exports into audit bundles
  live_harness.py     # run real harness CLIs and normalize redacted trace artifacts
  snapshots.py        # pin tool, matrix, skill, and file versions under eval
  e2e.py              # read-oriented credentialed service and harness checks
  reports.py          # HTML and PR-comment rendering for JSON results
  pr_packets.py       # upstream PR packets with pins, examples, and reproduction commands
  harness_checks.py   # reusable harness optimization check catalog
  tool_selection.py  # tool description and selection optimizer
  value_bar.py       # adversarially-confirmed value-bar checks
  adapters.py        # transcript normalizers for provider and runtime event exports
  cli.py             # render, score, lint-tools, eval, judge-prompt
recipes/             # ready-to-edit agent recipes
evals/examples/      # small local eval cases
evals/checks/        # reusable harness optimization check families
evals/model_matrix/  # cross-provider model matrix configs
prompts/             # reusable prompt snippets
docs/                # technique map and source map
tests/               # standard-library unit tests
scripts/             # prose gate for public artifacts
.claude/skills/      # project-local Claude Code skill for agent audits
```

## Start Here

| Need | Open |
|---|---|
| Send a founder one clean finding | [Founder Findings](https://github.com/cfregly/claude-agent-harness-opt/tree/main/docs/findings) |
| See every promoted win and guardrail | [Confirmed Improvements](https://github.com/cfregly/claude-agent-harness-opt/blob/main/docs/confirmed-improvements.md) |
| Review the YC P2026 sweep | [YC P2026 MCP Sweep](https://github.com/cfregly/claude-agent-harness-opt/blob/main/docs/yc-p2026-mcp-sweep.md) |
| Learn the tool-writing standard | [Tool Writing Best Practices](https://github.com/cfregly/claude-agent-harness-opt/blob/main/docs/tool-writing-best-practices.md) |
| Decide whether a workflow is a skill or a tool | [Skills vs Tools](https://github.com/cfregly/claude-agent-harness-opt/blob/main/docs/skills-vs-tools.md) |
| Run the broader public MCP sweep | [Public MCP Sweep](https://github.com/cfregly/claude-agent-harness-opt/blob/main/docs/public-mcp-sweep.md) |

## Founder Packets

These links are meant to be shared directly. A confirmed packet has a live baseline-to-tuned delta.
A guardrail packet means the public catalog already passed the tested slice, so no change is
promoted.

| Target | Result | Packet |
|---|---|---|
| InsForge | Confirmed improvement | [InsForge](https://github.com/cfregly/claude-agent-harness-opt/tree/main/docs/findings/insforge) |
| Screenpipe | Confirmed improvement | [Screenpipe](https://github.com/cfregly/claude-agent-harness-opt/tree/main/docs/findings/screenpipe) |
| Firecrawl | Confirmed improvement | [Firecrawl](https://github.com/cfregly/claude-agent-harness-opt/tree/main/docs/findings/firecrawl) |
| Supabase | Confirmed improvement | [Supabase](https://github.com/cfregly/claude-agent-harness-opt/tree/main/docs/findings/supabase) |
| Zymtrace | Confirmed improvement | [Zymtrace](https://github.com/cfregly/claude-agent-harness-opt/tree/main/docs/findings/zymtrace) |
| Humwork | Guardrail | [Humwork](https://github.com/cfregly/claude-agent-harness-opt/tree/main/docs/findings/humwork) |
| OpenWork | Guardrail | [OpenWork](https://github.com/cfregly/claude-agent-harness-opt/tree/main/docs/findings/openwork) |

## Deeper References

| Topic | Doc |
|---|---|
| GitHub MCP baseline | [GitHub MCP Tool Tuning](https://github.com/cfregly/claude-agent-harness-opt/blob/main/docs/github-mcp-tool-tuning.md) |
| Firecrawl finding | [Firecrawl MCP Tool Tuning](https://github.com/cfregly/claude-agent-harness-opt/blob/main/docs/firecrawl-mcp-tool-tuning.md) |
| Supabase finding | [Supabase MCP Tool Tuning](https://github.com/cfregly/claude-agent-harness-opt/blob/main/docs/supabase-mcp-tool-tuning.md) |
| Screenpipe finding | [Screenpipe MCP Tool Tuning](https://github.com/cfregly/claude-agent-harness-opt/blob/main/docs/screenpipe-mcp-tool-tuning.md) |
| InsForge finding | [InsForge MCP Tool Tuning](https://github.com/cfregly/claude-agent-harness-opt/blob/main/docs/insforge-mcp-tool-tuning.md) |
| Upstream PR packets | [Upstream PR Flywheel](https://github.com/cfregly/claude-agent-harness-opt/blob/main/docs/upstream-pr-flywheel.md) |
| Harness grinding | [Autoresearch Hill Climbing](https://github.com/cfregly/claude-agent-harness-opt/blob/main/docs/autoresearch-hill-climbing.md) |
| Harness imports | [Repeatable Harness Lab](https://github.com/cfregly/claude-agent-harness-opt/blob/main/docs/repeatable-harness-lab.md) |
| Live CLI harnesses | [Live Harness Hardening](https://github.com/cfregly/claude-agent-harness-opt/blob/main/docs/live-harness-hardening.md) |
| SDK harnesses | [SDK Harness Coverage](https://github.com/cfregly/claude-agent-harness-opt/blob/main/docs/sdk-harness-coverage.md) |
| Agent SDK reference | [Agent SDK Harnesses](https://github.com/cfregly/claude-agent-harness-opt/blob/main/docs/agent-sdk-harnesses.md) |
| Service probes | [Credentialed Service Probes](https://github.com/cfregly/claude-agent-harness-opt/blob/main/docs/credentialed-service-probes.md) |
| gstack routing audit | [gstack Skill Routing Audit](https://github.com/cfregly/claude-agent-harness-opt/blob/main/docs/gstack-skill-routing-audit.md) |
| Model migration harnesses | [Codex and Model Migration Harnesses](https://github.com/cfregly/claude-agent-harness-opt/blob/main/docs/codex-and-model-migration-harnesses.md) |

## Claude Code Skill

The repo includes a project-local `/agent-audit` skill at
`.claude/skills/agent-audit/SKILL.md`. Use it when reviewing another agent's tools, traces, Claude
Messages API blocks, Agent SDK event exports, IDE-agent event exports, or trace suites. It chooses
the right CLI path, runs deterministic checks, and reports concrete prompt or tool changes. The skill
treats missing value-bar proof as a failed audit.

## Claude Judge

Use the Claude judge for real audits. It is the semantic gate for reasoning quality, tool-output
use, and final grounding:

```bash
export ANTHROPIC_API_KEY=...
python -m claude_agent_harness_opt review-trace evals/examples/agent_trace_good.json --claude-judge
python -m claude_agent_harness_opt audit-agent evals/examples/agent_audit_bundle.json --claude-judge --markdown
```

The judge reviews only visible artifacts: reasoning summaries, provider-returned reasoning blocks
when available, tool calls, tool outputs, and final answers. It does not claim access to hidden
chain-of-thought. If an agent runtime does not expose reasoning, instrument the agent to emit short
decision notes before and after tool calls.

GitHub Actions requires the `ANTHROPIC_API_KEY` repository secret and runs the same live judge
against the sample audit bundle on every push and pull request.

## Tool Selection Optimization

Use `optimize-tools` when the question is whether the agent has the right tool descriptions, schemas,
and calibration cases to choose tools correctly:

```bash
python -m claude_agent_harness_opt optimize-tools evals/examples/tool_tuning_before_bundle.json --markdown || true
python -m claude_agent_harness_opt optimize-tools evals/examples/agent_audit_bundle.json --markdown
python -m claude_agent_harness_opt optimize-tools evals/examples/agent_audit_bundle.json --claude-judge
```

The first command is a deliberate before-state negative control. It should fail and recommend an
`input_schema`, calibration cases, held-out cases, stronger avoid guidance, quality checks, and
runtime metrics. The second command is the after-state sample that passes.

The public MCP shortcut wraps the stored matrices for known targets:

```bash
make optimize mcp=insforge
make optimize mcp=humwork
make optimize mcp=openwork
make optimize mcp=screenpipe
make optimize url=https://github.com/InsForge/insforge-mcp
```

Unknown URLs fail rather than falling back to another target.

The optimizer checks that every tool has a distinct purpose, `use_when`, `avoid_when`,
`input_schema`, and result `quality_checks`. It also checks `tool_selection_cases` and maps trace
failures back to concrete changes like stronger avoid rules, argument schemas, examples, or stop
criteria. `audit-agent --claude-judge` includes this optimizer automatically.

## How Prompts And Tools Are Chosen

The process is a bounded search, not a random prompt sweep.

Start by inventorying the surface under test:

- public docs and source pins
- MCP `tools/list` and resource list
- installed skills and project rules
- live smoke calls when credentials are available
- existing traces or user reports that show bad tool choice

Then build a boundary map. A good boundary is one where the first wrong tool call changes cost,
safety, correctness, or recoverability. Common boundaries are:

- adjacent tools that sound similar
- required arguments that models often omit
- resource-first paths versus direct tool fallback
- broad search versus exact lookup
- discovery calls versus value-query calls
- metadata discovery versus full payload fetch
- no-tool safety cases where any tool call is wrong
- workflow rules supplied by a skill or `CLAUDE.md`

Skills are one input, not the whole descent. They are useful because they encode expert workflow
rules, but the descent also uses live MCP inventories, generated schemas, resource lists, upstream
docs, source pins, trace failures, support reports, and smoke-call output. A case is stronger when
at least two of those sources agree that a boundary matters.

The coverage target is the product of those inputs, not a single list of skills. For completeness,
build cases across these axes:

- skill workflow rules and `CLAUDE.md` style host rules
- live MCP tool names, descriptions, and argument schemas
- MCP resources and the resource-first versus direct-tool fallback path
- generated REST helpers and low-level tools that the model may overuse
- exact lookup, broad search, metadata, drilldown, write, and no-tool safety families
- provider and harness variants, including native tools and prompt-JSON wrappers
- known trace failures, support reports, and smoke-call observations

That is the "hill descent" part. We deliberately walk toward likely failure valleys by writing
adversarial prompts that make one boundary measurable. Each case names the expected tool,
confusable alternatives, a `check_family`, and any required argument checks. The point is to find a
small prompt where the transcript can be judged without taste.

Run a corpus audit before claiming the matrix is broad enough:

```bash
python -m claude_agent_harness_opt matrix-coverage evals/model_matrix/zymtrace_mcp_tool_selection.json --markdown
python -m claude_agent_harness_opt matrix-coverage-suite evals/model_matrix --markdown
```

`matrix-coverage` checks the matrix as an eval corpus before any provider call:

- every catalog tool is expected by at least one case
- every catalog tool appears as a forbidden confusable somewhere
- expected tools with arguments have at least one argument assertion
- every tuned tool has quality checks
- every case has forbidden tools and a `check_family`
- every required `check_family` declared by the matrix is covered
- every tool-description variant exposes the same tool surface unless the matrix explicitly opts out
- duplicate tool names inside a variant are surfaced
- `source.tool_count` matches the effective tool surface when it is declared
- unknown expected or forbidden tool names are surfaced

This does not replace live scoring. It prevents a clean live run from hiding an untested tool,
untested negative, missing argument boundary, forgotten family, or accidental tool-surface drift.
The `coverage.required_check_families` field is the edge-family contract for a matrix.
`coverage.allow_variant_tool_delta` is reserved for matrices that intentionally compare different
tool catalogs. Store the matrix, coverage report, live result, and PR packet together so the same
cases can be rerun later as evals.

For the full repository, the current ledger is stored at
`evals/results/model_matrix_coverage_suite_2026-06-30.md`: it audits 18 matrices, 152 tools, 199
cases, and 805 boundary pairs. All stored matrices now pass the strict structural coverage contract.
That proves catalog coverage, negative coverage, argument assertions, quality checks, and family
labels are present, that each matrix's required family contract is covered, and that variant tool
surfaces have parity. It does not prove every live model will choose correctly, so promoted
behavioral claims still need live `model-matrix` results.

After baseline failures repeat, the "hill climb" part starts:

1. Run `model-matrix` on the baseline tool surface.
2. Cluster failures by tool, argument, provider, harness, and instruction variant.
3. Draft the smallest candidate change that explains those failures.
4. Rerun the same live cells against baseline and candidate.
5. Rerun held-out cases that should not have been tailored to the failure.
6. Promote only when the candidate beats the threshold and held-out cells do not regress.
7. Store the result JSON and upstream packet so another maintainer can rerun or challenge it.

`grind-harness` automates that climb for simple description and harness variants:

```bash
python -m claude_agent_harness_opt grind-harness evals/model_matrix/coding_tool_selection.json \
  --env-file .env \
  --live \
  --require-live \
  --providers anthropic,openai,gemini \
  --harnesses native_tools,prompt_json \
  --instruction-variants boundary_rules \
  --cases "investigate trace review flow,map model matrix implementation" \
  --heldout-cases "find python files,read known file" \
  --min-improvement 0.05 \
  --max-live-calls 80 \
  --concurrency 8 \
  --markdown
```

For richer MCP surfaces, the same loop is often run manually first because the fix may span tool
descriptions, resource guidance, generated OpenAPI schemas, and skill instructions.

Zymtrace is the concrete example. The inspected MCP surface exposed 25 tools and 3 resources, while
the installed skills added CPU, GPU, allocation, resource-first, default-project, and bounded
`hot_traces` rules. That produced boundary cases such as:

- use default project `00000000-0000-0000-0000-000000000000` instead of searching projects
- discover metrics with `project_metrics_activity_aggr` before querying values
- start GPU and inference investigations with GPU, CPU, and framework metrics
- use `topentities` or `topfunctions` for rank-first CPU requests
- use MCP resources first for `topfunctions`, `topentities`, and `flamegraph`
- use `hot_traces` metadata first with `meta_only=true` and a small limit
- fetch a full trace only with a selected `prefix_hash`, `meta_only=false`, and `limit=1`

The first Zymtrace matrix proved an improvement but the coverage audit found untouched generated
REST helpers. The hardened matrix now has 34 cases, covers 25 of 25 tools as expected tools, covers
25 of 25 tools as forbidden confusables, carries 85 boundary pairs, and labels every case with a
`check_family`.

The expanded Zymtrace live run used those boundaries across Anthropic, OpenAI, and Gemini:

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
  --out /tmp/zymtrace-live.json
```

The stock Zymtrace surface passed 14 of 24 selected cells. The tuned surface passed 24 of 24. That
is why the Zymtrace finding was promoted and packaged under
[docs/findings/zymtrace](https://github.com/cfregly/claude-agent-harness-opt/tree/main/docs/findings/zymtrace).

### Abbreviated Diff Examples

These are shortened examples of the kind of change the loop promotes. The full packets live under
[docs/findings](https://github.com/cfregly/claude-agent-harness-opt/tree/main/docs/findings).

Firecrawl fixed a scrape-versus-extract boundary:

```diff
- Use firecrawl_extract for structured fields from a page.
+ Use firecrawl_scrape when the exact page URL is known and the task needs that page's content,
+ metadata, screenshot, branding, or structured fields.
+ Use firecrawl_extract when the user asks for fields across several pages or a broader structured
+ extraction job. Avoid for one known URL.
```

Supabase fixed a migration-safety boundary:

```diff
- Use execute_sql for SQL statements.
+ Use apply_migration for DDL and schema-changing SQL.
+ Use execute_sql only for regular SQL that does not change database schema.
```

Zymtrace fixed workflow and argument boundaries:

```diff
- Use project tools for the requested project.
- Use hot_traces for call-tree analysis.
+ Use default project 00000000-0000-0000-0000-000000000000 unless the user names another project.
+ Discover metrics with project_metrics_activity_aggr before querying metric values.
+ First hot_traces calls use meta_only=true and limit<=5.
+ Full trace fetches require prefix_hash, meta_only=false, and limit=1.
```

Screenpipe fixed exact keyword lookup:

```diff
- Use search-content for screen or transcript search.
+ Use keyword-search for literal terms and exact phrases.
+ Use search-content for transcript lines, screen text, speaker or window filters, tags, memories,
+ and broader content search.
```

InsForge fixed a no-tool safety case:

```diff
- Use create-deployment when the user asks to deploy a local source tree.
+ Use create-deployment only when the user provides an absolute sourceDirectory path.
+ Return NO_TOOL for relative paths like "." until the path is resolved.
```

## Model Matrix

Use `model-matrix` when tuning tool descriptions or `CLAUDE.md` style instructions for a new model,
provider, reasoning mode, or harness:

```bash
python -m claude_agent_harness_opt model-matrix evals/model_matrix/coding_tool_selection.json --markdown
python -m claude_agent_harness_opt matrix-coverage evals/model_matrix/zymtrace_mcp_tool_selection.json --markdown
python -m claude_agent_harness_opt matrix-coverage-suite evals/model_matrix --markdown --out /tmp/model-matrix-coverage.md
python -m claude_agent_harness_opt model-matrix evals/model_matrix/coding_tool_selection.json --env-file .env --live --concurrency 8 --markdown
python -m claude_agent_harness_opt model-matrix evals/model_matrix/agent_audit_skill_selection.json --env-file .env --live --require-live --providers anthropic --harnesses prompt_json --variants thin_workflow_tools --instruction-variants no_skill,agent_audit_skill --markdown
python -m claude_agent_harness_opt model-matrix evals/model_matrix/github_mcp_tool_selection.json --env-file .env --live --require-live --providers anthropic,openai,gemini --harnesses native_tools,prompt_json --variants stock_github_mcp,tuned_github_mcp_boundaries --instruction-variants github_mcp_host_rules --concurrency 4 --markdown
make optimize mcp=screenpipe
make optimize url=https://github.com/screenpipe/screenpipe
```

The included matrix tests Claude Code style `Task`, `Glob`, `Grep`, and `Read` tool selection across
Anthropic, OpenAI, and Gemini. It compares short descriptions against tuned boundary descriptions,
and it compares native provider tool calling against a standardized JSON-choice harness.
The agent-audit skill matrix shows how to test a skill as an instruction variant against a no-skill
baseline and a thin-description stress case.
The GitHub MCP matrix shows how to import a public MCP tool catalog, compare stock descriptions to
a tuned boundary variant, and avoid promoting description changes when the stock catalog already
passes.

Use `grind-harness` when the goal is to tune the harness itself. It runs a baseline matrix cell,
creates a candidate tool-description variant from the failed cases, reruns the selected cells,
checks held-out cells, and marks the value bar as passed only when the live candidate beats the
baseline by the configured threshold without regressions:

```bash
python -m claude_agent_harness_opt grind-harness evals/model_matrix/coding_tool_selection.json \
  --env-file .env \
  --live \
  --require-live \
  --providers anthropic,openai,gemini \
  --harnesses native_tools,prompt_json \
  --instruction-variants boundary_rules \
  --cases "investigate trace review flow,map model matrix implementation" \
  --heldout-cases "find python files,read known file" \
  --min-improvement 0.05 \
  --concurrency 8 \
  --markdown
```

Treat each runtime as a harness target. Provider native tools, prompt JSON wrappers, Agent SDK
loops, Codex JSONL exports, IDE agents, and Cursor-like environments should export the same visible
trace contract: decision notes, tool calls, tool results, and final answers. Once the adapter emits
that contract, the trace suite, Claude judge, model matrix, and harness grind can compare it against
other harnesses. See [Harness Optimization](https://github.com/cfregly/claude-agent-harness-opt/blob/main/docs/harness-optimization.md) for the adapter
and upgrade loop.

To test an exported harness without an API key, normalize a runtime event file and run the fixture
matrix:

```bash
python -m claude_agent_harness_opt normalize-runtime evals/examples/agent_sdk_trace_review_events.json
python -m claude_agent_harness_opt model-matrix evals/model_matrix/harness_trace_adapters.json \
  --live \
  --require-live \
  --providers trace_fixture \
  --harnesses agent_sdk_trace,cursor_trace \
  --variants exported_trace_tools \
  --instruction-variants exported_trace \
  --markdown
python -m claude_agent_harness_opt model-matrix evals/model_matrix/codex_harness_trace_adapter.json \
  --live \
  --require-live \
  --providers trace_fixture \
  --harnesses codex_exec_jsonl \
  --variants codex_exported_trace_tools \
  --instruction-variants codex_exported_trace \
  --markdown
```

## Verify it

```bash
python scripts/deslop_check.py
python -m compileall claude_agent_harness_opt scripts
python -m unittest discover -s tests -q
python -m claude_agent_harness_opt eval evals/examples/search_answer.json
python -m claude_agent_harness_opt review-trace evals/examples/agent_trace_good.json
python -m claude_agent_harness_opt normalize-claude evals/examples/claude_messages.json
python -m claude_agent_harness_opt normalize-runtime evals/examples/cursor_trace_review_events.json
python -m claude_agent_harness_opt import-run evals/examples/import_run_cursor_export.json --adapter cursor --out-dir /tmp/imported-run
python -m claude_agent_harness_opt audit-agent /tmp/imported-run/agent_audit_bundle.json
python -m claude_agent_harness_opt snapshot-surface --matrix evals/model_matrix/harness_trace_adapters.json --bundle evals/examples/agent_audit_bundle.json --skill .claude/skills/agent-audit/SKILL.md --out /tmp/surface-snapshot.json
python -m claude_agent_harness_opt mcp-e2e evals/e2e/github_readonly.json --dry-run --out /tmp/github-e2e.json
python -m claude_agent_harness_opt trace-suite evals/suites/agent_trace_suite.json
python -m claude_agent_harness_opt audit-agent evals/examples/agent_audit_bundle.json
python -m claude_agent_harness_opt audit-agent evals/examples/agent_audit_bundle.json --claude-judge
python -m claude_agent_harness_opt optimize-tools evals/examples/agent_audit_bundle.json --claude-judge
python -m claude_agent_harness_opt model-matrix evals/model_matrix/coding_tool_selection.json
python -m claude_agent_harness_opt model-matrix evals/model_matrix/agent_audit_skill_selection.json --providers anthropic --harnesses prompt_json --variants thin_workflow_tools --instruction-variants agent_audit_skill --max-cases 2
python -m claude_agent_harness_opt model-matrix evals/model_matrix/github_mcp_tool_selection.json --providers anthropic --harnesses prompt_json --variants stock_github_mcp --instruction-variants github_mcp_host_rules --max-cases 2
python -m claude_agent_harness_opt model-matrix evals/model_matrix/firecrawl_mcp_tool_selection.json --providers anthropic --harnesses prompt_json --variants tuned_firecrawl_mcp_boundaries --instruction-variants firecrawl_host_rules --max-cases 2
python -m claude_agent_harness_opt model-matrix evals/model_matrix/supabase_mcp_database_tool_selection.json --providers anthropic --harnesses prompt_json --variants tuned_supabase_database_boundaries --instruction-variants supabase_database_host_rules --max-cases 2
python -m claude_agent_harness_opt model-matrix evals/model_matrix/clickhouse_mcp_tool_selection.json --providers anthropic --harnesses prompt_json --variants tuned_clickhouse_readonly_boundaries --instruction-variants clickhouse_host_rules --max-cases 2
python -m claude_agent_harness_opt matrix-coverage evals/model_matrix/zymtrace_mcp_tool_selection.json --strict --out /tmp/zymtrace-coverage.json
python -m claude_agent_harness_opt matrix-coverage-suite evals/model_matrix --out /tmp/model-matrix-coverage-suite.json
python -m claude_agent_harness_opt model-matrix evals/model_matrix/zymtrace_mcp_tool_selection.json --providers anthropic --harnesses prompt_json --variants tuned_zymtrace_mcp_boundaries --instruction-variants zymtrace_host_and_skill_rules --max-cases 2
python -m claude_agent_harness_opt model-matrix evals/model_matrix/harness_trace_adapters.json --live --require-live --providers trace_fixture
python -m claude_agent_harness_opt model-matrix evals/model_matrix/codex_harness_trace_adapter.json --live --require-live --providers trace_fixture
python -m claude_agent_harness_opt model-matrix evals/model_matrix/harness_trace_adapters.json --providers trace_fixture --harnesses agent_sdk_trace --max-cases 1 --out /tmp/harness-matrix.json
python -m claude_agent_harness_opt render-report /tmp/harness-matrix.json --out /tmp/harness-matrix.html
python -m claude_agent_harness_opt pr-comment /tmp/harness-matrix.json --out /tmp/harness-matrix.md
python -m claude_agent_harness_opt harness-checks --markdown
python -m claude_agent_harness_opt upstream-pr-packet /tmp/harness-matrix.json --target-name "Example MCP" --baseline-variant stock --candidate-variant tuned --out-dir /tmp/upstream-pr
python -m claude_agent_harness_opt grind-harness evals/model_matrix/coding_tool_selection.json
python scripts/probe_service_keys.py --env-file .env --no-fail
python scripts/check_value_bar.py
```

## Sources

The technique map is grounded in Anthropic's public video and docs. See
[Source Map](https://github.com/cfregly/claude-agent-harness-opt/blob/main/docs/source-map.md) for the source list and timestamps used while building the
repo. See [Video Coverage Audit](https://github.com/cfregly/claude-agent-harness-opt/blob/main/docs/video-coverage-audit.md) for the implementation
coverage check against the talk.

## License

MIT.
