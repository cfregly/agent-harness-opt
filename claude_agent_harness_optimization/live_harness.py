"""Run live headless agent harnesses and normalize their traces."""

from __future__ import annotations

from dataclasses import dataclass
import datetime as dt
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import time
from typing import Any

from .adapters import normalize_run_export
from .model_matrix import load_env_file
from .trace_review import review_trace


DEFAULT_TIMEOUT_SECONDS = 180
TEXT_ADAPTERS = {"opencode", "opencode_text", "opencode_log"}
STRICT_DIRECTED_THINKING_RUBRIC = {
    "max_duplicate_calls": 1,
    "pass_score": 1.0,
    "require_directed_after_tool_reasoning": True,
    "require_directed_initial_reasoning": True,
    "require_reasoning_after_tool_results": True,
    "require_reasoning_before_first_tool": True,
    "require_result_quality_assessment": True,
}


class LiveHarnessError(RuntimeError):
    """Raised when a live harness spec cannot be loaded or run."""


@dataclass(frozen=True)
class LiveHarnessFilters:
    harnesses: set[str] | None = None
    cases: set[str] | None = None


def load_live_harness_spec(path: str | Path) -> dict[str, Any]:
    spec_path = Path(path)
    with spec_path.open("r", encoding="utf-8") as handle:
        spec = json.load(handle)
    _validate_spec(spec)
    spec["_spec_path"] = str(spec_path)
    spec["_base_dir"] = str(spec_path.parent)
    return spec


