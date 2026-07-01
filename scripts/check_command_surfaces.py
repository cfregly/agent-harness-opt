#!/usr/bin/env python3
"""Validate CLI, CI, and documented command surfaces stay in sync."""

from __future__ import annotations

import ast
import contextlib
from dataclasses import dataclass
from dataclasses import field
import io
from pathlib import Path
import re
import shlex
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
CI_WORKFLOW = ROOT / ".github" / "workflows" / "ci.yml"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from claude_agent_harness_opt.cli import build_parser  # noqa: E402

CLI_COMMAND_RE = re.compile(r"python\s+-m\s+claude_agent_harness_opt\s+([a-z0-9][a-z0-9-]*)")
SCRIPT_COMMAND_RE = re.compile(r"python\s+(scripts/[A-Za-z0-9_./-]+\.py)")
HELP_COMMANDS_RE = re.compile(r"\{([^}]+)\}")

DOC_COMMAND_PATHS = (
    ROOT / "README.md",
    ROOT / "CLAUDE.md",
    ROOT / "AGENTS.md",
    ROOT / ".github" / "workflows" / "ci.yml",
    ROOT / ".claude" / "skills",
    ROOT / "docs",
    ROOT / "evals" / "pr_packets",
)

PATH_SUFFIXES = (
    ".html",
    ".json",
    ".jsonl",
    ".md",
    ".py",
    ".txt",
    ".yaml",
    ".yml",
)

SKIP_PATH_PREFIXES = (
    "/dev/",
    "/tmp/",
    "http://",
    "https://",
    "path/to/",
)

SKIP_PATH_VALUES = {
    ".env",
    "-",
}


@dataclass(frozen=True)
class Invocation:
    source: Path
    line: int
    raw: str
    command: str
    tokens: tuple[str, ...]


@dataclass(frozen=True)
class ScriptContract:
    options: frozenset[str]
    required_options: frozenset[str]
    required_positionals: int
    value_options: frozenset[str] = frozenset()
    option_choices: dict[str, frozenset[str]] = field(default_factory=dict)
    option_types: dict[str, str] = field(default_factory=dict)
    positional_choices: tuple[frozenset[str], ...] = ()
    positional_types: tuple[str, ...] = ()


def main() -> int:
    failures = check_command_surfaces()
    if failures:
        print("\n".join(sorted(failures)))
        return 1
    print("command surface check passed")
    return 0


