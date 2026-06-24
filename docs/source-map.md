# Source Map

Checked on 2026-06-24.

## Public Video

- [Prompting for Agents | Code w/ Claude](https://www.youtube.com/watch?v=XSZP9GhhuAc)
  - [Agents as models using tools in a loop](https://www.youtube.com/watch?v=XSZP9GhhuAc&t=85s)
  - [Task-fit checklist: complexity, value, viability, and error cost](https://www.youtube.com/watch?v=XSZP9GhhuAc&t=160s)
  - [Use cases: coding, search, computer use, and data analysis](https://www.youtube.com/watch?v=XSZP9GhhuAc&t=270s)
  - [Think like the agent and simulate its tool environment](https://www.youtube.com/watch?v=XSZP9GhhuAc&t=448s)
  - [Reasonable heuristics and tool-call budgets](https://www.youtube.com/watch?v=XSZP9GhhuAc&t=587s)
  - [Tool selection guidance](https://www.youtube.com/watch?v=XSZP9GhhuAc&t=644s)
  - [Interleaved thinking between tool calls](https://www.youtube.com/watch?v=XSZP9GhhuAc&t=738s)
  - [Plan, reflect after tool calls, and verify source quality](https://www.youtube.com/watch?v=XSZP9GhhuAc&t=702s)
  - [Unintended side effects and stop criteria](https://www.youtube.com/watch?v=XSZP9GhhuAc&t=776s)
  - [Context management with compaction, external files, and subagents](https://www.youtube.com/watch?v=XSZP9GhhuAc&t=821s)
  - [Parallel web searches in the demo](https://www.youtube.com/watch?v=XSZP9GhhuAc&t=1123s)
  - [Start simple and iterate from test cases](https://www.youtube.com/watch?v=XSZP9GhhuAc&t=1597s)
  - [Agent evals: answer accuracy, tool use accuracy, and final state](https://www.youtube.com/watch?v=XSZP9GhhuAc&t=1428s)
  - [LLM-as-judge with a clear rubric](https://www.youtube.com/watch?v=XSZP9GhhuAc&t=1360s)
  - [Use realistic tasks](https://www.youtube.com/watch?v=XSZP9GhhuAc&t=1332s)

## Claude Docs

- [Prompt engineering overview](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview)
  - Used for the rule that prompt work should start with success criteria and empirical tests.
- [Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)
  - Used for clear instructions, XML structure, tool-use guidance, thinking guidance, context
    workflows, safety, research, subagents, and coding-agent caveats.
- [Define success criteria and build evaluations](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests)
  - Used for task-specific evals, automated grading, LLM-based grading rubrics, and multidimensional
    success criteria.
- [Extended thinking](https://platform.claude.com/docs/en/build-with-claude/extended-thinking)
  - Used for thinking blocks, summarized or omitted display, interleaved thinking with tools,
    preserving thinking blocks during tool use, and redacted thinking blocks.
- [Tool use with Claude](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview)
  - Used for `tool_use` and `tool_result` content block terminology.
- [Using the Messages API](https://platform.claude.com/docs/en/build-with-claude/working-with-messages)
  - Used for the live Claude judge path, which sends a full user message to Claude and reads the
    returned text block.

## Local Screenshots

The initial implementation also used user-provided screenshots of these slides:

- examples of good agent use cases
- tips for evaluating agentic systems
- examples of evals for agents
- the agentic search demo prompt
