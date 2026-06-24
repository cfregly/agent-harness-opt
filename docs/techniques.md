# Agent Prompting Techniques

This repo implements these techniques as recipes, rendered prompts, linters, local evals, and a live
Claude judge for semantic trace review.

## 1. Fit The Task Before Prompting

Agents are best for tasks where the path is not fully known in advance. Score the task before
building the prompt:

- complexity and ambiguity
- value of completing the task
- viability of the available tools and data
- cost of error
- recoverability and error visibility

The `score` command turns those dimensions into a verdict. High error cost and weak recovery move
the task toward human review even when the task is valuable.

## 2. Enforce The Value Bar

Use "adversarially-confirmed to add value" as the pass bar. A prompt, tool, agent, or eval change is
not accepted because it looks cleaner or passes an easy case. It must:

- state the value claim
- compare against a baseline
- meet a minimum improvement threshold
- include an adversarial challenge
- leave no open adversarial objections

## 3. Start Simple

Begin with a short role, task, and tool list. Add instructions only after test cases show a repeated
failure. The recipes are meant to be edited from observed failures, not written as a maximal prompt
on the first pass.

## 4. Think Like The Agent

The agent's world is its tools, tool schemas, tool results, and prompt. If a human reading the same
tool descriptions would be confused, the agent will be confused too. The `lint-tools` command catches
thin descriptions, missing avoid rules, duplicate names, and search-like overlap.

## 5. Give Heuristics

Agent prompts need concepts and operating rules:

- what counts as done
- when to stop searching
- when to verify
- when to ask for help
- what actions are hard to reverse
- what budgets to use for simple, standard, and complex tasks

The prompt renderer turns these into explicit sections so the agent does not infer them from vague
tool descriptions.

## 6. Guide Tool Selection

Each tool gets a purpose, use rule, avoid rule, and quality checks. Similar tools should be merged or
renamed so the model does not have to guess which nearly identical tool should be used.

## 7. Guide The Reasoning Process

The recipes ask the agent to plan before acting, reflect after tool results, and self-check before
finishing. The guidance focuses on what to consider instead of prescribing a fixed chain of steps.

## 8. Manage Side Effects

Agents run loops, so a small prompt change can have a large behavior change. Each recipe has stop
conditions and fallback instructions. If a new instruction causes runaway search or over-action,
remove or narrow that instruction and add an eval case for the failure.

## 9. Manage Context

Long tasks need state outside the current turn. Recipes can name a progress file, compaction trigger,
and subagent policy. The goal is to preserve decisions, sources, open questions, and next actions.

## 10. Use Parallelism Carefully

Independent searches and independent file reads can run in parallel. Dependent actions should stay
sequential because later tool inputs depend on earlier outputs.

When traces include parallel calls, use `parallel_group` on the calls and results. The reviewer then
checks reflection after the batch of results before the next action.

## 11. Evaluate Agents Three Ways

The local eval harness covers the three eval families from the talk:

- answer accuracy: check content, numeric ranges, and judge prompts
- tool use accuracy: check which tools were used and with which parameters
- final state accuracy: check that files, data, or workflow state ended correctly

Start with a small realistic set, keep it consistent, and expand it when failures repeat.

## 12. Use Examples Sparingly

Few-shot examples are still useful when they clarify an edge case or output shape. They should not
force a fixed process for an agent that needs to adapt to tool results. Prefer principles, done
criteria, and quality checks before adding a long demonstration.

## 13. Keep Human Review In The Loop

Claude judge rubrics are useful because agent outputs vary in structure. They do not replace looking
at real transcripts, checking rough edges, and testing with real users. Use `--claude-judge` for
real agent audits, and keep the local deterministic checks visible beside it.
