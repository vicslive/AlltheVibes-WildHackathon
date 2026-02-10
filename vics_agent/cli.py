"""CLI entry point for Vics Agent."""

from __future__ import annotations

import sys
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel

from vics_agent import __version__
from vics_agent.agent import Agent
from vics_agent.config import AgentConfig

console = Console()

BANNER = r"""
 ██╗   ██╗██╗ ██████╗███████╗     █████╗  ██████╗ ███████╗███╗   ██╗████████╗
 ██║   ██║██║██╔════╝██╔════╝    ██╔══██╗██╔════╝ ██╔════╝████╗  ██║╚══██╔══╝
 ██║   ██║██║██║     ███████╗    ███████║██║  ███╗█████╗  ██╔██╗ ██║   ██║
 ╚██╗ ██╔╝██║██║     ╚════██║    ██╔══██║██║   ██║██╔══╝  ██║╚██╗██║   ██║
  ╚████╔╝ ██║╚██████╗███████║    ██║  ██║╚██████╔╝███████╗██║ ╚████║   ██║
   ╚═══╝  ╚═╝ ╚═════╝╚══════╝    ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝   ╚═╝
"""


@click.group(invoke_without_command=True)
@click.option("--version", "-v", is_flag=True, help="Show version.")
@click.pass_context
def main(ctx, version):
    """Vics Agent — Coding your day away."""
    if version:
        click.echo(f"vics-agent v{__version__}")
        return
    if ctx.invoked_subcommand is None:
        ctx.invoke(chat)


@main.command()
@click.option("--workspace", "-w", type=click.Path(), default="./workspace", help="Workspace directory.")
@click.option("--model", "-m", type=str, default=None, help="Override LLM model name.")
@click.option("--verbose", is_flag=True, help="Show debug info.")
def chat(workspace, model, verbose):
    """Start an interactive chat session with Vics Agent."""
    config = AgentConfig.from_env()
    config.workspace = Path(workspace)
    config.verbose = verbose
    if model:
        config.llm.model = model

    if not config.llm.api_key:
        console.print(
            "[red]No API key found![/red] Set OPENAI_API_KEY or ANTHROPIC_API_KEY "
            "in your environment or .env file.\n"
            "See .env.example for details."
        )
        sys.exit(1)

    console.print(BANNER, style="cyan")
    console.print(
        Panel(
            f"[bold]Provider:[/bold] {config.llm.provider}  |  "
            f"[bold]Model:[/bold] {config.llm.model}  |  "
            f"[bold]Workspace:[/bold] {config.workspace.resolve()}",
            title="⚙ Configuration",
            border_style="dim",
        )
    )
    console.print("[dim]Type your request. Use 'quit' to exit, 'reset' to clear history.[/dim]\n")

    agent = Agent(config)

    while True:
        try:
            user_input = console.input("[bold green]You>[/bold green] ").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[dim]Goodbye![/dim]")
            break

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "q"):
            console.print("[dim]Goodbye![/dim]")
            break
        if user_input.lower() == "reset":
            agent.reset()
            console.print("[dim]Conversation reset.[/dim]\n")
            continue

        console.print()
        agent.run(user_input)
        console.print()


@main.command()
@click.argument("prompt")
@click.option("--workspace", "-w", type=click.Path(), default="./workspace", help="Workspace directory.")
@click.option("--model", "-m", type=str, default=None, help="Override LLM model name.")
def ask(prompt, workspace, model):
    """Run a single prompt (non-interactive mode)."""
    config = AgentConfig.from_env()
    config.workspace = Path(workspace)
    if model:
        config.llm.model = model

    if not config.llm.api_key:
        console.print("[red]No API key found![/red] Set OPENAI_API_KEY or ANTHROPIC_API_KEY.")
        sys.exit(1)

    agent = Agent(config)
    agent.run(prompt)


if __name__ == "__main__":
    main()