def check_command_surfaces(
    root: Path = ROOT,
    cli_commands: set[str] | None = None,
    cli_options: dict[str, set[str]] | None = None,
    script_options: dict[str, set[str] | ScriptContract] | None = None,
) -> list[str]:
    failures: list[str] = []
    commands = cli_commands or _load_cli_commands(root)
    options = (
        cli_options
        if cli_options is not None
        else _load_cli_options(root, commands)
        if cli_commands is None
        else {command: set() for command in commands}
    )
    helper_contracts = (
        _normalize_script_contracts(script_options)
        if script_options is not None
        else _load_script_contracts(root)
    )
    readme = (root / "README.md").read_text(encoding="utf-8") if (root / "README.md").exists() else ""
    ci = (
        (root / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
        if (root / ".github" / "workflows" / "ci.yml").exists()
        else ""
    )

    failures.extend(_check_gate_scripts(root, readme, ci))

    invocations = _collect_invocations(root)
    failures.extend(_check_cli_invocations(root, invocations, commands, options))
    if cli_commands is None:
        failures.extend(_check_cli_parse_contract(invocations))
    failures.extend(_check_cli_command_documentation(commands, invocations))
    failures.extend(_check_script_invocations(root, _collect_script_invocations(root), helper_contracts))
    return failures


def _load_cli_commands(root: Path = ROOT) -> set[str]:
    result = subprocess.run(
        [sys.executable, "-m", "claude_agent_harness_opt", "--help"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    match = HELP_COMMANDS_RE.search(result.stdout)
    if not match:
        raise RuntimeError("could not parse CLI command list from --help")
    return {command.strip() for command in match.group(1).split(",") if command.strip()}


def _load_cli_options(root: Path, commands: set[str]) -> dict[str, set[str]]:
    return {command: _load_command_options(root, command) for command in commands}


def _load_command_options(root: Path, command: str) -> set[str]:
    result = subprocess.run(
        [sys.executable, "-m", "claude_agent_harness_opt", command, "--help"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    return set(re.findall(r"(?<![\w-])--[a-z0-9][a-z0-9-]*", result.stdout))


def _load_script_options(root: Path) -> dict[str, set[str]]:
    return {
        script: set(contract.options)
        for script, contract in _load_script_contracts(root).items()
    }


def _load_script_contracts(root: Path) -> dict[str, ScriptContract]:
    contracts: dict[str, ScriptContract] = {}
    for path in sorted((root / "scripts").glob("*.py")):
        rel = path.relative_to(root).as_posix()
        contracts[rel] = _extract_script_contract(path)
    return contracts


def _extract_script_options(path: Path) -> set[str]:
    return set(_extract_script_contract(path).options)


def _extract_script_contract(path: Path) -> ScriptContract:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except SyntaxError:
        return ScriptContract(frozenset(), frozenset(), 0, frozenset())
    options: set[str] = set()
    required_options: set[str] = set()
    required_positionals = 0
    value_options: set[str] = set()
    option_choices: dict[str, frozenset[str]] = {}
    option_types: dict[str, str] = {}
    positional_choices: list[frozenset[str]] = []
    positional_types: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if not isinstance(node.func, ast.Attribute) or node.func.attr != "add_argument":
            continue
        arg_strings = [
            arg.value
            for arg in node.args
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str)
        ]
        if not arg_strings:
            continue
        option_strings = [value for value in arg_strings if value.startswith("-")]
        long_options = [
            value
            for value in option_strings
            if re.fullmatch(r"--[a-z0-9][a-z0-9-]*", value)
        ]
        for arg in node.args:
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                if re.fullmatch(r"--[a-z0-9][a-z0-9-]*", arg.value):
                    options.add(arg.value)
        if long_options and _option_consumes_value(node):
            value_options.update(long_options)
        choices = _keyword_choices(node, "choices")
        if long_options and choices:
            for option in long_options:
                option_choices[option] = choices
        value_type = _keyword_type(node, "type")
        if long_options and value_type:
            for option in long_options:
                option_types[option] = value_type
        if long_options and _keyword_bool(node, "required"):
            required_options.update(long_options)
        if not option_strings:
            if choices:
                positional_choices.append(choices)
            else:
                positional_choices.append(frozenset())
            positional_types.append(value_type or "")
            if _positional_is_required(node):
                required_positionals += 1
    return ScriptContract(
        frozenset(options),
        frozenset(required_options),
        required_positionals,
        frozenset(value_options),
        option_choices,
        option_types,
        tuple(positional_choices),
        tuple(positional_types),
    )


def _normalize_script_contracts(
    raw_contracts: dict[str, set[str] | ScriptContract],
) -> dict[str, ScriptContract]:
    contracts: dict[str, ScriptContract] = {}
    for script, contract in raw_contracts.items():
        if isinstance(contract, ScriptContract):
            contracts[script] = contract
            continue
        contracts[script] = ScriptContract(frozenset(contract), frozenset(), 0, frozenset(contract))
    return contracts


def _keyword_bool(node: ast.Call, name: str) -> bool:
    for keyword in node.keywords:
        if keyword.arg == name and isinstance(keyword.value, ast.Constant):
            return bool(keyword.value.value)
    return False


def _keyword_string(node: ast.Call, name: str) -> str | None:
    for keyword in node.keywords:
        if keyword.arg == name and isinstance(keyword.value, ast.Constant):
            value = keyword.value.value
            return value if isinstance(value, str) else None
    return None


def _keyword_value(node: ast.Call, name: str) -> object:
    for keyword in node.keywords:
        if keyword.arg == name and isinstance(keyword.value, ast.Constant):
            return keyword.value.value
    return None


def _keyword_choices(node: ast.Call, name: str) -> frozenset[str]:
    for keyword in node.keywords:
        if keyword.arg != name:
            continue
        value = keyword.value
        if isinstance(value, (ast.List, ast.Set, ast.Tuple)):
            choices = [
                item.value
                for item in value.elts
                if isinstance(item, ast.Constant) and isinstance(item.value, str)
            ]
            return frozenset(choices)
    return frozenset()


def _keyword_type(node: ast.Call, name: str) -> str:
    for keyword in node.keywords:
        if keyword.arg != name:
            continue
        value = keyword.value
        if isinstance(value, ast.Name) and value.id in {"float", "int", "str"}:
            return value.id
    return ""


def _positional_is_required(node: ast.Call) -> bool:
    nargs = _keyword_string(node, "nargs")
    return nargs not in {"?", "*"}


def _option_consumes_value(node: ast.Call) -> bool:
    action = _keyword_string(node, "action")
    if action in {"append_const", "count", "help", "store_const", "store_false", "store_true", "version"}:
        return False
    nargs = _keyword_value(node, "nargs")
    return nargs != 0


def _check_gate_scripts(root: Path, readme: str, ci: str) -> list[str]:
    failures: list[str] = []
    gate_scripts = [
        *sorted((root / "scripts").glob("check_*.py")),
        root / "scripts" / "deslop_check.py",
    ]
    existing_gate_scripts = [path for path in gate_scripts if path.exists()]
    if not existing_gate_scripts:
        return ["scripts: no check gate scripts found"]

    for path in existing_gate_scripts:
        rel = path.relative_to(root).as_posix()
        command = f"python {rel}"
        if command not in ci:
            failures.append(f"{rel}: missing from .github/workflows/ci.yml")
        if command not in readme:
            failures.append(f"{rel}: missing from README Verify it commands")
        if path.name.startswith("check_"):
            test_path = root / "tests" / f"test_{path.stem}_script.py"
            if not test_path.exists():
                failures.append(f"{rel}: missing test file {test_path.relative_to(root)}")
    return failures


def _collect_invocations(root: Path = ROOT) -> list[Invocation]:
    invocations: list[Invocation] = []
    for path in _command_surface_files(root):
        text = path.read_text(encoding="utf-8")
        invocations.extend(_extract_cli_invocations(path, text))
    return invocations


def _collect_script_invocations(root: Path = ROOT) -> list[Invocation]:
    invocations: list[Invocation] = []
    for path in _command_surface_files(root):
        text = path.read_text(encoding="utf-8")
        invocations.extend(_extract_script_invocations(path, text))
    return invocations


def _command_surface_files(root: Path = ROOT) -> list[Path]:
    paths: list[Path] = []
    for source in DOC_COMMAND_PATHS:
        path = root / source.relative_to(ROOT) if source.is_absolute() else root / source
        if not path.exists():
            continue
        if path.is_file():
            paths.append(path)
        else:
            paths.extend(sorted(path.rglob("*.md")))
            paths.extend(sorted(path.rglob("*.yml")))
            paths.extend(sorted(path.rglob("*.yaml")))
    return sorted(set(paths))


def _extract_cli_invocations(source: Path, text: str) -> list[Invocation]:
    normalized = re.sub(r"\\\n\s*", " ", text)
    invocations: list[Invocation] = []
    for line_number, line in enumerate(normalized.splitlines(), start=1):
        if "python -m claude_agent_harness_opt" not in line:
            continue
        for match in CLI_COMMAND_RE.finditer(line):
            raw = line[match.start() :].strip()
            command = match.group(1)
            tokens = _safe_split(raw)
            invocations.append(
                Invocation(
                    source=source,
                    line=line_number,
                    raw=raw,
                    command=command,
                    tokens=tuple(tokens),
                )
            )
    return invocations


def _extract_script_invocations(source: Path, text: str) -> list[Invocation]:
    normalized = re.sub(r"\\\n\s*", " ", text)
    invocations: list[Invocation] = []
    for line_number, line in enumerate(normalized.splitlines(), start=1):
        if "python scripts/" not in line:
            continue
        for match in SCRIPT_COMMAND_RE.finditer(line):
            raw = line[match.start() :].strip()
            script = match.group(1)
            tokens = _safe_split(raw)
            invocations.append(
                Invocation(
                    source=source,
                    line=line_number,
                    raw=raw,
                    command=script,
                    tokens=tuple(tokens),
                )
            )
    return invocations


def _safe_split(raw: str) -> list[str]:
    command_text = raw
    if "`" in command_text:
        command_text = command_text.split("`", 1)[0]
    for separator in (" || ", " && ", "; then", "; fi"):
        command_text = command_text.split(separator, 1)[0]
    try:
        return shlex.split(command_text)
    except ValueError:
        return command_text.split()


def _check_cli_invocations(
    root: Path,
    invocations: list[Invocation],
    commands: set[str],
    options: dict[str, set[str]],
) -> list[str]:
    failures: list[str] = []
    for invocation in invocations:
        prefix = f"{_rel(invocation.source, root)}:{invocation.line}"
        if invocation.command not in commands:
            failures.append(f"{prefix}: unknown CLI command {invocation.command!r}")
        failures.extend(_check_cli_options(prefix, invocation, options.get(invocation.command, set())))
        failures.extend(_check_invocation_paths(root, invocation, prefix, argument_start=4))
    return failures


def _check_cli_options(prefix: str, invocation: Invocation, known_options: set[str]) -> list[str]:
    return _check_known_options(
        prefix,
        invocation,
        known_options,
        label=f"CLI command {invocation.command!r}",
        argument_start=4,
    )


def _check_cli_parse_contract(invocations: list[Invocation]) -> list[str]:
    parser = build_parser()
    failures: list[str] = []
    for invocation in invocations:
        if _is_inline_reference(invocation.raw):
            continue
        prefix = f"{_rel(invocation.source)}:{invocation.line}"
        args = _parse_only_args(invocation.tokens, argument_start=3)
        try:
            with contextlib.redirect_stderr(io.StringIO()):
                parser.parse_args(args)
        except SystemExit as exc:
            failures.append(
                f"{prefix}: documented CLI invocation does not parse: "
                f"{invocation.raw!r} exited with {exc.code}"
            )
    return failures


def _is_inline_reference(raw: str) -> bool:
    return "`" in raw


def _parse_only_args(tokens: tuple[str, ...], *, argument_start: int) -> list[str]:
    args: list[str] = []
    for token in tokens[argument_start:]:
        if token in {">", "1>", "2>", "|"}:
            break
        args.append(token)
    return args


def _check_known_options(
    prefix: str,
    invocation: Invocation,
    known_options: set[str],
    *,
    label: str,
    argument_start: int,
) -> list[str]:
    failures: list[str] = []
    for token in invocation.tokens[argument_start:]:
        if token == "--":
            break
        if not token.startswith("--"):
            continue
        option = token.split("=", 1)[0]
        if option not in known_options:
            failures.append(f"{prefix}: {label} has unknown option {option!r}")
    return failures


def _check_script_invocations(
    root: Path,
    invocations: list[Invocation],
    script_contracts: dict[str, ScriptContract],
) -> list[str]:
    failures: list[str] = []
    for invocation in invocations:
        prefix = f"{_rel(invocation.source, root)}:{invocation.line}"
        script_path = root / invocation.command
        if not script_path.is_file():
            failures.append(f"{prefix}: documented script missing: {invocation.command}")
        else:
            contract = script_contracts.get(
                invocation.command,
                ScriptContract(frozenset(), frozenset(), 0, frozenset()),
            )
            failures.extend(
                _check_known_options(
                    prefix,
                    invocation,
                    set(contract.options),
                    label=f"script {invocation.command!r}",
                    argument_start=2,
                )
            )
            failures.extend(_check_script_required_args(prefix, invocation, contract))
            failures.extend(_check_script_value_types(prefix, invocation, contract))
            failures.extend(_check_script_choices(prefix, invocation, contract))
        failures.extend(_check_invocation_paths(root, invocation, prefix, argument_start=2))
    return failures


def _check_script_required_args(
    prefix: str,
    invocation: Invocation,
    contract: ScriptContract,
) -> list[str]:
    failures: list[str] = []
    present_options = _present_long_options(invocation.tokens, argument_start=2)
    missing_options = sorted(set(contract.required_options) - present_options)
    for option in missing_options:
        failures.append(f"{prefix}: script {invocation.command!r} missing required option {option!r}")

    positional_count = len(
        _present_positionals(
            invocation.tokens,
            argument_start=2,
            value_options=set(contract.value_options),
        )
    )
    if positional_count < contract.required_positionals:
        failures.append(
            f"{prefix}: script {invocation.command!r} has {positional_count} positional "
            f"argument(s), expected at least {contract.required_positionals}"
        )
    return failures


def _check_script_value_types(
    prefix: str,
    invocation: Invocation,
    contract: ScriptContract,
) -> list[str]:
    failures: list[str] = []
    option_values = _present_option_values(
        invocation.tokens,
        argument_start=2,
        value_options=set(contract.value_options),
    )
    for option, type_name in contract.option_types.items():
        if option not in option_values:
            continue
        value = option_values[option]
        if not _value_matches_type(value, type_name):
            failures.append(
                f"{prefix}: script {invocation.command!r} option {option!r} "
                f"expects {type_name}, got {value!r}"
            )

    positionals = _present_positionals(
        invocation.tokens,
        argument_start=2,
        value_options=set(contract.value_options),
    )
    for index, type_name in enumerate(contract.positional_types):
        if not type_name or index >= len(positionals):
            continue
        value = positionals[index]
        if not _value_matches_type(value, type_name):
            failures.append(
                f"{prefix}: script {invocation.command!r} positional {index + 1} "
                f"expects {type_name}, got {value!r}"
            )
    return failures


def _check_script_choices(
    prefix: str,
    invocation: Invocation,
    contract: ScriptContract,
) -> list[str]:
    failures: list[str] = []
    option_values = _present_option_values(
        invocation.tokens,
        argument_start=2,
        value_options=set(contract.value_options),
    )
    for option, choices in contract.option_choices.items():
        if option not in option_values:
            continue
        value = option_values[option]
        if value not in choices:
            allowed = ", ".join(sorted(choices))
            failures.append(
                f"{prefix}: script {invocation.command!r} option {option!r} "
                f"has invalid choice {value!r}; expected one of: {allowed}"
            )

    positionals = _present_positionals(
        invocation.tokens,
        argument_start=2,
        value_options=set(contract.value_options),
    )
    for index, choices in enumerate(contract.positional_choices):
        if not choices or index >= len(positionals):
            continue
        value = positionals[index]
        if value not in choices:
            allowed = ", ".join(sorted(choices))
            failures.append(
                f"{prefix}: script {invocation.command!r} positional {index + 1} "
                f"has invalid choice {value!r}; expected one of: {allowed}"
            )
    return failures


def _value_matches_type(value: str, type_name: str) -> bool:
    if type_name == "float":
        try:
            float(value)
        except ValueError:
            return False
        return True
    if type_name == "int":
        try:
            int(value)
        except ValueError:
            return False
        return True
    return True


def _present_long_options(tokens: tuple[str, ...], *, argument_start: int) -> set[str]:
    options: set[str] = set()
    for token in tokens[argument_start:]:
        if token == "--":
            break
        if token.startswith("--"):
            options.add(token.split("=", 1)[0])
    return options


def _present_option_values(
    tokens: tuple[str, ...],
    *,
    argument_start: int,
    value_options: set[str],
) -> dict[str, str]:
    values: dict[str, str] = {}
    args = list(tokens[argument_start:])
    index = 0
    while index < len(args):
        token = args[index]
        if token in {">", "1>", "2>", "|", "--"}:
            break
        if not token.startswith("--"):
            index += 1
            continue
        option, separator, value = token.partition("=")
        if option not in value_options:
            index += 1
            continue
        if separator:
            values[option] = value
            index += 1
            continue
        if index + 1 < len(args):
            values[option] = args[index + 1]
            index += 2
            continue
        index += 1
    return values


def _present_positionals(
    tokens: tuple[str, ...],
    *,
    argument_start: int,
    value_options: set[str],
) -> list[str]:
    positionals: list[str] = []
    args = list(tokens[argument_start:])
    index = 0
    while index < len(args):
        token = args[index]
        if token in {">", "1>", "2>", "|"}:
            break
        if token == "--":
            positionals.extend(args[index + 1 :])
            break
        if token.startswith("--"):
            option = token.split("=", 1)[0]
            if (
                "=" not in token
                and option in value_options
                and index + 1 < len(args)
                and not args[index + 1].startswith("-")
            ):
                index += 2
                continue
            index += 1
            continue
        if token.startswith("-"):
            index += 1
            continue
        positionals.append(token)
        index += 1
    return positionals


def _check_invocation_paths(
    root: Path,
    invocation: Invocation,
    prefix: str,
    *,
    argument_start: int,
) -> list[str]:
    failures: list[str] = []
    for token in _argument_tokens(invocation.tokens, argument_start=argument_start):
        if not _looks_like_repo_path(token):
            continue
        if _should_skip_path_token(token):
            continue
        path = root / token
        if not path.exists():
            failures.append(f"{prefix}: command references missing local path {token!r}")
    return failures


def _argument_tokens(tokens: tuple[str, ...], *, argument_start: int) -> list[str]:
    if len(tokens) <= argument_start:
        return []
    args = list(tokens[argument_start:])
    result: list[str] = []
    skip_next = False
    for token in args:
        if skip_next:
            skip_next = False
            continue
        if token in {">", "1>", "2>", "|"}:
            skip_next = token != "|"
            continue
        result.append(token)
    return result


def _looks_like_repo_path(token: str) -> bool:
    cleaned = token.strip().strip("'\"")
    if "/" in cleaned:
        return True
    if cleaned.startswith("."):
        return True
    return cleaned.endswith(PATH_SUFFIXES)


def _should_skip_path_token(token: str) -> bool:
    cleaned = token.strip().strip("'\"")
    if cleaned in SKIP_PATH_VALUES:
        return True
    if Path(cleaned).is_absolute():
        return True
    if any(cleaned.startswith(prefix) for prefix in SKIP_PATH_PREFIXES):
        return True
    if any(marker in cleaned for marker in ("<", ">", "{", "}", "$", "*", "(", ")")):
        return True
    if "," in cleaned:
        return True
    return False


def _check_cli_command_documentation(
    commands: set[str],
    invocations: list[Invocation],
) -> list[str]:
    documented = {invocation.command for invocation in invocations}
    missing = sorted(commands - documented)
    return [f"CLI command lacks a documented invocation: {command}" for command in missing]


def _rel(path: Path, root: Path = ROOT) -> Path:
    try:
        return path.relative_to(root)
    except ValueError:
        return path


if __name__ == "__main__":
    raise SystemExit(main())
