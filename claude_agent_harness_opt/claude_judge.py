"""Claude-backed semantic judging for agent traces."""

from __future__ import annotations

from dataclasses import dataclass
import json
import os
from typing import Any, Callable
from urllib import error, request

from .provider_status import anthropic_credit_block_fields
from .trace_review import TraceReview


DEFAULT_MODEL = "claude-opus-4-8"
DEFAULT_BASE_URL = "https://api.anthropic.com"
DEFAULT_ANTHROPIC_VERSION = "2023-06-01"

JudgeRequestFn = Callable[[dict[str, Any], dict[str, str], str, int], dict[str, Any]]


class ClaudeJudgeError(RuntimeError):
    """Raised when the Claude judge cannot run or returns invalid output."""


@dataclass(frozen=True)
class ClaudeJudgeResult:
    passed: bool
    score: float
    model: str
    judge: dict[str, Any]
    raw_text: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "judge": self.judge,
            "model": self.model,
            "passed": self.passed,
            "raw_text": self.raw_text,
            "score": self.score,
        }


def judge_trace_with_claude(
    trace: dict[str, Any],
    deterministic_review: TraceReview,
    *,
    model: str | None = None,
    max_tokens: int = 2048,
    api_key: str | None = None,
    base_url: str | None = None,
    anthropic_version: str = DEFAULT_ANTHROPIC_VERSION,
    timeout: int = 60,
    request_fn: JudgeRequestFn | None = None,
) -> ClaudeJudgeResult:
    """Ask Claude to semantically judge visible trace reasoning and tool output use."""

    resolved_model = model or os.getenv("CLAUDE_JUDGE_MODEL") or DEFAULT_MODEL
    prompt = build_claude_trace_judge_prompt(trace, deterministic_review)
    response = call_claude_messages(
        prompt,
        model=resolved_model,
        max_tokens=max_tokens,
        api_key=api_key,
        base_url=base_url,
        anthropic_version=anthropic_version,
        timeout=timeout,
        request_fn=request_fn,
    )
    raw_text = _response_text(response)
    judge = parse_judge_json(raw_text)
    passed = bool(judge.get("passed", False))
    score = float(judge.get("score", 0.0))
    return ClaudeJudgeResult(
        judge=judge,
        model=resolved_model,
        passed=passed,
        raw_text=raw_text,
        score=score,
    )


def judge_tool_selection_with_claude(
    bundle: dict[str, Any],
    deterministic_review: dict[str, Any],
    *,
    model: str | None = None,
    max_tokens: int = 2048,
    api_key: str | None = None,
    base_url: str | None = None,
    anthropic_version: str = DEFAULT_ANTHROPIC_VERSION,
    timeout: int = 60,
    request_fn: JudgeRequestFn | None = None,
) -> ClaudeJudgeResult:
    """Ask Claude to judge whether tool descriptions support correct selection."""

    resolved_model = model or os.getenv("CLAUDE_JUDGE_MODEL") or DEFAULT_MODEL
    prompt = build_claude_tool_selection_judge_prompt(bundle, deterministic_review)
    response = call_claude_messages(
        prompt,
        model=resolved_model,
        max_tokens=max_tokens,
        api_key=api_key,
        base_url=base_url,
        anthropic_version=anthropic_version,
        timeout=timeout,
        request_fn=request_fn,
    )
    raw_text = _response_text(response)
    judge = parse_judge_json(raw_text)
    passed = bool(judge.get("passed", False))
    score = float(judge.get("score", 0.0))
    return ClaudeJudgeResult(
        judge=judge,
        model=resolved_model,
        passed=passed,
        raw_text=raw_text,
        score=score,
    )


