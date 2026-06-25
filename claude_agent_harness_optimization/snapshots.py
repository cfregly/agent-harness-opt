"""Create version snapshots for tools, skills, matrices, and files."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any

from .adapters import load_json


SNAPSHOT_VERSION = "1"


def build_surface_snapshot(
    *,
    matrices: list[str | Path] | None = None,
    bundles: list[str | Path] | None = None,
    skills: list[str | Path] | None = None,
    files: list[str | Path] | None = None,
) -> dict[str, Any]:
    """Return a JSON snapshot of the surfaces under eval."""

    items: list[dict[str, Any]] = []
    for path in matrices or []:
        items.append(snapshot_matrix(path))
    for path in bundles or []:
        items.append(snapshot_bundle(path))
    for path in skills or []:
        items.append(snapshot_skill(path))
    for path in files or []:
        items.append(snapshot_file(path))

    return {
        "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "hash": _hash_json(items),
        "items": items,
        "snapshot_version": SNAPSHOT_VERSION,
    }


def write_surface_snapshot(snapshot: dict[str, Any], out: str | Path) -> Path:
    path = Path(out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(snapshot, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def snapshot_matrix(path: str | Path) -> dict[str, Any]:
    matrix_path = Path(path)
    matrix = load_json(matrix_path)
    return {
        "case_count": len(matrix.get("cases", [])),
        "hash": _hash_json(matrix),
        "instruction_variants": [
            {
                "hash": _hash_text(str(item.get("instructions", ""))),
                "name": item.get("name", ""),
            }
            for item in matrix.get("instruction_variants", [])
            if isinstance(item, dict)
        ],
        "name": matrix.get("name", matrix_path.stem),
        "path": str(matrix_path),
        "profiles": [
            {
                "harnesses": profile.get("harnesses", []),
                "model": profile.get("model", ""),
                "model_env": profile.get("model_env", ""),
                "name": profile.get("name", ""),
                "provider": profile.get("provider", ""),
            }
            for profile in matrix.get("profiles", [])
            if isinstance(profile, dict)
        ],
        "source": matrix.get("source", {}),
        "tool_variants": [
            _snapshot_tool_variant(variant)
            for variant in matrix.get("tool_variants", [])
            if isinstance(variant, dict)
        ],
        "type": "model_matrix",
    }


def snapshot_bundle(path: str | Path) -> dict[str, Any]:
    bundle_path = Path(path)
    bundle = load_json(bundle_path)
    return {
        "hash": _hash_json(bundle),
        "heldout_case_count": len(bundle.get("heldout_tool_selection_cases", [])),
        "name": bundle.get("name", bundle_path.stem),
        "path": str(bundle_path),
        "tool_count": len(bundle.get("tools", [])),
        "tool_selection_case_count": len(bundle.get("tool_selection_cases", [])),
        "tools": [_snapshot_tool(tool) for tool in bundle.get("tools", []) if isinstance(tool, dict)],
        "trace_count": len(bundle.get("traces", [])),
        "traces": bundle.get("traces", []),
        "type": "agent_audit_bundle",
        "value_bar_hash": _hash_json(bundle.get("value_bar", {})),
    }


def snapshot_skill(path: str | Path) -> dict[str, Any]:
    skill_path = Path(path)
    text = skill_path.read_text(encoding="utf-8")
    return {
        "hash": _hash_text(text),
        "heading": _first_heading(text),
        "line_count": len(text.splitlines()),
        "path": str(skill_path),
        "type": "skill",
        "version": _frontmatter_value(text, "version"),
    }


def snapshot_file(path: str | Path) -> dict[str, Any]:
    file_path = Path(path)
    data = file_path.read_bytes()
    return {
        "hash": hashlib.sha256(data).hexdigest(),
        "path": str(file_path),
        "size_bytes": len(data),
        "type": "file",
    }


def _snapshot_tool_variant(variant: dict[str, Any]) -> dict[str, Any]:
    tools = [tool for tool in variant.get("tools", []) if isinstance(tool, dict)]
    return {
        "hash": _hash_json(variant),
        "name": variant.get("name", ""),
        "tool_count": len(tools),
        "tools": [_snapshot_tool(tool) for tool in tools],
    }


def _snapshot_tool(tool: dict[str, Any]) -> dict[str, Any]:
    description = "\n".join(
        str(tool.get(key, "")).strip()
        for key in ("purpose", "use_when", "avoid_when")
        if str(tool.get(key, "")).strip()
    )
    return {
        "description_hash": _hash_text(description),
        "name": tool.get("name", ""),
        "schema_hash": _hash_json(tool.get("input_schema") or tool.get("parameters") or {}),
        "surface_hash": _hash_json(tool),
    }


def _hash_json(value: Any) -> str:
    return _hash_text(json.dumps(value, sort_keys=True, separators=(",", ":")))


def _hash_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _first_heading(text: str) -> str:
    for line in text.splitlines():
        if line.startswith("#"):
            return line.lstrip("#").strip()
    return ""


def _frontmatter_value(text: str, key: str) -> str:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return ""
    for line in lines[1:]:
        if line.strip() == "---":
            return ""
        if line.startswith(f"{key}:"):
            return line.split(":", 1)[1].strip().strip("'\"")
    return ""
