from __future__ import annotations

from fastapi import FastAPI
from gradio import mount_gradio_app

from continuity.api.routes import router
from continuity.observability import configure_logging
from continuity.ui.app import build_gradio_app

configure_logging()

app = FastAPI(
    title="Continuity API",
    description=(
        "Institutional knowledge-capture and fault-diagnosis assistant. "
        "Independent portfolio PoC — see README for scope and sourcing."
    ),
    version="0.1.0",
)
app.include_router(router, prefix="/api")

# The Gradio UI and the /api/* routes both call the same underlying agent
# function in-process (see continuity.agent.graph.run_continuity_agent).
# Mounting Gradio onto the FastAPI app keeps this a single deployable
# service while still exposing a clean, independently callable HTTP API
# that a production consumer could hit without touching the UI at all.
app = mount_gradio_app(app, build_gradio_app(), path="/")
