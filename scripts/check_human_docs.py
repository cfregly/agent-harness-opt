#!/usr/bin/env python3
"""Validate public Markdown keeps human-readable content before audit detail."""

from __future__ import annotations

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_MARKDOWN_GLOBS = ("README.md", "docs/**/*.md", "evals/pr_packets/**/*.md")
LLM_SUMMARY = "<summary>LLM / Machine-readable details</summary>"
REPO_LINK = "https://github.com/cfregly/claude-agent-harness-opt/"
ACTION_SUMMARY_DOCS = {
    "docs/confirmed-improvements.md",
    "docs/public-mcp-sweep.md",
    "docs/yc-p2026-mcp-sweep.md",
}
ACTION_SECTION_DOCS = {
}
SUPPORTING_EVIDENCE_DOCS = {
    "docs/frontier-stress-2026-07-01.md",
}
FOUNDER_HANDOFF_SECTIONS = (
    "## Summary",
    "## Why This Matters",
    "## Recommended Actions",
    "## Run This In Your Repo",
    "## Model Coverage",
    "## Evidence Bundle",
)
LOCAL_AGENT_CTA_MARKERS = (
    "codex exec -C /path/to/repo --sandbox read-only -",
    "claude -p --permission-mode plan",
    "gemini --approval-mode plan --output-format text",
    "Review this action-first finding:",
    "Do not edit files yet.",
)
EVIDENCE_HEAVY_MARKERS = (
    "evidence.json",
    "evals/model_matrix/",
    "evals/results/",
    "REPRODUCTION.md",
    "PR_BODY.md",
    "PR_TITLE.txt",
)
HUMAN_INTRO_MACHINE_DETAIL_LIMIT = 20
ROOT_HUMAN_SECTIONS = (
    "## Demo",
    "## Share This",
    "## Quickstart",
    "## What it implements",
    "## How It Works",
    "## Start Here",
    "## Shareable Bundles",
)
ROOT_MACHINE_HEADINGS = (
    "## Layout",
    "## Founder Packets",
    "## Claude Code Skill",
    "## Claude Judge",
    "## Tool Selection Optimization",
    "## Verify it",
    "## Sources",
)
MACHINE_DETAIL_RE = re.compile(
    r"(?i)(?:scripts/check_|matrix-coverage|matrix-coverage-suite|claude_agent_harness_opt|"
    r"evals/(?:results|model_matrix|targets|pr_packets)|evidence\.json|schema|"
    r"check_family|tool_selection_cases|source pins|coverage\.required)"
)


def main() -> int:
    failures = check_human_docs()
    if failures:
        print("\n".join(sorted(failures)))
        return 1
    print("human docs check passed")
    return 0


def check_human_docs(root: Path = ROOT) -> list[str]:
    failures: list[str] = []
    for path in _public_markdown_paths(root):
        text = path.read_text(encoding="utf-8")
        rel = _rel(path, root)
        failures.extend(_check_details_balance(rel, text))
        if rel.as_posix() == "README.md":
            failures.extend(_check_root_readme(rel, text))
        elif _is_bundle_index(rel):
            failures.extend(_check_bundle_index(rel, text))
        elif _is_sendable_packet(rel):
            failures.extend(_check_sendable_packet(rel, text))
        elif _is_pr_body(rel):
            failures.extend(_check_founder_handoff(rel, text, require_share_link=False))
            failures.extend(_check_machine_detail_placement(rel, text))
        elif _is_pr_reproduction(rel):
            failures.extend(_check_supporting_evidence_note(rel, text, start_markers=("PR_BODY.md",)))
            failures.extend(_check_machine_detail_placement(rel, text))
        elif rel.as_posix() in ACTION_SUMMARY_DOCS:
            failures.extend(_check_action_summary_doc(rel, text))
            failures.extend(_check_machine_detail_placement(rel, text))
        elif rel.as_posix() in ACTION_SECTION_DOCS:
            failures.extend(_check_action_first_sections(rel, text, require_full_bundle=False))
            failures.extend(_check_machine_detail_placement(rel, text))
        elif rel.as_posix() in SUPPORTING_EVIDENCE_DOCS:
            failures.extend(
                _check_supporting_evidence_note(
                    rel,
                    text,
                    start_markers=("Founder Findings", "Confirmed Improvements", "PR/evidence bundle"),
                )
            )
            failures.extend(_check_machine_detail_placement(rel, text))
        else:
            failures.extend(_check_machine_detail_placement(rel, text))
    return failures