def run_live_harness_spec(
    path: str | Path,
    *,
    env_file: str | Path | None = None,
    out_dir: str | Path | None = None,
    filters: LiveHarnessFilters | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    spec = load_live_harness_spec(path)
    env_values = load_env_file(env_file)
    env = os.environ.copy()
    env.update(env_values)
    redactions = _redaction_values(env_values)
    selected = _selected_runs(spec, filters or LiveHarnessFilters())
    timestamp = _timestamp()
    artifact_root = Path(out_dir) if out_dir else Path("/tmp") / "claude-agent-harness-optimization" / f"live-harness-{timestamp}"
    artifact_root.mkdir(parents=True, exist_ok=True)

    results = []
    for run in selected:
        results.append(
            _run_one(
                run,
                env=env,
                redactions=redactions,
                artifact_root=artifact_root,
                dry_run=dry_run,
            )
        )

    summary = _summary(results, dry_run=dry_run)
    return {
        "artifact_root": str(artifact_root),
        "case_definitions": [
            {
                "name": run["case"].get("name", ""),
                "prompt_template": run["case"].get("prompt_template", run["case"].get("prompt", "")),
            }
            for run in selected
        ],
        "checked_at": timestamp,
        "description": spec.get("description", ""),
        "dry_run": dry_run,
        "env_file_used": bool(env_file),
        "env_keys_loaded": sorted(env_values),
        "harnesses": [harness.get("name", "") for harness in spec.get("harnesses", [])],
        "name": spec.get("name", str(path)),
        "passed": summary["failed"] == 0 and summary["errors"] == 0 and summary["not_installed"] == 0,
        "results": results,
        "source": spec.get("source", {}),
        "spec_path": spec.get("_spec_path", str(path)),
        "summary": summary,
        "value_bar": spec.get("value_bar", {}),
    }


def render_live_harness_markdown(result: dict[str, Any]) -> str:
    summary = result["summary"]
    lines = [
        f"# {result['name']}",
        "",
        f"Checked: {result['checked_at']}",
        f"Dry run: {'yes' if result['dry_run'] else 'no'}",
        f"Passed: {'yes' if result['passed'] else 'no'}",
        f"Artifacts: `{result['artifact_root']}`",
        "",
        "## Summary",
        "",
        "| Metric | Count |",
        "|---|---:|",
        f"| Passed | {summary['passed']} |",
        f"| Failed | {summary['failed']} |",
        f"| Errors | {summary['errors']} |",
        f"| Not installed | {summary['not_installed']} |",
        f"| Directed-thinking visible | {summary['directed_thinking_visible']} |",
        "",
        "## Results",
        "",
        "| Harness | Case | Version | Status | Exit | Tool Calls | Tool Pass | Directed Thinking | Artifact |",
        "|---|---|---|---|---:|---:|---|---|---|",
    ]
    for item in result["results"]:
        artifact = item.get("artifacts", {}).get("combined", "")
        lines.append(
            "| {harness} | {case} | {version} | {status} | {exit_code} | {tool_calls} | {tool_pass} | "
            "{thinking} | `{artifact}` |".format(
                harness=item.get("harness", ""),
                case=item.get("case", ""),
                version=_md_cell(item.get("version", "")),
                status=item.get("status", ""),
                exit_code=item.get("exit_code", ""),
                tool_calls=item.get("tool_call_count", 0),
                tool_pass="yes" if item.get("tool_use_passed") else "no",
                thinking="yes" if item.get("directed_thinking_passed") else "no",
                artifact=artifact,
            )
        )
    lines.extend(["", "## Findings", ""])
    for item in result["results"]:
        lines.append(f"### {item.get('harness', '')} / {item.get('case', '')}")
        lines.append("")
        for finding in item.get("findings", []):
            lines.append(f"- {finding}")
        if item.get("error"):
            lines.append(f"- Error: {item['error']}")
        lines.append("")
    return "\n".join(lines)


def _validate_spec(spec: dict[str, Any]) -> None:
    missing = sorted({"cases", "harnesses"} - set(spec))
    if missing:
        raise LiveHarnessError(f"live harness spec missing required fields: {', '.join(missing)}")
    if not spec["cases"]:
        raise LiveHarnessError("live harness spec must include at least one case")
    if not spec["harnesses"]:
        raise LiveHarnessError("live harness spec must include at least one harness")


def _selected_runs(spec: dict[str, Any], filters: LiveHarnessFilters) -> list[dict[str, Any]]:
    runs: list[dict[str, Any]] = []
    for harness in spec.get("harnesses", []):
        if filters.harnesses and harness.get("name", "") not in filters.harnesses:
            continue
        for case in spec.get("cases", []):
            if filters.cases and case.get("name", "") not in filters.cases:
                continue
            runs.append({"case": case, "harness": harness, "spec": spec})
    return runs


def _run_one(
    run: dict[str, Any],
    *,
    env: dict[str, str],
    redactions: list[str],
    artifact_root: Path,
    dry_run: bool,
) -> dict[str, Any]:
    harness = run["harness"]
    case = run["case"]
    name = str(harness.get("name", "harness"))
    case_name = str(case.get("name", "case"))
    context = _context(harness, case)
    command = _format_command(harness.get("command", []), context)
    cwd = Path(harness.get("cwd") or run["spec"].get("cwd") or ".").resolve()
    result: dict[str, Any] = {
        "adapter": harness.get("adapter", ""),
        "case": case_name,
        "command": _command_for_report(command),
        "harness": name,
        "required": bool(harness.get("required", True)),
        "status": "planned" if dry_run else "error",
    }

    version = _version_info(harness, env=env, cwd=cwd, redactions=redactions)
    result["version"] = version.get("version", "")
    result["version_command"] = version.get("command", [])
    result["version_exit_code"] = version.get("exit_code")

    if dry_run:
        result["status"] = "planned"
        result["findings"] = ["Command rendered but not executed."]
        return result

    if not command:
        result.update({"error": "missing command", "status": "error"})
        return result
    executable = shutil.which(command[0])
    if not executable:
        result.update(
            {
                "error": f"command not found: {command[0]}",
                "findings": [f"{name} is not installed on PATH."],
                "status": "not_installed",
            }
        )
        return result

    started = time.monotonic()
    timeout_seconds = int(harness.get("timeout_seconds", DEFAULT_TIMEOUT_SECONDS))
    try:
        completed = subprocess.run(
            command,
            cwd=cwd,
            env=env,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
        elapsed_ms = int((time.monotonic() - started) * 1000)
        stdout = _redact(completed.stdout, redactions)
        stderr = _redact(completed.stderr, redactions)
        combined = stdout + ("\n" if stdout and stderr else "") + stderr
        artifacts = _write_artifacts(
            artifact_root,
            harness_name=name,
            case_name=case_name,
            stdout=stdout,
            stderr=stderr,
            combined=combined,
        )
        result.update(
            {
                "artifacts": artifacts,
                "elapsed_ms": elapsed_ms,
                "exit_code": completed.returncode,
                "stdout_bytes": len(stdout.encode("utf-8")),
                "stderr_bytes": len(stderr.encode("utf-8")),
            }
        )
    except subprocess.TimeoutExpired as exc:
        elapsed_ms = int((time.monotonic() - started) * 1000)
        stdout = _redact(exc.stdout or "", redactions)
        stderr = _redact(exc.stderr or "", redactions)
        combined = stdout + ("\n" if stdout and stderr else "") + stderr
        artifacts = _write_artifacts(
            artifact_root,
            harness_name=name,
            case_name=case_name,
            stdout=stdout,
            stderr=stderr,
            combined=combined,
        )
        result.update(
            {
                "artifacts": artifacts,
                "elapsed_ms": elapsed_ms,
                "error": f"timed out after {timeout_seconds}s",
                "exit_code": None,
                "status": "error",
            }
        )
        return result

    trace_result = _normalize_and_review(
        harness,
        case,
        stdout=stdout,
        stderr=stderr,
        combined=combined,
        artifact_root=artifact_root,
        harness_name=name,
        case_name=case_name,
    )
    result.update(trace_result)
    status = "passed" if result.get("tool_use_passed") and result.get("exit_code") == 0 else "failed"
    if result.get("exit_code") != 0 and _looks_like_auth_failure(combined):
        status = "auth_failed"
    result["status"] = status
    return result


def _normalize_and_review(
    harness: dict[str, Any],
    case: dict[str, Any],
    *,
    stdout: str,
    stderr: str,
    combined: str,
    artifact_root: Path,
    harness_name: str,
    case_name: str,
) -> dict[str, Any]:
    adapter = str(harness.get("adapter", "runtime_events"))
    payload = combined if adapter in TEXT_ADAPTERS else stdout
    rubric = _smoke_rubric(harness, case)
    findings: list[str] = []
    marker = _required_marker(harness, case)
    marker_present = bool(marker and marker.lower() in combined.lower())
    if marker:
        findings.append(
            f"Final marker {marker!r} was {'present' if marker_present else 'missing'} in captured output."
        )

    try:
        trace = normalize_run_export(payload, adapter)
        trace["name"] = f"{harness_name}_{case_name}"
        trace["rubric"] = rubric
        trace_path = _artifact_path(artifact_root, harness_name, case_name, "trace", ".json")
        trace_path.write_text(json.dumps(trace, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        review = review_trace(trace).to_dict()
        strict_trace = {**trace, "rubric": {**rubric, **STRICT_DIRECTED_THINKING_RUBRIC}}
        directed_review = review_trace(strict_trace).to_dict()
    except Exception as exc:  # noqa: BLE001
        findings.append(f"Trace normalization failed for adapter {adapter!r}: {exc}")
        return {
            "directed_thinking_passed": False,
            "error": str(exc),
            "findings": findings,
            "marker_present": marker_present,
            "tool_call_count": 0,
            "tool_result_count": 0,
            "tool_use_passed": False,
            "trace_review": {},
        }

    calls = [step for step in trace.get("steps", []) if step.get("type") == "tool_call"]
    results = [step for step in trace.get("steps", []) if step.get("type") == "tool_result"]
    reasoning = [step for step in trace.get("steps", []) if step.get("type") == "reasoning"]
    tool_passed = bool(review.get("passed")) and (marker_present or not marker)
    directed_passed = bool(directed_review.get("passed"))
    expected_tool = harness.get("expected_tool")
    if expected_tool:
        used = any(call.get("name") == expected_tool for call in calls)
        findings.append(f"Expected tool {expected_tool!r} was {'used' if used else 'not used'}.")
    if not reasoning:
        findings.append("No visible before/after tool reasoning was exported by this harness run.")
    elif not directed_passed:
        findings.append("Visible reasoning exists, but it did not satisfy the strict directed-thinking rubric.")
    else:
        findings.append("Visible reasoning satisfied the strict directed-thinking rubric.")

    return {
        "directed_thinking_passed": directed_passed,
        "directed_thinking_review": directed_review,
        "findings": findings,
        "marker_present": marker_present,
        "normalized_trace": str(trace_path),
        "tool_call_count": len(calls),
        "tool_result_count": len(results),
        "tool_use_passed": tool_passed,
        "trace_review": review,
        "visible_reasoning_steps": len(reasoning),
    }


def _smoke_rubric(harness: dict[str, Any], case: dict[str, Any]) -> dict[str, Any]:
    rubric: dict[str, Any] = {
        "max_duplicate_calls": 1,
        "max_tool_calls": int(harness.get("max_tool_calls", case.get("max_tool_calls", 1))),
        "min_tool_calls": int(harness.get("min_tool_calls", case.get("min_tool_calls", 1))),
        "pass_score": float(harness.get("pass_score", 1.0)),
        "require_directed_after_tool_reasoning": False,
        "require_directed_initial_reasoning": False,
        "require_error_recovery_reasoning": False,
        "require_reasoning_after_tool_results": False,
        "require_reasoning_before_first_tool": False,
        "require_result_quality_assessment": False,
    }
    expected_tool = harness.get("expected_tool")
    if expected_tool:
        rubric["required_tools"] = [expected_tool]
    expected_args = harness.get("expected_args_contains") or case.get("expected_args_contains")
    if expected_tool and isinstance(expected_args, dict):
        rubric["expected_call_args"] = [{"args_contains": expected_args, "name": expected_tool}]
    marker = _required_marker(harness, case)
    if marker:
        rubric["required_final_contains"] = [marker]
    return rubric


def _version_info(
    harness: dict[str, Any],
    *,
    env: dict[str, str],
    cwd: Path,
    redactions: list[str],
) -> dict[str, Any]:
    command = harness.get("version_command", [])
    if not command:
        return {"command": [], "exit_code": None, "version": ""}
    rendered = _format_command(command, {})
    if not rendered or not shutil.which(rendered[0]):
        return {"command": _command_for_report(rendered), "exit_code": None, "version": "not installed"}
    try:
        completed = subprocess.run(
            rendered,
            cwd=cwd,
            env=env,
            check=False,
            capture_output=True,
            text=True,
            timeout=20,
        )
    except Exception as exc:  # noqa: BLE001
        return {"command": _command_for_report(rendered), "exit_code": None, "version": str(exc)}
    text = _redact((completed.stdout or completed.stderr).strip(), redactions)
    return {
        "command": _command_for_report(rendered),
        "exit_code": completed.returncode,
        "version": _first_line(text),
    }


def _context(harness: dict[str, Any], case: dict[str, Any]) -> dict[str, str]:
    context = {
        "harness": str(harness.get("name", "")),
        "marker": str(harness.get("marker", harness.get("name", ""))),
        "shell_command": str(case.get("shell_command", "pwd")),
    }
    prompt_template = str(case.get("prompt_template", case.get("prompt", "")))
    context["prompt"] = prompt_template.format(**context)
    return context


def _format_command(command: list[Any], context: dict[str, str]) -> list[str]:
    rendered = []
    for part in command:
        text = str(part)
        if context:
            for key, value in context.items():
                text = text.replace("{" + key + "}", value)
        rendered.append(text)
    return rendered


def _required_marker(harness: dict[str, Any], case: dict[str, Any]) -> str:
    if harness.get("required_marker"):
        return str(harness["required_marker"])
    marker_template = str(case.get("required_marker_template", "HARNESS_OK {marker}"))
    return marker_template.format(marker=str(harness.get("marker", harness.get("name", ""))))


def _write_artifacts(
    artifact_root: Path,
    *,
    harness_name: str,
    case_name: str,
    stdout: str,
    stderr: str,
    combined: str,
) -> dict[str, str]:
    stdout_path = _artifact_path(artifact_root, harness_name, case_name, "stdout", ".txt")
    stderr_path = _artifact_path(artifact_root, harness_name, case_name, "stderr", ".txt")
    combined_path = _artifact_path(artifact_root, harness_name, case_name, "combined", ".txt")
    stdout_path.write_text(stdout, encoding="utf-8")
    stderr_path.write_text(stderr, encoding="utf-8")
    combined_path.write_text(combined, encoding="utf-8")
    return {
        "combined": str(combined_path),
        "stderr": str(stderr_path),
        "stdout": str(stdout_path),
    }


def _artifact_path(root: Path, harness_name: str, case_name: str, kind: str, suffix: str) -> Path:
    name = _slug(f"{harness_name}-{case_name}-{kind}") + suffix
    return root / name


def _summary(results: list[dict[str, Any]], *, dry_run: bool) -> dict[str, int]:
    if dry_run:
        return {
            "directed_thinking_visible": 0,
            "errors": 0,
            "failed": 0,
            "not_installed": 0,
            "passed": 0,
            "planned": len(results),
        }
    return {
        "directed_thinking_visible": sum(1 for item in results if item.get("directed_thinking_passed")),
        "errors": sum(1 for item in results if item.get("status") in {"error", "auth_failed"}),
        "failed": sum(1 for item in results if item.get("status") == "failed"),
        "not_installed": sum(1 for item in results if item.get("status") == "not_installed"),
        "passed": sum(1 for item in results if item.get("status") == "passed"),
        "planned": 0,
    }


def _redaction_values(values: dict[str, str]) -> list[str]:
    return sorted(
        {value for value in values.values() if isinstance(value, str) and len(value) >= 8},
        key=len,
        reverse=True,
    )


def _redact(text: str, values: list[str]) -> str:
    redacted = text
    for value in values:
        redacted = redacted.replace(value, "[REDACTED]")
    return redacted


def _command_for_report(command: list[str]) -> list[str]:
    return [part if len(part) <= 240 else part[:237] + "..." for part in command]


def _first_line(text: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped:
            return stripped
    return ""


def _timestamp() -> str:
    return dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _slug(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9_.-]+", "-", value).strip("-").lower()
    return slug or "artifact"


def _looks_like_auth_failure(text: str) -> bool:
    lower = text.lower()
    return any(term in lower for term in ("sign in", "not logged in", "login", "authentication"))


def _md_cell(value: str) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")
