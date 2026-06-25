from pathlib import Path
import subprocess
import sys
import unittest

from claude_agent_harness_optimization.adapters import (
    claude_messages_to_trace,
    load_json,
    load_run_export,
    normalize_run_export,
    runtime_events_to_trace,
    supported_adapters,
)
from claude_agent_harness_optimization.trace_review import review_trace


ROOT = Path(__file__).resolve().parents[1]


class AdapterTests(unittest.TestCase):
    def test_claude_messages_normalize_to_trace(self):
        payload = load_json(ROOT / "evals" / "examples" / "claude_messages.json")
        trace = claude_messages_to_trace(payload)
        self.assertEqual("claude_messages_trace", trace["name"])
        self.assertEqual("reasoning", trace["steps"][0]["type"])
        self.assertEqual("tool_call", trace["steps"][1]["type"])
        self.assertEqual("tool_result", trace["steps"][2]["type"])
        self.assertEqual("final", trace["steps"][-1]["type"])

    def test_cli_normalize_claude(self):
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "claude_agent_harness_optimization",
                "normalize-claude",
                "evals/examples/claude_messages.json",
            ],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn('"type": "tool_call"', result.stdout)

    def test_runtime_events_normalize_to_trace(self):
        payload = load_json(ROOT / "evals" / "examples" / "agent_sdk_trace_review_events.json")
        trace = runtime_events_to_trace(payload)
        self.assertEqual("agent_sdk_trace_review_events", trace["name"])
        self.assertEqual("reasoning", trace["steps"][0]["type"])
        self.assertEqual("tool_call", trace["steps"][1]["type"])
        self.assertEqual("tool_result", trace["steps"][2]["type"])
        self.assertEqual("final", trace["steps"][-1]["type"])
        self.assertTrue(review_trace(trace).passed)

    def test_runtime_events_accept_camel_case_exports(self):
        trace = runtime_events_to_trace(
            {
                "events": [
                    {
                        "type": "assistantThinking",
                        "text": "This is a standard task. Budget one tool call and stop when enough evidence is found.",
                    },
                    {
                        "type": "toolCall",
                        "callId": "call_1",
                        "toolName": "Task",
                        "arguments": "{\"description\":\"trace review audit\"}",
                    },
                    {
                        "type": "toolResult",
                        "toolCallId": "call_1",
                        "output": "Trace review audit data.",
                    },
                    {
                        "type": "decision",
                        "text": "The output is relevant evidence. Verification is complete, so stop and final answer.",
                    },
                    {"type": "finalAnswer", "text": "Done."},
                ],
                "rubric": {"required_tools": ["Task"]},
            }
        )

        self.assertEqual("Task", trace["steps"][1]["name"])
        self.assertEqual("trace review audit", trace["steps"][1]["args"]["description"])
        self.assertEqual("call_1", trace["steps"][2]["tool_call_id"])
        self.assertTrue(review_trace(trace).passed)

    def test_codex_jsonl_export_normalizes_nested_item_events(self):
        payload = load_run_export(ROOT / "evals" / "examples" / "codex_repo_inspection_events.jsonl")
        trace = normalize_run_export(
            {
                "adapter": "codex_jsonl",
                "events": payload,
                "harness": "codex_exec_jsonl",
                "rubric": {
                    "expected_args_contains": {"command": "rg"},
                    "required_tools": ["Bash"],
                    "require_directed_after_tool_reasoning": True,
                    "require_reasoning_before_first_tool": True,
                },
            }
        )

        self.assertEqual("reasoning", trace["steps"][0]["type"])
        self.assertEqual("Bash", trace["steps"][1]["name"])
        self.assertIn("rg", trace["steps"][1]["args"]["command"])
        self.assertEqual("tool_result", trace["steps"][2]["type"])
        self.assertEqual("final", trace["steps"][-1]["type"])
        self.assertTrue(review_trace(trace).passed)

    def test_cli_normalize_runtime(self):
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "claude_agent_harness_optimization",
                "normalize-runtime",
                "evals/examples/cursor_trace_review_events.json",
            ],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn('"source_harness": "cursor_trace"', result.stdout)
        self.assertIn('"type": "tool_call"', result.stdout)

    def test_adapter_aliases_normalize_same_trace_contract(self):
        payload = load_json(ROOT / "evals" / "examples" / "cursor_trace_review_events.json")
        trace = normalize_run_export(payload, "cursor")
        self.assertEqual("cursor_trace_review_events", trace["name"])
        self.assertEqual("Task", trace["steps"][1]["name"])
        self.assertIn("openai_agents", supported_adapters())
        self.assertIn("codex_jsonl", supported_adapters())


if __name__ == "__main__":
    unittest.main()