def _check_details_balance(rel: Path, text: str) -> list[str]:
    failures: list[str] = []
    if text.count("<details>") != text.count("</details>"):
        failures.append(f"{rel}: unbalanced <details> disclosures")
    if LLM_SUMMARY in text and "</details>" not in text:
        failures.append(f"{rel}: LLM disclosure is missing closing </details>")
    return failures


def _check_root_readme(rel: Path, text: str) -> list[str]:
    failures: list[str] = []
    summary_index = text.find(LLM_SUMMARY)
    if summary_index == -1:
        failures.append(f"{rel}: missing bottom LLM / Machine-readable details disclosure")
        summary_index = len(text)

    previous = -1
    for heading in ROOT_HUMAN_SECTIONS:
        index = text.find(heading)
        if index == -1:
            failures.append(f"{rel}: missing human-facing section {heading}")
            continue
        if index > summary_index:
            failures.append(f"{rel}: human-facing section {heading} is inside LLM details")
        if index < previous:
            failures.append(f"{rel}: section {heading} is out of human-first order")
        previous = index

    for heading in ROOT_MACHINE_HEADINGS:
        index = text.find(heading)
        if index != -1 and index < summary_index:
            failures.append(f"{rel}: machine section {heading} appears before LLM details")

    if "## License" in text and summary_index > text.find("## License"):
        failures.append(f"{rel}: LLM details must stay above License and below human sections")
    if "scripts/check_" in text[:summary_index]:
        failures.append(f"{rel}: checker inventory appears above LLM details")
    return failures


def _check_sendable_packet(rel: Path, text: str) -> list[str]:
    failures: list[str] = []
    first_lines = "\n".join(text.splitlines()[:12])
    if "Share link: [" not in first_lines:
        failures.append(f"{rel}: share link must be clickable in the first 12 lines")
    if "Share link: [" in first_lines and REPO_LINK not in first_lines:
        failures.append(f"{rel}: share link must use a public GitHub URL")
    failures.extend(_check_founder_handoff(rel, text, require_share_link=True))
    return failures


