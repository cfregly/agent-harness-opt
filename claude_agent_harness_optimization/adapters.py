"""Adapters that normalize provider transcripts into trace-review events."""

from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Any


CLAUDE_MESSAGE_ADAPTERS = {
    "anthropic",
    "anthropic_messages",
    "claude",
    "claude_messages",
    "messages",
}
CLAUDE_CODE_STREAM_ADAPTERS = {
    "claude_code",
    "claude_code_stream",
    "claude_code_stream_json",
    "claude_code_jsonl",
}
GEMINI_STREAM_ADAPTERS = {
    "gemini",
    "gemini_cli",
    "gemini_stream",
    "gemini_stream_json",
    "gemini_jsonl",
}
OPENCODE_TEXT_ADAPTERS = {
    "opencode",
    "opencode_text",
    "opencode_log",
}
RUNTIME_EVENT_ADAPTERS = {
    "agent_sdk",
    "codex",
    "codex_cli",
    "codex_exec",
    "codex_jsonl",
    "codex_trace",
    "cursor",
    "cursor_agent",
    "cursor_agent_stream",
    "cursor_agent_stream_json",
    "cursor_trace",
    "generic_runtime",
    "ide_agent",
    "langgraph",
    "langsmith",
    "openai_agents",
    "runtime",
    "runtime_events",
}


def load_json(path: str | Path) -> Any:
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_run_export(path: str | Path) -> Any:
    """Load a JSON, JSONL, or raw text harness export."""

    source_path = Path(path)
    text = source_path.read_text(encoding="utf-8")
    stripped = text.strip()
    if not stripped:
        return []
    if source_path.suffix in {".txt", ".log", ".out", ".err"}:
        return text
    if source_path.suffix == ".jsonl" or (
        "\n" in stripped and not stripped.startswith(("{", "["))
    ):
        return [json.loads(line) for line in stripped.splitlines() if line.strip()]
    return json.loads(stripped)


def supported_adapters() -> list[str]:
    """Return adapter names accepted by normalize_run_export."""

    return sorted(
        CLAUDE_CODE_STREAM_ADAPTERS
        | CLAUDE_MESSAGE_ADAPTERS
        | GEMINI_STREAM_ADAPTERS
        | OPENCODE_TEXT_ADAPTERS
        | RUNTIME_EVENT_ADAPTERS
        | {"auto"}
    )


def normalize_run_export(
    payload: dict[str, Any] | list[dict[str, Any]] | str,
    adapter: str | None = None,
) -> dict[str, Any]:
    """Normalize a raw run export into the shared trace-review contract."""

    adapter_name = (adapter or _infer_adapter(payload)).strip().lower()
    if adapter_name == "auto":
        adapter_name = _infer_adapter(payload)
    if adapter_name in CLAUDE_CODE_STREAM_ADAPTERS:
        return claude_code_stream_to_trace(payload)
    if adapter_name in GEMINI_STREAM_ADAPTERS:
        return gemini_stream_to_trace(payload)
    if adapter_name in OPENCODE_TEXT_ADAPTERS:
        return opencode_text_to_trace(payload)
    if adapter_name in CLAUDE_MESSAGE_ADAPTERS:
        return claude_messages_to_trace(payload)
    if adapter_name in RUNTIME_EVENT_ADAPTERS:
        if isinstance(payload, str):
            payload = _jsonl_events(payload)
        return runtime_events_to_trace(payload)
    raise ValueError(f"unsupported run adapter: {adapter_name}")


