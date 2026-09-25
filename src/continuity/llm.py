"""Thin structured-output helper around the Anthropic SDK.

Uses forced tool-use (tool_choice pinned to a single tool) to get validated
JSON back from Claude, rather than prompting for JSON text and regexing it
out of the response — the latter is a common source of flaky eval harnesses
and flaky agents, and tool-use is the mechanism Anthropic's API provides
specifically to avoid it.
"""
from __future__ import annotations

import json
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


def _coerce_json_strings(value: Any, schema: dict[str, Any]) -> Any:
    """Recursively repairs values the model stringified instead of nesting
    properly, guided by the JSON schema we actually asked for. Observed
    empirically during eval: forced tool-use is not a hard guarantee — on
    different calls against the *same* schema, Claude has stringified the
    entire payload under one field, or individual array items, rather than
    nesting them as real objects/arrays. This walks the schema so any of
    those shapes gets normalized, not just the one that happened to be
    seen first."""
    schema_type = schema.get("type")
    if isinstance(value, str) and schema_type in ("object", "array"):
        try:
            value = json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value
    if schema_type == "object" and isinstance(value, dict):
        properties = schema.get("properties", {})
        return {
            key: (_coerce_json_strings(v, properties[key]) if key in properties else v)
            for key, v in value.items()
        }
    if schema_type == "array" and isinstance(value, list):
        item_schema = schema.get("items", {})
        return [_coerce_json_strings(item, item_schema) for item in value]
    return value


def _repair_if_nested_as_string(raw: dict[str, Any], required_keys: list[str]) -> dict[str, Any]:
    """Observed empirically during eval, not a hypothetical: on at least one
    forced tool-use call, Claude returned a tool input missing its required
    top-level keys, with the *entire* intended payload instead JSON-encoded
    as a string inside one of the other fields (e.g. `{"causes": "{\\"summary\\":
    ..., \\"causes\\": [...]}"}` instead of `{"summary": ..., "causes": [...]}`).
    Rather than crash every downstream consumer of this shape, attempt one
    cheap repair pass: if any field's value parses as JSON and that parsed
    object actually contains the required keys, use it instead."""
    if all(k in raw for k in required_keys):
        return raw
    for value in raw.values():
        if not isinstance(value, str):
            continue
        try:
            parsed = json.loads(value)
        except (json.JSONDecodeError, TypeError):
            continue
        if isinstance(parsed, dict) and all(k in parsed for k in required_keys):
            return parsed
    return raw  # unrepairable — let the caller's own validation fail loudly


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
            required_keys = input_schema.get("required", [])
            repaired = _repair_if_nested_as_string(block.input, required_keys)
            return _coerce_json_strings(repaired, {"type": "object", **input_schema})
    raise RuntimeError(f"Model did not call the expected tool '{tool_name}'")
