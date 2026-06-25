#!/usr/bin/env python3
"""Inspect latest agent SDK packages for required harness-optimization surfaces."""

from __future__ import annotations

import importlib
import importlib.metadata as metadata
import inspect
import json
from typing import Any


SURFACE_CHECKS = {
    "claude-agent-sdk": {
        "module": "claude_agent_sdk",
        "source": "https://code.claude.com/docs/en/agent-sdk/overview",
        "checks": [
            {"name": "agent_loop", "symbols": ["query", "ClaudeSDKClient", "ClaudeAgentOptions"]},
            {"name": "mcp_servers", "symbols": ["create_sdk_mcp_server", "McpServerConfig", "SdkMcpTool"]},
            {
                "name": "permissions",
                "symbols": ["PermissionMode", "PermissionResultAllow", "PermissionResultDeny"],
                "options": ["permission_mode", "can_use_tool", "permission_prompt_tool_name"],
            },
            {
                "name": "hooks",
                "symbols": ["HookCallback", "PreToolUseHookInput", "PostToolUseHookInput"],
                "options": ["hooks", "include_hook_events"],
            },
            {"name": "skills", "symbols": ["SdkPluginConfig"], "options": ["skills", "plugins"]},
            {"name": "subagents", "symbols": ["AgentDefinition", "SubagentStartHookInput"], "options": ["agents"]},
            {
                "name": "sessions",
                "symbols": ["InMemorySessionStore", "SessionStore", "fork_session"],
                "options": ["resume", "session_id", "session_store", "continue_conversation"],
            },
            {
                "name": "thinking_and_budget",
                "symbols": ["ThinkingConfigEnabled", "EffortLevel", "TaskBudget"],
                "options": ["thinking", "effort", "max_thinking_tokens", "max_budget_usd", "task_budget"],
            },
            {
                "name": "claude_code_product_bridge",
                "options": ["cli_path", "cwd", "tools", "allowed_tools", "mcp_servers"],
            },
        ],
    },
    "openai-agents": {
        "module": "agents",
        "source": "https://openai.github.io/openai-agents-python/agents/",
        "checks": [
            {"name": "agent_loop", "symbols": ["Agent", "Runner", "RunConfig"]},
            {
                "name": "function_tools",
                "symbols": ["function_tool", "FunctionTool", "ToolCallItem", "ToolCallOutputItem"],
                "agent_signature": ["tools"],
            },
            {
                "name": "mcp_servers",
                "symbols": ["HostedMCPTool", "MCPListToolsItem", "MCPApprovalRequestItem"],
                "agent_signature": ["mcp_servers", "mcp_config"],
            },
            {
                "name": "handoffs",
                "symbols": ["Handoff", "HandoffCallItem", "HandoffOutputItem"],
                "agent_signature": ["handoffs"],
            },
            {
                "name": "guardrails",
                "symbols": ["InputGuardrail", "OutputGuardrail", "GuardrailFunctionOutput"],
                "agent_signature": ["input_guardrails", "output_guardrails"],
            },
            {"name": "sessions", "symbols": ["Session", "OpenAIConversationsSession", "SessionSettings"]},
            {"name": "tracing", "symbols": ["Span", "AgentSpanData", "FunctionSpanData", "HandoffSpanData"]},
            {"name": "hosted_and_local_tools", "symbols": ["ShellTool", "LocalShellTool", "ComputerTool", "FileSearchTool"]},
        ],
    },
    "google-adk": {
        "module": "google.adk",
        "source": "https://adk.dev/",
        "checks": [
            {"name": "agent_loop", "symbols": ["Agent", "Runner"]},
            {"name": "workflows", "symbols": ["Workflow"]},
            {
                "name": "tools",
                "submodules": ["google.adk.tools"],
                "agent_signature": ["tools", "before_tool_callback", "after_tool_callback", "on_tool_error_callback"],
            },
            {"name": "sessions", "submodules": ["google.adk.sessions"], "runner_signature": ["session_service"]},
            {"name": "memory", "submodules": ["google.adk.memory"], "runner_signature": ["memory_service"]},
            {
                "name": "multi_agent",
                "agent_signature": ["sub_agents", "disallow_transfer_to_parent", "disallow_transfer_to_peers"],
            },
            {"name": "planners", "submodules": ["google.adk.planners"], "agent_signature": ["planner"]},
            {"name": "code_execution", "submodules": ["google.adk.code_executors"], "agent_signature": ["code_executor"]},
            {"name": "telemetry", "submodules": ["google.adk.telemetry"], "runner_signature": ["plugins"]},
            {"name": "evaluation", "submodules": ["google.adk.evaluation"]},
        ],
    },
}


def main() -> int:
    result = build_inventory()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["passed"] else 1


def build_inventory() -> dict[str, Any]:
    packages = []
    for package, spec in SURFACE_CHECKS.items():
        packages.append(_inspect_package(package, spec))
    return {
        "name": "latest SDK surface inventory",
        "packages": packages,
        "passed": all(item["passed"] for item in packages),
        "value_bar": {
            "adversarial_result": "This inventory fails when a required symbol, constructor parameter, or submodule is missing.",
            "claim": "Latest SDK coverage is useful only if the packages expose the harness surfaces this repo intends to evaluate.",
        },
    }


def _inspect_package(package: str, spec: dict[str, Any]) -> dict[str, Any]:
    module = importlib.import_module(spec["module"])
    version = metadata.version(package)
    checks = [_inspect_check(module, check) for check in spec["checks"]]
    return {
        "checks": checks,
        "module": spec["module"],
        "package": package,
        "passed": all(check["passed"] for check in checks),
        "source": spec["source"],
        "version": version,
    }


def _inspect_check(module: Any, check: dict[str, Any]) -> dict[str, Any]:
    details = []
    missing = []
    for symbol in check.get("symbols", []):
        present = hasattr(module, symbol)
        details.append({"kind": "symbol", "name": symbol, "present": present})
        if not present:
            missing.append(f"symbol:{symbol}")

    option_names = set(check.get("options", []))
    if option_names:
        annotations = getattr(getattr(module, "ClaudeAgentOptions", None), "__annotations__", {})
        for option in sorted(option_names):
            present = option in annotations
            details.append({"kind": "claude_option", "name": option, "present": present})
            if not present:
                missing.append(f"option:{option}")

    for class_name, field in (("Agent", "agent_signature"), ("Runner", "runner_signature")):
        signature_names = set(check.get(field, []))
        if signature_names:
            params = _signature_params(getattr(module, class_name, None))
            for name in sorted(signature_names):
                present = name in params
                details.append({"kind": f"{class_name.lower()}_param", "name": name, "present": present})
                if not present:
                    missing.append(f"{class_name.lower()}_param:{name}")

    for submodule in check.get("submodules", []):
        present = _can_import(submodule)
        details.append({"kind": "submodule", "name": submodule, "present": present})
        if not present:
            missing.append(f"submodule:{submodule}")

    return {
        "details": details,
        "missing": missing,
        "name": check["name"],
        "passed": not missing,
    }


def _signature_params(obj: Any) -> set[str]:
    if obj is None:
        return set()
    try:
        return set(inspect.signature(obj).parameters)
    except (TypeError, ValueError):
        return set()


def _can_import(module_name: str) -> bool:
    try:
        importlib.import_module(module_name)
    except ModuleNotFoundError:
        return False
    return True


if __name__ == "__main__":
    raise SystemExit(main())