def claude_messages_to_trace(payload: dict[str, Any] | list[dict[str, Any]]) -> dict[str, Any]:
    """Normalize Claude-style Messages API content blocks into trace steps."""

    if isinstance(payload, list):
        messages = payload
        name = "claude_trace"
        task = ""
        rubric = {}
    else:
        messages = payload.get("messages", [])
        name = payload.get("name", "claude_trace")
        task = payload.get("task", "")
        rubric = payload.get("rubric", {})

    steps: list[dict[str, Any]] = []
    for message in messages:
        role = message.get("role")
        content = _content_blocks(message.get("content", []))
        for index, block in enumerate(content):
            block_type = block.get("type")
            if role == "assistant":
                if block_type == "thinking":
                    steps.append(
                        {
                            "source": "claude_thinking",
                            "summary": block.get("thinking", ""),
                            "signature_present": bool(block.get("signature")),
                            "type": "reasoning",
                        }
                    )
                elif block_type == "redacted_thinking":
                    steps.append(
                        {
                            "opaque": True,
                            "source": "claude_redacted_thinking",
                            "summary": "",
                            "type": "reasoning",
                        }
                    )
                elif block_type == "tool_use":
                    steps.append(
                        {
                            "args": block.get("input", {}),
                            "id": block.get("id"),
                            "name": block.get("name"),
                            "type": "tool_call",
                        }
                    )
                elif block_type == "text":
                    step_type = "reasoning" if _has_later_tool_use(content, index) else "final"
                    key = "summary" if step_type == "reasoning" else "text"
                    steps.append(
                        {
                            key: block.get("text", ""),
                            "source": "assistant_text" if step_type == "reasoning" else "assistant_final_text",
                            "type": step_type,
                        }
                    )
            elif role == "user" and block_type == "tool_result":
                steps.append(
                    {
                        "ok": not bool(block.get("is_error", False)),
                        "output": _stringify_tool_result(block.get("content", "")),
                        "tool_call_id": block.get("tool_use_id"),
                        "type": "tool_result",
                    }
                )

    return {
        "name": name,
        "rubric": rubric,
        "steps": _normalize_decision_note_steps(steps),
        "task": task,
    }


def claude_code_stream_to_trace(payload: dict[str, Any] | list[dict[str, Any]] | str) -> dict[str, Any]:
    """Normalize `claude -p --output-format stream-json --verbose` JSONL."""

    events, wrapper = _events_and_wrapper(payload)
    metadata: dict[str, Any] = {"source_harness": "claude_code_stream_json"}
    steps: list[dict[str, Any]] = []

    for event in events:
        event_type = _event_type(event)
        if event_type == "system" and event.get("subtype") == "init":
            metadata.update(
                {
                    "api_key_source": event.get("apiKeySource", ""),
                    "cwd": event.get("cwd", ""),
                    "harness_version": event.get("claude_code_version", ""),
                    "model": event.get("model", ""),
                    "permission_mode": event.get("permissionMode", ""),
                    "tools": event.get("tools", []),
                }
            )
            continue

        if event_type in {"assistant", "user"}:
            message = event.get("message", {})
            role = message.get("role", event_type) if isinstance(message, dict) else event_type
            content = _content_blocks(message.get("content", [])) if isinstance(message, dict) else []
            for index, block in enumerate(content):
                block_type = block.get("type")
                if role == "assistant":
                    if block_type == "thinking":
                        steps.append(
                            {
                                "source": "claude_code_thinking",
                                "summary": block.get("thinking", ""),
                                "signature_present": bool(block.get("signature")),
                                "type": "reasoning",
                            }
                        )
                    elif block_type == "redacted_thinking":
                        steps.append(
                            {
                                "opaque": True,
                                "source": "claude_code_redacted_thinking",
                                "summary": "",
                                "type": "reasoning",
                            }
                        )
                    elif block_type == "tool_use":
                        steps.append(
                            {
                                "args": block.get("input", {}),
                                "id": block.get("id"),
                                "name": block.get("name"),
                                "type": "tool_call",
                            }
                        )
                    elif block_type == "text":
                        step_type = "reasoning" if _has_later_tool_use(content, index) else "final"
                        steps.append(
                            {
                                "source": "claude_code_text",
                                "summary" if step_type == "reasoning" else "text": block.get("text", ""),
                                "type": step_type,
                            }
                        )
                elif role == "user" and block_type == "tool_result":
                    steps.append(
                        {
                            "ok": not bool(block.get("is_error", False)),
                            "output": _stringify_tool_result(block.get("content", "")),
                            "tool_call_id": block.get("tool_use_id"),
                            "type": "tool_result",
                        }
                    )
            continue

        if event_type == "result" and event.get("result"):
            metadata.update(
                {
                    "duration_ms": event.get("duration_ms"),
                    "terminal_reason": event.get("terminal_reason", ""),
                    "total_cost_usd": event.get("total_cost_usd"),
                }
            )
            if not _final_text(steps):
                steps.append({"text": str(event.get("result", "")), "type": "final"})

    return _trace_from_parts(
        wrapper,
        default_name="claude_code_stream_trace",
        default_task="",
        metadata={key: value for key, value in metadata.items() if value not in ("", None, [])},
        steps=steps,
    )


