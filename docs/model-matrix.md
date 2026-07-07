# Model Matrix

The model matrix is the tuning layer for new model generations. It runs the same tool-selection
cases across provider profiles, harnesses, tool-description variants, and instruction variants.

Use it when changing:

- model id
- reasoning effort or thinking budget
- provider harness
- tool names
- tool descriptions
- argument schemas
- `CLAUDE.md`
- skills
- system prompts

> [!NOTE]
> This page starts with the human summary. Detailed eval, command, and machine-readable material is preserved below.


## Why It Exists

Models do not read tool descriptions the same way. A description that works for one model can fail
on another model, or fail when moved from prompt JSON to native tool calling. The matrix makes that
visible before a prompt or tool change is promoted.

The pass bar is still adversarially-confirmed to add value. A tuned description should beat the
baseline on realistic cases, survive held-out cases, and avoid regressions on direct easy cases.

This repo treats the harness as a variable, not background plumbing. A harness can be provider
native tool calling, a prompt JSON wrapper, an Agent SDK loop, an IDE agent, or any runtime that can
export the same trace contract. The useful question is whether a model plus harness chooses the
right tool, passes the right arguments, reasons visibly between tool calls, and uses tool outputs
before the final answer.

For ProofPlane pilots, the matrix result is upstream harness behavior evidence.
It can support a runtime lane in the Customer Workflow Proof Pack, but it is not
GPU workload proof or hosted readiness proof. See
[ProofPlane Evidence Role](https://github.com/cfregly/agent-harness-opt/blob/main/docs/proofplane-evidence-role.md).

## Included Matrix

`evals/model_matrix/coding_tool_selection.json` tests Claude Code style tools:

- `Task`: broad delegated investigation
- `Glob`: file path discovery
- `Grep`: content search
- `Read`: exact file read

The hard cases distinguish `Task` from `Grep`. Short descriptions often make models pick `Grep` for
broad investigation. Tuned descriptions state when to delegate to `Task` and when to stay with direct
file tools.

`evals/model_matrix/harness_trace_adapters.json` tests exported runtime traces as named harnesses:

- `agent_sdk_trace`: normalized Agent SDK style event exports
- `cursor_trace`: normalized IDE-agent style event exports
- `trace_fixture`: keyless provider that reads saved event files through an adapter

This matrix proves that exported harness runs can enter the same tool-selection contract as live
provider calls. It is also the smoke test for adapter changes.

<details>
<summary>LLM / Machine-readable details</summary>

## Commands

Dry run:

```bash
python -m claude_agent_harness_opt model-matrix evals/model_matrix/coding_tool_selection.json --markdown
```

Smoke test one provider and a few cases:

```bash
python -m claude_agent_harness_opt model-matrix evals/model_matrix/coding_tool_selection.json \
  --env-file .env \
  --live \
  --require-live \
  --providers anthropic \
  --harnesses native_tools \
  --variants tuned_boundaries \
  --instruction-variants boundary_rules \
  --max-cases 2 \
  --markdown
```

Full local sweep:

```bash
python -m claude_agent_harness_opt model-matrix evals/model_matrix/coding_tool_selection.json \
  --env-file .env \
  --live \
  --require-live \
  --concurrency 8 \
  --markdown
```

Write JSON for review artifacts:

```bash
python -m claude_agent_harness_opt model-matrix evals/model_matrix/harness_trace_adapters.json \
  --providers trace_fixture \
  --harnesses agent_sdk_trace \
  --max-cases 1 \
  --out /tmp/harness-matrix.json
python -m claude_agent_harness_opt render-report /tmp/harness-matrix.json --out /tmp/harness-matrix.html
python -m claude_agent_harness_opt pr-comment /tmp/harness-matrix.json --out /tmp/harness-matrix.md
```

Adapter smoke test:

```bash
python -m claude_agent_harness_opt model-matrix evals/model_matrix/harness_trace_adapters.json \
  --live \
  --require-live \
  --providers trace_fixture \
  --harnesses agent_sdk_trace,cursor_trace \
  --variants exported_trace_tools \
  --instruction-variants exported_trace \
  --markdown
```

Hill-climb one hard boundary from a baseline:

```bash
python -m claude_agent_harness_opt grind-harness evals/model_matrix/coding_tool_selection.json \
  --env-file .env \
  --live \
  --require-live \
  --providers anthropic,openai,gemini \
  --harnesses native_tools,prompt_json \
  --instruction-variants boundary_rules \
  --cases "investigate trace review flow,map model matrix implementation" \
  --heldout-cases "find python files,read known file" \
  --min-improvement 0.05 \
  --concurrency 8 \
  --max-live-calls 60 \
  --markdown
```

`grind-harness` runs the baseline, creates a candidate tool-description variant from the failed
cases, reruns the selected cells, confirms held-out cells, and promotes only if the live score
improves by the configured threshold without held-out regression. Dry runs are useful for checking
scope and call counts, but they do not satisfy the value bar.

This is the repo's autoresearch-style loop. It uses evals as the optimization surface and the
experiment log as the research record. Each iteration says which candidate was kept or rejected and
why.

## Reading Results

The report has one row per case and a cell summary grouped by:

- provider
- harness
- tool-description variant
- instruction variant

Use the cell summary to isolate the cause:

- If only one provider fails, tune the provider profile or model-specific instructions.
- If native tools fail but prompt JSON passes, tune provider tool schemas.
- If baseline fails and tuned passes, promote the tuned tool descriptions after held-out checks.
- If both variants fail, add harder schema guidance or split the tool.
- If instruction variants change the score, tune `CLAUDE.md`, skill instructions, or system prompt text.
- If trace fixture harnesses fail, fix the adapter or trace instrumentation before tuning prompts.

Use the same loop for `CLAUDE.md` and skill updates:

1. Add a narrow instruction variant that represents the proposed `CLAUDE.md` or skill wording.
2. Run a dry matrix to confirm the selected cells.
3. Run a live matrix or harness grind with `.env`.
4. Promote only when the candidate beats the baseline on target cells and does not regress held-out
   cells.
5. Add the failure as a named case so the next model generation can be retested.

## Live Result From June 24, 2026

Using local Anthropic, OpenAI, and Gemini keys, the historical smoke matrix was run against:

- Anthropic `claude-sonnet-4-5`
- OpenAI `gpt-4.1`
- Gemini `gemini-2.5-pro`

Native tool harness:

- `baseline_short`: 72 of 84 passed
- `tuned_boundaries`: every provider and instruction variant scored 7 of 7

Prompt JSON harness:

- `baseline_short`: 73 of 84 passed
- `tuned_boundaries`: every provider and instruction variant scored 7 of 7

The repeated failure was the same useful one: short descriptions made models choose `Grep` for broad
repository investigation tasks that should use `Task`. Tuned boundary descriptions fixed that across
all three providers and both harnesses.

Gemini `prompt_json` initially failed because `maxOutputTokens` was too small for `gemini-2.5-pro`.
Increasing the profile output budget to 4096 removed those harness errors.

This was a useful first pass, not a comprehensive frontier sweep. Current target matrices should
separate model profiles by tier:

- frontier profiles for the strongest available model in a provider family
- high profiles for expensive, capable models that are stable enough for repeated sweeps
- balanced profiles for cheaper regression runs and CI-sized checks

The gstack target currently includes these named profiles:

- `anthropic-fable-frontier`
- `anthropic-opus-high`
- `anthropic-sonnet-balanced`
- `openai-gpt55-frontier`
- `openai-gpt54-high`
- `openai-gpt41-balanced`
- `gemini-31-pro-customtools-frontier`
- `gemini-25-pro-high`

Use a provider filter such as `--providers anthropic` to run every Anthropic profile. Use a named
profile such as `--providers anthropic-opus-high` when the run should isolate one model. Upstream
claims should say which profile tier was used and should not imply a whole-provider conclusion from a
single balanced-model run.

## Harness Grind Result From June 24, 2026

Using local Anthropic, OpenAI, and Gemini keys, `grind-harness` was run on the two broad
investigation cases that distinguish `Task` from `Grep`.

Selected cells:

- providers: Anthropic, OpenAI, Gemini
- harnesses: native tools and prompt JSON
- instruction variant: `boundary_rules`
- baseline variant: `baseline_short`

Result:

- baseline: 1 of 12 passed
- candidate: 12 of 12 passed
- improvement: 0.917
- promoted: yes
- value bar passed: yes

The repeated failure was that short descriptions made models choose `Grep` for broad repository
investigation. The generated candidate sharpened the `Task` boundary and passed all selected live
provider and harness cells.

</details>
