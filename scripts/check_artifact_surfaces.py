#!/usr/bin/env python3
"""Validate tracked non-code artifacts that support public docs."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import shlex


ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
DEMO_GIF = "demo.gif"
DEMO_TAPE = "demo.tape"
MIN_DEMO_GIF_BYTES = 50_000
MIN_DEMO_FRAMES = 5


@dataclass(frozen=True)
class GifInfo:
    width: int
    height: int
    frames: int


def main() -> int:
    failures = check_artifact_surfaces()
    if failures:
        print("\n".join(sorted(failures)))
        return 1
    print("artifact surface check passed")
    return 0


def check_artifact_surfaces(root: Path = ROOT) -> list[str]:
    failures: list[str] = []
    failures.extend(_check_demo_assets(root))
    failures.extend(_check_result_receipt_reachability(root))
    return failures


def _check_demo_assets(root: Path = ROOT) -> list[str]:
    failures: list[str] = []
    readme = (root / "README.md").read_text(encoding="utf-8") if (root / "README.md").exists() else ""
    tape_path = root / DEMO_TAPE
    gif_path = root / DEMO_GIF

    if DEMO_GIF not in readme:
        failures.append(f"README.md: missing public reference to {DEMO_GIF}")
    missing_required_file = False
    if not tape_path.is_file():
        failures.append(f"{DEMO_TAPE}: missing")
        missing_required_file = True
    if not gif_path.is_file():
        failures.append(f"{DEMO_GIF}: missing")
        missing_required_file = True
    if missing_required_file:
        return failures

    tape = tape_path.read_text(encoding="utf-8")
    if f"Output {DEMO_GIF}" not in tape:
        failures.append(f"{DEMO_TAPE}: missing Output {DEMO_GIF}")
    if "vhs demo.tape" not in tape:
        failures.append(f"{DEMO_TAPE}: missing regeneration command")

    gif_size = gif_path.stat().st_size
    if gif_size < MIN_DEMO_GIF_BYTES:
        failures.append(f"{DEMO_GIF}: too small to be a useful demo artifact")

    try:
        gif = _parse_gif(gif_path)
    except ValueError as exc:
        failures.append(f"{DEMO_GIF}: {exc}")
        return failures

    if gif.frames < MIN_DEMO_FRAMES:
        failures.append(f"{DEMO_GIF}: expected at least {MIN_DEMO_FRAMES} frames")

    tape_width = _extract_tape_int(tape, "Width")
    tape_height = _extract_tape_int(tape, "Height")
    if tape_width != gif.width:
        failures.append(f"{DEMO_TAPE}: Set Width {tape_width} does not match {DEMO_GIF} width {gif.width}")
    if tape_height != gif.height:
        failures.append(f"{DEMO_TAPE}: Set Height {tape_height} does not match {DEMO_GIF} height {gif.height}")

    for local_path in _local_paths_referenced_by_tape(tape):
        if not (root / local_path).exists():
            failures.append(f"{DEMO_TAPE}: referenced path missing: {local_path}")

    return failures


def _parse_gif(path: Path) -> GifInfo:
    data = path.read_bytes()
    if len(data) < 14:
        raise ValueError("file is too short")
    if data[:6] not in {b"GIF87a", b"GIF89a"}:
        raise ValueError("missing GIF header")
    width = int.from_bytes(data[6:8], "little")
    height = int.from_bytes(data[8:10], "little")
    packed = data[10]
    index = 13
    if packed & 0x80:
        index += 3 * (2 ** ((packed & 0x07) + 1))

    frames = 0
    while index < len(data):
        marker = data[index]
        index += 1
        if marker == 0x3B:
            return GifInfo(width=width, height=height, frames=frames)
        if marker == 0x21:
            index += 1
            index = _skip_sub_blocks(data, index)
            continue
        if marker == 0x2C:
            frames += 1
            if index + 9 > len(data):
                raise ValueError("truncated image descriptor")
            local_packed = data[index + 8]
            index += 9
            if local_packed & 0x80:
                index += 3 * (2 ** ((local_packed & 0x07) + 1))
            index += 1
            index = _skip_sub_blocks(data, index)
            continue
        raise ValueError(f"unexpected GIF marker 0x{marker:02x}")

    raise ValueError("missing GIF trailer")


def _skip_sub_blocks(data: bytes, index: int) -> int:
    while index < len(data):
        size = data[index]
        index += 1
        if size == 0:
            return index
        index += size
    raise ValueError("truncated GIF sub-block")


def _extract_tape_int(tape: str, name: str) -> int | None:
    match = re.search(rf"^Set {re.escape(name)}\s+(\d+)\s*$", tape, flags=re.MULTILINE)
    return int(match.group(1)) if match else None


def _local_paths_referenced_by_tape(tape: str) -> set[str]:
    paths: set[str] = set()
    for match in re.finditer(r'^Type\s+"(.+)"\s*$', tape, flags=re.MULTILINE):
        try:
            tokens = shlex.split(match.group(1))
        except ValueError:
            tokens = match.group(1).split()
        for token in tokens:
            if token.startswith(("docs/", "evals/", "recipes/", "prompts/", "scripts/")):
                paths.add(token)
    return paths


def _check_result_receipt_reachability(root: Path = ROOT) -> list[str]:
    results_dir = root / "evals" / "results"
    if not results_dir.exists():
        return []
    public_text = _public_reference_text(root)
    failures: list[str] = []
    for path in sorted(results_dir.iterdir()):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        if rel in public_text or path.name in public_text:
            continue
        if path.suffix == ".json" and (path.with_suffix(".md").name in public_text):
            continue
        failures.append(f"{rel}: result artifact is not referenced by README/docs/PR packet text")
    return failures


def _public_reference_text(root: Path = ROOT) -> str:
    paths = [
        root / "README.md",
        *sorted((root / "docs").rglob("*.md")),
        *sorted((root / "evals" / "pr_packets").rglob("*.md")),
    ]
    return "\n".join(path.read_text(encoding="utf-8") for path in paths if path.exists())


if __name__ == "__main__":
    raise SystemExit(main())
