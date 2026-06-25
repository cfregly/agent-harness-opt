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

    def test_visible_decision_notes_are_reviewable_reasoning(self):
        payload = [
            {
                "type": "item.completed",
                "item": {
                    "id": "message_0",
                    "type": "agent_message",
                    "text": (
                        "DECISION_NOTE_BEFORE complexity simple; tool budget one call; "
                        "evidence needed is pwd output; stop criteria is successful output."
                    ),
                },
            },
            {
                "type": "item.started",
                "item": {
                    "id": "call_1",
                    "type": "command_execution",
                    "command": "pwd",
                    "status": "in_progress",
                },
            },
            {
                "type": "item.completed",
                "item": {
                    "id": "call_1",
                    "type": "command_execution",
                    "command": "pwd",
                    "aggregated_output": "/tmp/repo",
                    "status": "completed",
                },
            },
            {
                "type": "item.completed",
                "item": {
                    "id": "message_1",
                    "type": "agent_message",
                    "text": (
                        "DECISION_NOTE_AFTER quality is direct; verification confirmed expected output; "
                        "decision stop and final answer.\nHARNESS_OK codex /tmp/repo"
                    ),
                },
            },
        ]
        trace = normalize_run_export(
            {
                "adapter": "codex_jsonl",
                "events": payload,
                "rubric": {
                    "expected_call_args": [{"args_contains": {"command": "pwd"}, "name": "Bash"}],
                    "required_final_contains": ["HARNESS_OK codex"],
                    "required_tools": ["Bash"],
                },
            }
        )

        self.assertEqual(["reasoning", "tool_call", "tool_result", "reasoning", "final"], [s["type"] for s in trace["steps"]])
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

    def test_claude_code_stream_json_normalizes_tool_use_and_result(self):
        payload = [
            {
                "type": "system",
                "subtype": "init",
                "model": "claude-opus-4-8",
                "tools": ["Bash"],
                "claude_code_version": "2.1.179",
            },
            {
                "type": "assistant",
                "message": {
                    "role": "assistant",
                    "content": [
                        {
                            "type": "tool_use",
                            "id": "toolu_1",
                            "name": "Bash",
                            "input": {"command": "pwd", "description": "Print cwd"},
                        }
                    ],
                },
            },
            {
                "type": "user",
                "message": {
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": "toolu_1",
                            "content": "/tmp/repo",
                            "is_error": False,
                        }
                    ],
                },
            },
            {
                "type": "assistant",
                "message": {
                    "role": "assistant",
                    "content": [{"type": "text", "text": "HARNESS_OK claude /tmp/repo"}],
                },
            },
        ]

        trace = normalize_run_export(payload, "claude_code_stream_json")

        self.assertEqual("claude_code_stream_json", trace["metadata"]["source_harness"])
        self.assertEqual("Bash", trace["steps"][0]["name"])
        self.assertEqual("tool_result", trace["steps"][1]["type"])
        self.assertEqual("final", trace["steps"][2]["type"])

    def test_gemini_stream_json_normalizes_tool_use_and_final_deltas(self):
        payload = [
            {"type": "init", "model": "auto"},
            {
                "type": "tool_use",
                "tool_name": "run_shell_command",
                "tool_id": "call_1",
                "parameters": {"command": "pwd", "description": "Print cwd"},
            },
            {
                "type": "tool_result",
                "tool_id": "call_1",
                "status": "success",
                "output": "/tmp/repo",
            },
            {"type": "message", "role": "assistant", "content": "HARNESS_OK gemini ", "delta": True},
            {"type": "message", "role": "assistant", "content": "/tmp/repo", "delta": True},
        ]

        trace = normalize_run_export(payload, "gemini_stream_json")

        self.assertEqual("run_shell_command", trace["steps"][0]["name"])
        self.assertEqual("call_1", trace["steps"][1]["tool_call_id"])
        self.assertIn("HARNESS_OK gemini", trace["steps"][2]["text"])

    def test_gemini_stream_buffers_split_decision_note_deltas(self):
        payload = [
            {"type": "message", "role": "assistant", "content": "DECISION_NOTE_BEFORE complexity low, tool budget one call, evidence", "delta": True},
            {"type": "message", "role": "assistant", "content": " needed is pwd output, stop criteria success.", "delta": True},
            {
                "type": "tool_use",
                "tool_name": "run_shell_command",
                "tool_id": "call_1",
                "parameters": {"command": "pwd"},
            },
            {"type": "tool_result", "tool_id": "call_1", "status": "success", "output": "/tmp/repo"},
            {"type": "message", "role": "assistant", "content": "DECISION_NOTE_AFTER result", "delta": True},
            {
                "type": "message",
                "role": "assistant",
                "content": " quality direct, verification confirmed, decision stop.\nHARNESS_OK gemini /tmp/repo",
                "delta": True,
            },
            {"type": "result", "status": "success"},
        ]
        trace = normalize_run_export(
            {
                "adapter": "gemini_stream_json",
                "events": payload,
                "rubric": {
                    "expected_call_args": [
                        {"args_contains": {"command": "pwd"}, "name": "run_shell_command"}
                    ],
                    "required_final_contains": ["HARNESS_OK gemini"],
                    "required_tools": ["run_shell_command"],
                },
            }
        )

        self.assertEqual(["reasoning", "tool_call", "tool_result", "reasoning", "final"], [s["type"] for s in trace["steps"]])
        self.assertTrue(review_trace(trace).passed)

    def test_opencode_text_normalizes_command_logs_when_json_export_is_missing(self):
        raw = "\n".join(
            [
                'type=tool-call part {"command":"pwd","timeout":60000}',
                "HARNESS_OK opencode",
                "Command output:",
                "/tmp/repo",
            ]
        )

        trace = normalize_run_export(raw, "opencode_text")

        self.assertEqual("opencode_text", trace["metadata"]["source_harness"])
        self.assertEqual("Bash", trace["steps"][0]["name"])
        self.assertEqual("pwd", trace["steps"][0]["args"]["command"])
        self.assertEqual("final", trace["steps"][-1]["type"])


if __name__ == "__main__":
    unittest.main()
