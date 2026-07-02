# YC P2026 MCP Sweep

This page tracks the YC Spring/P2026 MCP surfaces found during the public sweep and whether their
tool descriptions produced an adversarially-confirmed to add value improvement.

## Summary

| Company | Exact change | Before | After | Result |
|---|---|---|---|---|
| InsForge | Require an absolute `sourceDirectory`. Reject relative paths before calling `create-deployment`. | README-level descriptions passed 15/16 but called `create-deployment` for a relative source path. | Relative paths stop before `create-deployment`. | Source-tuned descriptions passed 16/16 and chose `NO_TOOL` for the same request. |
| Humwork | No wording change promoted from this slice. | README-level descriptions passed 7/7 on the tested expert-consultation and no-tool cases. | Keep current wording and retain the cases. | Skill-tuned descriptions also passed 7/7. Guardrail only. |
| OpenWork | No wording change promoted from this slice. | Docs-level descriptions passed 7/7 on the tested UI bridge and no-tool cases. | Keep current wording and retain the cases. | Source-tuned descriptions also passed 7/7. Guardrail only. |
| Screenpipe | Treat this as a broader YC S26/public-MCP action, not a Spring/P2026 result: route exact phrases to `keyword-search`. | README-level descriptions passed 6/7 but routed exact keyword lookup to `search-content`. | Exact keyword lookup routes to `keyword-search`. | Source-level tuned descriptions passed 7/7. |

## Implemented Targets

| Company | Public MCP Surface | Matrix | Live Result |
|---|---|---|---|
| InsForge | [InsForge/insforge-mcp](https://github.com/InsForge/insforge-mcp) | [insforge_mcp_tool_selection.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/model_matrix/insforge_mcp_tool_selection.json) | Confirmed improvement. README-level relative deploy path chose `create-deployment`, tuned chose `NO_TOOL`. |
| Humwork | [humworkai/humwork-mcp](https://github.com/humworkai/humwork-mcp) | [humwork_mcp_tool_selection.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/model_matrix/humwork_mcp_tool_selection.json) | Guardrail. README-level and skill-tuned variants both passed 7/7. |
| OpenWork | [different-ai/openwork](https://github.com/different-ai/openwork), package `openwork-ui-mcp` | [openwork_ui_mcp_tool_selection.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/model_matrix/openwork_ui_mcp_tool_selection.json) | Guardrail. Docs-level and source-tuned variants both passed 7/7. |

## Commands

Run the stored YC P2026 targets:

```bash
make optimize mcp=insforge
make optimize mcp=humwork
make optimize mcp=openwork
```

Run a dry check before spending provider calls:

```bash
make optimize-dry mcp=insforge MAX_CASES=2
```

Run a repo URL directly:

```bash
make optimize url=https://github.com/InsForge/insforge-mcp
```

Unknown URLs fail instead of falling back to another matrix.

## Live Results

InsForge:

- Anthropic prompt JSON: README-level 15/16, source-tuned 16/16.
- Baseline failure: relative path deployment request chose `create-deployment`.
- Tuned fix: require absolute `sourceDirectory`, and choose `NO_TOOL` for relative deploy paths.
- Receipt: [insforge_mcp_tool_selection_2026-06-28.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/insforge_mcp_tool_selection_2026-06-28.md).

Humwork:

- Anthropic prompt JSON: README-level 7/7, skill-tuned 7/7.
- Covered expert consultation start, active session follow-up, message retrieval, close, rating,
  basic-docs no-tool, and secrets no-tool.
- Receipt: [humwork_mcp_tool_selection_2026-06-28.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/humwork_mcp_tool_selection_2026-06-28.md).

OpenWork:

- Anthropic prompt JSON: docs-level 7/7, source-tuned 7/7.
- Covered status, snapshot, action listing, known action execution, unknown action discovery,
  coordinate-click no-tool, and app-closed status check.
- Receipt: [openwork_ui_mcp_tool_selection_2026-06-28.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/openwork_ui_mcp_tool_selection_2026-06-28.md).

## Related Non-P2026 Result

Screenpipe is a confirmed public MCP improvement, but public sources identify it as YC S26 rather
than Spring/P2026. Keep it in the broader public MCP sweep and founder packets. Do not count it as a
Spring/P2026 deck win.

- Anthropic prompt JSON: README-level 6/7, source-tuned 7/7.
- Receipt: [screenpipe_mcp_tool_selection_2026-06-28.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/screenpipe_mcp_tool_selection_2026-06-28.md).

```bash
make optimize mcp=screenpipe
```

## Searched But Not Testable

The deck-priority YC Spring/P2026 companies below were searched for public MCP catalogs. I did not
find a public server or tool list with enough concrete callable descriptions to build a fair matrix:

- Sazabi
- Tasklet
- Complir
- Arga Labs
- Silmaril
- Superset
- Lightsprint
- 9 Mothers
- Adialante
- Dispatch
- Ploy

Do not describe these as optimized. The honest deck line is that they are candidate workloads, while
the confirmed Spring/P2026 public MCP optimization is
[InsForge](https://github.com/cfregly/claude-agent-harness-opt/tree/main/docs/findings/insforge).
Humwork and OpenWork are useful guardrails because their public descriptions already routed
correctly on the tested Anthropic slice. Screenpipe is confirmed but belongs in the broader YC S26
or public MCP story, not the Spring/P2026 count.

One adjacent public MCP candidate, [Mireye](https://github.com/Mireye-Labs/mireye-earth-mcp), was
excluded from this Spring/P2026 sweep after checking the current YC batch label because it is not in
the requested Spring/P2026 set.

## Also Checked This Pass

These were not added to the matrix set:

- Armature, Glen, Scope, Clara, and Zenbu: searched for public MCP repos or callable catalogs, none
  found.
- [Kinro MCP server](https://github.com/Guru6163/kinro-mcp-server): public repo found, but it is not
  attributable to the YC company from the public repo metadata.
- [OptionsAhoy MCP](https://github.com/AlvisoOculus/optionsahoy-mcp): public repo found, but no
  confirmed Spring/P2026 attribution was found in this pass.
