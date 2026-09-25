from __future__ import annotations

import anthropic
import gradio as gr

from continuity.agent.graph import run_continuity_agent
from continuity.agent.tools import log_resolved_case
from continuity.llm import MissingAPIKeyError

EQUIPMENT_OPTIONS = [
    "",
    "AMX-5200 Plasma Etch System",
    "Vantage PECVD 300 Deposition System",
    "Orbis CMP-7 Polisher",
    "Helios NXP-2100 Lithography Scanner",
    "ThermaLine VF-800 Vertical Diffusion Furnace",
]

DISCLAIMER = (
    "**This is an independent portfolio PoC.** Every SOP, incident log, and "
    "knowledge-capture interview in its knowledge base is synthetic and "
    "illustrative — none of it is real company data. See the README for sourcing "
    "and scope."
)


def _format_diagnosis(result: dict) -> tuple[str, str]:
    sources = ", ".join(sorted({r.chunk.doc_id for r in result.get("retrieved", [])})) or "none"
    if result.get("escalated"):
        body = (
            f"### ⚠️ Escalation recommended\n\n{result['escalation']['message']}\n\n"
            f"*Retrieved but judged insufficient: {sources}*"
        )
        return body, sources
    answer = result["answer"]
    lines = [f"### Diagnosis\n\n{answer.get('summary', '')}\n"]
    for i, cause in enumerate(answer.get("causes", []), start=1):
        if not isinstance(cause, dict):
            lines.append(f"**{i}.** _[unparseable cause entry, skipped]_\n")
            continue
        lines.append(
            f"**{i}. {cause.get('cause', '?')}**  _(confidence: {cause.get('confidence', '?')})_\n\n"
            f"- Recommended action: {cause.get('recommended_action', '?')}\n"
            f"- Cited sources: {', '.join(cause.get('cited_sources', [])) or 'none'}\n"
        )
    lines.append(f"\n*Retrieved context: {sources}*")
    return "\n".join(lines), sources


def diagnose_handler(query: str, equipment: str):
    if not query or len(query.strip()) < 5:
        return "Please describe the fault in a bit more detail.", ""
    try:
        result = run_continuity_agent(query.strip(), equipment or None)
    except MissingAPIKeyError as exc:
        return f"### Configuration needed\n\n{exc}", ""
    except anthropic.APIError as exc:
        return f"### Upstream Anthropic API error\n\n{exc}", ""
    return _format_diagnosis(result)


def resolve_handler(query: str, equipment: str, resolution: str, resolved_by: str):
    if not query.strip() or not resolution.strip():
        return "Fault description and resolution summary are both required to log a case."
    record = log_resolved_case(
        query=query.strip(),
        resolution_summary=resolution.strip(),
        equipment=equipment or None,
        resolved_by=resolved_by or None,
    )
    return (
        f"Logged as `{record['doc_id']}` and re-indexed into the knowledge base — "
        "future queries can now retrieve this resolution."
    )


def build_gradio_app() -> gr.Blocks:
    with gr.Blocks(title="Continuity") as demo:
        gr.Markdown("# Continuity\nInstitutional knowledge-capture & fault-diagnosis assistant")
        gr.Markdown(DISCLAIMER)

        with gr.Tab("Diagnose a fault"):
            with gr.Row():
                with gr.Column(scale=2):
                    query_in = gr.Textbox(
                        label="Fault description",
                        placeholder="Describe what you're seeing, e.g. 'RF match on chamber 3 is tuning slow, about 13 seconds...'",
                        lines=4,
                    )
                    equipment_in = gr.Dropdown(
                        EQUIPMENT_OPTIONS, label="Equipment (optional)", value=""
                    )
                    diagnose_btn = gr.Button("Diagnose", variant="primary")
                with gr.Column(scale=3):
                    output_md = gr.Markdown(label="Result")
                    sources_out = gr.Textbox(label="Retrieved source doc_ids", interactive=False)

            diagnose_btn.click(
                diagnose_handler, inputs=[query_in, equipment_in], outputs=[output_md, sources_out]
            )

        with gr.Tab("Log a resolved case"):
            gr.Markdown(
                "Once a fault is resolved, log it here so the resolution is written back "
                "into the knowledge base and retrievable for future similar faults."
            )
            resolve_query = gr.Textbox(label="Fault description", lines=3)
            resolve_equipment = gr.Dropdown(EQUIPMENT_OPTIONS, label="Equipment (optional)", value="")
            resolve_summary = gr.Textbox(label="How it was resolved", lines=3)
            resolve_by = gr.Textbox(label="Resolved by (optional)")
            resolve_btn = gr.Button("Save to knowledge base", variant="primary")
            resolve_status = gr.Markdown()

            resolve_btn.click(
                resolve_handler,
                inputs=[resolve_query, resolve_equipment, resolve_summary, resolve_by],
                outputs=[resolve_status],
            )

    return demo


if __name__ == "__main__":
    build_gradio_app().launch()