def gemini_stream_to_trace(payload: dict[str, Any] | list[dict[str, Any]] | str) -> dict[str, Any]:
    """Normalize `gemini --output-format stream-json` JSONL."""

    events, wrapper = _events_and_wrapper(payload)
    metadata: dict[str, Any] = {"source_harness": "gemini_cli_stream_json"}
    steps: list[dict[str, Any]] = []
    assistant_deltas: list[str] = []

    def flush_assistant_deltas() -> None:
        if not assistant_deltas:
            return
        text = "".join(assistant_deltas).strip()
        assistant_deltas.clear()
        if text:
            steps.extend(_steps_from_visible_text(text, source="gemini_visible_decision_note"))

    for event in events:
        event_type = _event_type(event)
        if event_type == "init":
            metadata.update({"model": event.get("model", ""), "session_id": event.get("session_id", "")})
        elif event_type == "tool_use":
            flush_assistant_deltas()
            steps.append(
                {
                    "args": _event_args(event),
                    "id": _first_value(event, "tool_id", "id", "call_id", "tool_call_id"),
                    "name": _first_value(event, "tool_name", "tool", "name"),
                    "type": "tool_call",
                }
            )
        elif event_type == "tool_result":
            flush_assistant_deltas()
            steps.append(
                {
                    "ok": str(event.get("status", "")).lower() not in {"error", "failed", "failure"},
                    "output": _first_text(event, "output", "result", "content", "text", "message"),
                    "tool_call_id": _first_value(event, "tool_id", "tool_call_id", "call_id", "id"),
                    "type": "tool_result",
                }
            )
        elif event_type == "message" and event.get("role") == "assistant":
            assistant_deltas.append(str(event.get("content", "")))
        elif event_type == "result":
            flush_assistant_deltas()
            metadata.update({"result_status": event.get("status", ""), "stats": event.get("stats", {})})

    flush_assistant_deltas()

    return _trace_from_parts(
        wrapper,
        default_name="gemini_cli_stream_trace",
        default_task="",
        metadata={key: value for key, value in metadata.items() if value not in ("", None, {})},
        steps=steps,
    )


def opencode_text_to_trace(payload: dict[str, Any] | list[dict[str, Any]] | str) -> dict[str, Any]:
    """Normalize OpenCode text logs when a structured export is unavailable."""

    if isinstance(payload, dict):
        raw = str(payload.get("text", payload.get("raw", "")))
        wrapper = payload
    elif isinstance(payload, list):
        raw = "\n".join(json.dumps(item, sort_keys=True) for item in payload)
        wrapper = {}
    else:
        raw = payload
        wrapper = {}

    steps: list[dict[str, Any]] = []
    command_matches = re.findall(r'"command"\s*:\s*"([^"]+)"', raw)
    timeout_matches = re.findall(r'"timeout"\s*:\s*(\d+)', raw)
    for index, command in enumerate(command_matches):
        steps.append(
            {
                "args": {
                    "command": command,
                    **({"timeout": int(timeout_matches[index])} if index < len(timeout_matches) else {}),
                },
                "id": f"opencode_tool_{index}",
                "name": "Bash",
                "type": "tool_call",
            }
        )
        status = "error" if "tool_call_error" in raw and index == 0 else "completed"
        steps.append(
            {
                "ok": status != "error",
                "output": _opencode_command_output(raw, command),
                "tool_call_id": f"opencode_tool_{index}",
                "type": "tool_result",
            }
        )
    final_text = _opencode_final_text(raw)
    if final_text:
        steps.append({"text": final_text, "type": "final"})
    if not steps and raw.strip():
        steps.append({"text": raw.strip(), "type": "final"})

    return _trace_from_parts(
        wrapper,
        default_name="opencode_text_trace",
        default_task="",
        metadata={"source_harness": "opencode_text"},
        steps=steps,
    )


