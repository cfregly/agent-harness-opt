# Codex And Model Migration Harnesses

This repo treats Codex as a harness, not only as the local agent running the repo. A Codex harness
means the Codex CLI, app, IDE extension, GitHub Action, SDK, app-server, MCP-server mode, hooks,
skills, plugins, AGENTS.md loading, sandbox policy, and JSONL event stream that sit around the
model.

Checked on 2026-06-25.

## Codex Harness Surface

Codex exposes several surfaces that can change tool-use behavior:

- `AGENTS.md`: durable repo instructions loaded before work. Nested files and overrides can change
  behavior by directory.
- Skills: reusable workflows with progressive disclosure. Skill descriptions are a tool-selection
  surface because Codex chooses skills from descriptions before reading full `SKILL.md`.
- MCP configuration: external tools, resources, prompts, server instructions, allow lists, deny
  lists, approval policy, and timeouts.
- Hooks: lifecycle enforcement before or after tools, compaction, prompts, and stop events.
- `codex exec --json`: machine-readable event streams containing reasoning, command executions,
  MCP tool calls, file changes, and final messages.
- Codex SDK and app-server: programmatic thread, turn, item, approval, and streaming controls.
- Codex MCP server: another harness can call Codex through the `codex` and `codex-reply` MCP tools.
- Codex GitHub Action: CI harness with model, effort, sandbox, safety strategy, and output capture.

## What We Added

The Codex adapter now accepts JSONL exports and normalizes nested Codex `item.*` events into the
same trace contract used for Claude, Agent SDK, Cursor-style, LangGraph, and LangSmith traces.

Run the fixture matrix:

```bash
python -m claude_agent_harness_optimization model-matrix evals/model_matrix/codex_harness_trace_adapter.json \
  --live \
  --require-live \
  --providers trace_fixture \
  --harnesses codex_exec_jsonl \
  --variants codex_exported_trace_tools \
  --instruction-variants codex_exported_trace \
  --markdown
```

The matrix has two starter cases:

| Case | Expected preserved signal |
|---|---|
| `codex repo inspection uses shell search` | first selected tool is `Bash` and arguments include `rg` |
| `codex mcp docs call preserves tool name` | first selected tool is `mcp__context7__get-library-docs` and arguments include `/upstash/context7` |

This is a fixture proof, not a live Codex quality claim. A live Codex harness run should be exported
with `codex exec --json` or app-server event capture, imported with `--adapter codex_jsonl`, and then
reviewed with `review-trace`, `audit-agent`, and a named model matrix.

## Popular Harnesses To Test

Highest-value harnesses for this repo:

| Harness | Why it matters | Current status |
|---|---|---|
| Claude native tools | Baseline for Anthropic tool use, thinking summaries, and MCP-style tool contracts. | Live matrix supported. |
| OpenAI native tools / Responses API | Different function-call schema and reasoning behavior. | Live matrix supported. |
| Gemini function calling | Third provider with different schema and tool-selection behavior. | Live matrix supported. |
| Prompt JSON | Cheap cross-provider control harness that makes tool-choice output explicit. | Live matrix supported. |
| Codex CLI / app-server / SDK | Real coding-agent runtime with AGENTS.md, skills, MCP, hooks, sandbox, command execution, and JSONL traces. | Fixture and live `codex exec --json` adapter covered. |
| Claude Code / Claude API skill | Anthropic coding-agent runtime and bundled migration skill. | Live `claude -p --output-format stream-json --verbose` adapter covered. |
| Claude Agent SDK | Library harness that exposes Claude Code's loop and capabilities. | Live latest-package `claude-agent-sdk` smoke plus surface inventory covered. |
| OpenAI Agents SDK | Common multi-agent SDK with handoffs, MCP, traces, and guardrails. | Live latest-package `openai-agents` smoke plus surface inventory covered. |
| Google ADK | Google's Agent Development Kit for code-first agent development. | Live latest-package `google-adk` smoke plus surface inventory covered. |
| Cursor-style IDE agents | Popular IDE harness with hidden/system rules and codebase tools. | Fixture adapter supported. Live Cursor Agent currently auth-failed locally. |
| LangGraph / LangSmith | Common production orchestration and trace-review stack. | Adapter aliases supported. Deeper schema fixtures needed. |
| OpenCode | Popular terminal coding harness with provider-backed model selection and command logs. | Live text-log adapter covered. |
| Vercel AI SDK / Mastra / CrewAI / AutoGen / Pydantic AI | Popular app-agent orchestration layers with different loop and tool policies. | Candidate adapters. No live claim until runnable traces are captured. |

