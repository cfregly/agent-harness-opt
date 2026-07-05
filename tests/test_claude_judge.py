import json
from pathlib import Path
import unittest
from unittest import mock
from urllib import error

from claude_agent_harness_opt.claude_judge import (
    ClaudeJudgeError,
    build_claude_trace_judge_prompt,
    build_claude_tool_selection_judge_prompt,
    call_claude_messages,
    judge_tool_selection_with_claude,
    judge_trace_with_claude,
    parse_judge_json,
)
from claude_agent_harness_opt.agent_audit import load_agent_bundle
from claude_agent_harness_opt.tool_selection import review_tool_selection
from claude_agent_harness_opt.trace_review import load_trace, review_trace


ROOT = Path(__file__).resolve().parents[1]


class FakeErrorBody:
    def __init__(self, body: bytes) -> None:
        self.body = body

    def read(self) -> bytes:
        return self.body

    def close(self) -> None:
        pass


def fake_request(
    payload: dict,
    headers: dict[str, str],
    url: str,
    timeout: int,
) -> dict:
    assert payload["model"] == "claude-test"
    assert headers["x-api-key"] == "test-key"
    assert url == "https://api.anthropic.com/v1/messages"
    assert timeout == 60
    return {
        "content": [
            {
                "type": "text",
                "text": json.dumps(
                    {
                        "findings": ["trace uses fetched evidence before calculating"],
                        "passed": True,
                        "recommended_changes": [],
                        "score": 0.91,
                        "scores": {
                            "final_answer_grounding": 0.9,
                            "reasoning_quality": 0.9,
                            "tool_effectiveness": 0.95,
                            "tool_output_use": 0.9,
                            "value_over_baseline": 0.9,
                        },
                    }
                ),
            }
        ]
    }


class ClaudeJudgeTests(unittest.TestCase):
    def test_build_prompt_includes_visible_trace_and_no_hidden_cot_instruction(self):
        trace = load_trace(ROOT / "evals" / "examples" / "agent_trace_good.json")
        review = review_trace(trace)
        prompt = build_claude_trace_judge_prompt(trace, review)
        self.assertIn("reasoning summaries", prompt)
        self.assertIn("Do not infer hidden chain-of-thought", prompt)
        self.assertIn("Rivian R1S cargo volume", prompt)

    def test_parse_judge_json_accepts_fenced_json(self):
        parsed = parse_judge_json('```json\n{"passed": true, "score": 0.8}\n```')
        self.assertTrue(parsed["passed"])
        self.assertEqual(0.8, parsed["score"])

    def test_call_claude_messages_uses_messages_api_shape(self):
        response = call_claude_messages(
            "judge this",
            api_key="test-key",
            model="claude-test",
            request_fn=fake_request,
        )
        self.assertEqual("text", response["content"][0]["type"])

    def test_call_claude_messages_maps_credit_lockout_to_provider_blocker(self):
        body = FakeErrorBody(
            b'{"error":{"message":"Your credit balance is too low to access the Anthropic API."}}'
        )
        blocked = error.HTTPError(
            "https://api.anthropic.com/v1/messages",
            400,
            "Bad Request",
            hdrs=None,
            fp=body,
        )
        with mock.patch("claude_agent_harness_opt.claude_judge.request.urlopen", side_effect=blocked):
            with self.assertRaisesRegex(ClaudeJudgeError, "billing or usage credits"):
                call_claude_messages("judge this", api_key="test-key", model="claude-test")

    def test_judge_trace_with_claude_returns_semantic_score(self):
        trace = load_trace(ROOT / "evals" / "examples" / "agent_trace_good.json")
        review = review_trace(trace)
        result = judge_trace_with_claude(
            trace,
            review,
            api_key="test-key",
            model="claude-test",
            request_fn=fake_request,
        )
        self.assertTrue(result.passed)
        self.assertEqual(0.91, result.score)
        self.assertEqual("claude-test", result.model)

    def test_build_tool_selection_prompt_includes_cases_and_value_bar(self):
        bundle = load_agent_bundle(ROOT / "evals" / "examples" / "agent_audit_bundle.json")
        review = review_tool_selection(bundle, ROOT / "evals" / "examples")
        prompt = build_claude_tool_selection_judge_prompt(bundle, review.to_dict())
        self.assertIn("tool-selection cases", prompt)
        self.assertIn("adversarially-confirmed to add value", prompt)
        self.assertIn("discover unknown current sources", prompt)

    def test_judge_tool_selection_with_claude_returns_semantic_score(self):
        bundle = load_agent_bundle(ROOT / "evals" / "examples" / "agent_audit_bundle.json")
        review = review_tool_selection(bundle, ROOT / "evals" / "examples")
        result = judge_tool_selection_with_claude(
            bundle,
            review.to_dict(),
            api_key="test-key",
            model="claude-test",
            request_fn=fake_request,
        )
        self.assertTrue(result.passed)
        self.assertEqual(0.91, result.score)
        self.assertEqual("claude-test", result.model)


if __name__ == "__main__":
    unittest.main()
