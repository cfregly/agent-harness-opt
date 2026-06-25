"""Import external harness runs into the local trace and audit contracts."""

from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Any

from .adapters import load_json, normalize_run_export


def import_run_export(
    input_path: str | Path,
    *,
    adapter: str | None = None,
    name: str | None = None,
    out_dir: str | Path | None = None,
    task: str | None = None,
    tool_inventory: str | Path | None = None,
    value_bar: str | Path | None = None,
) -> dict[str, Any]:
    """Normalize one harness export and write a trace plus audit bundle."""

    source_path = Path(input_path)
    payload = load_json(source_path)
    trace = normalize_run_export(payload, adapter)
    if name:
        trace["name"] = name
    if task:
        trace["task"] = task

    target_dir = Path(out_dir) if out_dir else source_path.parent / f"{source_path.stem}_import"
    target_dir.mkdir(parents=True, exist_ok=True)
    trace_name = _slug(trace.get("name") or source_path.stem)
    trace_path = target_dir / f"{trace_name}.trace.json"
    trace_path.write_text(json.dumps(trace, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    bundle = _bundle_from_payload(
        payload,
        bundle_name=name or _payload_text(payload, "name") or f"{source_path.stem} audit",
        trace_file=trace_path.name,
        tool_inventory=tool_inventory,
        value_bar=value_bar,
    )
    bundle_path = target_dir / "agent_audit_bundle.json"
    bundle_path.write_text(json.dumps(bundle, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    return {
        "adapter": adapter or "auto",
        "bundle": str(bundle_path),
        "name": bundle["name"],
        "trace": str(trace_path),
        "trace_steps": len(trace.get("steps", [])),
    }


def _bundle_from_payload(
    payload: Any,
    *,
    bundle_name: str,
    trace_file: str,
    tool_inventory: str | Path | None,
    value_bar: str | Path | None,
) -> dict[str, Any]:
    data = payload if isinstance(payload, dict) else {}
    bundle = {
        "heldout_tool_selection_cases": _list_field(data, "heldout_tool_selection_cases"),
        "name": bundle_name,
        "tool_metrics": _dict_field(data, "tool_metrics"),
        "tool_selection_cases": _list_field(data, "tool_selection_cases"),
        "tools": _tools_from(data, tool_inventory),
        "traces": [{"name": bundle_name, "trace": trace_file}],
    }
    value_proof = _value_bar_from(data, value_bar)
    if value_proof:
        bundle["value_bar"] = value_proof
    return bundle


def _tools_from(data: dict[str, Any], tool_inventory: str | Path | None) -> list[dict[str, Any]]:
    if tool_inventory:
        payload = load_json(tool_inventory)
        return _extract_tools(payload)
    return _extract_tools(data)


def _extract_tools(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if not isinstance(payload, dict):
        return []
    for key in ("tools", "tool_inventory"):
        value = payload.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
        if isinstance(value, dict):
            nested = _extract_tools(value)
            if nested:
                return nested
    return []


def _value_bar_from(data: dict[str, Any], value_bar: str | Path | None) -> dict[str, Any] | None:
    if value_bar:
        payload = load_json(value_bar)
        return payload if isinstance(payload, dict) else None
    payload = data.get("value_bar")
    return payload if isinstance(payload, dict) else None


def _list_field(data: dict[str, Any], key: str) -> list[Any]:
    value = data.get(key)
    return value if isinstance(value, list) else []


def _dict_field(data: dict[str, Any], key: str) -> dict[str, Any]:
    value = data.get(key)
    return value if isinstance(value, dict) else {}


def _payload_text(payload: Any, key: str) -> str:
    if isinstance(payload, dict) and payload.get(key):
        return str(payload[key])
    return ""


def _slug(value: Any) -> str:
    text = re.sub(r"[^a-zA-Z0-9._-]+", "_", str(value).strip()).strip("_")
    return text or "imported_trace"
