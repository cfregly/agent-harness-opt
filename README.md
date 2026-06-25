# claude-agent-harness-optimization

[![ci](https://github.com/cfregly/claude-agent-harness-optimization/actions/workflows/ci.yml/badge.svg)](https://github.com/cfregly/claude-agent-harness-optimization/actions/workflows/ci.yml)
[![license: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

A runnable prompt kit for Claude-style agents: decide whether a task deserves an agent, render a
structured system prompt, check tool design, run local evals over agent transcripts, and optionally
ask Claude to semantically judge trace quality.

The bar is always "adversarially-confirmed to add value." An audit passes only when it names the
value claim, compares against a baseline, meets a minimum improvement threshold, and survives an
adversarial check with no open objections.

The repo turns the main ideas from Anthropic's "Prompting for Agents" talk into code and templates.
The deterministic checks run first, then real semantic audits call Claude through the Messages API
with `ANTHROPIC_API_KEY`. CI requires a live Claude judge pass.

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e .

python -m claude_agent_harness_optimization render recipes/agentic_search.json
python -m claude_agent_harness_optimization score recipes/agentic_search.json
python -m claude_agent_harness_optimization lint-tools recipes/agentic_search.json
python -m claude_agent_harness_optimization eval evals/examples/search_answer.json
python -m claude_agent_harness_optimization review-trace evals/examples/agent_trace_good.json
python -m claude_agent_harness_optimization review-trace evals/examples/agent_trace_parallel_good.json
python -m claude_agent_harness_optimization normalize-claude evals/examples/claude_messages.json
python -m claude_agent_harness_optimization normalize-runtime evals/examples/cursor_trace_review_events.json
python -m claude_agent_harness_optimization import-run evals/examples/import_run_cursor_export.json --adapter cursor --out-dir /tmp/imported-run
python -m claude_agent_harness_optimization snapshot-surface --matrix evals/model_matrix/harness_trace_adapters.json --skill .claude/skills/agent-audit/SKILL.md --out /tmp/surface-snapshot.json
python -m claude_agent_harness_optimization mcp-e2e evals/e2e/github_readonly.json --dry-run
python -m claude_agent_harness_optimization trace-suite evals/suites/agent_trace_suite.json
python -m claude_agent_harness_optimization audit-agent evals/examples/agent_audit_bundle.json --markdown
python -m claude_agent_harness_optimization audit-agent evals/examples/agent_audit_bundle.json --claude-judge
python -m claude_agent_harness_optimization optimize-tools evals/examples/agent_audit_bundle.json --markdown
python -m claude_agent_harness_optimization optimize-tools evals/examples/agent_audit_bundle.json --claude-judge
python -m claude_agent_harness_optimization model-matrix evals/model_matrix/coding_tool_selection.json --markdown
python -m claude_agent_harness_optimization model-matrix evals/model_matrix/harness_trace_adapters.json --live --require-live --providers trace_fixture --markdown
python -m claude_agent_harness_optimization model-matrix evals/model_matrix/coding_tool_selection.json --env-file .env --live --concurrency 8 --markdown
python -m claude_agent_harness_optimization grind-harness evals/model_matrix/coding_tool_selection.json --env-file .env --live --concurrency 8 --heldout-cases "find python files,read known file" --markdown
python -m claude_agent_harness_optimization live-harness evals/live_harnesses/headless_cli_smoke.json --env-file .env --out-dir /tmp/aho-live --markdown
python -m claude_agent_harness_optimization live-harness evals/live_harnesses/sdk_agent_smoke.json --env-file .env --out-dir /tmp/aho-sdk-live --markdown
uvx --with claude-agent-sdk --with openai-agents --with google-adk python scripts/sdk_surface_inventory.py
python -m claude_agent_harness_optimization render-report /tmp/harness-matrix.json --out /tmp/harness-matrix.html
python -m claude_agent_harness_optimization pr-comment /tmp/harness-matrix.json --out /tmp/harness-matrix.md
python scripts/probe_service_keys.py --env-file .env --no-fail
python -m claude_agent_harness_optimization judge-prompt evals/examples/search_answer.json
```

## What it implements

The kit encodes the agent prompting patterns that show up repeatedly in the talk and the current
Claude prompt engineering docs:

- task-fit scoring across complexity, value, viability, error cost, and recoverability
- simple starting prompts that grow only from observed failures
- explicit tool-selection guidance instead of relying on short tool descriptions
- distinct tool names and descriptions, with linting for overlap
- tool-writing checks for verifiable outcomes, held-out cases, response formats, context controls,
  helpful errors, and namespace hygiene
- initial planning, reflection after tool results, source verification, and self-checks
- directed thinking checks for initial complexity, tool budget, evidence or stop criteria, result
  quality, verification, and continue or stop decisions
- tool-call budgets for simple, standard, and complex work
- stop criteria, fallback behavior, and rollback of harmful prompt changes
- reversibility rules for destructive, shared, or hard to undo actions
- context strategy through progress files, compaction notes, and subagent summaries
- parallel tool calls when work is independent
- evals for answer accuracy, tool use accuracy, and final state accuracy
- flexible verifiers for alternate phrasing, numeric ranges, regex output shape, and valid tool paths
- small realistic eval sets, LLM judge rubrics, and manual review
- examples added only after failures show where they help
- ordered trace review for reasoning, tool calls, tool outputs, and final answers
- trace regression suites for keeping known-good and known-bad cases stable
- agent audit bundles that review a tool inventory plus representative traces
- Claude-backed semantic judging of visible reasoning summaries, tool outputs, and final grounding
- tool-selection optimization from tool descriptions, schemas, calibration cases, and trace failures
- model matrix sweeps across providers, model ids, harnesses, instruction variants, and tool-description variants
- trace adapters that normalize exported Agent SDK and IDE-agent runs into the same matrix contract
- run import that writes both a normalized trace and an audit bundle for external harness exports
- surface snapshots for the exact matrix, tool catalog, skill, and prompt files under evaluation
- read-oriented credentialed E2E specs for service-backed MCP and harness checks
- static HTML and PR-comment reports with backing data from audit, matrix, grind, snapshot, and E2E JSON
- upstream PR packets with source pins, exact examples, reproduction commands, and result evidence
- reusable harness check families for boundary, safety, argument, recovery, output, resource, thinking, parity, and reproducibility failures
- live headless CLI harness probes for Codex, Claude Code, Gemini CLI, Cursor Agent, and OpenCode,
  with redacted artifacts, version pins, normalized traces, and directed-thinking visibility status
- live latest-package SDK probes for Claude Agent SDK, OpenAI Agents SDK, and Google ADK
- latest-package SDK surface inventory for Claude Agent SDK, OpenAI Agents SDK, and Google ADK
- autoresearch-style harness grinding that turns matrix failures into candidate variants, checks
  held-out cases, logs keep or reject decisions, and promotes only live improvements
- value-bar enforcement for baseline comparison, minimum improvement, and adversarial confirmation

## Layout

```
claude_agent_harness_optimization/
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

Start with [docs/tool-writing-best-practices.md](docs/tool-writing-best-practices.md) when designing
or reviewing a new tool catalog.
Use [docs/skills-vs-tools.md](docs/skills-vs-tools.md) when deciding whether a workflow belongs in
a callable tool description or in a skill instruction policy.
Use [docs/github-mcp-tool-tuning.md](docs/github-mcp-tool-tuning.md) for a public GitHub MCP Server
tool-selection baseline across Anthropic, OpenAI, Gemini, native tools, and prompt JSON harnesses.
Use [docs/public-mcp-sweep.md](docs/public-mcp-sweep.md) for the broader public MCP sweep across
GitHub, Playwright, Slack, Filesystem, Postgres MCP Pro, Firecrawl, Context7, Supabase, and
ClickHouse, and Zymtrace.
Use [docs/confirmed-improvements.md](docs/confirmed-improvements.md) for the pinned ledger of
confirmed tuning wins, guardrails without promotion, and the upstream MCP versions those results
apply to.
Use [docs/upstream-pr-flywheel.md](docs/upstream-pr-flywheel.md) when turning a confirmed matrix win
into an upstream pull request packet with reproducible evidence.
Use [docs/codex-and-model-migration-harnesses.md](docs/codex-and-model-migration-harnesses.md)
when treating Codex exports or provider model-migration tools as harnesses under test.
Use [docs/firecrawl-mcp-tool-tuning.md](docs/firecrawl-mcp-tool-tuning.md) for the confirmed
Firecrawl scrape-versus-extract description optimization.
Use [docs/supabase-mcp-tool-tuning.md](docs/supabase-mcp-tool-tuning.md) for the confirmed
Supabase DDL-versus-SQL migration boundary optimization.
Use [docs/gstack-skill-routing-audit.md](docs/gstack-skill-routing-audit.md) for the cross-provider
gstack skills-as-tools routing matrix and upstream PR packet evidence.
Use [docs/credentialed-service-probes.md](docs/credentialed-service-probes.md) to verify local
service credentials without printing secrets or mutating vendor state.
Use [docs/autoresearch-hill-climbing.md](docs/autoresearch-hill-climbing.md) when the goal is to
run an eval-driven optimization loop over harness, tool, `CLAUDE.md`, or skill changes.
Use [docs/repeatable-harness-lab.md](docs/repeatable-harness-lab.md) to import a real harness run,
pin the tested surfaces, run credentialed read checks, and produce review artifacts.
Use [docs/live-harness-hardening.md](docs/live-harness-hardening.md) when testing Codex, Claude
Code, Gemini CLI, Cursor Agent, OpenCode, or another installed harness as the system under test.
Use [docs/sdk-harness-coverage.md](docs/sdk-harness-coverage.md) when testing Claude Agent SDK,
OpenAI Agents SDK, Google ADK, or another SDK harness directly.
Use [docs/agent-sdk-harnesses.md](docs/agent-sdk-harnesses.md) for the versioned public reference
on how the Claude Agent SDK, Claude Managed Agents, OpenAI Agents SDK, and Google ADK harnesses work.

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
python -m claude_agent_harness_optimization review-trace evals/examples/agent_trace_good.json --claude-judge
python -m claude_agent_harness_optimization audit-agent evals/examples/agent_audit_bundle.json --claude-judge --markdown
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
python -m claude_agent_harness_optimization optimize-tools evals/examples/agent_audit_bundle.json --markdown
python -m claude_agent_harness_optimization optimize-tools evals/examples/agent_audit_bundle.json --claude-judge
```

The optimizer checks that every tool has a distinct purpose, `use_when`, `avoid_when`,
`input_schema`, and result `quality_checks`. It also checks `tool_selection_cases` and maps trace
failures back to concrete changes like stronger avoid rules, argument schemas, examples, or stop
criteria. `audit-agent --claude-judge` includes this optimizer automatically.

## Model Matrix

Use `model-matrix` when tuning tool descriptions or `CLAUDE.md` style instructions for a new model,
provider, reasoning mode, or harness:

```bash
python -m claude_agent_harness_optimization model-matrix evals/model_matrix/coding_tool_selection.json --markdown
python -m claude_agent_harness_optimization model-matrix evals/model_matrix/coding_tool_selection.json --env-file .env --live --concurrency 8 --markdown
python -m claude_agent_harness_optimization model-matrix evals/model_matrix/agent_audit_skill_selection.json --env-file .env --live --require-live --providers anthropic --harnesses prompt_json --variants thin_workflow_tools --instruction-variants no_skill,agent_audit_skill --markdown
python -m claude_agent_harness_optimization model-matrix evals/model_matrix/github_mcp_tool_selection.json --env-file .env --live --require-live --providers anthropic,openai,gemini --harnesses native_tools,prompt_json --variants stock_github_mcp,tuned_github_mcp_boundaries --instruction-variants github_mcp_host_rules --concurrency 4 --markdown
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
python -m claude_agent_harness_optimization grind-harness evals/model_matrix/coding_tool_selection.json \
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
other harnesses. See [docs/harness-optimization.md](docs/harness-optimization.md) for the adapter
and upgrade loop.

To test an exported harness without an API key, normalize a runtime event file and run the fixture
matrix:

```bash
python -m claude_agent_harness_optimization normalize-runtime evals/examples/agent_sdk_trace_review_events.json
python -m claude_agent_harness_optimization model-matrix evals/model_matrix/harness_trace_adapters.json \
  --live \
  --require-live \
  --providers trace_fixture \
  --harnesses agent_sdk_trace,cursor_trace \
  --variants exported_trace_tools \
  --instruction-variants exported_trace \
  --markdown
python -m claude_agent_harness_optimization model-matrix evals/model_matrix/codex_harness_trace_adapter.json \
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
python -m compileall claude_agent_harness_optimization scripts
python -m unittest discover -s tests -q
python -m claude_agent_harness_optimization eval evals/examples/search_answer.json
python -m claude_agent_harness_optimization review-trace evals/examples/agent_trace_good.json
python -m claude_agent_harness_optimization normalize-claude evals/examples/claude_messages.json
python -m claude_agent_harness_optimization normalize-runtime evals/examples/cursor_trace_review_events.json
python -m claude_agent_harness_optimization import-run evals/examples/import_run_cursor_export.json --adapter cursor --out-dir /tmp/imported-run
python -m claude_agent_harness_optimization audit-agent /tmp/imported-run/agent_audit_bundle.json
python -m claude_agent_harness_optimization snapshot-surface --matrix evals/model_matrix/harness_trace_adapters.json --bundle evals/examples/agent_audit_bundle.json --skill .claude/skills/agent-audit/SKILL.md --out /tmp/surface-snapshot.json
python -m claude_agent_harness_optimization mcp-e2e evals/e2e/github_readonly.json --dry-run --out /tmp/github-e2e.json
python -m claude_agent_harness_optimization trace-suite evals/suites/agent_trace_suite.json
python -m claude_agent_harness_optimization audit-agent evals/examples/agent_audit_bundle.json
python -m claude_agent_harness_optimization audit-agent evals/examples/agent_audit_bundle.json --claude-judge
python -m claude_agent_harness_optimization optimize-tools evals/examples/agent_audit_bundle.json --claude-judge
python -m claude_agent_harness_optimization model-matrix evals/model_matrix/coding_tool_selection.json
python -m claude_agent_harness_optimization model-matrix evals/model_matrix/agent_audit_skill_selection.json --providers anthropic --harnesses prompt_json --variants thin_workflow_tools --instruction-variants agent_audit_skill --max-cases 2
python -m claude_agent_harness_optimization model-matrix evals/model_matrix/github_mcp_tool_selection.json --providers anthropic --harnesses prompt_json --variants stock_github_mcp --instruction-variants github_mcp_host_rules --max-cases 2
python -m claude_agent_harness_optimization model-matrix evals/model_matrix/firecrawl_mcp_tool_selection.json --providers anthropic --harnesses prompt_json --variants tuned_firecrawl_mcp_boundaries --instruction-variants firecrawl_host_rules --max-cases 2
python -m claude_agent_harness_optimization model-matrix evals/model_matrix/supabase_mcp_database_tool_selection.json --providers anthropic --harnesses prompt_json --variants tuned_supabase_database_boundaries --instruction-variants supabase_database_host_rules --max-cases 2
python -m claude_agent_harness_optimization model-matrix evals/model_matrix/clickhouse_mcp_tool_selection.json --providers anthropic --harnesses prompt_json --variants tuned_clickhouse_readonly_boundaries --instruction-variants clickhouse_host_rules --max-cases 2
python -m claude_agent_harness_optimization model-matrix evals/model_matrix/zymtrace_mcp_tool_selection.json --providers anthropic --harnesses prompt_json --variants tuned_zymtrace_mcp_boundaries --instruction-variants zymtrace_host_and_skill_rules --max-cases 2
python -m claude_agent_harness_optimization model-matrix evals/model_matrix/harness_trace_adapters.json --live --require-live --providers trace_fixture
python -m claude_agent_harness_optimization model-matrix evals/model_matrix/codex_harness_trace_adapter.json --live --require-live --providers trace_fixture
python -m claude_agent_harness_optimization model-matrix evals/model_matrix/harness_trace_adapters.json --providers trace_fixture --harnesses agent_sdk_trace --max-cases 1 --out /tmp/harness-matrix.json
python -m claude_agent_harness_optimization render-report /tmp/harness-matrix.json --out /tmp/harness-matrix.html
python -m claude_agent_harness_optimization pr-comment /tmp/harness-matrix.json --out /tmp/harness-matrix.md
python -m claude_agent_harness_optimization harness-checks --markdown
python -m claude_agent_harness_optimization upstream-pr-packet /tmp/harness-matrix.json --target-name "Example MCP" --baseline-variant stock --candidate-variant tuned --out-dir /tmp/upstream-pr
python -m claude_agent_harness_optimization grind-harness evals/model_matrix/coding_tool_selection.json
python scripts/probe_service_keys.py --env-file .env --no-fail
python scripts/check_value_bar.py
```

## Sources

The technique map is grounded in Anthropic's public video and docs. See
[docs/source-map.md](docs/source-map.md) for the source list and timestamps used while building the
repo. See [docs/video-coverage-audit.md](docs/video-coverage-audit.md) for the implementation
coverage check against the talk.

## License

MIT.
