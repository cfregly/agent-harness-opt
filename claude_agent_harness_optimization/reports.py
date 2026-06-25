"""Render portable reports from optimizer and audit JSON output."""

from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any

from .adapters import load_json


def load_report_input(path: str | Path) -> dict[str, Any]:
    payload = load_json(path)
    if not isinstance(payload, dict):
        raise ValueError("report input must be a JSON object")
    return payload


def render_html_report(payload: dict[str, Any], *, title: str = "Harness Report") -> str:
    summary = _summary_rows(payload)
    rows = "\n".join(
        f"<tr><th>{html.escape(label)}</th><td>{html.escape(value)}</td></tr>"
        for label, value in summary
    )
    tables = "\n".join(_tables(payload))
    raw = html.escape(json.dumps(payload, indent=2, sort_keys=True))
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 32px; color: #202124; }}
    table {{ border-collapse: collapse; width: 100%; margin: 16px 0; }}
    th, td {{ border: 1px solid #d0d7de; padding: 8px 10px; text-align: left; vertical-align: top; }}
    th {{ background: #f6f8fa; }}
    .pass {{ color: #116329; font-weight: 700; }}
    .fail {{ color: #a40e26; font-weight: 700; }}
    pre {{ background: #f6f8fa; padding: 16px; overflow: auto; }}
  </style>
</head>
<body>
  <h1>{html.escape(title)}</h1>
  <table>
    <tbody>
{rows}
    </tbody>
  </table>
{tables}
  <h2>Raw JSON</h2>
  <pre>{raw}</pre>
</body>
</html>
"""


def render_pr_comment(payload: dict[str, Any], *, title: str = "Harness Report") -> str:
    rows = _summary_rows(payload)
    lines = [f"## {title}", ""]
    for label, value in rows:
        lines.append(f"- **{label}:** {value}")
    failures = _failure_lines(payload)
    if failures:
        lines.extend(["", "### Attention", ""])
        lines.extend(f"- {item}" for item in failures[:12])
    else:
        lines.extend(["", "No failing checks were found in this report."])
    return "\n".join(lines) + "\n"


def write_report(text: str, out: str | Path) -> Path:
    path = Path(out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _summary_rows(payload: dict[str, Any]) -> list[tuple[str, str]]:
    rows = [
        ("Name", str(payload.get("name") or payload.get("matrix") or "report")),
        ("Passed", "yes" if bool(payload.get("passed")) else "no"),
    ]
    score = _score(payload)
    if score is not None:
        rows.append(("Score", f"{score:.3f}"))
    summary = payload.get("summary")
    if isinstance(summary, dict):
        for key in ("total", "passed_cases", "failed_cases", "errors", "skipped"):
            if key in summary:
                rows.append((key.replace("_", " ").title(), str(summary[key])))
    if "live" in payload:
        rows.append(("Live", "yes" if payload.get("live") else "no"))
    if "dry_run" in payload:
        rows.append(("Dry Run", "yes" if payload.get("dry_run") else "no"))
    return rows


def _score(payload: dict[str, Any]) -> float | None:
    for key in ("overall_score", "score"):
        if key in payload:
            return float(payload[key])
    summary = payload.get("summary")
    if isinstance(summary, dict) and "score" in summary:
        return float(summary["score"])
    value_bar = payload.get("value_bar")
    if isinstance(value_bar, dict) and "score" in value_bar:
        return float(value_bar["score"])
    return None


def _tables(payload: dict[str, Any]) -> list[str]:
    tables = []
    for key in ("cells", "results", "checks", "traces"):
        value = payload.get(key)
        if isinstance(value, list) and value and all(isinstance(item, dict) for item in value):
            tables.append(_dict_table(key.replace("_", " ").title(), value[:50]))
    return tables


def _dict_table(title: str, rows: list[dict[str, Any]]) -> str:
    keys = sorted({key for row in rows for key in row if _is_scalar(row.get(key))})
    header = "".join(f"<th>{html.escape(str(key))}</th>" for key in keys)
    body = []
    for row in rows:
        cells = "".join(f"<td>{html.escape(str(row.get(key, '')))}</td>" for key in keys)
        body.append(f"<tr>{cells}</tr>")
    return f"<h2>{html.escape(title)}</h2><table><thead><tr>{header}</tr></thead><tbody>{''.join(body)}</tbody></table>"


def _failure_lines(payload: dict[str, Any]) -> list[str]:
    failures = []
    for key in ("findings", "results", "checks", "traces"):
        value = payload.get(key)
        if not isinstance(value, list):
            continue
        for item in value:
            if isinstance(item, dict) and item.get("passed") is False:
                label = item.get("name") or item.get("case") or item.get("check") or key
                detail = item.get("detail") or item.get("status") or item.get("error") or "failed"
                failures.append(f"{label}: {detail}")
    for nested in ("tool_selection", "value_bar", "tool_inventory"):
        value = payload.get(nested)
        if isinstance(value, dict) and value.get("passed") is False:
            failures.append(f"{nested}: failed")
    return failures


def _is_scalar(value: Any) -> bool:
    return value is None or isinstance(value, (str, int, float, bool))
