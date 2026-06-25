# Harness Optimization

Harness optimization is the layer that tests whether a model and runtime use tools well. The tool
description is only one input. The harness also includes the provider API shape, native function
calling, prompt JSON wrappers, Agent SDK loop rules, IDE agent behavior, trace capture, and the
instructions that sit beside the tools.

## What To Tune

Tune the smallest surface that explains the failure:

- tool names
- tool descriptions
- argument schemas
- provider native tool schemas
- prompt JSON wrappers
- system prompt rules
- `CLAUDE.md` style project rules
- skill instructions
- Agent SDK loop controls
- trace capture and reasoning summaries

Do not promote a change because it sounds better. Promote only when it is adversarially-confirmed
to add value against a baseline.

## Trace Contract

Every harness should export the same trace shape:

- a short visible decision note before the first tool call that names complexity, tool budget, and
  evidence or stop criteria
- ordered tool calls with ids, names, arguments, and optional parallel groups
- tool outputs linked to tool-call ids
- a visible decision note after tool results that names result quality, verification, and the
  continue or stop decision
- the final answer or final state

Some providers return thinking blocks or reasoning summaries. Some runtimes do not. When the
runtime does not expose reasoning, instrument the agent to emit short decision notes. Do not claim
access to hidden chain-of-thought.

## Matrix Contract

Use `model-matrix` when the question is tool choice:

```bash
python -m claude_agent_harness_optimization model-matrix evals/model_matrix/coding_tool_selection.json \
  --env-file .env \
  --live \
  --require-live \
  --providers anthropic,openai,gemini \
  --harnesses native_tools,prompt_json \
  --instruction-variants boundary_rules \
  --markdown
```

Use `grind-harness` when a baseline fails and you want a candidate tool-description variant:

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
  --max-live-calls 60 \
  --markdown
```

The grind loop is intentionally bounded:

- dry run first to confirm selected cells
- cap live calls with `--max-live-calls`
- generate a candidate from observed failures
- rerun the same cells live
- confirm against held-out cells when a candidate beats the baseline
- promote only when the candidate clears the minimum improvement threshold without held-out regression
- log every keep or reject decision

This is the autoresearch pattern applied to agent harnesses. The editable surface is not model
training code. It is the harness surface that changes tool choice: tool descriptions, schemas,
provider wrappers, prompt wrappers, `CLAUDE.md`, skills, and trace adapters. The metric is the model
matrix and trace review score. The keep or reject rule is the value bar.

## Adapter Contract

For a new Agent SDK, Codex JSONL export, IDE agent, or Cursor-like harness, add an adapter that does
two things:

- converts raw runtime events into the trace contract
- maps the harness into matrix profiles and harness names

The first adapter should be thin. Capture actual tool calls and outputs before writing opinions
about the harness. Normalize the event export first:

```bash
python -m claude_agent_harness_optimization normalize-runtime path/to/events.json > path/to/trace.json
python -m claude_agent_harness_optimization import-run path/to/events.json --adapter cursor --out-dir /tmp/imported-run
python -m claude_agent_harness_optimization import-run path/to/codex-events.jsonl --adapter codex_jsonl --out-dir /tmp/imported-codex-run
```

Once a real trace exists, run:

```bash
python -m claude_agent_harness_optimization review-trace path/to/trace.json --claude-judge
python -m claude_agent_harness_optimization audit-agent /tmp/imported-run/agent_audit_bundle.json --claude-judge
python -m claude_agent_harness_optimization trace-suite path/to/suite.json --markdown
python -m claude_agent_harness_optimization snapshot-surface --bundle /tmp/imported-run/agent_audit_bundle.json --out /tmp/surface.json
```

Then add the exported run as a named harness in a model matrix. The fixture provider is useful for
testing adapters without spending live provider calls:

```bash
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

## Reliable Upgrade Loop

Use this loop for every new model generation or harness version:

1. Freeze a baseline matrix and trace suite.
2. Add the new model, reasoning effort, or harness as a profile.
3. Run deterministic checks.
4. Run a paid live matrix with `.env`.
5. Run `grind-harness` on repeated failures.
6. Add held-out cases for any boundary that improved.
7. Promote only if the candidate clears the value bar.

The pain points are predictable:

- traces often lack visible reasoning between tool calls
- reasoning notes often omit complexity, budget, evidence thresholds, verification, or stop decisions
- tool descriptions are too short for similar tools
- native provider schemas and prompt JSON wrappers fail differently
- a change that helps one model can hurt another
- harnesses may hide or transform tool arguments
- live sweeps need budget caps and small case sets

Those pain points are why the repo separates trace review, tool-selection optimization, model
matrix runs, and bounded harness grinding.