def _check_founder_handoff(rel: Path, text: str, *, require_share_link: bool) -> list[str]:
    failures: list[str] = []
    indexes: dict[str, int] = {}
    for heading in FOUNDER_HANDOFF_SECTIONS:
        index = text.find(heading)
        indexes[heading] = index
        if index == -1:
            failures.append(f"{rel}: missing founder-handoff section {heading}")
        elif text.count(heading) != 1:
            failures.append(f"{rel}: duplicate founder-handoff section {heading}")
    present = [indexes[heading] for heading in FOUNDER_HANDOFF_SECTIONS if indexes[heading] != -1]
    if len(present) == len(FOUNDER_HANDOFF_SECTIONS) and present != sorted(present):
        failures.append(f"{rel}: founder-handoff sections are out of order")

    if "## Actions By Company" in text:
        failures.append(f"{rel}: replace ## Actions By Company with target-owned Recommended Actions and Model Coverage")
    if "## Founder Summary" in text:
        failures.append(f"{rel}: collapse ## Founder Summary into ## Summary and ## Why This Matters")

    exact_heading = "### Exact Text To Apply"
    exact_table = "| Where to edit | Baseline text | Suggested replacement text |"
    behavior_heading = "### Baseline / Suggested Behavior"
    behavior_table = "| Suggested change | Baseline / before description | Suggested / after description | Result |"
    table_index = indexes.get("## Summary", -1)
    why_index = indexes.get("## Why This Matters", -1)
    if table_index != -1:
        table_window = text[table_index : why_index if why_index != -1 else table_index + 1200]
        if exact_heading not in table_window:
            failures.append(f"{rel}: Summary must include ### Exact Text To Apply before behavior summary")
        if exact_table not in table_window:
            failures.append(f"{rel}: Exact Text To Apply table must include Where to edit, Baseline text, and Suggested replacement text columns")
        if behavior_heading not in table_window:
            failures.append(f"{rel}: Summary must include ### Baseline / Suggested Behavior after exact text")
        if behavior_table not in table_window:
            failures.append(f"{rel}: Summary must include Suggested change, Baseline / before description, Suggested / after description, and Result columns")
        if exact_heading in table_window and behavior_heading in table_window and table_window.find(exact_heading) > table_window.find(behavior_heading):
            failures.append(f"{rel}: Exact Text To Apply must appear before Baseline / Suggested Behavior")
        if exact_table in table_window and behavior_table in table_window and table_window.find(exact_table) > table_window.find(behavior_table):
            failures.append(f"{rel}: exact copy/paste table must appear before behavior summary table")
        if "Model coverage:" in table_window or "Evidence lane" in table_window:
            failures.append(f"{rel}: Summary tables must show target-owned value, not provider coverage")
        if "The target surface states" in table_window or "Baseline mistakes clustered" in table_window:
            failures.append(f"{rel}: Summary tables must show exact repo-owned before/after changes, not eval-summary filler")
        if "no wording change promoted" not in table_window.casefold() and "Suggested change" not in table_window:
            failures.append(f"{rel}: Summary table must show exact target-owned suggested changes before Why This Matters")
        if require_share_link:
            first_twelve = "\n".join(text.splitlines()[:12])
            if "## Summary" not in first_twelve:
                failures.append(f"{rel}: Summary table must be visible in the first 12 lines")
    if re.search(r"(?m)^## Suggested Change\s*$", text):
        failures.append(f"{rel}: move ## Suggested Change into the top Summary table or remove the duplicate section")
    if re.search(r"(?m)^## Evidence\s*$", text):
        failures.append(f"{rel}: use one founder-facing ## Evidence Bundle section, not a second ## Evidence section")

    cta_index = indexes.get("## Run This In Your Repo", -1)
    evidence_index = indexes.get("## Evidence Bundle", -1)
    for heading in ("## Result", "## What Failed", "## Additional Live Findings"):
        section_index = text.find(heading)
        if section_index == -1:
            continue
        if why_index != -1 and section_index > why_index:
            failures.append(f"{rel}: {heading} must appear before Why This Matters")
        if cta_index != -1 and section_index > cta_index:
            failures.append(f"{rel}: {heading} must appear before Run This In Your Repo")
        detail_index = text.find(LLM_SUMMARY)
        if detail_index != -1 and section_index > detail_index:
            failures.append(f"{rel}: {heading} must appear before LLM details")
    if cta_index != -1 and evidence_index != -1 and evidence_index < cta_index:
        failures.append(f"{rel}: Evidence Bundle must appear after Run This In Your Repo")

    if cta_index != -1:
        for marker in LOCAL_AGENT_CTA_MARKERS:
            if marker not in text[cta_index:]:
                failures.append(f"{rel}: missing local-agent CTA marker {marker}")
        early_evidence = [
            marker
            for marker in EVIDENCE_HEAVY_MARKERS
            if marker in text[:cta_index]
        ]
        if early_evidence:
            failures.append(f"{rel}: evidence-heavy links must appear after local-agent CTA")

    actions_index = indexes.get("## Recommended Actions", -1)
    if why_index != -1:
        why_end = actions_index if actions_index != -1 else why_index + 2000
        if "Value proposition:" not in text[why_index:why_end]:
            failures.append(f"{rel}: Why This Matters must include a value proposition")

    if actions_index != -1:
        actions_end = indexes.get("## Run This In Your Repo", -1)
        action_window = text[actions_index:actions_end if actions_end != -1 else actions_index + 3000]
        if any(provider in action_window for provider in ("### Anthropic", "### OpenAI", "### Google Gemini")):
            failures.append(f"{rel}: provider-specific action sections must not appear above target-owned actions")

    if "guardrail" in text.casefold() and "no upstream change is promoted" not in text.casefold():
        failures.append(f"{rel}: guardrail handoff must say no upstream change is promoted")
    if "0.000 gain" in text or "improved score from 1.000 to 1.000" in text:
        failures.append(f"{rel}: guardrail or no-delta copy must not be framed as a gain")

    detail_index = text.find(LLM_SUMMARY)
    if detail_index != -1:
        for heading, index in indexes.items():
            if index != -1 and index > detail_index:
                failures.append(f"{rel}: {heading} must appear before LLM details")
    if require_share_link and "Share link: [" not in "\n".join(text.splitlines()[:12]):
        failures.append(f"{rel}: share link must appear before founder-handoff sections")
    return failures


def _check_bundle_index(rel: Path, text: str) -> list[str]:
    failures: list[str] = []
    bundles_index = text.find("## Shareable Bundles")
    summary_index = text.find(LLM_SUMMARY)
    if bundles_index == -1:
        failures.append(f"{rel}: missing ## Shareable Bundles")
    if summary_index == -1:
        failures.append(f"{rel}: machine-heavy doc must end with LLM / Machine-readable details")
    elif bundles_index != -1 and bundles_index > summary_index:
        failures.append(f"{rel}: Shareable Bundles table must appear before LLM details")
    return failures


