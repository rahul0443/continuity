import json

from continuity.llm import _coerce_json_strings, _repair_if_nested_as_string

ANSWER_SCHEMA = {
    "type": "object",
    "properties": {
        "summary": {"type": "string"},
        "causes": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "cause": {"type": "string"},
                    "confidence": {"type": "string"},
                },
            },
        },
    },
    "required": ["summary", "causes"],
}


def test_passthrough_when_already_well_formed():
    raw = {"summary": "s", "causes": []}
    assert _repair_if_nested_as_string(raw, ["summary", "causes"]) == raw


def test_repairs_json_stringified_payload_nested_in_a_field():
    # Reproduces the exact shape observed from a real Claude tool-use call
    # during eval: required keys missing at the top level, but present in
    # a JSON string value nested under one of the other keys.
    inner = {"summary": "real summary", "causes": [{"cause": "x"}]}
    raw = {"causes": __import__("json").dumps(inner)}
    repaired = _repair_if_nested_as_string(raw, ["summary", "causes"])
    assert repaired == inner


def test_gives_up_gracefully_when_unrepairable():
    raw = {"something_else": "not json at all"}
    assert _repair_if_nested_as_string(raw, ["summary", "causes"]) == raw


def test_coerce_passthrough_when_already_well_formed():
    raw = {"summary": "s", "causes": [{"cause": "x", "confidence": "high"}]}
    assert _coerce_json_strings(raw, ANSWER_SCHEMA) == raw


def test_coerce_fixes_individual_stringified_array_items():
    # Reproduces a second real shape observed during eval: the top-level
    # object and the causes array are both properly structured, but one
    # array item is itself a JSON string instead of a nested object.
    raw = {
        "summary": "s",
        "causes": [
            json.dumps({"cause": "x", "confidence": "high"}),
            {"cause": "y", "confidence": "low"},
        ],
    }
    coerced = _coerce_json_strings(raw, ANSWER_SCHEMA)
    assert coerced["causes"][0] == {"cause": "x", "confidence": "high"}
    assert coerced["causes"][1] == {"cause": "y", "confidence": "low"}


def test_coerce_fixes_whole_array_stringified():
    raw = {"summary": "s", "causes": json.dumps([{"cause": "x", "confidence": "high"}])}
    coerced = _coerce_json_strings(raw, ANSWER_SCHEMA)
    assert coerced["causes"] == [{"cause": "x", "confidence": "high"}]
