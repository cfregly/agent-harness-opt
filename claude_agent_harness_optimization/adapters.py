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
    "claude_code",
    "claude_messages",
    "messages",
}
RUNTIME_EVENT_ADAPTERS = {
    "agent_sdk",
    "codex",
    "codex_cli",
    "codex_exec",
    "codex_jsonl",
    "codex_trace",
    "cursor",
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
    """Load a JSON or JSONL harness export."""

    source_path = Path(path)
    text = source_path.read_text(encoding="utf-8")
    stripped = text.strip()
    if not stripped:
        return []
    if source_path.suffix == ".jsonl" or (
        "\n" in stripped and not stripped.startswith(("{", "["))
    ):
        return [json.loads(line) for line in stripped.splitlines() if line.strip()]
    return json.loads(stripped)


def supported_adapters() -> list[str]:
    """Return adapter names accepted by normalize_run_export."""

    return sorted(CLAUDE_MESSAGE_ADAPTERS | RUNTIME_EVENT_ADAPTERS | {"auto"})


def normalize_run_export(
    payload: dict[str, Any] | list[dict[str, Any]],
    adapter: str | None = None,
) -> dict[str, Any]:
    """Normalize a raw run export into the shared trace-review contract."""

    adapter_name = (adapter or _infer_adapter(payload)).strip().lower()
    if adapter_name == "auto":
        adapter_name = _infer_adapter(payload)
    if adapter_name in CLAUDE_MESSAGE_ADAPTERS:
        return claude_messages_to_trace(payload)
    if adapter_name in RUNTIME_EVENT_ADAPTERS:
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
        "steps": steps,
        "task": task,
    }


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
        "steps": steps,
        "task": task,
    }


def _content_blocks(content: Any) -> list[dict[str, Any]]:
    if isinstance(content, str):
        return [{"text": content, "type": "text"}]
    if isinstance(content, list):
        return [block for block in content if isinstance(block, dict)]
    return []


def _infer_adapter(payload: Any) -> str:
    if isinstance(payload, list):
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
                "output": _first_text(item, "output", "result", "text", "message"),
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
