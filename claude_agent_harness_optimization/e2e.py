"""Run read-oriented credentialed harness checks from JSON specs."""

from __future__ import annotations

import json
import os
import base64
from pathlib import Path
from typing import Any, Callable
from urllib import error, request

from .adapters import load_json
from .model_matrix import load_env_file


HttpRequestFn = Callable[[str, str, dict[str, str], bytes | None, int], tuple[int, Any]]


class E2EError(RuntimeError):
    """Raised when an E2E spec cannot run safely."""


def run_e2e_spec(
    spec_path: str | Path,
    *,
    env_file: str | Path | None = None,
    allow_mutation: bool = False,
    dry_run: bool = False,
    request_fn: HttpRequestFn | None = None,
) -> dict[str, Any]:
    spec = load_json(spec_path)
    if not isinstance(spec, dict):
        raise E2EError("E2E spec must be a JSON object")
    env = os.environ.copy()
    env.update(load_env_file(env_file))
    required = spec.get("env", {}).get("required", [])
    missing = [] if dry_run else [key for key in required if not env.get(key)]
    if missing:
        return {
            "checks": [],
            "dry_run": dry_run,
            "missing_env": missing,
            "name": spec.get("name", Path(spec_path).stem),
            "passed": False,
        }

    results = []
    for check in spec.get("checks", []):
        if not isinstance(check, dict):
            continue
        results.append(
            _run_check(
                check,
                env,
                allow_mutation=allow_mutation,
                dry_run=dry_run,
                request_fn=request_fn or _http_json,
            )
        )
    return {
        "checks": results,
        "dry_run": dry_run,
        "missing_env": [],
        "name": spec.get("name", Path(spec_path).stem),
        "passed": bool(results) and all(item["passed"] for item in results),
    }


def _run_check(
    check: dict[str, Any],
    env: dict[str, str],
    *,
    allow_mutation: bool,
    dry_run: bool,
    request_fn: HttpRequestFn,
) -> dict[str, Any]:
    check_type = check.get("type", "http_json")
    if check_type != "http_json":
        return _result(check, False, f"unsupported check type: {check_type}")
    method = str(check.get("method", "GET")).upper()
    read_only = bool(check.get("read_only", method in {"GET", "HEAD"}))
    if method not in {"GET", "HEAD"} and not (allow_mutation or read_only):
        return _result(check, False, f"{method} requires read_only=true or --allow-mutation")
    if dry_run:
        return _result(check, True, "dry run validated check shape", status="planned")

    url = _substitute(str(check.get("url", "")), env)
    headers = {
        str(key): _substitute(str(value), env)
        for key, value in check.get("headers", {}).items()
        if value is not None
    }
    headers.update(_basic_auth_header(check.get("basic_auth"), env))
    body = _body_bytes(check.get("json"))
    timeout = int(check.get("timeout", 30))
    try:
        status_code, payload = request_fn(method, url, headers, body, timeout)
    except Exception as exc:  # noqa: BLE001
        return _result(check, False, f"request failed: {exc}", status="error")

    expected_status = int(check.get("expect_status", 200))
    if status_code != expected_status:
        return _result(
            check,
            False,
            f"expected status {expected_status}, got {status_code}",
            http_status=status_code,
        )
    path = str(check.get("expect_json_path", "")).strip()
    if path:
        value = _json_path(payload, path)
        if value is None:
            return _result(check, False, f"missing JSON path {path}", http_status=status_code)
        if "expect_json_value" in check and value != check["expect_json_value"]:
            return _result(check, False, f"JSON path {path} had unexpected value", http_status=status_code)
        if "expect_json_contains" in check and str(check["expect_json_contains"]) not in str(value):
            return _result(check, False, f"JSON path {path} did not contain expected text", http_status=status_code)
    return _result(check, True, "check passed", http_status=status_code)


def _http_json(
    method: str,
    url: str,
    headers: dict[str, str],
    body: bytes | None,
    timeout: int,
) -> tuple[int, Any]:
    req = request.Request(url, data=body, headers=headers, method=method)
    if body is not None and "content-type" not in {key.lower() for key in headers}:
        req.add_header("content-type", "application/json")
    try:
        with request.urlopen(req, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
            return response.status, json.loads(raw) if raw else {}
    except error.HTTPError as exc:
        raw = exc.read().decode("utf-8")
        try:
            payload = json.loads(raw) if raw else {}
        except json.JSONDecodeError:
            payload = {"body": raw[:500]}
        return exc.code, payload


def _result(
    check: dict[str, Any],
    passed: bool,
    detail: str,
    *,
    http_status: int | None = None,
    status: str | None = None,
) -> dict[str, Any]:
    return {
        "detail": detail,
        "http_status": http_status,
        "method": str(check.get("method", "GET")).upper(),
        "name": check.get("name", ""),
        "passed": passed,
        "read_only": bool(check.get("read_only", True)),
        "status": status or ("passed" if passed else "failed"),
        "type": check.get("type", "http_json"),
    }


def _substitute(value: str, env: dict[str, str]) -> str:
    output = value
    for key, replacement in env.items():
        output = output.replace("${" + key + "}", replacement)
    return output


def _body_bytes(value: Any) -> bytes | None:
    if value is None:
        return None
    return json.dumps(value, sort_keys=True).encode("utf-8")


def _basic_auth_header(value: Any, env: dict[str, str]) -> dict[str, str]:
    if not isinstance(value, dict):
        return {}
    username = _substitute(str(value.get("username", "")), env)
    password = _substitute(str(value.get("password", "")), env)
    if value.get("username_env"):
        username = env.get(str(value["username_env"]), "")
    if value.get("password_env"):
        password = env.get(str(value["password_env"]), "")
    token = base64.b64encode(f"{username}:{password}".encode("utf-8")).decode("ascii")
    return {"Authorization": f"Basic {token}"}


def _json_path(payload: Any, path: str) -> Any:
    current = payload
    for part in path.split("."):
        if isinstance(current, dict):
            current = current.get(part)
        elif isinstance(current, list) and part.isdigit():
            current = current[int(part)]
        else:
            return None
    return current
