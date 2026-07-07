# ProofPlane Evidence Role

agent-harness-opt is the model, tool, and harness behavior proof layer for a
ProofPlane pilot. It validates whether a model/runtime/harness combination can
choose the right tools, expose reviewable traces, and clear held-out behavior
checks before that workflow is trusted inside ProofPlane.

## Inputs

- Tool names, descriptions, and argument schemas.
- Prompt and instruction variants.
- Provider harnesses such as native tool calling, prompt JSON wrappers, Agent
  SDK loops, IDE agents, and CLI runtimes.
- Exported traces and normalized runtime events.
- Model-matrix cases that represent the risky workflow boundary.

## Outputs

- Model-matrix receipts showing baseline and candidate behavior.
- Trace reviews that show tool calls, arguments, outputs, and visible decision
  notes.
- Harness optimization packets that promote only measured improvements.
- Retained evidence bundles with reproduction commands and result summaries.

## ProofPlane Boundary

Use this repo before or during a ProofPlane pilot when the question is model or
harness behavior: tool choice, trace quality, prompt wording, provider wrapper
behavior, or regression across model/runtime lanes.

The output can support a ProofPlane Customer Workflow Proof Pack as runtime-lane
confidence. It does not replace ProofPlane receipts. ProofPlane still owns
workflow authority, replay, hosted evidence, gates, and promotion.

This repo also does not prove GPU performance, workload cost, macro-kernel
backend correctness, hosted readiness, or customer workload verdicts. Those
claims belong to the workload or backend evidence layers.

## Cross-Project Contract

The expected chain is:

```text
agent-harness-opt harness evidence
  -> ProofPlane Customer Workflow Proof Pack
  -> gpu-perf-tune workload proof packet
  -> optional macro-kernel backend/device artifacts
```

The canonical cross-project boundary lives in the
[ProofPlane evidence contract](https://github.com/cfregly/macro-harness/blob/main/docs/evidence-contract.md).
Use [gpu-perf-tune](https://github.com/cfregly/gpu-perf-tune/blob/main/docs/workload-proof-packet.md)
for workload-level GPU and inference evidence. Use macro-kernel backend artifacts
only after their native B200 gates pass and they are packaged through a workload
proof packet.
