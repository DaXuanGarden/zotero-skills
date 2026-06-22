#!/usr/bin/env python3
"""Read-only sanity checks for local Zotero/PubMed MCP client configs.

This script inspects common ZCode/OpenCode config files. It does not spawn MCP
servers, query Zotero, contact PubMed/NCBI, or modify any configuration.
"""

from __future__ import annotations

import argparse
import json
import os
import stat
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

HOME = Path.home()

ZOTERO_HINTS = ("zotero",)
PUBMED_HINTS = ("pubmed", "ncbi", "pancrepal", "simple-pubmed")
GUI_PATH_RISK_COMMANDS = {"node", "npm", "npx", "python", "python3", "uv", "uvx", "pipx", "zotero-mcp"}
SENSITIVE_ENV_NAMES = {"PUBMED_API_KEY", "NCBI_API_KEY", "ZOTERO_API_KEY"}


@dataclass(frozen=True)
class ConfigSpec:
    client: str
    label: str
    path: Path
    expected_shape: str


CONFIG_SPECS = [
    ConfigSpec("zcode", "ZCode v2", HOME / ".zcode/v2/config.json", "top-level mcp"),
    ConfigSpec("zcode", "ZCode CLI legacy", HOME / ".zcode/cli/config.json", "mcp.servers"),
    ConfigSpec("opencode", "OpenCode", HOME / ".config/opencode/opencode.json", "top-level mcp"),
]


@dataclass
class Finding:
    severity: str
    message: str


class Reporter:
    def __init__(self) -> None:
        self.findings: list[Finding] = []

    def info(self, message: str) -> None:
        self.findings.append(Finding("info", message))

    def warn(self, message: str) -> None:
        self.findings.append(Finding("warn", message))

    def error(self, message: str) -> None:
        self.findings.append(Finding("error", message))

    def has_errors(self) -> bool:
        return any(f.severity == "error" for f in self.findings)

    def has_warnings(self) -> bool:
        return any(f.severity == "warn" for f in self.findings)

    def print(self) -> None:
        icons = {"info": "ℹ️", "warn": "⚠️", "error": "❌"}
        for finding in self.findings:
            print(f"{icons[finding.severity]} {finding.message}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Read-only MCP config sanity checker for ZCode/OpenCode")
    parser.add_argument(
        "--client",
        choices=("auto", "zcode", "opencode", "all"),
        default="auto",
        help="Which client config family to inspect. auto checks existing known config files.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit non-zero when warnings are present. JSON parse errors and malformed server entries always fail.",
    )
    return parser.parse_args()


def load_json(path: Path, reporter: Reporter) -> Any | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        reporter.error(f"{path}: invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}")
        return None
    except OSError as exc:
        reporter.error(f"{path}: cannot read file: {exc}")
        return None


def selected_specs(client: str) -> list[ConfigSpec]:
    if client == "all":
        return CONFIG_SPECS
    if client == "auto":
        existing = [spec for spec in CONFIG_SPECS if spec.path.exists()]
        return existing or CONFIG_SPECS
    return [spec for spec in CONFIG_SPECS if spec.client == client]


def normalize_servers(data: Any, spec: ConfigSpec, reporter: Reporter) -> dict[str, Any]:
    if not isinstance(data, dict):
        reporter.error(f"{spec.path}: root JSON value should be an object")
        return {}

    if "mcpServers" in data:
        reporter.warn(
            f"{spec.path}: found Claude-style 'mcpServers'; ZCode/OpenCode usually expect 'mcp' "
            "(top-level for v2/OpenCode, or mcp.servers for legacy CLI)"
        )

    mcp = data.get("mcp")
    if not isinstance(mcp, dict):
        reporter.warn(f"{spec.path}: no object-valued 'mcp' section found")
        return {}

    if spec.expected_shape == "mcp.servers":
        servers = mcp.get("servers")
        if isinstance(servers, dict):
            return servers
        direct_servers = {k: v for k, v in mcp.items() if isinstance(v, dict) and k not in {"enabled", "type"}}
        if direct_servers:
            reporter.warn(f"{spec.path}: legacy ZCode CLI config commonly uses mcp.servers, but direct mcp entries were found")
            return direct_servers
        reporter.warn(f"{spec.path}: no mcp.servers object found")
        return {}

    if isinstance(mcp.get("servers"), dict):
        reporter.warn(f"{spec.path}: found mcp.servers; current {spec.label} examples usually use top-level mcp entries")
        return mcp["servers"]

    servers = {k: v for k, v in mcp.items() if isinstance(v, dict)}
    if not servers:
        reporter.warn(f"{spec.path}: mcp section has no server objects")
    return servers


def env_from_server(server: dict[str, Any]) -> dict[str, Any]:
    for key in ("env", "environment"):
        value = server.get(key)
        if isinstance(value, dict):
            return value
    return {}


def command_parts(server: dict[str, Any]) -> tuple[str | None, list[str]]:
    command = server.get("command")
    args = server.get("args")
    if isinstance(command, list):
        if not command:
            return None, []
        return str(command[0]), [str(part) for part in command[1:]]
    if isinstance(command, str):
        return command, [str(part) for part in args] if isinstance(args, list) else []
    return None, []


def is_probably_disabled(server: dict[str, Any]) -> bool:
    enabled = server.get("enabled")
    disabled = server.get("disabled")
    return enabled is False or disabled is True


