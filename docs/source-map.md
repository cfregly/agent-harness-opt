# Source Map

Checked on 2026-06-25.

## Public Video

- [Prompting for Agents | Code w/ Claude](https://www.youtube.com/watch?v=XSZP9GhhuAc)
  - [Agents as models using tools in a loop](https://www.youtube.com/watch?v=XSZP9GhhuAc&t=85s)
  - [Task-fit checklist: complexity, value, viability, and error cost](https://www.youtube.com/watch?v=XSZP9GhhuAc&t=160s)
  - [Use cases: coding, search, computer use, and data analysis](https://www.youtube.com/watch?v=XSZP9GhhuAc&t=270s)
  - [Think like the agent and simulate its tool environment](https://www.youtube.com/watch?v=XSZP9GhhuAc&t=448s)
  - [Reasonable heuristics and tool-call budgets](https://www.youtube.com/watch?v=XSZP9GhhuAc&t=587s)
  - [Tool selection guidance](https://www.youtube.com/watch?v=XSZP9GhhuAc&t=644s)
  - [Guide thinking without prescribing hidden chain-of-thought](https://www.youtube.com/watch?v=XSZP9GhhuAc&t=699s)
  - [Interleaved thinking between tool calls](https://www.youtube.com/watch?v=XSZP9GhhuAc&t=738s)
  - [Plan, reflect after tool calls, and verify source quality](https://www.youtube.com/watch?v=XSZP9GhhuAc&t=702s)
  - [Unintended side effects and stop criteria](https://www.youtube.com/watch?v=XSZP9GhhuAc&t=776s)
  - [Context management with compaction, external files, and subagents](https://www.youtube.com/watch?v=XSZP9GhhuAc&t=821s)
  - [Parallel web searches in the demo](https://www.youtube.com/watch?v=XSZP9GhhuAc&t=1123s)
  - [Start simple and iterate from test cases](https://www.youtube.com/watch?v=XSZP9GhhuAc&t=1597s)
  - [Use the thinking phase efficiently](https://www.youtube.com/watch?v=XSZP9GhhuAc&t=1726s)
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
- [Migration guide](https://platform.claude.com/docs/en/about-claude/models/migration-guide)
  - Used for model-migration coverage: `/claude-api migrate`, model ID swaps, breaking parameter
    changes, prefill replacement, effort calibration, platform-specific model ID formats, thinking
    output handling, refusal stop details, and migration checklists.
- [Console prompting tools](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-tools)
  - Used for prompt improver and test-case generator coverage: generated prompt changes and
    examples must be validated by evals instead of promoted from prose alone.
- [Define tools](https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools)
  - Used for tool-description coverage: descriptions should explain what a tool does, when to use
    it, what it returns, and argument meaning.
- [Claude Code skills](https://code.claude.com/docs/en/skills)
  - Used for Claude Code skill migration coverage and the custom-command-to-skill transition.

## OpenAI Codex Docs

- [Codex manual](https://developers.openai.com/codex/codex-manual.md)
  - Used for Codex harness coverage: AGENTS.md discovery, skills, MCP configuration, hooks,
    `codex exec --json`, Codex SDK, app-server, Codex MCP server, GitHub Action, plugins, and
    import behavior.

## Live Harness CLI Docs

- [Claude Code CLI reference](https://code.claude.com/docs/en/cli-reference)
  - Used for `claude -p`, `--output-format stream-json`, `--verbose`, permission mode, tool
    selection, and budget flags in the live harness suite.
- [Claude Code headless mode](https://code.claude.com/docs/en/headless)
  - Used for treating Claude Code as a non-interactive harness under test.
- [Gemini CLI docs](https://developers.google.com/gemini-code-assist/docs/gemini-cli)
  - Used for Gemini CLI stream JSON, shell-tool use, and MCP-capable CLI coverage.
- [Cursor CLI headless mode](https://cursor.com/docs/cli/headless)
  - Used for Cursor Agent headless execution and auth expectations.
- [Cursor CLI output format](https://cursor.com/docs/cli/reference/output-format)
  - Used for Cursor Agent stream JSON output coverage.
- [OpenCode CLI docs](https://opencode.ai/docs/cli/)
  - Used for OpenCode `run`, model selection, and log capture coverage.

## Live SDK Harness Docs

- [Claude Agent SDK overview](https://code.claude.com/docs/en/agent-sdk/overview)
  - Used for the distinction between Claude Code as a product and Claude Agent SDK as the library
    harness that exposes Claude Code's loop and capabilities.
- [Migrate to Claude Agent SDK](https://code.claude.com/docs/en/agent-sdk/migration-guide)
  - Used for the rename from Claude Code SDK to Claude Agent SDK.
- [Claude Agent SDK Python reference](https://code.claude.com/docs/en/agent-sdk/python)
  - Used for `query`, `ClaudeAgentOptions`, custom tools, in-process MCP server coverage, hooks,
    permissions, skills, subagents, sessions, and thinking or budget surface inventory.
- [OpenAI Agents SDK guide](https://developers.openai.com/api/docs/guides/agents)
  - Used for OpenAI's equivalent agent SDK coverage and its role as an orchestration layer over
    model calls and tools.
- [OpenAI Agents SDK Python reference](https://openai.github.io/openai-agents-python/agents/)
  - Used for `Agent`, `Runner`, function-tool smoke coverage, handoffs, guardrails, MCP, sessions,
    tracing, hosted tools, shell tools, and computer-tool surface inventory.
- [Google Agent Development Kit](https://adk.dev/)
  - Used for Google's equivalent SDK coverage, supported language scope, tools, workflows, sessions,
    memory, planners, code execution, telemetry, and evaluation surface inventory.
- [Google ADK Cloud docs](https://docs.cloud.google.com/gemini-enterprise-agent-platform/build/adk)
  - Used for Google ADK positioning as an enterprise-scale agent development framework.

## Anthropic Engineering

- [Writing effective tools for agents](https://www.anthropic.com/engineering/writing-tools-for-agents)
  - Used for prototype-first tool design, realistic multi-tool eval tasks, verifiable outcomes,
    flexible verifiers, optional expected tool calls, avoiding strategy overfit, direct API eval
    loops, reasoning and feedback blocks, transcript review, tool-call metrics, held-out test sets,
    selective tool design, namespacing, meaningful output context, response formats, token
    efficiency, actionable errors, and prompt-engineered tool descriptions.

## Autoresearch Pattern

- [Autoresearch repository](https://github.com/karpathy/autoresearch)
  - Used for the fixed-budget experiment loop: choose one editable surface, run a bounded
    experiment, measure a clear score, keep or discard the candidate, and preserve an experiment
    log. In this repo the editable surface is the agent harness rather than model training code.

## Public MCP Sources

- [Zymtrace getting started](https://docs.zymtrace.com/getting-started/)
  - Used for the Zymtrace MCP and profiler setup context in the public MCP sweep.
- [Zymtrace Model Context Protocol docs](https://docs.zymtrace.com/category/model-context-protocol-mcp/)
  - Used for the Zymtrace MCP tool-selection matrix and sweep source links.

## Local Screenshots

The initial implementation also used user-provided screenshots of these slides:

- examples of good agent use cases
- tips for evaluating agentic systems
- examples of evals for agents
- the agentic search demo prompt
