#!/usr/bin/env python3
"""Validate public Markdown links are shareable outside a local checkout."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_MARKDOWN_GLOBS = ("README.md", "docs/**/*.md")
ALLOWED_PREFIXES = ("https://", "http://", "#", "mailto:")
MARKDOWN_LINK_RE = re.compile(r"(!?)\[([^\]]*)\]\(([^)]*)\)")
WRAPPED_IMAGE_LINK_RE = re.compile(r"\[!\[[^\]]*\]\(([^)]*)\)\]\(([^)]*)\)")
REFERENCE_DEF_RE = re.compile(r"^\[([^\]]+)\]:\s*(\S+)", flags=re.MULTILINE)
REFERENCE_USE_RE = re.compile(r"(!?)\[([^\]]+)\]\[([^\]]*)\]")
FENCE_RE = re.compile(r"^```.*?$.*?^```$", flags=re.DOTALL | re.MULTILINE)


@dataclass(frozen=True)
class Link:
    path: Path
    line: int
    raw_target: str
    is_image: bool


def main() -> int:
    failures = check_public_links()
    if failures:
        print("\n".join(sorted(failures)))
        return 1
    print("public link check passed")
    return 0


def check_public_links(root: Path = ROOT) -> list[str]:
    failures: list[str] = []
    for link in _iter_links(root):
        rel = _rel(link.path, root)
        target = _target_url(link.raw_target)
        label = "image target" if link.is_image else "link target"
        if not target:
            failures.append(f"{rel}:{link.line}: empty {label}")
            continue
        if not target.startswith(ALLOWED_PREFIXES):
            failures.append(f"{rel}:{link.line}: local {label} is not shareable: {target}")
    return failures


def _iter_links(root: Path = ROOT) -> list[Link]:
    links: list[Link] = []
    for path in _public_markdown_paths(root):
        text = _strip_fenced_blocks(path.read_text(encoding="utf-8"))
        references = {
            _reference_key(match.group(1)): match.group(2).strip()
            for match in REFERENCE_DEF_RE.finditer(text)
        }
        for match in REFERENCE_USE_RE.finditer(text):
            label = match.group(3).strip() or match.group(2).strip()
            links.append(
                Link(
                    path=path,
                    line=text.count("\n", 0, match.start()) + 1,
                    raw_target=references.get(_reference_key(label), ""),
                    is_image=bool(match.group(1)),
                )
            )
        for match in WRAPPED_IMAGE_LINK_RE.finditer(text):
            links.append(
                Link(
                    path=path,
                    line=text.count("\n", 0, match.start()) + 1,
                    raw_target=match.group(1).strip(),
                    is_image=True,
                )
            )
            links.append(
                Link(
                    path=path,
                    line=text.count("\n", 0, match.start()) + 1,
                    raw_target=match.group(2).strip(),
                    is_image=False,
                )
            )
        for match in MARKDOWN_LINK_RE.finditer(text):
            links.append(
                Link(
                    path=path,
                    line=text.count("\n", 0, match.start()) + 1,
                    raw_target=match.group(3).strip(),
                    is_image=bool(match.group(1)),
                )
            )
    return links


def _public_markdown_paths(root: Path = ROOT) -> list[Path]:
    paths: set[Path] = set()
    for pattern in PUBLIC_MARKDOWN_GLOBS:
        paths.update(path for path in root.glob(pattern) if path.is_file())
    return sorted(paths)


def _strip_fenced_blocks(text: str) -> str:
    def replace(match: re.Match[str]) -> str:
        return "\n" * match.group(0).count("\n")

    return FENCE_RE.sub(replace, text)


def _target_url(raw_target: str) -> str:
    if not raw_target:
        return ""
    if raw_target.startswith("<") and ">" in raw_target:
        return raw_target[1 : raw_target.index(">")].strip()
    return raw_target.split(maxsplit=1)[0].strip()


def _reference_key(label: str) -> str:
    return " ".join(label.casefold().split())


def _rel(path: Path, root: Path = ROOT) -> Path:
    try:
        return path.relative_to(root)
    except ValueError:
        return path


if __name__ == "__main__":
    raise SystemExit(main())
