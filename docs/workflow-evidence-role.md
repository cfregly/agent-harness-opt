# Optional Integration Note

agent-harness-opt stands on its own as a harness behavior workbench. Use it to
test whether a model, runtime, prompt, and tool surface choose the right tools,
pass the right arguments, expose reviewable traces, and clear held-out behavior
checks before a change is promoted.

## Local Concepts

- Harness behavior evidence: a named model/runtime/tool surface, the risky
  behavior it is expected to handle, and the cases that exercise that boundary.
- Model-matrix receipt: a baseline-versus-candidate result across providers,
  harnesses, tool-description variants, instruction variants, and held-out
  cases.
- Trace review: a normalized record of tool calls, arguments, outputs, visible
  decision notes, verification, and final state.
- Harness optimization packet: the smallest measured prompt, tool, schema, or
  harness change that improves a failing baseline without regressing held-out
  cases.
- Retained evidence bundle: result summaries, reproduction commands, matrix
  inputs, raw receipts, and packet metadata kept in this repo.

## Non-Claims

This repo does not prove hosted workflow authority, customer workload verdicts,
GPU performance, workload cost, backend correctness, device-level parity, or
production readiness. It proves only the model and harness behavior represented
by the retained local evidence.

## Optional Workflow Mapping

When a wider workflow proof system consumes this repo, treat agent-harness-opt
output as runtime-lane evidence. It can support a customer workflow proof pack
by showing that the model and harness layer chose tools correctly, produced
reviewable traces, and passed regression cases before the workflow is governed
elsewhere.

The mapping is intentionally loose:

```text
agent-harness-opt retained harness evidence
  -> workflow proof pack runtime-lane confidence
  -> optional workload or backend evidence layers
```

The consuming workflow system owns workflow authority, replay, hosted evidence,
gates, and promotion. Workload and backend layers own their own performance,
cost, correctness, and readiness claims.
