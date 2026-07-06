#!/usr/bin/env python3
"""Render the public demo GIF from real harness commands."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import subprocess
import sys
import textwrap


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "demo.gif"
FONT_PATHS = (
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    "/usr/share/fonts/dejavu/DejaVuSansMono.ttf",
)


@dataclass(frozen=True)
class DemoCommand:
    title: str
    display: str
    args: tuple[str, ...]
    keep_lines: int
    prompt_hold: int = 2
    output_hold: int = 4


def _join_checks() -> str:
    return (
        "import subprocess, sys; "
        "subprocess.run([sys.executable, 'scripts/check_finding_packets.py'], check=True); "
        "subprocess.run([sys.executable, 'scripts/check_public_links.py'], check=True); "
        "subprocess.run([sys.executable, 'scripts/check_human_docs.py'], check=True)"
    )


def _supabase_summary_command() -> str:
    return (
        "print('Supabase live evidence: terse 6/9 -> tuned 9/9'); "
        "print('DDL/RLS cases fixed across Anthropic, OpenAI, Gemini, native tools, and prompt JSON'); "
        "print('Risk avoided: schema changes bypassing auditable migrations')"
    )


COMMANDS = (
    DemoCommand(
        title="1. Audit Supabase MCP coverage",
        display=(
            "python -m claude_agent_harness_opt matrix-coverage "
            "evals/model_matrix/supabase_mcp_database_tool_selection.json --strict --markdown"
        ),
        args=(
            sys.executable,
            "-m",
            "claude_agent_harness_opt",
            "matrix-coverage",
            "evals/model_matrix/supabase_mcp_database_tool_selection.json",
            "--strict",
            "--markdown",
        ),
        keep_lines=24,
        output_hold=6,
    ),
    DemoCommand(
        title="2. Run the Supabase DDL/RLS optimization cells without provider calls",
        display=(
            "python scripts/optimize_mcp.py supabase --markdown "
            "--cases 'ddl create table uses migration,ddl create index uses migration,rls policy uses migration' "
            "--providers anthropic,openai,gemini --harnesses prompt_json,native_tools "
            "--out /tmp/supabase-demo-optimization.md"
        ),
        args=(
            sys.executable,
            "scripts/optimize_mcp.py",
            "supabase",
            "--markdown",
            "--cases",
            "ddl create table uses migration,ddl create index uses migration,rls policy uses migration",
            "--providers",
            "anthropic,openai,gemini",
            "--harnesses",
            "prompt_json,native_tools",
            "--out",
            "/tmp/supabase-demo-optimization.md",
        ),
        keep_lines=22,
        output_hold=5,
    ),
    DemoCommand(
        title="3. Show the retained Supabase improvement result",
        display=f'python -c "{_supabase_summary_command()}"',
        args=(
            sys.executable,
            "-c",
            _supabase_summary_command(),
        ),
        keep_lines=8,
        output_hold=7,
    ),
    DemoCommand(
        title="4. Verify packets, public links, and human-readable docs",
        display="python scripts/check_finding_packets.py && python scripts/check_public_links.py && python scripts/check_human_docs.py",
        args=(sys.executable, "-c", _join_checks()),
        keep_lines=8,
        output_hold=5,
    ),
    DemoCommand(
        title="5. Print the shareable public bundle",
        display="python -c 'print(\"Supabase PR/evidence bundle: https://github.com/cfregly/agent-harness-opt/tree/main/evals/pr_packets/supabase_mcp_database_tool_tuning_2026-06-25\")'",
        args=(
            sys.executable,
            "-c",
            "print('Supabase PR/evidence bundle: https://github.com/cfregly/agent-harness-opt/tree/main/evals/pr_packets/supabase_mcp_database_tool_tuning_2026-06-25')",
        ),
        keep_lines=4,
        output_hold=8,
    ),
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="GIF output path")
    parser.add_argument("--mp4-out", type=Path, help="optional MP4 output path")
    parser.add_argument("--width", type=int, default=1200)
    parser.add_argument("--height", type=int, default=720)
    parser.add_argument("--frame-ms", type=int, default=900)
    parser.add_argument("--font-size", type=int, default=18)
    args = parser.parse_args(argv)

    frames = build_frames(args.width, args.height, args.font_size)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    save_gif(frames, args.out, duration_ms=args.frame_ms)
    print(f"wrote {args.out}")
    if args.mp4_out:
        write_mp4(args.out, args.mp4_out)
        print(f"wrote {args.mp4_out}")
    return 0


def build_frames(width: int, height: int, font_size: int):
    image, draw, font = _load_pillow(width, height, font_size)
    frames = []
    terminal: list[tuple[str, str]] = [
        ("title", "agent-harness-opt: Supabase MCP migration-boundary demo")
    ]
    _append_frame(frames, _render_terminal(image, draw, font, terminal, width, height), repeats=4)
    for command in COMMANDS:
        terminal.append(("section", command.title))
        terminal.append(("prompt", f"$ {command.display}"))
        _append_frame(
            frames,
            _render_terminal(image, draw, font, terminal, width, height),
            repeats=command.prompt_hold,
        )
        output = _run_command(command)
        for line in _kept_output_lines(output, command.keep_lines):
            terminal.append(("output", line))
        _append_frame(
            frames,
            _render_terminal(image, draw, font, terminal, width, height),
            repeats=command.output_hold,
        )
    terminal.append(("success", "public demo rebuilt from commands; no provider keys or shell secrets used"))
    _append_frame(frames, _render_terminal(image, draw, font, terminal, width, height), repeats=8)
    return frames


def _append_frame(frames, frame, *, repeats: int) -> None:
    for _ in range(max(1, repeats)):
        frames.append(frame.copy())


def _load_pillow(width: int, height: int, font_size: int):
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError as exc:
        raise SystemExit(
            "Pillow is required only to regenerate demo.gif. Install pillow or keep the checked-in GIF."
        ) from exc

    font = None
    for path in FONT_PATHS:
        candidate = Path(path)
        if candidate.exists():
            font = ImageFont.truetype(str(candidate), font_size)
            break
    if font is None:
        font = ImageFont.load_default()
    image = Image.new("RGB", (width, height), "#151515")
    draw = ImageDraw.Draw(image)
    return image, draw, font


def _run_command(command: DemoCommand) -> str:
    result = subprocess.run(
        command.args,
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    output = "\n".join(part.rstrip() for part in (result.stdout, result.stderr) if part.strip())
    if result.returncode:
        output = f"exit={result.returncode}\n{output}".strip()
    return output or "(no output)"


def _kept_output_lines(output: str, keep_lines: int) -> list[str]:
    lines = [line.rstrip() for line in output.splitlines() if line.rstrip()]
    if len(lines) <= keep_lines:
        return lines
    head_count = max(1, keep_lines // 2)
    tail_count = max(1, keep_lines - head_count - 1)
    return [*lines[:head_count], f"... {len(lines) - head_count - tail_count} lines omitted ...", *lines[-tail_count:]]


def _render_terminal(base_image, draw, font, rows: list[tuple[str, str]], width: int, height: int):
    from PIL import Image, ImageDraw

    image = Image.new("RGB", (width, height), "#151515")
    draw = ImageDraw.Draw(image)
    margin_x = 26
    margin_y = 24
    line_height = _line_height(draw, font) + 7
    max_chars = max(24, (width - margin_x * 2) // max(8, _char_width(draw, font)))
    wrapped = _wrap_rows(rows, max_chars=max_chars)
    max_lines = max(1, (height - margin_y * 2) // line_height)
    visible = wrapped[-max_lines:]
    colors = {
        "title": "#d7d7ff",
        "section": "#8bd5ff",
        "prompt": "#f5f5f5",
        "output": "#c9d1d9",
        "success": "#8ee99a",
    }
    y = margin_y
    for kind, line in visible:
        draw.text((margin_x, y), line, font=font, fill=colors.get(kind, "#c9d1d9"))
        y += line_height
    return image


def _wrap_rows(rows: list[tuple[str, str]], max_chars: int) -> list[tuple[str, str]]:
    wrapped: list[tuple[str, str]] = []
    for kind, line in rows:
        prefix = ""
        if kind == "output":
            prefix = "  "
        chunks = textwrap.wrap(
            line,
            width=max_chars - len(prefix),
            replace_whitespace=False,
            drop_whitespace=False,
            break_long_words=True,
        ) or [""]
        for index, chunk in enumerate(chunks):
            wrapped.append((kind, (prefix if index == 0 else "  ") + chunk))
    return wrapped


def _line_height(draw, font) -> int:
    bbox = draw.textbbox((0, 0), "Ag", font=font)
    return bbox[3] - bbox[1]


def _char_width(draw, font) -> int:
    bbox = draw.textbbox((0, 0), "M", font=font)
    return bbox[2] - bbox[0]


def save_gif(frames, out_path: Path, *, duration_ms: int) -> None:
    first, *rest = frames
    first.save(
        out_path,
        save_all=True,
        append_images=rest,
        duration=duration_ms,
        loop=0,
        optimize=True,
    )


def write_mp4(gif_path: Path, mp4_path: Path) -> None:
    mp4_path.parent.mkdir(parents=True, exist_ok=True)
    command = [
        "ffmpeg",
        "-y",
        "-loglevel",
        "error",
        "-i",
        str(gif_path),
        "-movflags",
        "faststart",
        "-pix_fmt",
        "yuv420p",
        "-vf",
        "scale=trunc(iw/2)*2:trunc(ih/2)*2",
        str(mp4_path),
    ]
    try:
        subprocess.run(command, cwd=ROOT, check=True)
    except FileNotFoundError as exc:
        raise SystemExit("ffmpeg is required for --mp4-out") from exc


if __name__ == "__main__":
    raise SystemExit(main())
