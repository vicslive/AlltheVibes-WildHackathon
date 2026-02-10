"""Unified LLM client abstraction — supports OpenAI and Anthropic."""

from __future__ import annotations

import json
from dataclasses import dataclass, field

from vics_agent.config import LLMConfig


@dataclass
class Message:
    """A single message in the conversation."""

    role: str  # "system", "user", "assistant", "tool"
    content: str = ""
    tool_calls: list[dict] = field(default_factory=list)
    tool_call_id: str | None = None
    name: str | None = None


class LLMClient:
    """Provider-agnostic LLM client with tool-calling support."""

    def __init__(self, config: LLMConfig):
        self.config = config
        self.provider = config.provider

        if self.provider == "openai":
            from openai import OpenAI

            self.client = OpenAI(api_key=config.api_key)
        elif self.provider == "anthropic":
            import anthropic

            self.client = anthropic.Anthropic(api_key=config.api_key)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    def chat(
        self,
        messages: list[Message],
        tools: list[dict] | None = None,
    ) -> Message:
        """Send messages to the LLM and return the assistant response."""
        if self.provider == "openai":
            return self._chat_openai(messages, tools)
        else:
            return self._chat_anthropic(messages, tools)

    # ── OpenAI ───────────────────────────────────────────────────────────

    def _chat_openai(self, messages: list[Message], tools: list[dict] | None) -> Message:
        formatted = []
        for m in messages:
            entry: dict = {"role": m.role, "content": m.content}
            if m.tool_calls:
                entry["tool_calls"] = m.tool_calls
            if m.tool_call_id:
                entry["tool_call_id"] = m.tool_call_id
            if m.name:
                entry["name"] = m.name
            formatted.append(entry)

        kwargs: dict = {
            "model": self.config.model,
            "messages": formatted,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
        }
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"

        response = self.client.chat.completions.create(**kwargs)
        choice = response.choices[0]
        msg = choice.message

        tool_calls = []
        if msg.tool_calls:
            for tc in msg.tool_calls:
                tool_calls.append(
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                )

        return Message(
            role="assistant",
            content=msg.content or "",
            tool_calls=tool_calls,
        )

    # ── Anthropic ────────────────────────────────────────────────────────

    def _chat_anthropic(self, messages: list[Message], tools: list[dict] | None) -> Message:
        # Extract system message
        system_text = ""
        api_messages = []
        for m in messages:
            if m.role == "system":
                system_text = m.content
                continue
            if m.role == "tool":
                api_messages.append(
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": m.tool_call_id,
                                "content": m.content,
                            }
                        ],
                    }
                )
                continue
            if m.tool_calls:
                # Assistant message with tool use
                content_blocks = []
                if m.content:
                    content_blocks.append({"type": "text", "text": m.content})
                for tc in m.tool_calls:
                    content_blocks.append(
                        {
                            "type": "tool_use",
                            "id": tc["id"],
                            "name": tc["function"]["name"],
                            "input": json.loads(tc["function"]["arguments"]),
                        }
                    )
                api_messages.append({"role": "assistant", "content": content_blocks})
                continue
            api_messages.append({"role": m.role, "content": m.content})

        # Convert tools from OpenAI format to Anthropic format
        anthropic_tools = None
        if tools:
            anthropic_tools = []
            for t in tools:
                fn = t["function"]
                anthropic_tools.append(
                    {
                        "name": fn["name"],
                        "description": fn.get("description", ""),
                        "input_schema": fn.get("parameters", {"type": "object", "properties": {}}),
                    }
                )

        kwargs: dict = {
            "model": self.config.model,
            "max_tokens": self.config.max_tokens,
            "messages": api_messages,
        }
        if system_text:
            kwargs["system"] = system_text
        if anthropic_tools:
            kwargs["tools"] = anthropic_tools

        response = self.client.messages.create(**kwargs)

        # Parse response
        text_parts = []
        tool_calls = []
        for block in response.content:
            if block.type == "text":
                text_parts.append(block.text)
            elif block.type == "tool_use":
                tool_calls.append(
                    {
                        "id": block.id,
                        "type": "function",
                        "function": {
                            "name": block.name,
                            "arguments": json.dumps(block.input),
                        },
                    }
                )

        return Message(
            role="assistant",
            content="\n".join(text_parts),
            tool_calls=tool_calls,
        )
