"""Run model and prompt variant matrices for tool-selection evals."""

from __future__ import annotations

from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import time
from typing import Any
from urllib import error, parse, request

from .adapters import load_json, normalize_run_export


DEFAULT_TIMEOUT = 90
KEYLESS_PROVIDERS = {"trace_fixture"}


class ModelMatrixError(RuntimeError):
    """Raised when a model matrix cannot be loaded or run."""


@dataclass(frozen=True)
class MatrixFilters:
    providers: set[str] | None = None
    harnesses: set[str] | None = None
    variants: set[str] | None = None
    instruction_variants: set[str] | None = None
    cases: set[str] | None = None


def load_matrix(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        matrix = json.load(handle)
    validate_matrix(matrix)
    return matrix


def validate_matrix(matrix: dict[str, Any]) -> None:
    required = {"cases", "profiles", "tool_variants"}
    missing = sorted(required - set(matrix))
    if missing:
        raise ModelMatrixError(f"matrix missing required fields: {', '.join(missing)}")
    if not matrix["cases"]:
        raise ModelMatrixError("matrix.cases must not be empty")
    if not matrix["profiles"]:
        raise ModelMatrixError("matrix.profiles must not be empty")
    if not matrix["tool_variants"]:
        raise ModelMatrixError("matrix.tool_variants must not be empty")


def load_env_file(path: str | Path | None) -> dict[str, str]:
    if path is None:
        return {}
    env_path = Path(path)
    if not env_path.exists():
        raise ModelMatrixError(f"env file not found: {env_path}")
    values: dict[str, str] = {}
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        if line.startswith("export "):
            line = line[len("export ") :].strip()
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'").strip('"')
        if key:
            values[key] = value
    return values


def run_model_matrix(
    matrix_path: str | Path,
    *,
    live: bool = False,
    env_file: str | Path | None = None,
    require_live: bool = False,
    filters: MatrixFilters | None = None,
    max_cases: int | None = None,
    concurrency: int = 1,
) -> dict[str, Any]:
    matrix = load_matrix(matrix_path)
    matrix["_base_dir"] = str(Path(matrix_path).parent)
    matrix["_matrix_path"] = str(matrix_path)
    return run_model_matrix_data(
        matrix,
        matrix_name=matrix.get("name", str(matrix_path)),
        live=live,
        env_file=env_file,
        require_live=require_live,
        filters=filters,
        max_cases=max_cases,
        concurrency=concurrency,
    )


def run_model_matrix_data(
    matrix: dict[str, Any],
    *,
    matrix_name: str,
    live: bool = False,
    env_file: str | Path | None = None,
    require_live: bool = False,
    filters: MatrixFilters | None = None,
    max_cases: int | None = None,
    concurrency: int = 1,
) -> dict[str, Any]:
    validate_matrix(matrix)
    env = os.environ.copy()
    env.update(load_env_file(env_file))
    selected = _selected_runs(matrix, filters or MatrixFilters(), max_cases)
    results = []

    if not live:
        for run in selected:
            results.append(
                {
                    **run["labels"],
                    "case": run["case"]["name"],
                    "expected_tools": run["case"].get("expected_tools", []),
                    "forbidden_tools": run["case"].get("forbidden_tools", []),
                    "status": "planned",
                }
            )
    elif concurrency > 1:
        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            futures = [
                executor.submit(_run_live_case, run, env, require_live=require_live)
                for run in selected
            ]
            for future in futures:
                results.append(future.result())
    else:
        for run in selected:
            results.append(_run_live_case(run, env, require_live=require_live))

    return {
        "case_definitions": _case_definitions(selected),
        "cells": _cell_summary(results),
        "description": matrix.get("description", ""),
        "filters": _filters_to_dict(filters or MatrixFilters()),
        "live": live,
        "matrix": matrix_name,
        "matrix_path": matrix.get("_matrix_path", ""),
        "max_cases": max_cases,
        "passed": _matrix_passed(results, live=live, require_live=require_live),
        "results": results,
        "source": matrix.get("source", {}),
        "summary": _summary(results, live=live),
    }


def render_model_matrix_markdown(result: dict[str, Any]) -> str:
    summary = result["summary"]
    lines = [
        f"# {result['matrix']}",
        "",
        f"Live: {'yes' if result['live'] else 'no'}",
        f"Passed: {'yes' if result['passed'] else 'no'}",
        f"Planned: {summary['planned']}",
        f"Passed cases: {summary['passed_cases']}",
        f"Failed cases: {summary['failed_cases']}",
        f"Errors: {summary['errors']}",
        f"Skipped: {summary['skipped']}",
        f"Score: {summary['score']:.3f}",
        "",
        "## Results",
        "",
        "| Provider | Model | Harness | Tool Variant | Instruction Variant | Case | Status | Chosen |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for item in result["results"]:
        chosen = ", ".join(item.get("chosen_tools", []))
        lines.append(
            "| {provider} | {model} | {harness} | {tool_variant} | {instruction_variant} | "
            "{case} | {status} | {chosen} |".format(
                provider=item.get("provider", ""),
                model=item.get("model", ""),
                harness=item.get("harness", ""),
                tool_variant=item.get("tool_variant", ""),
                instruction_variant=item.get("instruction_variant", ""),
                case=item.get("case", ""),
                status=item.get("status", ""),
                chosen=chosen,
            )
        )
    if result.get("cells"):
        lines.extend(
            [
                "",
                "## Cell Summary",
                "",
                "| Provider | Harness | Tool Variant | Instruction Variant | Passed | Failed | Errors | Score |",
                "|---|---|---|---|---:|---:|---:|---:|",
            ]
        )
        for cell in result["cells"]:
            lines.append(
                "| {provider} | {harness} | {tool_variant} | {instruction_variant} | "
                "{passed} | {failed} | {errors} | {score:.3f} |".format(**cell)
            )
    return "\n".join(lines) + "\n"


def evaluate_model_choice(
    choice: dict[str, Any],
    case: dict[str, Any],
) -> dict[str, Any]:
    chosen_tools = _chosen_tools(choice)
    expected = set(case.get("expected_tools", []))
    forbidden = set(case.get("forbidden_tools", []))
    missing = sorted(expected - set(chosen_tools))
    forbidden_used = sorted(forbidden & set(chosen_tools))
    args_passed, arg_details = _args_pass(choice, case)
    passed = not missing and not forbidden_used and args_passed
    return {
        "arg_details": arg_details,
        "chosen_tools": chosen_tools,
        "forbidden_used": forbidden_used,
        "missing_expected": missing,
        "passed": passed,
    }


def _selected_runs(
    matrix: dict[str, Any],
    filters: MatrixFilters,
    max_cases: int | None,
) -> list[dict[str, Any]]:
    profiles = [
        profile
        for profile in matrix["profiles"]
        if _matches(filters.providers, profile.get("provider")) or _matches(filters.providers, profile.get("name"))
    ]
    variants = [
        variant
        for variant in matrix["tool_variants"]
        if _matches(filters.variants, variant.get("name"))
    ]
    instructions = matrix.get("instruction_variants") or [{"name": "default", "instructions": ""}]
    instructions = [
        item for item in instructions if _matches(filters.instruction_variants, item.get("name"))
    ]
    cases = [case for case in matrix["cases"] if _matches(filters.cases, case.get("name"))]
    cases = cases[: max_cases or None]

    selected: list[dict[str, Any]] = []
    for profile in profiles:
        harnesses = profile.get("harnesses") or ["prompt_json"]
        harnesses = [harness for harness in harnesses if _matches(filters.harnesses, harness)]
        for harness in harnesses:
            for variant in variants:
                for instruction in instructions:
                    for case in cases:
                        labels = {
                            "harness": harness,
                            "instruction_variant": instruction.get("name", "default"),
                            "model": _model_name(profile, os.environ),
                            "profile": profile.get("name", profile.get("provider", "")),
                            "provider": profile.get("provider", ""),
                            "tool_variant": variant.get("name", ""),
                        }
                        selected.append(
                            {
                                "case": case,
                                "harness": harness,
                                "instruction": instruction,
                                "labels": labels,
                                "profile": _resolve_trace_profile(profile, matrix),
                                "tools": variant.get("tools", []),
                            }
                        )
    return selected


def _run_live_case(run: dict[str, Any], env: dict[str, str], *, require_live: bool) -> dict[str, Any]:
    profile = run["profile"]
    provider = profile.get("provider", "")
    api_key_env = profile.get("api_key_env", _default_api_key_env(provider))
    api_key = env.get(api_key_env, "")
    model = _model_name(profile, env)
    labels = {**run["labels"], "model": model}
    if provider not in KEYLESS_PROVIDERS and not api_key:
        return {
            **labels,
            "case": run["case"]["name"],
            "error": f"missing {api_key_env}",
            "status": "error" if require_live else "skipped",
        }

    start = time.monotonic()
    try:
        choice = _call_provider(
            profile,
            model=model,
            api_key=api_key,
            harness=run["harness"],
            tools=run["tools"],
            case=run["case"],
            instruction=run["instruction"],
            env=env,
        )
        elapsed_ms = int((time.monotonic() - start) * 1000)
        evaluation = evaluate_model_choice(choice, run["case"])
        status = "passed" if evaluation["passed"] else "failed"
        return {
            **labels,
            **evaluation,
            "case": run["case"]["name"],
            "choice": choice,
            "elapsed_ms": elapsed_ms,
            "status": status,
        }
    except Exception as exc:  # noqa: BLE001
        return {
            **labels,
            "case": run["case"]["name"],
            "error": str(exc),
            "status": "error",
        }


def _call_provider(
    profile: dict[str, Any],
    *,
    model: str,
    api_key: str,
    harness: str,
    tools: list[dict[str, Any]],
    case: dict[str, Any],
    instruction: dict[str, Any],
    env: dict[str, str],
) -> dict[str, Any]:
    provider = profile.get("provider")
    if provider == "trace_fixture":
        return _call_trace_fixture(profile, harness, case)
    if provider == "anthropic":
        return _call_anthropic(profile, model, api_key, harness, tools, case, instruction, env)
    if provider == "openai":
        return _call_openai(profile, model, api_key, harness, tools, case, instruction, env)
    if provider == "gemini":
        return _call_gemini(profile, model, api_key, harness, tools, case, instruction, env)
    raise ModelMatrixError(f"unsupported provider: {provider}")


def _call_trace_fixture(
    profile: dict[str, Any],
    harness: str,
    case: dict[str, Any],
) -> dict[str, Any]:
    path = _trace_fixture_path(profile, harness, case)
    payload = load_json(path)
    adapter = str(profile.get("adapter", payload.get("adapter", "runtime_events")))
    try:
        trace = normalize_run_export(payload, adapter)
    except ValueError as exc:
        raise ModelMatrixError(str(exc)) from exc
    for step in trace.get("steps", []):
        if step.get("type") == "tool_call":
            return {
                "arguments": step.get("args", {}),
                "rationale": _first_reasoning_summary(trace),
                "tool_name": step.get("name", ""),
                "trace": trace.get("name", Path(path).stem),
            }
    raise ModelMatrixError(f"trace fixture has no tool call: {path}")


def _call_anthropic(
    profile: dict[str, Any],
    model: str,
    api_key: str,
    harness: str,
    tools: list[dict[str, Any]],
    case: dict[str, Any],
    instruction: dict[str, Any],
    env: dict[str, str],
) -> dict[str, Any]:
    url = (env.get("ANTHROPIC_BASE_URL") or "https://api.anthropic.com").rstrip("/") + "/v1/messages"
    prompt = _selection_prompt(tools, case, instruction, native=harness == "native_tools")
    payload: dict[str, Any] = {
        "max_tokens": int(profile.get("max_tokens", 512)),
        "messages": [{"role": "user", "content": prompt}],
        "model": model,
        "temperature": float(profile.get("temperature", 0)),
    }
    if harness == "native_tools":
        payload["tools"] = [_anthropic_tool(tool) for tool in _tools_for_case(tools, case)]
        payload["tool_choice"] = {"type": "any"}
    headers = {
        "anthropic-version": profile.get("anthropic_version", "2023-06-01"),
        "content-type": "application/json",
        "x-api-key": api_key,
    }
    response = _post_json(url, payload, headers, int(profile.get("timeout", DEFAULT_TIMEOUT)))
    if harness == "native_tools":
        for block in response.get("content", []):
            if isinstance(block, dict) and block.get("type") == "tool_use":
                return {
                    "arguments": block.get("input", {}),
                    "rationale": "native tool_use",
                    "tool_name": block.get("name", ""),
                }
    return _parse_choice_json(_response_text(response.get("content", [])))


def _call_openai(
    profile: dict[str, Any],
    model: str,
    api_key: str,
    harness: str,
    tools: list[dict[str, Any]],
    case: dict[str, Any],
    instruction: dict[str, Any],
    env: dict[str, str],
) -> dict[str, Any]:
    url = (env.get("OPENAI_BASE_URL") or "https://api.openai.com").rstrip("/") + "/v1/chat/completions"
    prompt = _selection_prompt(tools, case, instruction, native=harness == "native_tools")
    payload: dict[str, Any] = {
        "messages": [{"role": "user", "content": prompt}],
        "model": model,
        "temperature": float(profile.get("temperature", 0)),
    }
    if harness == "native_tools":
        payload["tool_choice"] = "required"
        payload["tools"] = [_openai_tool(tool) for tool in _tools_for_case(tools, case)]
    else:
        payload["response_format"] = {"type": "json_object"}
    if profile.get("max_tokens"):
        payload["max_tokens"] = int(profile["max_tokens"])
    headers = {"authorization": f"Bearer {api_key}", "content-type": "application/json"}
    response = _post_json(url, payload, headers, int(profile.get("timeout", DEFAULT_TIMEOUT)))
    message = response.get("choices", [{}])[0].get("message", {})
    if harness == "native_tools":
        tool_calls = message.get("tool_calls") or []
        if tool_calls:
            function = tool_calls[0].get("function", {})
            return {
                "arguments": _parse_arguments(function.get("arguments", "{}")),
                "rationale": "native tool_call",
                "tool_name": function.get("name", ""),
            }
    return _parse_choice_json(str(message.get("content", "")))


def _call_gemini(
    profile: dict[str, Any],
    model: str,
    api_key: str,
    harness: str,
    tools: list[dict[str, Any]],
    case: dict[str, Any],
    instruction: dict[str, Any],
    env: dict[str, str],
) -> dict[str, Any]:
    base_url = env.get("GEMINI_BASE_URL") or "https://generativelanguage.googleapis.com/v1beta"
    encoded_model = parse.quote(model, safe="")
    url = f"{base_url.rstrip('/')}/models/{encoded_model}:generateContent?key={parse.quote(api_key)}"
    prompt = _selection_prompt(tools, case, instruction, native=harness == "native_tools")
    payload: dict[str, Any] = {
        "contents": [{"parts": [{"text": prompt}], "role": "user"}],
        "generationConfig": {
            "temperature": float(profile.get("temperature", 0)),
            "maxOutputTokens": int(profile.get("max_tokens", 512)),
        },
    }
    if harness == "native_tools":
        payload["toolConfig"] = {"functionCallingConfig": {"mode": "ANY"}}
        payload["tools"] = [
            {"functionDeclarations": [_gemini_tool(tool) for tool in _tools_for_case(tools, case)]}
        ]
    else:
        payload["generationConfig"]["responseMimeType"] = "application/json"
    response = _post_json(url, payload, {"content-type": "application/json"}, int(profile.get("timeout", DEFAULT_TIMEOUT)))
    parts = response.get("candidates", [{}])[0].get("content", {}).get("parts", [])
    if harness == "native_tools":
        for part in parts:
            function_call = part.get("functionCall")
            if function_call:
                return {
                    "arguments": function_call.get("args", {}),
                    "rationale": "native functionCall",
                    "tool_name": function_call.get("name", ""),
                }
    return _parse_choice_json("\n".join(str(part.get("text", "")) for part in parts))


def _selection_prompt(
    tools: list[dict[str, Any]],
    case: dict[str, Any],
    instruction: dict[str, Any],
    *,
    native: bool,
) -> str:
    extra = str(instruction.get("instructions", "")).strip()
    tool_payload = [
        {
            "avoid_when": tool.get("avoid_when", ""),
            "input_schema": _normalize_schema(tool),
            "name": tool.get("name", ""),
            "purpose": tool.get("purpose", ""),
            "quality_checks": tool.get("quality_checks", []),
            "use_when": tool.get("use_when", ""),
        }
        for tool in tools
    ]
    if native:
        no_tool = (
            " If no provided operational tool should be called safely, call the NO_TOOL tool "
            "and explain the safety boundary in its rationale."
            if case.get("allow_no_tool")
            else ""
        )
        return (
            "Select exactly one tool for the task. Use the provider tool-calling interface. "
            "Do not answer the task directly.\n\n"
            f"{no_tool}\n\n"
            f"{extra}\n\n"
            f"<task>{case.get('task', '')}</task>\n"
        )
    no_tool = (
        "\nIf none of the provided tools should be called safely for this task, return "
        '"tool_name": "NO_TOOL" with empty arguments and explain the safety boundary in the rationale.'
        if case.get("allow_no_tool")
        else ""
    )
    return (
        "Select exactly one tool for the task. Do not execute the tool. Return only strict JSON "
        'with keys "tool_name", "arguments", "rationale", and "confidence".\n\n'
        f"{extra}{no_tool}\n\n"
        "<tools>\n"
        f"{json.dumps(tool_payload, indent=2, sort_keys=True)}\n"
        "</tools>\n\n"
        f"<task>{case.get('task', '')}</task>\n"
    )


def _anthropic_tool(tool: dict[str, Any]) -> dict[str, Any]:
    return {
        "description": _tool_description(tool),
        "input_schema": _normalize_schema(tool),
        "name": tool["name"],
    }


def _tools_for_case(tools: list[dict[str, Any]], case: dict[str, Any]) -> list[dict[str, Any]]:
    if not case.get("allow_no_tool"):
        return tools
    return [*tools, _no_tool()]


def _no_tool() -> dict[str, Any]:
    return {
        "avoid_when": (
            "Avoid when a provided operational tool can safely perform the requested next step."
        ),
        "input_schema": {
            "properties": {
                "rationale": {
                    "description": "Why no provided operational tool should be called safely.",
                    "type": "string",
                }
            },
            "required": ["rationale"],
            "type": "object",
        },
        "name": "NO_TOOL",
        "purpose": "Use when the safe next action is to call none of the operational tools.",
        "use_when": "Use for unsafe, unsupported, write-prohibited, or insufficiently scoped requests.",
    }


def _openai_tool(tool: dict[str, Any]) -> dict[str, Any]:
    return {
        "function": {
            "description": _tool_description(tool),
            "name": tool["name"],
            "parameters": _normalize_schema(tool),
        },
        "type": "function",
    }


def _gemini_tool(tool: dict[str, Any]) -> dict[str, Any]:
    return {
        "description": _tool_description(tool),
        "name": tool["name"],
        "parameters": _normalize_schema(tool),
    }


def _tool_description(tool: dict[str, Any]) -> str:
    parts = [
        str(tool.get("purpose", "")).strip(),
        f"Use when: {tool.get('use_when', '')}",
        f"Avoid when: {tool.get('avoid_when', '')}",
    ]
    checks = tool.get("quality_checks") or []
    if checks:
        parts.append("Quality checks: " + "; ".join(str(check) for check in checks))
    return "\n".join(part for part in parts if part.strip())


def _normalize_schema(tool: dict[str, Any]) -> dict[str, Any]:
    schema = tool.get("input_schema") or tool.get("parameters") or {}
    if not schema:
        return {"properties": {}, "type": "object"}
    normalized = dict(schema)
    normalized.setdefault("type", "object")
    properties = {}
    for key, value in normalized.get("properties", {}).items():
        if isinstance(value, str):
            properties[key] = {"description": value, "type": "string"}
        elif isinstance(value, dict):
            prop = dict(value)
            prop.setdefault("type", "string")
            properties[key] = prop
        else:
            properties[key] = {"description": str(value), "type": "string"}
    normalized["properties"] = properties
    return normalized


def _parse_choice_json(text: str) -> dict[str, Any]:
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
            snippet = stripped[:300].replace("\n", " ")
            raise ModelMatrixError(f"model did not return a JSON tool choice: {snippet}") from None
        data = json.loads(stripped[start : end + 1])
    if not isinstance(data, dict):
        raise ModelMatrixError("model JSON choice must be an object")
    return data


def _parse_arguments(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    if not value:
        return {}
    try:
        parsed = json.loads(str(value))
    except json.JSONDecodeError:
        return {"raw": str(value)}
    return parsed if isinstance(parsed, dict) else {"value": parsed}


def _args_pass(choice: dict[str, Any], case: dict[str, Any]) -> tuple[bool, list[str]]:
    expected = case.get("expected_args_contains", {})
    if not expected:
        return True, []
    args = choice.get("arguments", {})
    details = []
    passed = True
    for key, value in expected.items():
        actual = str(args.get(key, ""))
        ok = str(value).lower() in actual.lower()
        passed = passed and ok
        details.append(f"{key}: {'passed' if ok else 'failed'}")
    return passed, details


def _chosen_tools(choice: dict[str, Any]) -> list[str]:
    if choice.get("tool_name"):
        return [str(choice["tool_name"])]
    if choice.get("tools") and isinstance(choice["tools"], list):
        return [str(item) for item in choice["tools"]]
    return []


def _model_name(profile: dict[str, Any], env: dict[str, str]) -> str:
    model_env = profile.get("model_env")
    if model_env and env.get(model_env):
        return env[model_env]
    return str(profile.get("model", ""))


def _resolve_trace_profile(profile: dict[str, Any], matrix: dict[str, Any]) -> dict[str, Any]:
    if profile.get("provider") != "trace_fixture":
        return profile
    base_dir = Path(str(matrix.get("_base_dir", ".")))
    resolved = dict(profile)
    if "trace_file" in resolved:
        resolved["trace_file"] = _resolve_fixture_path(base_dir, resolved["trace_file"])
    if "trace_cases" in resolved:
        resolved["trace_cases"] = _resolve_trace_cases(base_dir, resolved["trace_cases"])
    return resolved


def _resolve_trace_cases(base_dir: Path, value: Any) -> Any:
    if isinstance(value, str):
        return _resolve_fixture_path(base_dir, value)
    if isinstance(value, dict):
        return {key: _resolve_trace_cases(base_dir, item) for key, item in value.items()}
    return value


def _resolve_fixture_path(base_dir: Path, value: Any) -> str:
    path = Path(str(value))
    if path.is_absolute():
        return str(path)
    return str((base_dir / path).resolve())


def _trace_fixture_path(profile: dict[str, Any], harness: str, case: dict[str, Any]) -> Path:
    trace_cases = profile.get("trace_cases", {})
    case_name = case.get("name")
    if isinstance(trace_cases, dict):
        harness_cases = trace_cases.get(harness)
        if isinstance(harness_cases, dict) and harness_cases.get(case_name):
            return Path(str(harness_cases[case_name]))
        if trace_cases.get(case_name):
            return Path(str(trace_cases[case_name]))
    if profile.get("trace_file"):
        return Path(str(profile["trace_file"]))
    raise ModelMatrixError(f"no trace fixture for harness {harness!r} case {case_name!r}")


def _first_reasoning_summary(trace: dict[str, Any]) -> str:
    for step in trace.get("steps", []):
        if step.get("type") == "reasoning":
            return str(step.get("summary", ""))
    return "trace fixture"


def _matches(allowed: set[str] | None, value: Any) -> bool:
    return allowed is None or str(value) in allowed


def _default_api_key_env(provider: str) -> str:
    return {
        "anthropic": "ANTHROPIC_API_KEY",
        "gemini": "GEMINI_API_KEY",
        "openai": "OPENAI_API_KEY",
    }.get(provider, "")


def _matrix_passed(results: list[dict[str, Any]], *, live: bool, require_live: bool) -> bool:
    if not live:
        return bool(results)
    executed = [item for item in results if item["status"] in {"passed", "failed", "error"}]
    if require_live and any(item["status"] in {"skipped", "error"} for item in results):
        return False
    return bool(executed) and all(item["status"] == "passed" for item in executed)


def _summary(results: list[dict[str, Any]], *, live: bool) -> dict[str, Any]:
    counts = {status: sum(1 for item in results if item["status"] == status) for status in _statuses(results)}
    passed = counts.get("passed", 0)
    failed = counts.get("failed", 0)
    errors = counts.get("error", 0)
    planned = counts.get("planned", 0)
    skipped = counts.get("skipped", 0)
    denominator = passed + failed + errors if live else planned
    score = passed / denominator if denominator and live else (1.0 if planned else 0.0)
    return {
        "errors": errors,
        "failed_cases": failed,
        "planned": planned or len(results),
        "passed_cases": passed,
        "score": round(score, 3),
        "skipped": skipped,
        "total": len(results),
    }


def _cell_summary(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str, str, str], list[dict[str, Any]]] = {}
    for item in results:
        key = (
            str(item.get("provider", "")),
            str(item.get("harness", "")),
            str(item.get("tool_variant", "")),
            str(item.get("instruction_variant", "")),
        )
        groups.setdefault(key, []).append(item)
    cells = []
    for (provider, harness, tool_variant, instruction_variant), items in sorted(groups.items()):
        passed = sum(1 for item in items if item["status"] == "passed")
        failed = sum(1 for item in items if item["status"] == "failed")
        errors = sum(1 for item in items if item["status"] == "error")
        denominator = passed + failed + errors
        score = passed / denominator if denominator else 0.0
        cells.append(
            {
                "errors": errors,
                "failed": failed,
                "harness": harness,
                "instruction_variant": instruction_variant,
                "passed": passed,
                "provider": provider,
                "score": round(score, 3),
                "tool_variant": tool_variant,
            }
        )
    return cells


def _case_definitions(selected: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    cases: list[dict[str, Any]] = []
    for run in selected:
        case = run.get("case", {})
        if not isinstance(case, dict):
            continue
        name = str(case.get("name", ""))
        if not name or name in seen:
            continue
        seen.add(name)
        cases.append(
            {
                key: case[key]
                for key in (
                    "allow_no_tool",
                    "check_family",
                    "expected_args_contains",
                    "expected_tools",
                    "forbidden_tools",
                    "name",
                    "task",
                    "valid_tool_paths",
                )
                if key in case
            }
        )
    return cases


def _statuses(results: list[dict[str, Any]]) -> set[str]:
    return {str(item.get("status", "")) for item in results}


def _filters_to_dict(filters: MatrixFilters) -> dict[str, Any]:
    return {
        "harnesses": sorted(filters.harnesses) if filters.harnesses else None,
        "instruction_variants": (
            sorted(filters.instruction_variants) if filters.instruction_variants else None
        ),
        "cases": sorted(filters.cases) if filters.cases else None,
        "providers": sorted(filters.providers) if filters.providers else None,
        "variants": sorted(filters.variants) if filters.variants else None,
    }


def _response_text(content: list[dict[str, Any]]) -> str:
    return "\n".join(
        str(block.get("text", ""))
        for block in content
        if isinstance(block, dict) and block.get("type") == "text"
    ).strip()


def _post_json(
    url: str,
    payload: dict[str, Any],
    headers: dict[str, str],
    timeout: int,
) -> dict[str, Any]:
    body = json.dumps(payload).encode("utf-8")
    req = request.Request(url, data=body, headers=headers, method="POST")
    try:
        with request.urlopen(req, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise ModelMatrixError(f"HTTP {exc.code}: {detail}") from exc
    except error.URLError as exc:
        raise ModelMatrixError(f"request failed: {exc.reason}") from exc
