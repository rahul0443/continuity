"""Thin structured-output helper around the Anthropic SDK.

Uses forced tool-use (tool_choice pinned to a single tool) to get validated
JSON back from Claude, rather than prompting for JSON text and regexing it
out of the response — the latter is a common source of flaky eval harnesses
and flaky agents, and tool-use is the mechanism Anthropic's API provides
specifically to avoid it.
"""
from __future__ import annotations

from functools import lru_cache
from typing import Any

import anthropic

from continuity.config import settings


class MissingAPIKeyError(RuntimeError):
    """Raised when an operation needs the Anthropic API and no key is configured.

    Retrieval (Chroma + BM25) never raises this — only answer generation,
    triage, and LLM-judged eval scoring need a key.
    """


@lru_cache(maxsize=1)
def get_client() -> anthropic.Anthropic:
    if not settings.anthropic_api_key:
        raise MissingAPIKeyError(
            "ANTHROPIC_API_KEY is not set. Retrieval works without it, but "
            "agent generation and LLM-judged eval scoring require a key — "
            "copy .env.example to .env and add yours."
        )
    return anthropic.Anthropic(api_key=settings.anthropic_api_key)


def call_structured(
    system: str,
    user: str,
    tool_name: str,
    tool_description: str,
    input_schema: dict[str, Any],
    max_tokens: int = 1024,
) -> dict[str, Any]:
    """Forces Claude to respond by calling exactly one tool, and returns that
    tool call's validated input dict."""
    client = get_client()
    tool = {
        "name": tool_name,
        "description": tool_description,
        "input_schema": input_schema,
    }
    response = client.messages.create(
        model=settings.anthropic_model,
        max_tokens=max_tokens,
        system=system,
        tools=[tool],
        tool_choice={"type": "tool", "name": tool_name},
        messages=[{"role": "user", "content": user}],
    )
    for block in response.content:
        if block.type == "tool_use" and block.name == tool_name:
            return block.input
    raise RuntimeError(f"Model did not call the expected tool '{tool_name}'")
