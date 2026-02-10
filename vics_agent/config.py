"""Configuration management for Vics Agent."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()


class LLMConfig(BaseModel):
    """LLM provider configuration."""

    provider: str = Field(default="openai", description="LLM provider: 'openai' or 'anthropic'")
    api_key: str = Field(default="", description="API key for the chosen provider")
    model: str = Field(default="gpt-4o", description="Model name")
    temperature: float = Field(default=0.1, ge=0.0, le=2.0)
    max_tokens: int = Field(default=4096, gt=0)


class AgentConfig(BaseModel):
    """Top-level agent configuration."""

    llm: LLMConfig = Field(default_factory=LLMConfig)
    max_iterations: int = Field(default=25, gt=0, description="Max agent loop iterations")
    workspace: Path = Field(default=Path("./workspace"), description="Working directory for file ops")
    verbose: bool = Field(default=False)

    @classmethod
    def from_env(cls) -> AgentConfig:
        """Build configuration from environment variables."""
        # Determine provider
        anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")
        openai_key = os.getenv("OPENAI_API_KEY", "")

        if anthropic_key and not openai_key:
            provider = "anthropic"
            api_key = anthropic_key
            model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")
        else:
            provider = "openai"
            api_key = openai_key
            model = os.getenv("OPENAI_MODEL", "gpt-4o")

        llm = LLMConfig(provider=provider, api_key=api_key, model=model)

        return cls(
            llm=llm,
            max_iterations=int(os.getenv("VICS_MAX_ITERATIONS", "25")),
            workspace=Path(os.getenv("VICS_WORKSPACE", "./workspace")),
        )
