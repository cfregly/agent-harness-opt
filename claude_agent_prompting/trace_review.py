"""Review ordered agent traces for tool use and inter-tool reasoning."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any


QUALITY_TERMS = {
    "accurate",
    "current",
    "direct",
    "evidence",
    "fresh",
    "quality",
    "reliable",
    "relevant",
    "source",
    "stale",
    "uncertain",
    "verify",
}
ERROR_TERMS = {
    "fallback",
    "fix",
    "parameter",
    "recover",
    "retry",
    "schema",
    "tool error",
}


@dataclass(frozen=True)
class TraceFinding:
    check: str
    passed: bool
    detail: str
    severity: str = "medium"

    def to_dict(self) -> dict[str, Any]:
        return {
            "check": self.check,
            "detail": self.detail,
            "passed": self.passed,
            "severity": self.severity,
        }


@dataclass(frozen=True)
class TraceReview:
    passed: bool
    score: float
    scores: dict[str, float]
    findings: list[TraceFinding]

    def to_dict(self) -> dict[str, Any]:
        return {
            "findings": [finding.to_dict() for finding in self.findings],
            "passed": self.passed,
            "score": self.score,
            "scores": self.scores,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, sort_keys=True)


def load_trace(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def review_trace(trace: dict[str, Any]) -> TraceReview:
    steps = trace.get("steps", [])
    if not isinstance(steps, list) or not steps:
        raise ValueError("trace.steps must be a non-empty list")

    rubric = trace.get("rubric", {})
    findings: list[TraceFinding] = []
    findings.extend(_structure_findings(steps, rubric))
    findings.extend(_tool_use_findings(steps, rubric))
    findings.extend(_reasoning_findings(steps, rubric))
    findings.extend(_final_findings(steps, rubric))

    scores = {
        "structure": _score(findings, "structure."),
        "tool_use": _score(findings, "tool_use."),
        "reasoning": _score(findings, "reasoning."),
        "final": _score(findings, "final."),
    }
    overall = round(sum(scores.values()) / len(scores), 3)
    return TraceReview(
        passed=overall >= float(rubric.get("pass_score", 1.0)),
        score=overall,
        scores=scores,
        findings=findings,
    )


def build_trace_judge_prompt(trace: dict[str, Any]) -> str:
    rubric = trace.get("rubric", {})
    trace_excerpt = _compact_trace(trace.get("steps", []))
    return (
        "You are reviewing an agent trace for tool-use quality.\n\n"
        "<review_focus>\n"
        "- Did the agent choose the right tools for the task?\n"
        "- Did the agent pass appropriate tool arguments?\n"
        "- Did the agent inspect tool outputs before the next action?\n"
        "- Did inter-tool reasoning explain verification, recovery, or stopping decisions?\n"
        "- Did the final answer use the evidence gathered by the tools?\n"
        "- Is the trace adversarially-confirmed to add value over a baseline?\n"
        "</review_focus>\n\n"
        "<rubric>\n"
        f"{json.dumps(rubric, indent=2, sort_keys=True)}\n"
        "</rubric>\n\n"
        "<trace>\n"
        f"{trace_excerpt}\n"
        "</trace>\n\n"
        "Return JSON with keys passed, score, findings, and recommended_prompt_changes.\n"
    )


def _structure_findings(steps: list[dict[str, Any]], rubric: dict[str, Any]) -> list[TraceFinding]:
    findings: list[TraceFinding] = []
    allowed = {"reasoning", "tool_call", "tool_result", "final"}
    call_ids: set[str] = set()
    result_ids: set[str] = set()

    for index, step in enumerate(steps):
        step_type = step.get("type")
        findings.append(
            TraceFinding(
                "structure.known_step_type",
                step_type in allowed,
                f"step {index} has type {step_type!r}",
                "high",
            )
        )
        if step_type == "tool_call":
            call_id = step.get("id")
            findings.append(
                TraceFinding(
                    "structure.tool_call_has_id",
                    bool(call_id),
                    f"tool call at step {index} has id {call_id!r}",
                    "high",
                )
            )
            if call_id:
                findings.append(
                    TraceFinding(
                        "structure.tool_call_id_unique",
                        call_id not in call_ids,
                        f"tool call id {call_id!r} is unique",
                        "high",
                    )
                )
                call_ids.add(call_id)
            findings.append(
                TraceFinding(
                    "structure.tool_call_has_name",
                    bool(step.get("name")),
                    f"tool call at step {index} names a tool",
                    "high",
                )
            )
        if step_type == "tool_result":
            result_id = step.get("tool_call_id")
            if result_id:
                result_ids.add(result_id)
            findings.append(
                TraceFinding(
                    "structure.tool_result_references_call",
                    bool(result_id) and result_id in call_ids,
                    f"tool result at step {index} references {result_id!r}",
                    "high",
                )
            )

    allow_unresolved = bool(rubric.get("allow_unresolved_tools", False))
    for call_id in sorted(call_ids):
        findings.append(
            TraceFinding(
                "structure.tool_call_has_result",
                allow_unresolved or call_id in result_ids,
                f"tool call {call_id!r} has a result",
                "high",
            )
        )

    return findings


def _tool_use_findings(steps: list[dict[str, Any]], rubric: dict[str, Any]) -> list[TraceFinding]:
    calls = [step for step in steps if step.get("type") == "tool_call"]
    names = [str(call.get("name")) for call in calls]
    findings: list[TraceFinding] = []

    min_calls = rubric.get("min_tool_calls")
    if min_calls is not None:
        findings.append(
            TraceFinding(
                "tool_use.min_tool_calls",
                len(calls) >= int(min_calls),
                f"found {len(calls)} tool calls, expected at least {min_calls}",
                "medium",
            )
        )

    max_calls = rubric.get("max_tool_calls")
    if max_calls is not None:
        findings.append(
            TraceFinding(
                "tool_use.max_tool_calls",
                len(calls) <= int(max_calls),
                f"found {len(calls)} tool calls, expected at most {max_calls}",
                "medium",
            )
        )

    for name in rubric.get("required_tools", []):
        findings.append(
            TraceFinding(
                "tool_use.required_tool",
                name in names,
                f"required tool {name!r} was {'used' if name in names else 'not used'}",
                "high",
            )
        )

    for name in rubric.get("forbidden_tools", []):
        findings.append(
            TraceFinding(
                "tool_use.forbidden_tool",
                name not in names,
                f"forbidden tool {name!r} was {'not used' if name not in names else 'used'}",
                "high",
            )
        )

    for expected in rubric.get("expected_call_args", []):
        name = expected["name"]
        args_contains = expected.get("args_contains", {})
        findings.append(
            TraceFinding(
                "tool_use.expected_args",
                _has_call_args(calls, name, args_contains),
                f"expected args for {name!r}: {args_contains}",
                "medium",
            )
        )

    duplicate_limit = int(rubric.get("max_duplicate_calls", 1))
    duplicates = _duplicate_call_count(calls)
    findings.append(
        TraceFinding(
            "tool_use.duplicate_calls",
            duplicates <= duplicate_limit,
            f"found {duplicates} duplicate tool calls, limit is {duplicate_limit}",
            "medium",
        )
    )
    return findings


def _reasoning_findings(steps: list[dict[str, Any]], rubric: dict[str, Any]) -> list[TraceFinding]:
    findings: list[TraceFinding] = []
    if rubric.get("require_reasoning_before_first_tool", True):
        has_reasoning = _has_reasoning_before_first_tool(steps)
        findings.append(
            TraceFinding(
                "reasoning.before_first_tool",
                has_reasoning,
                (
                    "reasoning appears before the first tool call"
                    if has_reasoning
                    else "reasoning is missing before the first tool call"
                ),
                "medium",
            )
        )

    if rubric.get("require_reasoning_after_tool_results", True):
        for label, result_index in _tool_result_review_targets(steps):
            has_reasoning = _has_reasoning_before_next_action(steps, result_index)
            findings.append(
                TraceFinding(
                    "reasoning.after_tool_result",
                    has_reasoning,
                    (
                        f"{label} is followed by reasoning before next action"
                        if has_reasoning
                        else f"{label} is not followed by reasoning before next action"
                    ),
                    "high",
                )
            )

    if rubric.get("require_result_quality_assessment", True):
        for label, result_index in _tool_result_review_targets(steps):
            reasoning = _reasoning_between_result_and_next_action(steps, result_index)
            has_quality_assessment = _contains_any(reasoning, QUALITY_TERMS)
            findings.append(
                TraceFinding(
                    "reasoning.result_quality_assessment",
                    has_quality_assessment,
                    (
                        f"reasoning after {label} assesses quality or evidence"
                        if has_quality_assessment
                        else f"reasoning after {label} does not assess quality or evidence"
                    ),
                    "medium",
                )
            )

    if rubric.get("require_error_recovery_reasoning", True):
        for label, result_index in _error_result_review_targets(steps):
            reasoning = _reasoning_between_result_and_next_action(steps, result_index)
            has_recovery = _contains_any(reasoning, ERROR_TERMS)
            findings.append(
                TraceFinding(
                    "reasoning.error_recovery",
                    has_recovery,
                    (
                        f"error in {label} has recovery reasoning"
                        if has_recovery
                        else f"error in {label} is missing recovery reasoning"
                    ),
                    "high",
                )
            )

    return findings


def _final_findings(steps: list[dict[str, Any]], rubric: dict[str, Any]) -> list[TraceFinding]:
    final_text = "\n".join(str(step.get("text", "")) for step in steps if step.get("type") == "final")
    findings = [
        TraceFinding(
            "final.exists",
            bool(final_text.strip()),
            "trace has a final answer",
            "high",
        )
    ]
    for text in rubric.get("required_final_contains", []):
        contains_text = text.lower() in final_text.lower()
        findings.append(
            TraceFinding(
                "final.required_text",
                contains_text,
                (
                    f"final answer contains {text!r}"
                    if contains_text
                    else f"final answer is missing {text!r}"
                ),
                "medium",
            )
        )
    return findings


def _score(findings: list[TraceFinding], prefix: str) -> float:
    relevant = [finding for finding in findings if finding.check.startswith(prefix)]
    if not relevant:
        return 1.0
    passed = sum(1 for finding in relevant if finding.passed)
    return round(passed / len(relevant), 3)


def _has_call_args(calls: list[dict[str, Any]], name: str, args_contains: dict[str, Any]) -> bool:
    for call in calls:
        if call.get("name") != name:
            continue
        args = call.get("args", {})
        if all(str(value).lower() in str(args.get(key, "")).lower() for key, value in args_contains.items()):
            return True
    return False


def _duplicate_call_count(calls: list[dict[str, Any]]) -> int:
    seen: set[str] = set()
    duplicates = 0
    for call in calls:
        fingerprint = json.dumps(
            {"args": call.get("args", {}), "name": call.get("name")},
            sort_keys=True,
        )
        if fingerprint in seen:
            duplicates += 1
        seen.add(fingerprint)
    return duplicates


def _has_reasoning_before_first_tool(steps: list[dict[str, Any]]) -> bool:
    for step in steps:
        if step.get("type") == "tool_call":
            return False
        if step.get("type") == "reasoning" and str(step.get("summary", "")).strip():
            return True
    return False


def _tool_result_indexes(steps: list[dict[str, Any]]) -> list[int]:
    return [index for index, step in enumerate(steps) if step.get("type") == "tool_result"]


def _tool_result_review_targets(steps: list[dict[str, Any]]) -> list[tuple[str, int]]:
    grouped: dict[str, list[int]] = {}
    targets: list[tuple[str, int]] = []
    for index in _tool_result_indexes(steps):
        group = _parallel_group(steps[index])
        if group:
            grouped.setdefault(group, []).append(index)
        else:
            targets.append((f"tool result at step {index}", index))
    for group, indexes in sorted(grouped.items(), key=lambda item: item[1][-1]):
        targets.append((f"parallel group {group!r} ending at step {indexes[-1]}", indexes[-1]))
    return sorted(targets, key=lambda item: item[1])


def _error_result_review_targets(steps: list[dict[str, Any]]) -> list[tuple[str, int]]:
    grouped: dict[str, list[int]] = {}
    targets: list[tuple[str, int]] = []
    for index, step in enumerate(steps):
        if step.get("type") != "tool_result" or not _is_error_result(step):
            continue
        group = _parallel_group(step)
        if group:
            grouped.setdefault(group, []).append(index)
        else:
            targets.append((f"tool result at step {index}", index))
    for group, indexes in sorted(grouped.items(), key=lambda item: item[1][-1]):
        targets.append((f"parallel group {group!r} ending at step {indexes[-1]}", indexes[-1]))
    return sorted(targets, key=lambda item: item[1])


def _is_error_result(step: dict[str, Any]) -> bool:
    return step.get("ok") is False or bool(step.get("error"))


def _parallel_group(step: dict[str, Any]) -> str:
    return str(step.get("parallel_group") or step.get("batch_id") or "").strip()


def _has_reasoning_before_next_action(steps: list[dict[str, Any]], result_index: int) -> bool:
    return bool(_reasoning_between_result_and_next_action(steps, result_index).strip())


def _reasoning_between_result_and_next_action(steps: list[dict[str, Any]], result_index: int) -> str:
    parts: list[str] = []
    for step in steps[result_index + 1 :]:
        if step.get("type") in {"tool_call", "final"}:
            break
        if step.get("type") == "reasoning":
            parts.append(str(step.get("summary", "")))
    return "\n".join(parts)


def _contains_any(text: str, terms: set[str]) -> bool:
    lower = text.lower()
    return any(term in lower for term in terms)


def _compact_trace(steps: list[dict[str, Any]]) -> str:
    lines: list[str] = []
    for index, step in enumerate(steps):
        step_type = step.get("type")
        if step_type == "reasoning":
            lines.append(f"{index}. reasoning: {step.get('summary', '')}")
        elif step_type == "tool_call":
            args = json.dumps(step.get("args", {}), sort_keys=True)
            group = _parallel_group(step)
            group_text = f" parallel_group={group}" if group else ""
            lines.append(f"{index}. tool_call {step.get('id')}: {step.get('name')}{group_text} {args}")
        elif step_type == "tool_result":
            output = str(step.get("output", step.get("error", ""))).replace("\n", " ")
            group = _parallel_group(step)
            group_text = f" parallel_group={group}" if group else ""
            lines.append(f"{index}. tool_result for {step.get('tool_call_id')}{group_text}: {output[:500]}")
        elif step_type == "final":
            lines.append(f"{index}. final: {step.get('text', '')}")
        else:
            lines.append(f"{index}. {step_type}: {step}")
    return "\n".join(lines)
