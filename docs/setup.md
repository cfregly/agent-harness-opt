# Setup

This repo has three audit layers:

1. Deterministic checks that run without a network call.
2. Live Claude judge checks that require `ANTHROPIC_API_KEY`.
3. Live model and harness sweeps that use provider keys from `.env`.

Use both for real audits. The deterministic layer catches structure and regression failures. Claude
judges semantic quality, tool-output use, tool-description quality, and whether the trace adds value
over the baseline.

> [!NOTE]
> This page starts with the human summary. Detailed eval, command, and machine-readable material is preserved below.


## Install

```bash
git clone https://github.com/cfregly/agent-harness-opt.git
cd agent-harness-opt
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Local Claude Judge

```bash
cp .env.example .env
$EDITOR .env
python -m claude_agent_harness_opt audit-agent evals/examples/agent_audit_bundle.json --claude-judge
python -m claude_agent_harness_opt optimize-tools evals/examples/agent_audit_bundle.json --claude-judge
python -m claude_agent_harness_opt model-matrix evals/model_matrix/coding_tool_selection.json --env-file .env --live --concurrency 8
python -m claude_agent_harness_opt grind-harness evals/model_matrix/coding_tool_selection.json --env-file .env --live --concurrency 8 --heldout-cases "find python files,read known file" --min-improvement 0.05 --markdown
```

Do not commit `.env` files or API keys. The repo ignores local environment files. Commit only
`.env.example`.

<details>
<summary>LLM / Machine-readable details</summary>

## GitHub Actions

Set a repository secret named `ANTHROPIC_API_KEY`.

```bash
gh secret set ANTHROPIC_API_KEY --repo cfregly/agent-harness-opt
```

CI runs deterministic tests, the value-bar gate, the trace suite, the agent audit, and live Claude
judge checks. The live audit includes trace quality, tool-selection optimization, an Anthropic
model-matrix smoke test, and a live harness grind that must beat the short-description baseline.

## Trace Capture Contract

Export each agent run as JSON with ordered steps:

```json
{
  "name": "example_trace",
  "task": "Answer a research question with tools.",
  "rubric": {
    "required_tools": ["web_search", "web_fetch"],
    "forbidden_tools": ["send_email"],
    "required_final_contains": ["evidence", "uncertain"],
    "require_directed_initial_reasoning": true,
    "require_directed_after_tool_reasoning": true,
    "pass_score": 1.0
  },
  "steps": [
    {
      "type": "reasoning",
      "summary": "This is a standard research task. Budget two tool calls and stop when enough source evidence is found."
    },
    {"type": "tool_call", "id": "call_1", "name": "web_search", "args": {"query": "source query"}},
    {"type": "tool_result", "tool_call_id": "call_1", "ok": true, "output": "Tool output text."},
    {
      "type": "reasoning",
      "summary": "The source output is relevant evidence. Verification is needed through fetch before continuing."
    },
    {"type": "final", "text": "Final answer grounded in observed tool outputs."}
  ]
}
```

For parallel calls, add the same `parallel_group` value to the related calls and results. The
reviewer then expects one reasoning step after the batch before the next action.

For Agent SDK loops or IDE agents, normalize the raw runtime export first:

```bash
python -m claude_agent_harness_opt normalize-runtime evals/examples/cursor_trace_review_events.json
python -m claude_agent_harness_opt model-matrix evals/model_matrix/harness_trace_adapters.json --live --require-live --providers trace_fixture
```

## Audit Bundle Contract

Use an audit bundle when reviewing a full agent:

```json
{
  "name": "sample agent audit",
  "tools": [
    {
      "name": "web_search",
      "purpose": "Find candidate sources and fresh facts from the public web.",
      "use_when": "Use for unknown, current, or broad questions where source discovery is required.",
      "avoid_when": "Avoid when a known source URL should be fetched directly.",
      "input_schema": {
        "properties": {
          "query": "Specific query with entity, metric, and time frame.",
          "response_format": "concise or detailed"
        },
        "required": ["query"]
      },
      "output_schema": {"results": "Ranked sources with title, url, snippet, and date."},
      "context_controls": ["response_format", "query specificity"],
      "error_guidance": "If the query is too broad, suggest a narrower entity or time frame.",
      "quality_checks": ["Prefer primary sources.", "Compare snippets before fetching."]
    }
  ],
  "tool_selection_cases": [
    {
      "name": "discover unknown current sources",
      "task": "Find current cargo specifications for a vehicle model.",
      "expected_tools": ["web_search"],
      "forbidden_tools": ["web_fetch"],
      "rationale": "The task starts without a known URL, so source discovery comes first.",
      "verifier": {"type": "flexible_text", "must_include_any": [["cargo volume"], ["source"]]}
    }
  ],
  "heldout_tool_selection_cases": [
    {
      "name": "discover then compute",
      "task": "Estimate a quantity when required facts are unknown.",
      "valid_tool_paths": [["web_search", "web_fetch", "calculator"], ["web_search", "calculator"]],
      "verifier": {"type": "flexible_text", "must_include_any": [["estimate"], ["source"]]}
    }
  ],
  "tool_metrics": {
    "avg_runtime_ms": 1800,
    "avg_tool_calls": 4,
    "token_count": 4200,
    "tool_error_rate": 0
  },
  "traces": [{"name": "representative trace", "trace": "agent_trace_good.json"}],
  "value_bar": {
    "claim": "The audit harness separates a supported trace from a weak trace.",
    "metric": "trace_review.score",
    "baseline": {"score": 0.42, "source": "agent_trace_bad.json"},
    "candidate": {"score": 1.0, "source": "agent_trace_good.json"},
    "minimum_delta": 0.5,
    "adversarial_review": {
      "reviewer": "agent trace regression suite",
      "challenge": "Known-bad trace must fail.",
      "failed_to_disprove": true,
      "open_objections": []
    }
  }
}
```

Run:

```bash
python -m claude_agent_harness_opt audit-agent evals/examples/agent_audit_bundle.json --markdown
python -m claude_agent_harness_opt audit-agent evals/examples/agent_audit_bundle.json --claude-judge
python -m claude_agent_harness_opt optimize-tools evals/examples/agent_audit_bundle.json --markdown
```

## Where The Evals Are

- `evals/examples/search_answer.json` checks answer accuracy.
- `evals/examples/tool_use.json` checks tool-use accuracy.
- `evals/examples/final_state.json` checks final-state accuracy.
- `evals/examples/agent_trace_good.json` is the sequential passing trace.
- `evals/examples/agent_trace_parallel_good.json` is the parallel passing trace.
- `evals/examples/agent_trace_bad.json` is the known-bad negative control.
- `evals/suites/agent_trace_suite.json` runs trace regression cases.
- `evals/examples/agent_audit_bundle.json` ties tools, traces, selection cases, and value proof together.
- `evals/model_matrix/coding_tool_selection.json` runs provider, harness, instruction, and tool-description sweeps.
- `evals/model_matrix/harness_trace_adapters.json` checks exported Agent SDK and IDE-agent runs as named harnesses.

Use `docs/harness-optimization.md` when adding a new Agent SDK, IDE agent, or Cursor-like harness.
The new harness should export the trace contract first, then enter the matrix as a named harness.

</details>
