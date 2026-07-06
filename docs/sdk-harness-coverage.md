# SDK Harness Coverage

Checked on 2026-06-25.

This repo now separates terminal products from SDK harnesses.

For the public, versioned explanation of how the SDK harnesses work, including
examples and maintenance steps, see [Agent SDK Harnesses](https://github.com/cfregly/agent-harness-opt/blob/main/docs/agent-sdk-harnesses.md).

| Vendor | Product or SDK | What is covered |
|---|---|---|
| Anthropic | Claude Code | Headless CLI harness via `claude -p --output-format stream-json --verbose` |
| Anthropic | Claude Agent SDK | Python package `claude-agent-sdk`, formerly Claude Code SDK |
| OpenAI | OpenAI Agents SDK | Python package `openai-agents` |
| Google | Agent Development Kit | Python package `google-adk` |
| Google | Gemini CLI | Headless CLI harness via `gemini --output-format stream-json` |

Anthropic did not rename Claude Code. The SDK was renamed from Claude Code SDK to Claude Agent SDK
because the same harness is useful outside coding workflows. Claude Code remains the product. Claude
Agent SDK is the library version of the Claude Code loop and capabilities.

## Latest Package Resolution

The SDK live spec uses `uvx --refresh-package` for every run. That forces a fresh package resolution
instead of relying on a previously-created virtual environment.

```bash
python -m claude_agent_harness_opt live-harness \
  evals/live_harnesses/sdk_agent_smoke.json \
  --env-file .env \
  --out-dir /tmp/aho-sdk-live-v2/artifacts \
  --out /tmp/aho-sdk-live-v2/result.json
```

Committed summary ledger:
`evals/results/sdk_agent_smoke_2026-06-25.json`

## Live SDK Result

| Harness | Package | Version resolved by `uvx --refresh-package` | Status | Tool | Directed thinking |
|---|---|---:|---|---|---|
| `claude_agent_sdk_python_latest` | `claude-agent-sdk` | `0.2.110` | pass | `mcp__aho__pwd_tool` | pass |
| `openai_agents_sdk_python_latest` | `openai-agents` | `0.17.7` | pass | `pwd_tool` | pass |
| `google_adk_python_latest` | `google-adk` | `2.3.0` | pass | `pwd_tool` | pass |

Summary from `/tmp/aho-sdk-live-v2/result.json`:

```json
{
  "directed_thinking_visible": 3,
  "errors": 0,
  "failed": 0,
  "not_installed": 0,
  "passed": 3,
  "planned": 0
}
```

## SDK Surface Inventory

The live smoke proves the agent loop works. The inventory check pins the broader SDK surfaces that
need deeper evals, using the same latest-package discipline:

```bash
uvx --with claude-agent-sdk --with openai-agents --with google-adk \
  python scripts/sdk_surface_inventory.py \
  > evals/results/sdk_surface_inventory_2026-06-25.json
```

Committed summary ledger:
`evals/results/sdk_surface_inventory_2026-06-25.json`

The inventory passed for:

- `claude-agent-sdk` `0.2.110`: agent loop, MCP servers, permissions, hooks, skills/plugins,
  subagents, sessions, thinking/budget controls, and Claude Code bridge options.
- `openai-agents` `0.17.7`: agent loop, function tools, MCP servers, handoffs, guardrails,
  sessions, tracing, hosted tools, shell tools, and computer tools.
- `google-adk` `2.3.0`: agent loop, workflows, tools and tool callbacks, sessions, memory,
  multi-agent transfer controls, planners, code execution, telemetry, and evaluation modules.

## What The Smoke Proves

Each SDK executed a custom `pwd_tool` through the SDK agent loop. The normalized trace required:

- one tool call
- matching tool result
- final answer with `HARNESS_OK`
- visible before-tool decision note with complexity, tool budget, evidence, and stop criteria
- visible after-tool decision note with quality, verification, and stop decision

This does not prove full feature coverage for every SDK. It proves the basic loop can be exercised
live, version-pinned, and normalized into the same trace contract used by CLI harnesses. Deeper SDK
coverage should add separate cases for approvals, MCP servers, subagents or handoffs, sessions,
guardrails, tracing, skills, and hosted or managed runtime features.

## Coverage Gaps To Add

| SDK | Next live cases |
|---|---|
| Claude Agent SDK | permissions, hooks, skills, subagents, session resume, checkpoints, cost and usage |
| OpenAI Agents SDK | handoffs, guardrails, sessions, MCP servers, tracing export, hosted tools, local shell tool |
| Google ADK | callbacks, tool error recovery, multi-agent transfer, evaluation, deployment and tracing |

These should be added as separate live cases because each feature changes the harness surface. A
single `pwd_tool` smoke should not be overclaimed as complete SDK parity.

## Sources

- [Claude Agent SDK overview](https://code.claude.com/docs/en/agent-sdk/overview)
- [Claude Agent SDK Python reference](https://code.claude.com/docs/en/agent-sdk/python)
- [Migrate to Claude Agent SDK](https://code.claude.com/docs/en/agent-sdk/migration-guide)
- [OpenAI Agents SDK guide](https://developers.openai.com/api/docs/guides/agents)
- [OpenAI Agents SDK Python reference](https://openai.github.io/openai-agents-python/agents/)
- [Google Agent Development Kit](https://adk.dev/)
- [Google ADK Cloud docs](https://docs.cloud.google.com/gemini-enterprise-agent-platform/build/adk)
