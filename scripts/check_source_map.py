#!/usr/bin/env python3
"""Validate public source citations are retained in docs/source-map.md."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
SOURCE_MAP = Path("docs/source-map.md")
URL_RE = re.compile(r"https?://[^\s)<>,`]+")
CHECKED_RE = re.compile(r"^Checked on \d{4}-\d{2}-\d{2}\.$", flags=re.MULTILINE)
H2_RE = re.compile(r"^##\s+(.+)$", flags=re.MULTILINE)
FENCE_RE = re.compile(r"^```.*?$.*?^```$", flags=re.DOTALL | re.MULTILINE)
EXCLUDED_SOURCE_PREFIXES = (
    "https://github.com/cfregly/agent-harness-opt/",
    "https://img.shields.io/",
    "https://example.com/",
    "http://example.com/",
)
SECTIONS_WITHOUT_URLS = {"Local Screenshots"}


@dataclass(frozen=True)
class SourceUrl:
    path: Path
    url: str


def main() -> int:
    failures = check_source_map()
    if failures:
        print("\n".join(sorted(failures)))
        return 1
    print("source map check passed")
    return 0


def check_source_map(root: Path = ROOT) -> list[str]:
    path = root / SOURCE_MAP
    if not path.exists():
        return [f"{SOURCE_MAP}: missing"]

    text = path.read_text(encoding="utf-8")
    failures: list[str] = []
    if not text.startswith("# Source Map\n"):
        failures.append(f"{SOURCE_MAP}: first line must be '# Source Map'")
    if not CHECKED_RE.search(text):
        failures.append(f"{SOURCE_MAP}: missing Checked on YYYY-MM-DD line")
    failures.extend(_check_sections(path, text, root))
    failures.extend(_check_readme_sources(root))

    source_urls = _urls_in_text(text)
    if not source_urls:
        failures.append(f"{SOURCE_MAP}: no external source URLs found")
    for source in _external_public_doc_urls(root):
        if source.url not in source_urls:
            failures.append(f"{SOURCE_MAP}: missing source URL from {_rel(source.path, root)}: {source.url}")
    return failures


def _check_sections(path: Path, text: str, root: Path = ROOT) -> list[str]:
    failures: list[str] = []
    matches = list(H2_RE.finditer(text))
    if not matches:
        return [f"{_rel(path, root)}: missing source sections"]
    for index, match in enumerate(matches):
        title = match.group(1).strip()
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        body = text[start:end]
        if title not in SECTIONS_WITHOUT_URLS and not _urls_in_text(body):
            failures.append(f"{_rel(path, root)}: section {title!r} has no source URL")
    return failures


def _check_readme_sources(root: Path = ROOT) -> list[str]:
    path = root / "README.md"
    if not path.exists():
        return ["README.md: missing"]
    text = path.read_text(encoding="utf-8")
    failures: list[str] = []
    for required in ("docs/source-map.md", "docs/video-coverage-audit.md"):
        if required not in text:
            failures.append(f"README.md: Sources section missing {required}")
    return failures


def _external_public_doc_urls(root: Path = ROOT) -> list[SourceUrl]:
    urls: list[SourceUrl] = []
    for path in _public_doc_paths(root):
        if path == root / SOURCE_MAP:
            continue
        text = _strip_fenced_blocks(path.read_text(encoding="utf-8"))
        for url in _urls_in_text(text):
            if _is_external_source_url(url):
                urls.append(SourceUrl(path=path, url=url))
    return sorted(set(urls), key=lambda item: (item.path.as_posix(), item.url))


def _public_doc_paths(root: Path = ROOT) -> list[Path]:
    paths = [root / "README.md", *sorted((root / "docs").rglob("*.md"))]
    return [path for path in paths if path.exists()]


def _urls_in_text(text: str) -> set[str]:
    return {_normalize_url(match.group(0)) for match in URL_RE.finditer(text)}


def _normalize_url(url: str) -> str:
    return url.rstrip(".,")


def _is_external_source_url(url: str) -> bool:
    return not any(url.startswith(prefix) for prefix in EXCLUDED_SOURCE_PREFIXES)


def _strip_fenced_blocks(text: str) -> str:
    def replace(match: re.Match[str]) -> str:
        return "\n" * match.group(0).count("\n")

    return FENCE_RE.sub(replace, text)


def _rel(path: Path, root: Path = ROOT) -> Path:
    try:
        return path.relative_to(root)
    except ValueError:
        return path


if __name__ == "__main__":
    raise SystemExit(main())
