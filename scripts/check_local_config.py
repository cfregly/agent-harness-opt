#!/usr/bin/env python3
"""Validate local env samples, setup docs, and credentialed spec keys stay synchronized."""

from __future__ import annotations

from pathlib import Path
import json
import re


ROOT = Path(__file__).resolve().parents[1]
ENV_SAMPLE = ".env.example"
ENV_REF_RE = re.compile(r"\$\{([A-Z0-9_]+)\}")
ENV_GET_RE = re.compile(r'env\.get\("([A-Z0-9_]+)"\)')
OPTIONAL_DOC_KEYS = ("ZYMTRACE_LICENSE_KEY",)
REQUIRED_SETUP_PHRASES = (
    "cp .env.example .env",
    "Do not commit `.env`",
    "ANTHROPIC_API_KEY",
    "gh secret set ANTHROPIC_API_KEY",
)
REQUIRED_PROBE_DOC_PHRASES = (
    "python scripts/probe_service_keys.py --env-file .env",
    "python -m claude_agent_harness_opt mcp-e2e evals/e2e/github_readonly.json --env-file .env",
    "Firecrawl",
    "GitHub",
    "Cloudflare",
    "Cloudflare R2",
    "ClickHouse",
    "Stripe",
)


def main() -> int:
    failures = check_local_config()
    if failures:
        print("\n".join(sorted(failures)))
        return 1
    print("local config check passed")
    return 0


def check_local_config(root: Path = ROOT) -> list[str]:
    failures: list[str] = []
    sample_keys = _env_sample_keys(root / ENV_SAMPLE)
    if not sample_keys:
        failures.append(f"{ENV_SAMPLE}: no sample env keys found")

    required_keys = _required_config_keys(root)
    for key in sorted(required_keys - sample_keys):
        failures.append(f"{ENV_SAMPLE}: missing required local config key {key}")

    for key in OPTIONAL_DOC_KEYS:
        if key not in sample_keys:
            failures.append(f"{ENV_SAMPLE}: missing documented optional local config key {key}")

    failures.extend(_check_probe_alias_groups(root, sample_keys))
    failures.extend(_check_setup_docs(root))
    failures.extend(_check_probe_docs(root, sample_keys))
    return failures


def _env_sample_keys(path: Path) -> set[str]:
    if not path.exists():
        return set()
    keys: set[str] = set()
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key = line.split("=", 1)[0].strip()
        if key:
            keys.add(key)
    return keys


def _required_config_keys(root: Path = ROOT) -> set[str]:
    keys: set[str] = set()
    for spec_path in sorted((root / "evals" / "e2e").glob("*.json")):
        spec = json.loads(spec_path.read_text(encoding="utf-8"))
        keys.update(_e2e_env_keys(spec))
    for matrix_root in (root / "evals" / "model_matrix", root / "evals" / "targets"):
        for matrix_path in sorted(matrix_root.rglob("*.json")):
            payload = json.loads(matrix_path.read_text(encoding="utf-8"))
            keys.update(_json_values_for_key(payload, "api_key_env"))
    keys.update(_single_probe_keys(root / "scripts" / "probe_service_keys.py"))
    return keys


def _e2e_env_keys(spec: object) -> set[str]:
    keys: set[str] = set()
    if not isinstance(spec, dict):
        return keys
    required = spec.get("env", {}).get("required", [])
    if isinstance(required, list):
        keys.update(str(item) for item in required if str(item).strip())
    keys.update(ENV_REF_RE.findall(json.dumps(spec, sort_keys=True)))
    keys.update(_json_values_for_suffix(spec, "_env"))
    return keys


def _json_values_for_key(value: object, target_key: str) -> set[str]:
    found: set[str] = set()
    if isinstance(value, dict):
        for key, item in value.items():
            if key == target_key and isinstance(item, str):
                found.add(item)
            else:
                found.update(_json_values_for_key(item, target_key))
    elif isinstance(value, list):
        for item in value:
            found.update(_json_values_for_key(item, target_key))
    return found


def _json_values_for_suffix(value: object, suffix: str) -> set[str]:
    found: set[str] = set()
    if isinstance(value, dict):
        for key, item in value.items():
            if key.endswith(suffix) and isinstance(item, str):
                found.add(item)
            else:
                found.update(_json_values_for_suffix(item, suffix))
    elif isinstance(value, list):
        for item in value:
            found.update(_json_values_for_suffix(item, suffix))
    return found


def _single_probe_keys(path: Path) -> set[str]:
    keys: set[str] = set()
    if not path.exists():
        return keys
    for line in path.read_text(encoding="utf-8").splitlines():
        matches = ENV_GET_RE.findall(line)
        if len(matches) == 1:
            keys.add(matches[0])
    return keys


def _check_probe_alias_groups(root: Path, sample_keys: set[str]) -> list[str]:
    path = root / "scripts" / "probe_service_keys.py"
    if not path.exists():
        return ["scripts/probe_service_keys.py: missing"]
    failures: list[str] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        matches = ENV_GET_RE.findall(line)
        if len(matches) > 1 and not any(key in sample_keys for key in matches):
            failures.append(
                f"scripts/probe_service_keys.py:{line_number}: alias group missing from {ENV_SAMPLE}: "
                + ", ".join(matches)
            )
    return failures


def _check_setup_docs(root: Path = ROOT) -> list[str]:
    path = root / "docs" / "setup.md"
    if not path.exists():
        return ["docs/setup.md: missing"]
    text = path.read_text(encoding="utf-8")
    return [f"docs/setup.md: missing setup phrase {phrase!r}" for phrase in REQUIRED_SETUP_PHRASES if phrase not in text]


def _check_probe_docs(root: Path, sample_keys: set[str]) -> list[str]:
    path = root / "docs" / "credentialed-service-probes.md"
    if not path.exists():
        return ["docs/credentialed-service-probes.md: missing"]
    text = path.read_text(encoding="utf-8")
    failures = [
        f"docs/credentialed-service-probes.md: missing probe phrase {phrase!r}"
        for phrase in REQUIRED_PROBE_DOC_PHRASES
        if phrase not in text
    ]
    for key in sorted(_documented_service_keys(sample_keys)):
        if key not in text:
            failures.append(f"docs/credentialed-service-probes.md: missing env key {key}")
    return failures


def _documented_service_keys(sample_keys: set[str]) -> set[str]:
    return {
        key
        for key in sample_keys
        if key.startswith(("FIRECRAWL", "GITHUB", "CLOUDFLARE", "R2_", "CLICKHOUSE", "STRIPE", "ZYMTRACE"))
    }


if __name__ == "__main__":
    raise SystemExit(main())