The right next step is not to add every framework at once. Add one harness only when we can export
real traces with reasoning summaries, tool calls, tool outputs, final answers, source pins, and exact
commands.

## Anthropic Migration Guidance Coverage

Anthropic's migration guide says the bundled Claude API skill can be invoked in Claude Code with
`/claude-api migrate`. The documented scope includes model ID swaps, breaking parameter changes,
prefill replacement, effort calibration, platform-specific model ID formats, and a manual checklist.

The same guide also calls out migration checks that this repo should validate:

| Anthropic migration item | Repo coverage |
|---|---|
| Model ID swap | Covered as provider/model profiles in model matrices. No static code scanner yet. |
| Unsupported sampling parameters | Added as `model_migration_api` check family. Needs concrete fixtures. |
| Manual extended thinking and thinking budgets | Covered conceptually by directed-thinking checks. Migration fixtures should verify unsupported fields are removed or replaced. |
| Thinking output display and pass-through | Claude message adapter preserves thinking and redacted-thinking blocks. Migration fixtures should verify cross-model replay strips incompatible thinking blocks. |
| Assistant prefill replacement | Added as model-migration coverage gap. It should be validated with a fixture that rewrites prefill to system instructions or structured outputs. |
| Effort calibration | Model matrix already varies profiles. Migration docs now require effort to be treated as an evaluated parameter, not a prose default. |
| Refusal stop reason and stop details | Not yet encoded as a matrix case. Add API-response fixtures before claiming coverage. |
| Prompt caching and mid-conversation system messages | Not yet encoded. These are harness-level cost/cache checks, not tool-selection checks. |
| Provider-specific model ID formats for Bedrock, Vertex, AWS platform, and Foundry | Not yet encoded. This belongs in a migration static checker or fixture suite. |
| Prompt improver / generated examples | Covered by the value bar: prompt changes must beat baseline evals, use flexible verifiers, and avoid held-out regressions. |

## Can We Do Better Than `/claude-api migrate`?

Different job. The Anthropic skill is a code migration assistant for Claude API compatibility. This
repo is an eval and harness optimization lab.

The useful relationship is:

1. Run `/claude-api migrate` or any provider migration tool.
2. Snapshot the changed model IDs, prompts, tool descriptions, CLAUDE.md/AGENTS.md, skills, SDK loop,
   and harness config.
3. Run model-matrix cases on the old and new model/harness surfaces.
4. Run trace review on representative live runs.
5. Keep the migration only where it is adversarially-confirmed to add value.

That means this repo can validate migration tools and catch behavior regressions they do not try to
measure. It should not pretend to replace API-specific migration tools until it has static scanners
and fixtures for each provider's breaking API changes.

## Gaps To Close Next

- Add directed-reasoning instrumentation cases to the live headless CLI suite.
- Add deeper SDK cases for approvals, hooks, handoffs, sessions, tracing, and MCP servers.
- Authenticate Cursor Agent locally and rerun the live Cursor cell.
- Add model-migration fixtures for unsupported sampling parameters, prefill replacement, thinking
  config removal, refusal stop details, and provider-specific model IDs.
- Add cost and latency result fields so effort and prompt-caching migrations can be judged by more
  than tool-selection accuracy.
- Add a PR packet template specifically for "migration tool validated by harness matrix" claims.
