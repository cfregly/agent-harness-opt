# Trace Review

Use this repo to review someone else's agent by asking their harness to export an ordered trace.
The trace should capture what the agent saw and did, not private application state.

Every audit must clear the value bar: adversarially-confirmed to add value. Trace quality alone is
not enough. The audit bundle must show a value claim, a baseline, a candidate, a minimum improvement,
and an adversarial review with no open objections.

## Event Schema

Each trace has a `steps` array. The supported event types are:

- `reasoning`: a visible thinking summary, a provider-returned reasoning block, or an agent-authored
  decision note
- `tool_call`: the tool name, call id, and arguments sent to the tool
- `tool_result`: the output, error, or status returned by the tool
- `final`: the final answer or final state summary

For parallel tool calls, give each call and result the same `parallel_group`. The reviewer treats
the group as one evidence batch and requires reasoning after the batch before the next action. This
matches the agent demo pattern where independent searches run in parallel, then the agent reflects
on the combined results.

Run:

```bash
python -m claude_agent_prompting review-trace evals/examples/agent_trace_good.json
python -m claude_agent_prompting review-trace evals/examples/agent_trace_parallel_good.json
python -m claude_agent_prompting review-trace evals/examples/agent_trace_bad.json
python -m claude_agent_prompting trace-judge-prompt evals/examples/agent_trace_good.json
python -m claude_agent_prompting normalize-claude evals/examples/claude_messages.json
python -m claude_agent_prompting trace-suite evals/suites/agent_trace_suite.json
python -m claude_agent_prompting trace-suite evals/suites/agent_trace_suite.json --markdown
python -m claude_agent_prompting audit-agent evals/examples/agent_audit_bundle.json --markdown
python -m claude_agent_prompting audit-agent evals/examples/agent_audit_bundle.json --claude-judge
```

## What To Score

The deterministic reviewer checks:

- tool calls have ids, names, and matching results
- parallel tool calls and results can be grouped into evidence batches
- required tools were used and forbidden tools were avoided
- arguments contain expected values
- duplicate tool calls stay below the configured limit
- reasoning appears before the first tool call when required
- each tool result is followed by reasoning before the next action
- reasoning after tool results assesses evidence, relevance, or reliability
- tool errors are followed by recovery reasoning
- final answers contain required evidence or uncertainty language

Use the Claude judge for judgment that cannot be checked by string or structure alone, such as
whether the agent's reflection was good enough for the domain and whether the final answer really
uses the tool outputs.

```bash
export ANTHROPIC_API_KEY=...
python -m claude_agent_prompting review-trace evals/examples/agent_trace_good.json --claude-judge
```

The Claude judge receives the deterministic review plus the visible trace. It returns scores for
tool effectiveness, reasoning quality, tool-output use, final-answer grounding, and value over
baseline. Keep the deterministic review beside the Claude result because each catches different
failures.

## Capturing Claude Traces

For Claude API agents with thinking enabled, capture the returned content blocks in order:

- `thinking` blocks become `reasoning` events. Store summarized thinking when available.
- `redacted_thinking` or omitted thinking should be recorded as a reasoning event with an empty
  summary and a note that it was opaque.
- `tool_use` blocks become `tool_call` events.
- your `tool_result` messages become `tool_result` events.
- final `text` blocks become `final` events.

Do not rewrite provider-returned thinking blocks when continuing a Claude tool-use conversation. The
Claude docs state that thinking blocks used with tools should be passed back unchanged. For trace
review, store a separate normalized copy for evaluation.

If a provider does not expose reasoning, do not try to extract hidden reasoning. Instead, instrument
your agent to write short decision notes before and after tool calls. Those notes are often enough to
review whether the agent understood tool outputs and made sane next-step decisions.

## Minimal Harness Contract

Ask an agent owner to export one JSON file per run:

```json
{
  "task": "What the agent was asked to do",
  "rubric": {
    "required_tools": ["web_search"],
    "max_tool_calls": 6,
    "require_reasoning_after_tool_results": true
  },
  "steps": [
    {"type": "reasoning", "summary": "Why the first tool is needed"},
    {
      "type": "tool_call",
      "id": "call_1",
      "name": "web_search",
      "parallel_group": "initial_research",
      "args": {"query": "..."}
    },
    {
      "type": "tool_call",
      "id": "call_2",
      "name": "web_search",
      "parallel_group": "initial_research",
      "args": {"query": "..."}
    },
    {
      "type": "tool_result",
      "tool_call_id": "call_1",
      "parallel_group": "initial_research",
      "ok": true,
      "output": "..."
    },
    {
      "type": "tool_result",
      "tool_call_id": "call_2",
      "parallel_group": "initial_research",
      "ok": true,
      "output": "..."
    },
    {"type": "reasoning", "summary": "Whether the evidence batch was reliable enough"},
    {"type": "final", "text": "Final answer"}
  ]
}
```

That is enough to review most agent failures without coupling this repo to the agent runtime.

## Regression Suites

Use a trace suite when you want to keep a fixed set of agent behaviors stable. A suite can include
known-good traces that must pass and known-bad traces that must fail below a score threshold. This is
useful after prompt edits because it checks both sides of the gate.

```json
{
  "name": "agent trace regression suite",
  "cases": [
    {"name": "good trace passes", "trace": "../examples/agent_trace_good.json", "expect_passed": true},
    {"name": "bad trace fails", "trace": "../examples/agent_trace_bad.json", "expect_passed": false, "max_score": 0.75}
  ]
}
```

## Agent Audit Bundles

Use an audit bundle when someone gives you a tool inventory and representative traces. The bundle
first lints tool names and descriptions, then reviews each trace against its rubric, then enforces
the value bar.

```json
{
  "name": "sample research agent audit",
  "tools": [
    {
      "name": "web_search",
      "purpose": "Find candidate sources and fresh facts from the public web.",
      "use_when": "Use for unknown, current, or broad questions where source discovery is required.",
      "avoid_when": "Avoid when a known source URL should be fetched directly."
    }
  ],
  "traces": [
    {"name": "representative run", "trace": "agent_trace_good.json"}
  ],
  "value_bar": {
    "claim": "The new agent separates supported traces from weak traces.",
    "metric": "trace_review.score",
    "baseline": {"score": 0.42, "source": "agent_trace_bad.json"},
    "candidate": {"score": 1.0, "source": "agent_trace_good.json"},
    "minimum_delta": 0.5,
    "adversarial_review": {
      "challenge": "Known-bad traces must fail for missing tools and missing reasoning.",
      "failed_to_disprove": true,
      "open_objections": []
    }
  }
}
```

For real audits, require the Claude judge:

```bash
export ANTHROPIC_API_KEY=...
python -m claude_agent_prompting audit-agent evals/examples/agent_audit_bundle.json --claude-judge --markdown
```