def call_claude_messages(
    prompt: str,
    *,
    model: str,
    max_tokens: int = 2048,
    api_key: str | None = None,
    base_url: str | None = None,
    anthropic_version: str = DEFAULT_ANTHROPIC_VERSION,
    timeout: int = 60,
    request_fn: JudgeRequestFn | None = None,
) -> dict[str, Any]:
    """Call Anthropic's Messages API and return the decoded response."""

    resolved_api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
    if not resolved_api_key:
        raise ClaudeJudgeError("ANTHROPIC_API_KEY is required for --claude-judge")

    resolved_base_url = (base_url or os.getenv("ANTHROPIC_BASE_URL") or DEFAULT_BASE_URL).rstrip("/")
    url = f"{resolved_base_url}/v1/messages"
    payload = {
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}],
        "model": model,
    }
    headers = {
        "anthropic-version": anthropic_version,
        "content-type": "application/json",
        "x-api-key": resolved_api_key,
    }
    if request_fn is None:
        return _post_json(payload, headers, url, timeout)
    return request_fn(payload, headers, url, timeout)


def build_claude_trace_judge_prompt(
    trace: dict[str, Any],
    deterministic_review: TraceReview,
) -> str:
    """Build the semantic judge prompt from visible audit artifacts only."""

    return (
        "You are a strict evaluator for an AI agent trace.\n\n"
        "Review only the visible trace artifacts: reasoning summaries, tool calls, tool outputs, "
        "and the final answer. Do not infer hidden chain-of-thought. Do not reward a trace merely "
        "because its JSON shape is valid.\n\n"
        "<task>\n"
        f"{trace.get('task', '')}\n"
        "</task>\n\n"
        "<deterministic_review>\n"
        f"{json.dumps(deterministic_review.to_dict(), indent=2, sort_keys=True)}\n"
        "</deterministic_review>\n\n"
        "<trace>\n"
        f"{json.dumps(trace.get('steps', []), indent=2, sort_keys=True)}\n"
        "</trace>\n\n"
        "<semantic_rubric>\n"
        "- Did the agent choose tools that could actually answer the task?\n"
        "- Did the agent use the tool outputs, not just call tools?\n"
        "- Before the first tool, did visible reasoning classify complexity, name a tool budget, "
        "and define evidence or stop criteria?\n"
        "- After tool results, did visible reasoning assess quality, address verification, and name "
        "the continue, stop, or next-action decision?\n"
        "- Did inter-tool reasoning assess uncertainty, errors, and stop conditions?\n"
        "- Did the final answer follow from the observed tool outputs?\n"
        "- Did the trace create value over a weaker baseline, or is it just plausible activity?\n"
        "- What concrete prompt, tool, or eval change would improve the agent?\n"
        "</semantic_rubric>\n\n"
        "Return only strict JSON with this shape:\n"
        "{\n"
        '  "passed": true,\n'
        '  "score": 0.0,\n'
        '  "scores": {\n'
        '    "tool_effectiveness": 0.0,\n'
        '    "reasoning_quality": 0.0,\n'
        '    "tool_output_use": 0.0,\n'
        '    "final_answer_grounding": 0.0,\n'
        '    "value_over_baseline": 0.0\n'
        "  },\n"
        '  "findings": ["specific issue or strength"],\n'
        '  "recommended_changes": ["specific prompt, tool, or eval change"]\n'
        "}\n"
    )


