# Screenpipe MCP Tool Tuning

This audit adds a YC S26 public MCP target to the harness suite and confirms a narrow
tool-description optimization. README-level descriptions routed exact keyword lookup to broad
content search. Source-level tuned descriptions routed it to the dedicated keyword search tool.

Matrix: [screenpipe_mcp_tool_selection.json](https://github.com/cfregly/agent-harness-opt/blob/main/evals/model_matrix/screenpipe_mcp_tool_selection.json)

## Summary

| Before | After | Result |
|---|---|---|
| `readme_screenpipe_mcp` scored 0.857. Baseline focus: exact keyword uses keyword search. | `source_tuned_screenpipe_mcp` scored 1.000, a 0.143 gain. | Apply this change: Clarify that `keyword-search` is for literal terms and exact phrases. Reserve `search-content` for transcript lines, screen text, speaker or window filters, tags, memories, and broader content search. Add retained cases as regression coverage. |

## Recommended Actions

- Apply this change: Clarify that `keyword-search` is for literal terms and exact phrases. Reserve `search-content` for transcript lines, screen text, speaker or window filters, tags, memories, and broader content search.
- Add the 7 retained routing cases to upstream CI or release-blocking regression coverage.
- Keep the passing cells visible so maintainers preserve behavior that already works.

## Model Coverage

Provider/model rows are evidence lanes. The target repo actions above are the only primary CTA.

## Public Summary

- Outcome: Confirmed improvement.
- Focus: exact phrase lookup routing.
- Baseline: `readme_screenpipe_mcp` at 0.857.
- Candidate: `source_tuned_screenpipe_mcp` at 1.000.
- Delta: 0.143 against a 0.010 minimum.

<details>
<summary>LLM / Machine-readable details</summary>

## Target

- target: Screenpipe MCP
- repository: [screenpipe/screenpipe](https://github.com/screenpipe/screenpipe)
- commit: `2de07ff501a63d3d3f0f39a9a602640a833d151f`
- package: `screenpipe-mcp` 0.18.14
- checked: 2026-06-28
- YC batch: S26, from the public Screenpipe README

## Boundary

The tested slice covers local-first personal activity tools:

- broad recap routes to `activity-summary`
- exact keyword routes to `keyword-search`
- transcript or screen text with speaker/window/tag filters routes to `search-content`
- UI controls route to `search-elements`
- known frame detail routes to `frame-context`
- scheduled automation creation routes to `create-pipe`
- pipe verification routes to `pipe-logs`

## Result

The stored baseline compares README-level descriptions against the source-level tuned descriptions.
The live Anthropic prompt-JSON run produced a baseline-to-candidate delta:

- `readme_screenpipe_mcp`: 6/7
- `source_tuned_screenpipe_mcp`: 7/7

The README-level miss was:

- exact keyword lookup chose `search-content`

The source-level tuned pass was:

- exact keyword lookup chose `keyword-search`

Receipt: [screenpipe_mcp_tool_selection_2026-06-28.md](https://github.com/cfregly/agent-harness-opt/blob/main/evals/results/screenpipe_mcp_tool_selection_2026-06-28.md)

## Run It

Shortcut:

```bash
make optimize mcp=screenpipe
make optimize url=https://github.com/screenpipe/screenpipe
```

Dry plan:

```bash
make optimize-dry mcp=screenpipe
```

Underlying command:

```bash
python -m claude_agent_harness_opt model-matrix evals/model_matrix/screenpipe_mcp_tool_selection.json \
  --env-file .env \
  --live \
  --require-live \
  --providers anthropic \
  --harnesses prompt_json \
  --variants readme_screenpipe_mcp,source_tuned_screenpipe_mcp \
  --instruction-variants screenpipe_host_rules \
  --concurrency 2 \
  --markdown
```

## Why This Matters

The adversarially-confirmed to add value bar keeps this narrow. This is not a claim that Screenpipe
needs a broad catalog rewrite. The confirmed useful boundary is exact keyword search versus broader
semantic content search. Encoding that boundary protects local-activity agents from choosing a
broader retrieval path when the user gives a literal keyword or phrase.

</details>