def runtime_events_to_trace(payload: dict[str, Any] | list[dict[str, Any]]) -> dict[str, Any]:
    """Normalize generic Agent SDK or IDE-agent event exports into trace steps."""

    if isinstance(payload, list):
        events = payload
        name = "runtime_trace"
        task = ""
        rubric = {}
        harness = ""
    else:
        events = _runtime_events(payload)
        name = payload.get("name", "runtime_trace")
        task = payload.get("task", "")
        rubric = payload.get("rubric", {})
        harness = payload.get("harness", payload.get("source_harness", ""))

    steps = [_runtime_event_to_step(event) for event in events if isinstance(event, dict)]
    steps = [step for step in steps if step]
    return {
        "metadata": {"source_harness": harness} if harness else {},
        "name": name,
        "rubric": rubric,
        "steps": _normalize_decision_note_steps(steps),
        "task": task,
    }


def _content_blocks(content: Any) -> list[dict[str, Any]]:
    if isinstance(content, str):
        return [{"text": content, "type": "text"}]
    if isinstance(content, list):
        return [block for block in content if isinstance(block, dict)]
    return []


def _infer_adapter(payload: Any) -> str:
    if isinstance(payload, str):
        return "opencode_text"
    if isinstance(payload, list):
        event_types = {_event_type(item) for item in payload if isinstance(item, dict)}
        if {"system", "assistant", "user"} & event_types and any(
            isinstance(item, dict) and item.get("subtype") == "init" for item in payload
        ):
            return "claude_code_stream_json"
        if {"init", "tool_use", "tool_result"} & event_types and any(
            isinstance(item, dict) and item.get("tool_name") == "run_shell_command" for item in payload
        ):
            return "gemini_stream_json"
        if any(_looks_like_claude_message(item) for item in payload if isinstance(item, dict)):
            return "claude_messages"
        return "runtime_events"
    if not isinstance(payload, dict):
        return "runtime_events"
    declared = payload.get("adapter") or payload.get("source_adapter") or payload.get("format")
    if declared:
        return str(declared)
    messages = payload.get("messages")
    if isinstance(messages, list) and any(
        _looks_like_claude_message(item) for item in messages if isinstance(item, dict)
    ):
        return "claude_messages"
    return "runtime_events"


