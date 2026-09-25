"""LangGraph state machine for Continuity's diagnostic agent.

    retrieve -> triage -> (sufficient) -> answer -> END
                        -> (insufficient) -> escalate -> END

The triage node is the part that makes this an agent rather than a plain RAG
chain: it decides, per query, whether the retrieved evidence actually
supports a grounded diagnosis, and routes to escalation (with a logged
knowledge-gap) instead of forcing an answer when it doesn't. That routing
decision is what directly operationalizes this project's thesis — surfacing
where institutional knowledge is missing, not just answering when it's easy.
"""
from __future__ import annotations

from typing import Any, Literal, TypedDict

from langgraph.graph import END, StateGraph

from continuity.agent.prompts import (
    ANSWER_SYSTEM_PROMPT,
    ANSWER_USER_TEMPLATE,
    TRIAGE_SYSTEM_PROMPT,
    TRIAGE_USER_TEMPLATE,
)
from continuity.agent.tools import flag_knowledge_gap
from continuity.config import settings
from continuity.llm import call_structured
from continuity.retrieval.hybrid import HybridRetriever, RetrievedChunk
from continuity.retrieval.vectorstore import get_client, get_collection

TRIAGE_SCHEMA = {
    "type": "object",
    "properties": {
        "sufficient": {
            "type": "boolean",
            "description": "True only if the retrieved passages genuinely support a grounded diagnosis.",
        },
        "reasoning": {"type": "string"},
    },
    "required": ["sufficient", "reasoning"],
}

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
                    "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
                    "cited_sources": {"type": "array", "items": {"type": "string"}},
                    "recommended_action": {"type": "string"},
                },
                "required": ["cause", "confidence", "cited_sources", "recommended_action"],
            },
        },
    },
    "required": ["summary", "causes"],
}


class ContinuityState(TypedDict, total=False):
    query: str
    equipment: str | None
    retrieved: list[RetrievedChunk]
    triage: dict[str, Any]
    answer: dict[str, Any]
    escalation: dict[str, Any]
    escalated: bool


def _format_context(retrieved: list[RetrievedChunk]) -> str:
    if not retrieved:
        return "(no passages retrieved — knowledge base is empty or unreachable)"
    blocks = []
    for r in retrieved:
        c = r.chunk
        blocks.append(f"--- [{c.doc_id}] {c.title} / {c.section} ---\n{c.text}")
    return "\n\n".join(blocks)


def build_graph(retriever: HybridRetriever):
    def node_retrieve(state: ContinuityState) -> ContinuityState:
        retrieved = retriever.retrieve(state["query"], k=settings.retrieval_top_k)
        return {"retrieved": retrieved}

    def node_triage(state: ContinuityState) -> ContinuityState:
        retrieved = state["retrieved"]
        top_score = retrieved[0].fused_score if retrieved else 0.0
        if top_score < settings.min_fused_score_threshold:
            # Cheap heuristic gate: skip the LLM call entirely when nothing
            # retrieved even weakly matches, rather than paying for a model
            # call whose answer is a foregone conclusion.
            return {
                "triage": {
                    "sufficient": False,
                    "reasoning": (
                        f"Top fused retrieval score {top_score:.4f} is below the "
                        f"{settings.min_fused_score_threshold} threshold — nothing in "
                        "the knowledge base is even weakly related to this query."
                    ),
                }
            }
        context = _format_context(retrieved)
        triage = call_structured(
            system=TRIAGE_SYSTEM_PROMPT,
            user=TRIAGE_USER_TEMPLATE.format(
                query=state["query"], equipment=state.get("equipment") or "unspecified", context=context
            ),
            tool_name="submit_triage_decision",
            tool_description="Submit whether the retrieved evidence is sufficient to ground a diagnosis.",
            input_schema=TRIAGE_SCHEMA,
        )
        return {"triage": triage}

    def route_after_triage(state: ContinuityState) -> Literal["answer", "escalate"]:
        return "answer" if state["triage"]["sufficient"] else "escalate"

    def node_answer(state: ContinuityState) -> ContinuityState:
        context = _format_context(state["retrieved"])
        answer = call_structured(
            system=ANSWER_SYSTEM_PROMPT,
            user=ANSWER_USER_TEMPLATE.format(
                query=state["query"], equipment=state.get("equipment") or "unspecified", context=context
            ),
            tool_name="submit_diagnosis",
            tool_description="Submit the ranked, cited diagnosis.",
            input_schema=ANSWER_SCHEMA,
            max_tokens=1536,
        )
        return {"answer": answer, "escalated": False}

    def node_escalate(state: ContinuityState) -> ContinuityState:
        reasoning = state["triage"]["reasoning"]
        flag_knowledge_gap(state["query"], state.get("equipment"), reasoning)
        message = (
            "Knowledge base coverage is insufficient for a grounded diagnosis. "
            "This has been logged as a knowledge gap for follow-up. Recommend "
            "escalating to a senior equipment engineer rather than guessing. "
            f"Triage reasoning: {reasoning}"
        )
        return {"escalation": {"message": message, "reasoning": reasoning}, "escalated": True}

    # Node names are suffixed with "_step" because LangGraph's StateGraph
    # forbids a node name that exactly matches one of the state's own keys
    # (e.g. a node named "triage" would collide with the state's "triage"
    # field) — this tripped during smoke-testing and is kept as a comment
    # since the resulting error message doesn't make the cause obvious.
    graph = StateGraph(ContinuityState)
    graph.add_node("retrieve_step", node_retrieve)
    graph.add_node("triage_step", node_triage)
    graph.add_node("answer_step", node_answer)
    graph.add_node("escalate_step", node_escalate)

    graph.set_entry_point("retrieve_step")
    graph.add_edge("retrieve_step", "triage_step")
    graph.add_conditional_edges(
        "triage_step", route_after_triage, {"answer": "answer_step", "escalate": "escalate_step"}
    )
    graph.add_edge("answer_step", END)
    graph.add_edge("escalate_step", END)

    return graph.compile()


_compiled_graph = None
_retriever = None


def _get_graph():
    global _compiled_graph, _retriever
    if _compiled_graph is None:
        client = get_client(settings.chroma_persist_dir)
        collection = get_collection(client)
        _retriever = HybridRetriever(collection)
        _compiled_graph = build_graph(_retriever)
    return _compiled_graph


def run_continuity_agent(query: str, equipment: str | None = None) -> ContinuityState:
    graph = _get_graph()
    return graph.invoke({"query": query, "equipment": equipment})
