# 🤖 Vics Agent

> **Coding your day away** — An autonomous coding agent powered by LLMs

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Vics Agent is an autonomous coding agent that can read, write, edit, search code, and execute commands — all driven by natural language. It uses an agentic loop with tool calling to break down complex tasks and execute them step by step.

## ✨ Features

- **Autonomous coding** — Reads, writes, edits, and searches files automatically
- **Shell execution** — Runs commands, tests, and build scripts
- **Multi-provider** — Works with OpenAI (GPT-4o) or Anthropic (Claude)
- **Safety first** — Sandboxed workspace, blocked destructive commands
- **Interactive & batch** — Chat mode or single-prompt mode
- **Beautiful CLI** — Rich terminal output with syntax highlighting

## 🚀 Quick Start

### 1. Install

```bash
# Clone the repo
git clone https://github.com/shyamsridhar123/AlltheVibes-WildHackathon.git
cd AlltheVibes-WildHackathon

# Install with pip
pip install -e .
```

### 2. Configure

```bash
# Copy the example env file
cp .env.example .env

# Edit .env and add your API key
# OPENAI_API_KEY=sk-your-key-here
# or
# ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### 3. Run

```bash
# Interactive chat mode
vics chat

# Single prompt mode
vics ask "Create a Python Flask API with CRUD endpoints for a todo app"

# With options
vics chat --workspace ./my-project --model gpt-4o --verbose
```

## 🛠 Built-in Tools

| Tool | Description |
|------|-------------|
| `read_file` | Read file contents |
| `write_file` | Create or overwrite files |
| `edit_file` | Make targeted edits (find & replace) |
| `list_directory` | Browse workspace file structure |
| `search_files` | Grep across files with regex support |
| `run_command` | Execute shell commands |
| `delete_file` | Remove files |
| `think` | Internal reasoning (chain-of-thought) |

## 📁 Project Structure

```
AlltheVibes-WildHackathon/
├── pyproject.toml          # Package config & dependencies
├── .env.example            # Environment variable template
├── README.md               # You're here
├── LICENSE                 # MIT License
├── vics_agent/
│   ├── __init__.py         # Package metadata
│   ├── config.py           # Configuration management
│   ├── llm.py              # LLM client (OpenAI + Anthropic)
│   ├── tools.py            # Tool registry & implementations
│   ├── agent.py            # Core agent loop
│   └── cli.py              # CLI entry point
└── tests/
    └── test_tools.py       # Tool unit tests
```

## 💡 Example Usage

```
You> Create a Python script that generates fibonacci numbers

  ⚡ think(thought=I'll create a clean Python script...)
  ⚡ write_file(path=fibonacci.py, content=...)
  → Successfully wrote 342 bytes to fibonacci.py
  ⚡ run_command(command=python fibonacci.py)
  → 0, 1, 1, 2, 3, 5, 8, 13, 21, 34

╭─ Vics Agent ─────────────────────────────────────╮
│ Created `fibonacci.py` with a generator-based    │
│ implementation. The script outputs the first 10  │
│ Fibonacci numbers. ✓                             │
╰──────────────────────────────────────────────────╯
```

## ⚙ Configuration

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `OPENAI_API_KEY` | — | OpenAI API key |
| `OPENAI_MODEL` | `gpt-4o` | OpenAI model name |
| `ANTHROPIC_API_KEY` | — | Anthropic API key |
| `ANTHROPIC_MODEL` | `claude-sonnet-4-20250514` | Anthropic model name |
| `VICS_MAX_ITERATIONS` | `25` | Max agent loop iterations |
| `VICS_WORKSPACE` | `./workspace` | Default workspace directory |

## 🔒 Safety

- All file operations are sandboxed to the workspace directory
- Path traversal attacks are blocked
- Destructive system commands are blocked
- Commands have a configurable timeout (default: 60s)

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

**Built with ❤️ by Vics for the Wild Hackathon**