def build_claude_tool_selection_judge_prompt(
    bundle: dict[str, Any],
    deterministic_review: dict[str, Any],
) -> str:
    """Build the semantic judge prompt for tool description optimization."""

    payload = {
        "heldout_selection_cases": bundle.get("heldout_tool_selection_cases", []),
        "selection_cases": bundle.get("tool_selection_cases", []),
        "tool_metrics": bundle.get("tool_metrics", {}),
        "tools": bundle.get("tools", []),
        "trace_index": bundle.get("traces", []),
        "value_bar": bundle.get("value_bar", {}),
    }
    return (
        "You are a strict evaluator for an AI agent tool inventory and tool-selection harness.\n\n"
        "Review only visible artifacts: tool names, descriptions, input schemas, quality checks, "
        "tool-selection cases, trace-derived deterministic findings, and value-bar proof. Do not "
        "infer hidden chain-of-thought.\n\n"
        "<deterministic_tool_selection_review>\n"
        f"{json.dumps(deterministic_review, indent=2, sort_keys=True)}\n"
        "</deterministic_tool_selection_review>\n\n"
        "<bundle_extract>\n"
        f"{json.dumps(payload, indent=2, sort_keys=True)}\n"
        "</bundle_extract>\n\n"
        "<semantic_rubric>\n"
        "- Are similar tools easy to distinguish from the descriptions alone?\n"
        "- Are there a few agent-fit tools rather than many endpoint-shaped wrappers?\n"
        "- Do large catalogs use service or resource namespaces where useful?\n"
        "- Do use_when and avoid_when rules give the agent a reliable selection policy?\n"
        "- Do schemas and argument descriptions make valid calls likely?\n"
        "- Do tool outputs return meaningful context with predictable output contracts?\n"
        "- Do large-output tools expose pagination, filtering, range, truncation, or response_format controls?\n"
        "- Do error responses give actionable recovery guidance instead of opaque failures?\n"
        "- Do quality checks tell the agent how to inspect tool outputs before the next action?\n"
        "- Are evaluation prompts paired with verifiable responses or outcomes?\n"
        "- Are expected tool calls used as optional diagnostics instead of overfitted exact strategies?\n"
        "- Do selection cases cover confusing boundaries and held-out cases?\n"
        "- Do transcript metrics expose runtime, tool-call count, token use, and tool errors where available?\n"
        "- Do recommended changes improve value over the baseline instead of adding prompt bulk?\n"
        "- Is the result adversarially-confirmed to add value?\n"
        "</semantic_rubric>\n\n"
        "Return only strict JSON with this shape:\n"
        "{\n"
        '  "passed": true,\n'
        '  "score": 0.0,\n'
        '  "scores": {\n'
        '    "description_distinctness": 0.0,\n'
        '    "schema_quality": 0.0,\n'
        '    "selection_case_coverage": 0.0,\n'
        '    "trace_failure_mapping": 0.0,\n'
        '    "value_over_baseline": 0.0\n'
        "  },\n"
        '  "findings": ["specific issue or strength"],\n'
        '  "recommended_tool_changes": ["specific tool description or schema change"],\n'
        '  "recommended_eval_changes": ["specific selection case or trace fixture change"]\n'
        "}\n"
    )


def parse_judge_json(text: str) -> dict[str, Any]:
    """Parse strict JSON, tolerating a fenced JSON block if the model returns one."""

    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = stripped.strip("`")
        if stripped.lower().startswith("json"):
            stripped = stripped[4:].strip()
    try:
        data = json.loads(stripped)
    except json.JSONDecodeError:
        start = stripped.find("{")
        end = stripped.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise ClaudeJudgeError("Claude judge did not return JSON") from None
        data = json.loads(stripped[start : end + 1])
    if not isinstance(data, dict):
        raise ClaudeJudgeError("Claude judge JSON must be an object")
    if "passed" not in data or "score" not in data:
        raise ClaudeJudgeError("Claude judge JSON must include passed and score")
    return data


def _post_json(
    payload: dict[str, Any],
    headers: dict[str, str],
    url: str,
    timeout: int,
) -> dict[str, Any]:
    body = json.dumps(payload).encode("utf-8")
    req = request.Request(url, data=body, headers=headers, method="POST")
    try:
        with request.urlopen(req, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        fields = anthropic_credit_block_fields(detail)
        if fields:
            raise ClaudeJudgeError(fields["error"]) from exc
        raise ClaudeJudgeError(f"Claude API request failed: HTTP {exc.code}: {detail}") from exc
    except error.URLError as exc:
        raise ClaudeJudgeError(f"Claude API request failed: {exc.reason}") from exc


def _response_text(response: dict[str, Any]) -> str:
    parts: list[str] = []
    for block in response.get("content", []):
        if isinstance(block, dict) and block.get("type") == "text":
            parts.append(str(block.get("text", "")))
    text = "\n".join(part for part in parts if part).strip()
    if not text:
        raise ClaudeJudgeError("Claude judge response did not contain text")
    return text
