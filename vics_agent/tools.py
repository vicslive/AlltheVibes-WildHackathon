"""Tool registry and base definitions for the agent's capabilities."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any, Callable

# ── Tool Registry ────────────────────────────────────────────────────────

TOOL_REGISTRY: dict[str, Callable[..., str]] = {}
TOOL_SCHEMAS: list[dict] = []


def tool(name: str, description: str, parameters: dict):
    """Decorator to register a function as an agent tool."""

    def decorator(fn: Callable[..., str]) -> Callable[..., str]:
        TOOL_REGISTRY[name] = fn
        TOOL_SCHEMAS.append(
            {
                "type": "function",
                "function": {
                    "name": name,
                    "description": description,
                    "parameters": parameters,
                },
            }
        )
        return fn

    return decorator


def execute_tool(name: str, arguments: dict[str, Any], workspace: Path) -> str:
    """Execute a registered tool by name with the given arguments."""
    if name not in TOOL_REGISTRY:
        return f"Error: Unknown tool '{name}'"
    try:
        return TOOL_REGISTRY[name](workspace=workspace, **arguments)
    except Exception as e:
        return f"Error executing {name}: {type(e).__name__}: {e}"


# ═══════════════════════════════════════════════════════════════════════════
#  Built-in Tools
# ═══════════════════════════════════════════════════════════════════════════


@tool(
    name="read_file",
    description="Read the contents of a file. Returns the full text content.",
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Relative path to the file within the workspace.",
            }
        },
        "required": ["path"],
    },
)
def read_file(workspace: Path, path: str) -> str:
    target = (workspace / path).resolve()
    if not str(target).startswith(str(workspace.resolve())):
        return "Error: Access denied — path escapes workspace."
    if not target.exists():
        return f"Error: File not found: {path}"
    return target.read_text(encoding="utf-8", errors="replace")


@tool(
    name="write_file",
    description="Write content to a file. Creates the file and parent directories if they don't exist. Overwrites existing content.",
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Relative path to the file within the workspace.",
            },
            "content": {
                "type": "string",
                "description": "The full content to write to the file.",
            },
        },
        "required": ["path", "content"],
    },
)
def write_file(workspace: Path, path: str, content: str) -> str:
    target = (workspace / path).resolve()
    if not str(target).startswith(str(workspace.resolve())):
        return "Error: Access denied — path escapes workspace."
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return f"Successfully wrote {len(content)} bytes to {path}"


@tool(
    name="edit_file",
    description="Replace an exact string in a file with a new string. Use this for targeted edits.",
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Relative path to the file within the workspace.",
            },
            "old_string": {
                "type": "string",
                "description": "The exact text to find and replace (must match exactly).",
            },
            "new_string": {
                "type": "string",
                "description": "The replacement text.",
            },
        },
        "required": ["path", "old_string", "new_string"],
    },
)
def edit_file(workspace: Path, path: str, old_string: str, new_string: str) -> str:
    target = (workspace / path).resolve()
    if not str(target).startswith(str(workspace.resolve())):
        return "Error: Access denied — path escapes workspace."
    if not target.exists():
        return f"Error: File not found: {path}"
    content = target.read_text(encoding="utf-8")
    count = content.count(old_string)
    if count == 0:
        return "Error: old_string not found in file."
    if count > 1:
        return f"Error: old_string found {count} times — must be unique. Add more context."
    new_content = content.replace(old_string, new_string, 1)
    target.write_text(new_content, encoding="utf-8")
    return f"Successfully edited {path}"


@tool(
    name="list_directory",
    description="List files and directories in a given path. Returns names with '/' suffix for directories.",
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Relative path to the directory within the workspace. Use '.' for root.",
            }
        },
        "required": ["path"],
    },
)
def list_directory(workspace: Path, path: str) -> str:
    target = (workspace / path).resolve()
    if not str(target).startswith(str(workspace.resolve())):
        return "Error: Access denied — path escapes workspace."
    if not target.exists():
        return f"Error: Directory not found: {path}"
    if not target.is_dir():
        return f"Error: Not a directory: {path}"
    entries = []
    for item in sorted(target.iterdir()):
        name = item.name
        if item.is_dir():
            name += "/"
        entries.append(name)
    if not entries:
        return "(empty directory)"
    return "\n".join(entries)


@tool(
    name="search_files",
    description="Search for a text pattern across files in the workspace. Returns matching lines with file paths and line numbers.",
    parameters={
        "type": "object",
        "properties": {
            "pattern": {
                "type": "string",
                "description": "Text or regex pattern to search for.",
            },
            "file_glob": {
                "type": "string",
                "description": "Optional glob pattern to filter files (e.g., '*.py'). Defaults to all files.",
            },
        },
        "required": ["pattern"],
    },
)
def search_files(workspace: Path, pattern: str, file_glob: str = "**/*") -> str:
    import re

    results = []
    try:
        regex = re.compile(pattern, re.IGNORECASE)
    except re.error:
        regex = re.compile(re.escape(pattern), re.IGNORECASE)

    for file_path in workspace.resolve().rglob(file_glob):
        if not file_path.is_file():
            continue
        # Skip binary files and hidden dirs
        rel = file_path.relative_to(workspace.resolve())
        if any(part.startswith(".") for part in rel.parts):
            continue
        try:
            text = file_path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        for i, line in enumerate(text.splitlines(), 1):
            if regex.search(line):
                results.append(f"{rel}:{i}: {line.strip()}")
                if len(results) >= 50:
                    results.append("... (truncated at 50 matches)")
                    return "\n".join(results)
    if not results:
        return "No matches found."
    return "\n".join(results)


@tool(
    name="run_command",
    description="Execute a shell command in the workspace directory. Returns stdout and stderr. Use for running tests, installing packages, building projects, etc.",
    parameters={
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "The shell command to execute.",
            },
            "timeout": {
                "type": "integer",
                "description": "Timeout in seconds (default: 60).",
            },
        },
        "required": ["command"],
    },
)
def run_command(workspace: Path, command: str, timeout: int = 60) -> str:
    # Safety: block destructive system commands
    blocked = ["rm -rf /", "format c:", "del /f /s /q c:", ":(){:|:&};:"]
    if any(b in command.lower() for b in blocked):
        return "Error: This command is blocked for safety."

    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=str(workspace.resolve()),
            capture_output=True,
            text=True,
            timeout=timeout,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )
        output = ""
        if result.stdout:
            output += result.stdout
        if result.stderr:
            output += ("\n--- stderr ---\n" + result.stderr) if output else result.stderr
        if result.returncode != 0:
            output += f"\n(exit code: {result.returncode})"
        return output.strip() or "(no output)"
    except subprocess.TimeoutExpired:
        return f"Error: Command timed out after {timeout}s."


@tool(
    name="delete_file",
    description="Delete a file from the workspace.",
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Relative path to the file to delete.",
            }
        },
        "required": ["path"],
    },
)
def delete_file(workspace: Path, path: str) -> str:
    target = (workspace / path).resolve()
    if not str(target).startswith(str(workspace.resolve())):
        return "Error: Access denied — path escapes workspace."
    if not target.exists():
        return f"Error: File not found: {path}"
    if target.is_dir():
        return "Error: Use run_command to remove directories."
    target.unlink()
    return f"Deleted {path}"


@tool(
    name="think",
    description="Use this tool to think through complex problems step by step. Your thoughts are private and not shown to the user.",
    parameters={
        "type": "object",
        "properties": {
            "thought": {
                "type": "string",
                "description": "Your step-by-step reasoning about the current problem.",
            }
        },
        "required": ["thought"],
    },
)
def think(workspace: Path, thought: str) -> str:
    return "Thought recorded. Continue with your plan."