def _check_action_summary_doc(rel: Path, text: str) -> list[str]:
    failures: list[str] = []
    heading = "## Summary"
    index = text.find(heading)
    if index == -1:
        failures.append(f"{rel}: missing {heading}")
        return failures
    detail_index = text.find(LLM_SUMMARY)
    if detail_index != -1 and index > detail_index:
        failures.append(f"{rel}: {heading} must appear before LLM details")
    summary_window = text[index : index + 5000]
    if "Suggested change | Baseline / before description | Suggested / after description | Result" not in summary_window:
        failures.append(f"{rel}: action summary table must include Suggested change, Baseline / before description, Suggested / after description, and Result columns")
    if "Suggested change:" in summary_window:
        failures.append(f"{rel}: action summary table must use a Suggested change column, not Suggested change labels inside cells")
    if "No wording change promoted" not in summary_window and "Suggested change" not in summary_window:
        failures.append(f"{rel}: action summary table must show exact suggested changes or explicit no-change guardrails")
    return failures


def _check_supporting_evidence_note(
    rel: Path,
    text: str,
    *,
    start_markers: tuple[str, ...],
) -> list[str]:
    failures: list[str] = []
    first_lines = "\n".join(text.splitlines()[:24])
    if "supporting evidence" not in first_lines.casefold():
        failures.append(f"{rel}: supporting evidence doc must say so in the first 24 lines")
    if "Start with" not in first_lines:
        failures.append(f"{rel}: supporting evidence doc must point readers to the action-first doc")
    if not any(marker in first_lines for marker in start_markers):
        markers = ", ".join(start_markers)
        failures.append(f"{rel}: supporting evidence doc must name the action-first entrypoint ({markers})")
    return failures


def _check_machine_detail_placement(rel: Path, text: str) -> list[str]:
    failures: list[str] = []
    signals = _machine_detail_count(text)
    summary_index = text.find(LLM_SUMMARY)
    if _needs_llm_details(text, signals) and summary_index == -1:
        failures.append(f"{rel}: machine-heavy doc must end with LLM / Machine-readable details")
        return failures
    if summary_index != -1:
        before = text[:summary_index]
        before_for_count = _human_intro_before_required_evidence(before)
        if _machine_detail_count(before_for_count) >= HUMAN_INTRO_MACHINE_DETAIL_LIMIT:
            failures.append(f"{rel}: too much machine-readable detail appears before LLM disclosure")
        if len(before_for_count.splitlines()) > 140:
            failures.append(f"{rel}: human-facing content before LLM disclosure is too long")
    return failures


def _human_intro_before_required_evidence(text: str) -> str:
    evidence_index = text.find("## Evidence Bundle")
    cta_index = text.find("## Run This In Your Repo")
    if cta_index != -1 and evidence_index != -1 and cta_index < evidence_index:
        return text[:evidence_index]
    return text


def _needs_llm_details(text: str, signals: int) -> bool:
    lines = len(text.splitlines())
    return (lines >= 120 and signals >= 8) or signals >= 20


def _machine_detail_count(text: str) -> int:
    return len(MACHINE_DETAIL_RE.findall(text))


def _is_sendable_packet(rel: Path) -> bool:
    parts = rel.parts
    if len(parts) >= 4 and parts[0] == "docs" and parts[1] == "findings" and rel.name == "README.md":
        return True
    if len(parts) >= 4 and parts[0] == "evals" and parts[1] == "pr_packets" and rel.name == "README.md":
        return True
    return False


def _is_pr_body(rel: Path) -> bool:
    parts = rel.parts
    return len(parts) >= 4 and parts[0] == "evals" and parts[1] == "pr_packets" and rel.name == "PR_BODY.md"


def _is_pr_reproduction(rel: Path) -> bool:
    parts = rel.parts
    return len(parts) >= 4 and parts[0] == "evals" and parts[1] == "pr_packets" and rel.name == "REPRODUCTION.md"


def _is_bundle_index(rel: Path) -> bool:
    return rel.as_posix() == "docs/findings/README.md"


def _public_markdown_paths(root: Path = ROOT) -> list[Path]:
    paths: set[Path] = set()
    for pattern in PUBLIC_MARKDOWN_GLOBS:
        paths.update(path for path in root.glob(pattern) if path.is_file())
    return sorted(paths)


def _rel(path: Path, root: Path = ROOT) -> Path:
    try:
        return path.relative_to(root)
    except ValueError:
        return path


if __name__ == "__main__":
    raise SystemExit(main())
