#!/usr/bin/env python3
"""Validate retained non-matrix eval surfaces without live credentials."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from claude_agent_harness_opt.adapters import (  # noqa: E402
    claude_messages_to_trace,
    load_run_export,
    normalize_run_export,
)
from claude_agent_harness_opt.agent_audit import review_agent_bundle  # noqa: E402
from claude_agent_harness_opt.e2e import E2EError, run_e2e_spec  # noqa: E402
from claude_agent_harness_opt.evals import evaluate_case  # noqa: E402
from claude_agent_harness_opt.harness_checks import load_check_catalog  # noqa: E402
from claude_agent_harness_opt.import_run import import_run_export  # noqa: E402
from claude_agent_harness_opt.live_harness import (  # noqa: E402
    LiveHarnessError,
    run_live_harness_spec,
)
from claude_agent_harness_opt.tool_selection import review_tool_selection_bundle  # noqa: E402
from claude_agent_harness_opt.trace_review import review_trace  # noqa: E402
from claude_agent_harness_opt.trace_suite import run_trace_suite  # noqa: E402


EXAMPLES_DIR = ROOT / "evals" / "examples"
E2E_DIR = ROOT / "evals" / "e2e"
LIVE_HARNESSES_DIR = ROOT / "evals" / "live_harnesses"
TRACE_SUITES_DIR = ROOT / "evals" / "suites"
CHECKS_DIR = ROOT / "evals" / "checks"


class DisappearedDuringCheck(Exception):
    """Raised when a transient fixture disappears after directory discovery."""


def main() -> int:
    failures = check_eval_surfaces()
    if failures:
        print("\n".join(sorted(failures)))
        return 1
    print("eval surface check passed")
    return 0


def check_eval_surfaces() -> list[str]:
    failures: list[str] = []
    failures.extend(_check_example_fixtures())
    failures.extend(_check_e2e_specs())
    failures.extend(_check_live_harness_specs())
    failures.extend(_check_trace_suites())
    failures.extend(_check_check_catalogs())
    return failures


def _check_example_fixtures() -> list[str]:
    failures: list[str] = []
    paths = sorted(path for path in EXAMPLES_DIR.iterdir() if path.is_file())
    if not paths:
        return ["evals/examples: no example fixtures found"]
    for path in paths:
        rel = path.relative_to(ROOT)
        try:
            if path.suffix == ".jsonl":
                failures.extend(_check_normalized_runtime_example(rel, load_run_export(path)))
                continue
            payload = _load_object(path)
        except (DisappearedDuringCheck, FileNotFoundError):
            continue
        except ValueError as exc:
            failures.append(f"{rel}: {exc}")
            continue
        except Exception as exc:  # noqa: BLE001
            failures.append(f"{rel}: failed to load fixture: {exc}")
            continue

        try:
            handled = _check_json_example_fixture(path, rel, payload, failures)
        except Exception as exc:  # noqa: BLE001 - example gates should report every fixture.
            failures.append(f"{rel}: validation crashed: {exc}")
            handled = True
        if not handled:
            failures.append(f"{rel}: unclassified example fixture shape")
    return failures


def _check_json_example_fixture(
    path: Path,
    rel: Path,
    payload: dict[str, Any],
    failures: list[str],
) -> bool:
    if payload.get("type") in {"answer_accuracy", "tool_use_accuracy", "final_state_accuracy"}:
        result = evaluate_case(payload)
        if not result.passed:
            failures.append(f"{rel}: eval example did not pass")
        return True

    if isinstance(payload.get("steps"), list):
        result = review_trace(payload)
        if _is_negative_example(path):
            if result.passed:
                failures.append(f"{rel}: negative trace unexpectedly passed")
        elif not result.passed:
            failures.append(f"{rel}: trace review did not pass")
        return True

    if isinstance(payload.get("messages"), list):
        failures.extend(_check_trace_result(rel, claude_messages_to_trace(payload)))
        return True

    if isinstance(payload.get("events"), list):
        if isinstance(payload.get("tools"), list) or isinstance(payload.get("tool_selection_cases"), list):
            with tempfile.TemporaryDirectory(prefix="aho-import-example-") as tmpdir:
                imported = import_run_export(path, adapter=str(payload.get("adapter", "")) or None, out_dir=tmpdir)
                audit = review_agent_bundle(imported["bundle"])
                if not audit.get("passed"):
                    failures.append(f"{rel}: imported audit bundle did not pass")
                if not int(imported.get("trace_steps", 0)):
                    failures.append(f"{rel}: imported trace had no steps")
        else:
            failures.extend(_check_normalized_runtime_example(rel, payload))
        return True

    if _looks_like_agent_audit_bundle(payload):
        audit = review_agent_bundle(path)
        if _is_negative_example(path):
            if audit.get("passed") or audit.get("value_bar", {}).get("passed"):
                failures.append(f"{rel}: negative audit bundle unexpectedly passed")
        elif not audit.get("passed"):
            failures.append(f"{rel}: audit bundle did not pass")
        return True

    if isinstance(payload.get("tools"), list) and isinstance(payload.get("tool_selection_cases"), list):
        review = review_tool_selection_bundle(path)
        if _is_negative_example(path):
            if review.passed:
                failures.append(f"{rel}: negative tool-selection bundle unexpectedly passed")
        elif not review.passed:
            failures.append(f"{rel}: tool-selection bundle did not pass")
        return True

    return False


def _check_normalized_runtime_example(rel: Path, payload: Any) -> list[str]:
    trace = normalize_run_export(payload)
    return _check_trace_result(rel, trace)


def _check_trace_result(rel: Path, trace: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    if not trace.get("steps"):
        failures.append(f"{rel}: normalized trace has no steps")
        return failures
    result = review_trace(trace)
    if not result.passed:
        failures.append(f"{rel}: normalized trace did not pass review")
    return failures


def _looks_like_agent_audit_bundle(payload: dict[str, Any]) -> bool:
    return isinstance(payload.get("tools"), list) and isinstance(payload.get("traces"), list)


def _is_negative_example(path: Path) -> bool:
    stem = path.stem
    return any(marker in stem for marker in ("_bad", "missing_value_bar", "before_bundle"))


def _check_e2e_specs() -> list[str]:
    failures: list[str] = []
    paths = sorted(E2E_DIR.glob("*.json"))
    if not paths:
        return ["evals/e2e: no E2E specs found"]
    for path in paths:
        rel = path.relative_to(ROOT)
        try:
            spec = _load_object(path)
        except DisappearedDuringCheck:
            continue
        except ValueError as exc:
            failures.append(f"{rel}: {exc}")
            continue
        failures.extend(_check_e2e_spec_shape(rel, spec))
        try:
            result = run_e2e_spec(path, dry_run=True)
        except E2EError as exc:
            failures.append(f"{rel}: dry-run failed: {exc}")
            continue
        if not result.get("passed"):
            failures.append(f"{rel}: dry-run did not pass")
        if not result.get("checks"):
            failures.append(f"{rel}: dry-run produced no checks")
    return failures


def _check_e2e_spec_shape(rel: Path, spec: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    if not str(spec.get("name", "")).strip():
        failures.append(f"{rel}: missing name")
    required_env = spec.get("env", {}).get("required", [])
    if not isinstance(required_env, list) or not required_env:
        failures.append(f"{rel}: env.required must be a nonempty list")
    checks = spec.get("checks")
    if not isinstance(checks, list) or not checks:
        failures.append(f"{rel}: checks must be a nonempty list")
        return failures
    for index, check in enumerate(checks):
        if not isinstance(check, dict):
            failures.append(f"{rel}: checks[{index}] must be an object")
            continue
        prefix = f"{rel}: checks[{index}]"
        if not str(check.get("name", "")).strip():
            failures.append(f"{prefix} missing name")
        if check.get("type", "http_json") != "http_json":
            failures.append(f"{prefix} type must be http_json")
        method = str(check.get("method", "GET")).upper()
        if method not in {"GET", "HEAD"}:
            failures.append(f"{prefix} method must be GET or HEAD for read-only specs")
        if check.get("read_only") is not True:
            failures.append(f"{prefix} read_only must be true")
        if not str(check.get("url", "")).strip():
            failures.append(f"{prefix} missing url")
        if "expect_status" not in check:
            failures.append(f"{prefix} missing expect_status")
        if not any(key in check for key in ("expect_json_path", "expect_json_value", "expect_json_contains")):
            failures.append(f"{prefix} missing JSON expectation")
    return failures


def _check_live_harness_specs() -> list[str]:
    failures: list[str] = []
    paths = sorted(LIVE_HARNESSES_DIR.glob("*.json"))
    if not paths:
        return ["evals/live_harnesses: no live harness specs found"]
    with tempfile.TemporaryDirectory(prefix="aho-live-harness-dry-run-") as tmpdir:
        for path in paths:
            rel = path.relative_to(ROOT)
            try:
                spec = _load_object(path)
            except DisappearedDuringCheck:
                continue
            except ValueError as exc:
                failures.append(f"{rel}: {exc}")
                continue
            failures.extend(_check_live_harness_spec_shape(rel, spec))
            try:
                result = run_live_harness_spec(path, dry_run=True, out_dir=tmpdir)
            except FileNotFoundError:
                continue
            except LiveHarnessError as exc:
                failures.append(f"{rel}: dry-run failed: {exc}")
                continue
            if not result.get("passed"):
                failures.append(f"{rel}: dry-run did not pass")
            expected_cells = len(spec.get("cases", [])) * len(spec.get("harnesses", []))
            if len(result.get("results", [])) != expected_cells:
                failures.append(f"{rel}: dry-run did not select every case/harness cell")
    return failures


def _check_live_harness_spec_shape(rel: Path, spec: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    if not str(spec.get("name", "")).strip():
        failures.append(f"{rel}: missing name")
    cases = spec.get("cases")
    harnesses = spec.get("harnesses")
    if not isinstance(cases, list) or not cases:
        failures.append(f"{rel}: cases must be a nonempty list")
    if not isinstance(harnesses, list) or not harnesses:
        failures.append(f"{rel}: harnesses must be a nonempty list")
    value_bar = spec.get("value_bar")
    if not isinstance(value_bar, dict) or not str(value_bar.get("claim", "")).strip():
        failures.append(f"{rel}: value_bar.claim must be present")
    if isinstance(value_bar, dict) and not str(value_bar.get("adversarial_check", "")).strip():
        failures.append(f"{rel}: value_bar.adversarial_check must be present")
    for index, case in enumerate(cases if isinstance(cases, list) else []):
        if not isinstance(case, dict):
            failures.append(f"{rel}: cases[{index}] must be an object")
            continue
        if not str(case.get("name", "")).strip():
            failures.append(f"{rel}: cases[{index}] missing name")
        if not str(case.get("prompt_template", case.get("prompt", ""))).strip():
            failures.append(f"{rel}: cases[{index}] missing prompt_template")
    for index, harness in enumerate(harnesses if isinstance(harnesses, list) else []):
        if not isinstance(harness, dict):
            failures.append(f"{rel}: harnesses[{index}] must be an object")
            continue
        if not str(harness.get("name", "")).strip():
            failures.append(f"{rel}: harnesses[{index}] missing name")
        if not str(harness.get("marker", "")).strip():
            failures.append(f"{rel}: harnesses[{index}] missing marker")
        command = harness.get("command")
        if not isinstance(command, list) or not command:
            failures.append(f"{rel}: harnesses[{index}] command must be a nonempty list")
        else:
            failures.extend(_check_command_path_tokens(rel, f"harnesses[{index}].command", command))
        version_command = harness.get("version_command")
        if not isinstance(version_command, list) or not version_command:
            failures.append(f"{rel}: harnesses[{index}] version_command must be a nonempty list")
        else:
            failures.extend(
                _check_command_path_tokens(rel, f"harnesses[{index}].version_command", version_command)
            )
        if not str(harness.get("adapter", "")).strip():
            failures.append(f"{rel}: harnesses[{index}] missing adapter")
        if not str(harness.get("expected_tool", "")).strip():
            failures.append(f"{rel}: harnesses[{index}] missing expected_tool")
        expected_args = harness.get("expected_args_contains")
        if not isinstance(expected_args, dict) or not expected_args:
            failures.append(f"{rel}: harnesses[{index}] expected_args_contains must be a nonempty object")
    return failures


def _check_command_path_tokens(rel: Path, label: str, command: list[Any]) -> list[str]:
    failures: list[str] = []
    for index, part in enumerate(command):
        token = str(part)
        if not _looks_like_local_command_path(token):
            continue
        if not (ROOT / token).exists():
            failures.append(f"{rel}: {label}[{index}] local path missing: {token}")
    return failures


def _looks_like_local_command_path(token: str) -> bool:
    if not token or any(marker in token for marker in ("{", "}", "$")):
        return False
    if token.startswith(("http://", "https://", "/tmp/")):
        return False
    if Path(token).is_absolute():
        return False
    if token.startswith(("docs/", "evals/", "prompts/", "recipes/", "scripts/", ".claude/")):
        return True
    return token.endswith((".json", ".jsonl", ".md", ".py", ".txt", ".yaml", ".yml"))


def _check_trace_suites() -> list[str]:
    failures: list[str] = []
    paths = sorted(TRACE_SUITES_DIR.glob("*.json"))
    if not paths:
        return ["evals/suites: no trace suites found"]
    for path in paths:
        rel = path.relative_to(ROOT)
        try:
            result = run_trace_suite(path)
        except Exception as exc:  # noqa: BLE001 - report malformed suites without hiding others.
            failures.append(f"{rel}: trace suite failed: {exc}")
            continue
        if not result.get("passed"):
            failures.append(f"{rel}: trace suite expectations did not pass")
        if not result.get("cases"):
            failures.append(f"{rel}: trace suite has no cases")
    return failures


def _check_check_catalogs() -> list[str]:
    failures: list[str] = []
    paths = sorted(CHECKS_DIR.glob("*.json"))
    if not paths:
        return ["evals/checks: no check catalogs found"]
    seen_ids: set[str] = set()
    for path in paths:
        rel = path.relative_to(ROOT)
        try:
            catalog = load_check_catalog(path)
        except Exception as exc:  # noqa: BLE001
            failures.append(f"{rel}: check catalog failed: {exc}")
            continue
        for check in catalog.get("checks", []):
            check_id = str(check.get("id", ""))
            if check_id in seen_ids:
                failures.append(f"{rel}: duplicate check id across catalogs: {check_id}")
            seen_ids.add(check_id)
            if not str(check.get("prompt_pattern", "")).strip():
                failures.append(f"{rel}: check {check_id} missing prompt_pattern")
    return failures


def _load_object(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise DisappearedDuringCheck(str(path)) from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError("must be a JSON object")
    return payload


if __name__ == "__main__":
    raise SystemExit(main())
