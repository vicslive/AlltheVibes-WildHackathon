"""Core agent loop — the brain of Vics Agent."""

from __future__ import annotations

import json
from pathlib import Path

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from vics_agent.config import AgentConfig
from vics_agent.llm import LLMClient, Message
from vics_agent.tools import TOOL_SCHEMAS, execute_tool

console = Console()

SYSTEM_PROMPT = """\
You are **Vics Agent**, an autonomous coding assistant created by Vics.
Your tagline: "Coding your day away."

You are an expert software engineer. You can read, write, edit, search files, \
and execute shell commands inside the user's workspace.

## Guidelines
- Break complex tasks into small, verifiable steps.
- Always read existing files before editing them.
- After writing code, run it or run tests to verify correctness.
- Explain what you're doing briefly before each action.
- If you're unsure, use the `think` tool to reason step by step.
- Be concise and direct. Don't over-explain.
- If a task is impossible or dangerous, say so and explain why.
- When done, summarize what you accomplished.

## Workspace
All file operations are relative to the workspace directory.
The user's workspace is ready for you to use.
"""


class Agent:
    """The autonomous coding agent."""

    def __init__(self, config: AgentConfig | None = None):
        self.config = config or AgentConfig.from_env()
        self.llm = LLMClient(self.config.llm)
        self.messages: list[Message] = [Message(role="system", content=SYSTEM_PROMPT)]
        self.workspace = self.config.workspace.resolve()
        self.workspace.mkdir(parents=True, exist_ok=True)

    def run(self, user_input: str) -> str:
        """Run the agent loop for a single user request. Returns final text response."""
        self.messages.append(Message(role="user", content=user_input))

        for iteration in range(1, self.config.max_iterations + 1):
            if self.config.verbose:
                console.print(f"[dim]── iteration {iteration} ──[/dim]")

            # Ask the LLM
            response = self.llm.chat(self.messages, tools=TOOL_SCHEMAS)
            self.messages.append(response)

            # If no tool calls, we're done
            if not response.tool_calls:
                if response.content:
                    console.print(Panel(Markdown(response.content), title="Vics Agent", border_style="cyan"))
                return response.content

            # Print any thinking / text the model emitted alongside tool calls
            if response.content:
                console.print(f"[cyan]{response.content}[/cyan]")

            # Execute each tool call
            for tc in response.tool_calls:
                fn_name = tc["function"]["name"]
                try:
                    fn_args = json.loads(tc["function"]["arguments"])
                except json.JSONDecodeError:
                    fn_args = {}

                # Show what's happening
                args_summary = ", ".join(f"{k}={_shorten(v)}" for k, v in fn_args.items())
                console.print(f"  [yellow]⚡ {fn_name}[/yellow]({args_summary})")

                result = execute_tool(fn_name, fn_args, self.workspace)

                # Show short result
                display = result if len(result) <= 200 else result[:200] + "…"
                console.print(f"  [dim]→ {display}[/dim]")

                # Feed result back to the LLM
                self.messages.append(
                    Message(role="tool", content=result, tool_call_id=tc["id"], name=fn_name)
                )

        # Hit max iterations
        final = "Reached maximum iterations. Here's what I accomplished so far."
        console.print(f"[red]{final}[/red]")
        return final

    def reset(self):
        """Clear conversation history."""
        self.messages = [Message(role="system", content=SYSTEM_PROMPT)]


def _shorten(value, max_len: int = 60) -> str:
    """Shorten a value for display."""
    s = str(value)
    if len(s) > max_len:
        return s[: max_len - 3] + "..."
    return s