def _events_and_wrapper(payload: dict[str, Any] | list[dict[str, Any]] | str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if isinstance(payload, dict):
        wrapper = payload
        events = _runtime_events(payload)
        if not events and isinstance(payload.get("raw"), str):
            events = _jsonl_events(payload["raw"])
        return events, wrapper
    if isinstance(payload, str):
        return _jsonl_events(payload), {}
    return [event for event in payload if isinstance(event, dict)], {}


def _jsonl_events(text: str) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line.startswith("{"):
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(event, dict):
            events.append(event)
    return events


def _trace_from_parts(
    wrapper: dict[str, Any],
    *,
    default_name: str,
    default_task: str,
    metadata: dict[str, Any],
    steps: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "metadata": {**metadata, **wrapper.get("metadata", {})},
        "name": wrapper.get("name", default_name),
        "rubric": wrapper.get("rubric", {}),
        "steps": _normalize_decision_note_steps(steps),
        "task": wrapper.get("task", default_task),
    }


def _normalize_decision_note_steps(steps: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for step in steps:
        if step.get("type") != "final":
            normalized.append(step)
            continue
        for split_step in _steps_from_visible_text(str(step.get("text", "")), source="visible_decision_note"):
            if split_step.get("type") == "final":
                normalized.append({**step, "text": split_step.get("text", "")})
            else:
                normalized.append(split_step)
    return normalized


def _steps_from_visible_text(text: str, *, source: str) -> list[dict[str, Any]]:
    decision_lines: list[str] = []
    final_lines: list[str] = []
    for line in text.splitlines():
        if _looks_like_decision_note(line):
            decision_lines.append(line)
        else:
            final_lines.append(line)
    steps: list[dict[str, Any]] = []
    if decision_lines:
        steps.append(
            {
                "source": source,
                "summary": "\n".join(decision_lines).strip(),
                "type": "reasoning",
            }
        )
    final_text = "\n".join(final_lines).strip()
    if final_text:
        steps.append({"text": final_text, "type": "final"})
    return steps


def _looks_like_decision_note(text: str) -> bool:
    upper = text.strip().upper()
    return upper.startswith("DECISION_NOTE") or upper.startswith("DECISION NOTE")


def _final_text(steps: list[dict[str, Any]]) -> str:
    return "\n".join(str(step.get("text", "")) for step in steps if step.get("type") == "final")


def _opencode_final_text(raw: str) -> str:
    marker = "HARNESS_OK"
    index = raw.find(marker)
    if index >= 0:
        return _strip_opencode_logs(raw[index:].strip())
    return _strip_opencode_logs(raw.strip())


def _opencode_command_output(raw: str, command: str) -> str:
    output_match = re.search(r"Command output:\s*(.+)", raw, re.DOTALL)
    if output_match:
        return _strip_opencode_logs(output_match.group(1).strip())
    return f"OpenCode log references command {command!r}."


def _strip_opencode_logs(text: str) -> str:
    for marker in ("\nINFO ", "\nDEBUG ", "\nWARN ", "\nERROR ", "\ntype="):
        if marker in text:
            text = text.split(marker, 1)[0]
    return text.strip()


def _looks_like_claude_message(item: dict[str, Any]) -> bool:
    role = item.get("role")
    content = item.get("content")
    if role not in {"assistant", "user"}:
        return False
    if isinstance(content, list):
        return any(
            isinstance(block, dict)
            and block.get("type") in {"text", "thinking", "redacted_thinking", "tool_use", "tool_result"}
            for block in content
        )
    return isinstance(content, str)


def _runtime_events(payload: dict[str, Any]) -> list[dict[str, Any]]:
    for key in ("events", "steps", "trace", "messages"):
        value = payload.get(key)
        if isinstance(value, list):
            return value
    run = payload.get("run")
    if isinstance(run, dict):
        value = run.get("events")
        if isinstance(value, list):
            return value
    return []


def _runtime_event_to_step(event: dict[str, Any]) -> dict[str, Any]:
    event_type = _event_type(event)
    if event_type.startswith("item_"):
        return _codex_item_event_to_step(event)
    if event_type in {"reasoning", "thinking", "assistant_thinking", "thought", "plan", "reflection", "decision"}:
        return {
            "source": event.get("source", event_type),
            "summary": _first_text(event, "summary", "text", "thinking", "message", "content"),
            "type": "reasoning",
        }
    if event_type in {"tool_call", "tool_use", "function_call", "mcp_call", "action"}:
        return {
            "args": _event_args(event),
            "id": _first_value(event, "id", "call_id", "tool_call_id", "tool_use_id"),
            "name": _first_value(event, "tool", "tool_name", "name", "function", "action"),
            "parallel_group": _first_value(event, "parallel_group", "batch_id"),
            "type": "tool_call",
        }
    if event_type in {"tool_result", "tool_output", "observation", "result", "mcp_result"}:
        return {
            "ok": not bool(event.get("error") or event.get("is_error")),
            "output": _first_text(event, "output", "result", "content", "text", "message"),
            "parallel_group": _first_value(event, "parallel_group", "batch_id"),
            "tool_call_id": _first_value(event, "tool_call_id", "call_id", "tool_use_id", "id"),
            "type": "tool_result",
        }
    if event_type in {"final", "assistant_final", "final_answer", "message"}:
        return {
            "text": _first_text(event, "text", "message", "content", "output"),
            "type": "final",
        }
    if _looks_like_tool_result(event):
        return _runtime_event_to_step({**event, "type": "tool_result"})
    if _looks_like_tool_call(event):
        return _runtime_event_to_step({**event, "type": "tool_call"})
    if _looks_like_reasoning(event):
        return _runtime_event_to_step({**event, "type": "reasoning"})
    return {}


def _codex_item_event_to_step(event: dict[str, Any]) -> dict[str, Any]:
    item = event.get("item")
    if not isinstance(item, dict):
        return {}
    status = str(event.get("type", "")).lower()
    item_type = _event_type(item)
    if "started" in status:
        if item_type in {"command_execution", "command"}:
            return {
                "args": {"command": _first_text(item, "command", "cmd")},
                "id": _first_value(item, "id"),
                "name": "Bash",
                "type": "tool_call",
            }
        if item_type in {"mcp_tool_call", "mcp_call", "tool_call"}:
            tool_name = _codex_tool_name(item)
            return {
                "args": _event_args(item),
                "id": _first_value(item, "id", "call_id", "tool_call_id"),
                "name": tool_name,
                "type": "tool_call",
            }
        if item_type in {"web_search", "web_search_call"}:
            return {
                "args": {"query": _first_text(item, "query", "text")},
                "id": _first_value(item, "id"),
                "name": "web_search",
                "type": "tool_call",
            }
    if "completed" in status:
        if item_type in {"reasoning", "agent_reasoning"}:
            return {
                "source": "codex_reasoning",
                "summary": _first_text(item, "summary", "text", "message", "content"),
                "type": "reasoning",
            }
        if item_type in {"agent_message", "message", "assistant_message"}:
            return {
                "text": _first_text(item, "text", "message", "content"),
                "type": "final",
            }
        if item_type in {"command_execution", "command"}:
            return {
                "ok": str(item.get("status", "")).lower() not in {"failed", "error"},
                "output": _first_text(item, "output", "aggregated_output", "result", "text", "message"),
                "tool_call_id": _first_value(item, "id"),
                "type": "tool_result",
            }
        if item_type in {"mcp_tool_call", "mcp_tool_result", "mcp_call", "tool_call", "tool_result"}:
            return {
                "ok": not bool(item.get("error") or item.get("is_error")),
                "output": _first_text(item, "output", "result", "content", "text", "message"),
                "tool_call_id": _first_value(item, "id", "call_id", "tool_call_id"),
                "type": "tool_result",
            }
        if item_type in {"web_search", "web_search_call"}:
            return {
                "ok": not bool(item.get("error")),
                "output": _first_text(item, "output", "result", "content", "text", "message"),
                "tool_call_id": _first_value(item, "id"),
                "type": "tool_result",
            }
    return {}


def _codex_tool_name(item: dict[str, Any]) -> str:
    raw = _first_value(item, "tool_name", "tool", "name")
    if raw:
        return str(raw)
    server = _first_value(item, "server", "server_name", "mcp_server")
    tool = _first_value(item, "mcp_tool", "mcp_tool_name")
    if server and tool:
        return f"mcp__{server}__{tool}"
    return "mcp_tool"


def _event_type(event: dict[str, Any]) -> str:
    value = _first_value(event, "type", "event", "kind", "role")
    text = str(value).strip()
    text = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", text)
    return text.lower().replace("-", "_").replace(".", "_")


def _event_args(event: dict[str, Any]) -> dict[str, Any]:
    for key in ("args", "arguments", "input", "parameters", "tool_input"):
        value = event.get(key)
        if isinstance(value, dict):
            return value
        if isinstance(value, str) and value.strip().startswith("{"):
            try:
                decoded = json.loads(value)
            except json.JSONDecodeError:
                decoded = None
            if isinstance(decoded, dict):
                return decoded
    for key in ("function", "tool_call", "toolCall"):
        value = event.get(key)
        if isinstance(value, dict):
            args = _event_args(value)
            if args:
                return args
    return {}


def _first_value(event: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        value = event.get(key)
        if value not in (None, ""):
            return value
        camel = _to_camel_case(key)
        value = event.get(camel)
        if value not in (None, ""):
            return value
        for nested_key in ("function", "tool_call", "toolCall"):
            nested = event.get(nested_key)
            if not isinstance(nested, dict):
                continue
            value = nested.get(key)
            if value not in (None, ""):
                return value
            value = nested.get(camel)
            if value not in (None, ""):
                return value
    return ""


def _to_camel_case(key: str) -> str:
    parts = key.split("_")
    return parts[0] + "".join(part.capitalize() for part in parts[1:])


def _first_text(event: dict[str, Any], *keys: str) -> str:
    value = _first_value(event, *keys)
    if isinstance(value, str):
        return value
    if value in (None, ""):
        return ""
    return json.dumps(value, sort_keys=True)


def _looks_like_tool_call(event: dict[str, Any]) -> bool:
    return bool(_first_value(event, "tool", "tool_name", "function")) and any(
        key in event for key in ("args", "arguments", "input", "parameters", "tool_input", "toolInput")
    )


def _looks_like_tool_result(event: dict[str, Any]) -> bool:
    return bool(_first_value(event, "tool_call_id", "tool_use_id", "call_id")) and any(
        key in event for key in ("output", "result", "content", "error")
    )


def _looks_like_reasoning(event: dict[str, Any]) -> bool:
    return bool(_first_value(event, "summary", "thinking")) and not _looks_like_tool_call(event)


def _has_later_tool_use(content: list[dict[str, Any]], index: int) -> bool:
    return any(block.get("type") == "tool_use" for block in content[index + 1 :])


def _stringify_tool_result(content: Any) -> str:
    if isinstance(content, str):
        return content
    return json.dumps(content, sort_keys=True)