def classify_server(name: str, server: dict[str, Any]) -> set[str]:
    haystack_parts = [name]
    command, args = command_parts(server)
    if command:
        haystack_parts.append(command)
    haystack_parts.extend(args)
    haystack = " ".join(haystack_parts).lower()
    roles: set[str] = set()
    if any(hint in haystack for hint in ZOTERO_HINTS):
        roles.add("zotero")
    if any(hint in haystack for hint in PUBMED_HINTS):
        roles.add("pubmed")
    return roles


def redact_env_value(name: str, value: Any) -> str:
    if name in SENSITIVE_ENV_NAMES or "KEY" in name or "TOKEN" in name or "SECRET" in name:
        return "<set>" if value not in (None, "") else "<empty>"
    return repr(value)


def check_command(spec: ConfigSpec, server_name: str, server: dict[str, Any], reporter: Reporter) -> None:
    command, args = command_parts(server)
    prefix = f"{spec.path}: server '{server_name}'"
    if command is None:
        reporter.error(f"{prefix}: missing or invalid command")
        return

    if os.path.isabs(command):
        command_path = Path(command)
        if not command_path.exists():
            reporter.error(f"{prefix}: absolute command does not exist: {command}")
        elif not os.access(command_path, os.X_OK):
            mode = stat.filemode(command_path.stat().st_mode)
            reporter.warn(f"{prefix}: absolute command exists but may not be executable ({mode}): {command}")
        else:
            reporter.info(f"{prefix}: command path exists and is executable: {command}")
    else:
        first = Path(command).name
        if first in GUI_PATH_RISK_COMMANDS or "/" not in command:
            reporter.warn(
                f"{prefix}: command is not an absolute path ('{command}'); GUI-launched ZCode/OpenCode may not inherit shell PATH"
            )
        else:
            reporter.warn(f"{prefix}: command is relative rather than absolute: {command}")

    if not isinstance(server.get("command"), (str, list)):
        reporter.error(f"{prefix}: command should be a string or array")
    if "args" in server and not isinstance(server.get("args"), list):
        reporter.warn(f"{prefix}: args is present but is not an array")
    if args:
        reporter.info(f"{prefix}: args detected: {' '.join(args)}")


def check_env(spec: ConfigSpec, server_name: str, server: dict[str, Any], roles: set[str], reporter: Reporter) -> None:
    env = env_from_server(server)
    prefix = f"{spec.path}: server '{server_name}'"
    if not env:
        reporter.warn(f"{prefix}: no env/environment object found")
    else:
        shown = ", ".join(f"{k}={redact_env_value(k, v)}" for k, v in sorted(env.items()))
        reporter.info(f"{prefix}: env keys: {shown}")

    if "zotero" in roles:
        if str(env.get("ZOTERO_LOCAL", "")).lower() != "true":
            reporter.warn(f"{prefix}: Zotero server does not set ZOTERO_LOCAL=true; confirm the intended local-library mode")

    if "pubmed" in roles:
        if env.get("MCP_TRANSPORT") not in ("stdio", None):
            reporter.warn(f"{prefix}: PubMed MCP_TRANSPORT is {env.get('MCP_TRANSPORT')!r}; stdio is expected for local MCP clients")
        elif env.get("MCP_TRANSPORT") is None:
            reporter.warn(f"{prefix}: PubMed MCP_TRANSPORT is not set; expected stdio for local MCP clients")
        for key in ("ABSTRACT_MODE", "FULLTEXT_MODE"):
            if key not in env:
                reporter.warn(f"{prefix}: PubMed {key} is not set; confirm this matches your desired PancrePal/PubMed behavior")
        for key in ("PUBMED_EMAIL", "PUBMED_API_KEY"):
            reporter.info(f"{prefix}: {key} {'is set' if env.get(key) else 'is not set'}")


def check_config(spec: ConfigSpec, reporter: Reporter) -> None:
    if not spec.path.exists():
        reporter.info(f"{spec.label}: config not found at {spec.path}")
        return

    reporter.info(f"Inspecting {spec.label}: {spec.path}")
    data = load_json(spec.path, reporter)
    if data is None:
        return

    servers = normalize_servers(data, spec, reporter)
    if not servers:
        return

    seen_roles: set[str] = set()
    for name, server in sorted(servers.items()):
        if not isinstance(server, dict):
            reporter.error(f"{spec.path}: server '{name}' should be an object")
            continue
        roles = classify_server(name, server)
        seen_roles.update(roles)
        role_label = "+".join(sorted(roles)) if roles else "other"
        reporter.info(f"{spec.path}: server '{name}' detected as {role_label}")
        if is_probably_disabled(server):
            reporter.warn(f"{spec.path}: server '{name}' appears disabled")
        check_command(spec, name, server, reporter)
        check_env(spec, name, server, roles, reporter)

    if "zotero" not in seen_roles:
        reporter.warn(f"{spec.path}: no likely Zotero MCP server detected")
    if "pubmed" not in seen_roles:
        reporter.warn(f"{spec.path}: no likely PubMed/NCBI MCP server detected (ok if PubMed expansion is not needed)")


def main() -> None:
    args = parse_args()
    reporter = Reporter()
    specs = selected_specs(args.client)

    print("MCP config sanity check (read-only; no server spawn; no network).")
    for spec in specs:
        check_config(spec, reporter)

    print()
    reporter.print()

    if reporter.has_errors() or (args.strict and reporter.has_warnings()):
        print("\nMCP config sanity check completed with issues.")
        raise SystemExit(1)

    print("\nMCP config sanity check completed.")


if __name__ == "__main__":
    main()
