# Zymtrace MCP Frontier All-Provider Attempt - 2026-07-01

Passed: no
Live: yes

This is the retained historical all-provider frontier attempt. It includes Anthropic `claude-opus-4-8`, OpenAI `gpt-5.5`, and Gemini `gemini-3.1-pro-preview-customtools`. The run is intentionally retained as descent evidence because the initial all-provider attempt hit Anthropic API-credit exhaustion and the frontier prompt-JSON harness exposed additional parser and routing failures. Current Anthropic MCP coverage is superseded by the separate Opus receipt with 118 passed, 18 failed, and 0 errors.

## Matrix Summary

- total: 408
- passed_cases: 210
- failed_cases: 89
- errors: 109
- skipped: 0
- score: 0.515

## Status By Profile

| Profile | Model | Passed | Failed | Errors |
|---|---|---:|---:|---:|
| `anthropic-opus48-frontier` | `claude-opus-4-8` | 105 | 12 | 19 |
| `gemini-31-pro-customtools-frontier` | `gemini-3.1-pro-preview-customtools` | 31 | 24 | 81 |
| `openai-gpt55-frontier` | `gpt-5.5` | 74 | 53 | 9 |

## Blockers

- Anthropic `claude-fable-5` was unavailable to the provided key during smoke testing, so the all-provider attempt used accessible `claude-opus-4-8`.
- Historical note: Anthropic API-credit exhaustion stopped many `claude-opus-4-8` cells during the initial all-provider attempt. The separate current Opus receipt supersedes this Anthropic lane for MCP coverage.
- This all-provider attempt is not the promoted improvement receipt; it is retained failure-discovery evidence.

## Machine-readable Receipt

[JSON receipt](https://github.com/cfregly/agent-harness-opt/blob/main/evals/results/zymtrace_mcp_frontier_all_providers_attempt_2026-07-01.json)
