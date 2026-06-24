# Video Coverage Audit

Checked against the English subtitles for
[Prompting for Agents | Code w/ Claude](https://www.youtube.com/watch?v=XSZP9GhhuAc) on
2026-06-24.

The pass bar remains adversarially-confirmed to add value: each claimed coverage point must map to
code, tests, docs, or CI.

## Coverage

| Talk point | Repo coverage |
| --- | --- |
| Agents are models using tools in a loop. | Trace schema records ordered `reasoning`, `tool_call`, `tool_result`, and `final` events. |
| Agents update decisions from tool-call results. | `trace_review.py` requires reasoning after tool results and quality or evidence assessment before the next action. |
| Use agents when task path is ambiguous but valuable and recoverable. | `suitability.py` scores complexity, ambiguity, value, viability, error cost, and recoverability. |
| Think like the agent by inspecting tool names, schemas, and outputs. | `lint-tools` checks tool names and descriptions. `audit-agent` reviews the tool inventory beside traces. |
| Give explicit tool-selection principles. | Recipes require `purpose`, `use_when`, `avoid_when`, and optional quality checks for every tool. |
| Guide the thinking process, including reflection after web results. | Prompts include thinking guidance. Traces capture visible reasoning summaries or provider-returned reasoning blocks. |
| Use parallel tool calls when independent. | Traces support `parallel_group`, and `agent_trace_parallel_good.json` tests a parallel search batch. |
| Stop when the answer is found and avoid runaway search. | Prompt budgets and stop criteria are rendered from recipes and checked through trace rubrics. |
| Manage context in long tasks. | Recipes include context strategy, progress file, compaction trigger, and subagent policy fields. |
| Start simple and iterate from failures. | Recipes are compact, evals are small, and regression suites include known-good and known-bad cases. |
| Evaluate answer accuracy, tool-use accuracy, and final state. | `evals.py` implements all three eval families. |
| Use LLM-as-judge with a clear rubric. | `claude_judge.py` calls Claude with a semantic trace rubric, and CI requires the live judge. |
| Use realistic tasks and human review. | Examples use realistic research/tool traces, and docs require transcript inspection plus Claude judge results. |

## Reasoning And Tool-Call Tracking

The repo tracks visible reasoning chains as ordered events. A trace can include:

- provider-returned thinking summaries when available
- explicit agent decision notes when provider reasoning is not exposed
- tool calls with ids, tool names, arguments, and optional `parallel_group`
- tool results linked back to call ids
- final answer or final state summary

The deterministic reviewer uses that chain to score structure, tool use, reasoning, and final answer
grounding. The Claude judge then receives the deterministic review plus the full visible trace and
scores semantic quality: tool effectiveness, reasoning quality, tool-output use, final grounding,
and value over baseline.

The repo does not claim access to hidden chain-of-thought. If a runtime does not expose reasoning,
the audit contract requires short visible decision notes before and after tool calls.
