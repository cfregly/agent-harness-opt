# Live Harness Hardening

Checked on 2026-06-25.

This repo tests harnesses as first-class systems. A harness is the CLI, SDK, IDE agent, prompt
wrapper, approval mode, sandbox, tool registry, output format, and trace exporter that sits around a
model. Tool descriptions can be good and still fail if the harness hides reasoning, mis-shapes tool
arguments, drops tool results, blocks auth, or exports traces that cannot be reviewed.

## Command

```bash
python -m claude_agent_harness_optimization live-harness \
  evals/live_harnesses/headless_cli_smoke.json \
  --env-file .env \
  --out-dir /tmp/aho-live-suite-v3/artifacts \
  --out /tmp/aho-live-suite-v3/result.json
```

The runner writes redacted stdout, stderr, combined logs, and normalized traces. It records
environment variable names loaded from `.env`, but not secret values.

## Live Result

Latest coherent full run artifact root: `/tmp/aho-live-suite-v3/artifacts`

Committed summary ledger:
`evals/results/live_harness_headless_cli_smoke_2026-06-25.json`

| Harness | Version observed | Baseline smoke | Directed decision-note case | Tool calls | Tool result | Marker |
|---|---|---|---|---:|---|---|
| Codex CLI `codex exec --json` | `codex-cli 0.142.0` | pass, no visible reasoning | pass, strict reasoning visible | 1 per case | yes | present |
| Claude Code stream JSON | `2.1.179 (Claude Code)` | pass, no visible reasoning | pass, strict reasoning visible | 1 per case | yes | present |
| Gemini CLI stream JSON | `0.46.0` | pass, no visible reasoning | pass, strict reasoning visible | 1 per case | yes | present |
| Cursor Agent stream JSON | `32c684dc5c8a0e364043db77d4e5b9a5dc1e2d3b` | auth failed | auth failed | 0 | no | missing |
| OpenCode run logs | `0.3.133` | pass, no visible reasoning | pass, no visible reasoning | 1 per case | yes | present |

Summary from `/tmp/aho-live-suite-v3/result.json`:

```json
{
  "directed_thinking_visible": 3,
  "errors": 2,
  "failed": 0,
  "not_installed": 0,
  "passed": 8,
  "planned": 0
}
```

## Backing Data

The baseline smoke task was deliberately small:

```text
Run exactly one shell command: pwd. Then answer with HARNESS_OK <harness> and the command output.
```

The directed reasoning task adds visible decision-note instrumentation:

```text
Before using a tool, write exactly one line beginning with DECISION_NOTE_BEFORE that mentions
complexity, tool budget, evidence needed, and stop criteria. Then run exactly one shell command:
pwd. After the tool result and before the final answer, write exactly one line beginning with
DECISION_NOTE_AFTER that mentions result quality, verification, and the continue or stop decision.
Then answer with HARNESS_OK <harness> and the command output.
```

Observed normalized traces:

| Harness | Normalized call | Args signal | Directed case reasoning signal |
|---|---|---|---|
| Codex CLI | `Bash` | `"/bin/zsh -lc pwd"` | before note and after note both satisfy the strict rubric |
| Claude Code | `Bash` | `"command": "pwd"` | before note and after note both satisfy the strict rubric |
| Gemini CLI | `run_shell_command` | `"command": "pwd"` | before note and after note both satisfy the strict rubric after buffering stream deltas |
| OpenCode | `Bash` | `"command": "pwd", "timeout": 60000` | no decision notes preserved in the normalized text-log trace |

The strict directed-thinking rubric fails the baseline smoke for each passing harness because no
visible reasoning step is exported before the first tool call or after the tool result. The failing
checks are:

- before-first-tool reasoning did not classify complexity
- before-first-tool reasoning did not name a tool-call budget
- before-first-tool reasoning did not define evidence or stop criteria
- after-tool reasoning did not assess result quality
- after-tool reasoning did not address verification
- after-tool reasoning did not make a continue or stop decision

This does not mean the models failed to think. It means baseline harness configurations do not
export reviewable reasoning summaries for this run. The directed case confirms that Codex, Claude
Code, and Gemini can clear the rubric when explicitly instrumented. OpenCode still needs a better
prompt, output mode, or adapter to preserve the decision notes.

## What To Optimize

First optimization target: make directed-reasoning instrumentation part of each harness recipe. A
promoted harness change must clear both bars:

- tool-use smoke still passes with the same or lower tool-call count
- strict directed-thinking review passes without leaking private chain-of-thought

Second optimization target: OpenCode decision-note capture. The live tool-use path passes, but the
current text-log trace does not preserve visible before/after reasoning.

Third optimization target: Cursor Agent authentication. It is installed and version-pinned, but the
headless CLI returned a sign-in prompt. The current status is a measured auth failure, not an
untested harness.

## Installed Harness Inventory

Checked locally on 2026-06-25:

| CLI | Status |
|---|---|
| `codex` | installed |
| `claude` | installed |
| `gemini` | installed |
| `cursor-agent` | installed, not authenticated |
| `cursor` | installed |
| `opencode` | installed |
| `aider` / `aider-chat` | not installed |
| `goose` / `goose-cli` | not installed |
| `amp` | not installed |
| `qwen` | not installed |

No live quality claim is made for not-installed harnesses. Add them to
`evals/live_harnesses/headless_cli_smoke.json` only when the command can be run and its output can
be normalized or explicitly recorded as a measured install/auth failure.

## Sources

- [Codex manual](https://developers.openai.com/codex/codex-manual.md)
- [Claude Code CLI reference](https://code.claude.com/docs/en/cli-reference)
- [Claude Code headless mode](https://code.claude.com/docs/en/headless)
- [Gemini CLI docs](https://developers.google.com/gemini-code-assist/docs/gemini-cli)
- [Cursor CLI headless mode](https://cursor.com/docs/cli/headless)
- [Cursor CLI output format](https://cursor.com/docs/cli/reference/output-format)
- [OpenCode CLI docs](https://opencode.ai/docs/cli/)
