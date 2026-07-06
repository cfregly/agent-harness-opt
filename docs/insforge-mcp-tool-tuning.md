# InsForge MCP Tool Tuning

This page records a YC P2026 MCP optimization that cleared the
adversarially-confirmed to add value bar.

## Summary

| Before | After | Result |
|---|---|---|
| `readme_insforge_mcp` scored 0.938. Baseline focus: relative deploy path avoids tool. | `source_tuned_insforge_mcp` scored 1.000, a 0.062 gain. | Apply this change: Clarify that `create-deployment` requires an absolute `sourceDirectory` and must be avoided for relative paths, starter-template creation, deployment status lookup, or remote prepared-deployment triggering. Add retained cases as regression coverage. |

## Recommended Actions

- Apply this change: Clarify that `create-deployment` requires an absolute `sourceDirectory` and must be avoided for relative paths, starter-template creation, deployment status lookup, or remote prepared-deployment triggering.
- Add the 16 retained routing cases to upstream CI or release-blocking regression coverage.
- Keep the passing cells visible so maintainers preserve behavior that already works.

## Model Coverage

Provider/model rows are evidence lanes. The target repo actions above are the only primary CTA.

## Public Summary

- Outcome: Confirmed improvement.
- Focus: absolute-source deployment safety.
- Baseline: `readme_insforge_mcp` at 0.938.
- Candidate: `source_tuned_insforge_mcp` at 1.000.
- Delta: 0.062 against a 0.010 minimum.

<details>
<summary>LLM / Machine-readable details</summary>

## Source Pin

- Upstream repo: [InsForge/insforge-mcp](https://github.com/InsForge/insforge-mcp)
- Commit: `dad794d445d05e7df2efcb8280dba59682b97a87`
- Package: `@insforge/mcp` `1.2.10`
- Matrix: [insforge_mcp_tool_selection.json](https://github.com/cfregly/agent-harness-opt/blob/main/evals/model_matrix/insforge_mcp_tool_selection.json)
- Receipt: [insforge_mcp_tool_selection_2026-06-28.md](https://github.com/cfregly/agent-harness-opt/blob/main/evals/results/insforge_mcp_tool_selection_2026-06-28.md)

The tested catalog covers docs, SDK docs, anon token generation, container logs, backend metadata,
table schema, raw SQL, starter templates, bulk import, storage buckets, edge functions, and
deployment tools.

## Confirmed Signal

Live Anthropic prompt JSON run:

- `readme_insforge_mcp`: 15/16
- `source_tuned_insforge_mcp`: 16/16

The baseline failed the relative-path deployment boundary:

- Task: deploy the current directory `.` to InsForge.
- Baseline choice: `create-deployment`
- Tuned choice: `NO_TOOL`

The upstream source says deployment requires an absolute `sourceDirectory`. The tuned description
adds the operational boundary directly to `create-deployment`: deploy only from an absolute path,
and avoid the tool for relative paths.

## Suggested Tool Description Change

Use the tuned `create-deployment` guidance from the matrix as the upstream patch basis:

```text
Deploy or prepare upload for an existing source directory. Requires an absolute sourceDirectory
path.

Use when the user asks to deploy a local source tree and provides an absolute source directory.

Avoid for relative paths, starter-template creation, deployment status lookup, or triggering a
prepared deployment id in remote mode.
```

Keep the companion quality checks:

- Reject relative paths before calling.
- Do not include secret env var values in public artifacts.

## Reproduce

```bash
make optimize mcp=insforge OUT=evals/results/insforge_mcp_tool_selection_2026-06-28.md
```

For a narrower rerun:

```bash
python scripts/optimize_mcp.py insforge \
  --env-file .env \
  --live \
  --require-live \
  --markdown \
  --providers anthropic \
  --harnesses prompt_json \
  --cases "relative deploy path avoids tool" \
  --out /tmp/insforge-relative-deploy.md
```

</details>
