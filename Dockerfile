FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt pyproject.toml ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN pip install --no-cache-dir -e .

# Build the retrieval index at image build time (local embedding model only —
# no API key needed for this step). Generation/eval still need
# ANTHROPIC_API_KEY set at runtime.
RUN python scripts/ingest.py

# Render (and most PaaS platforms) inject a $PORT env var at container
# start and route traffic to whatever port the process actually binds —
# it is NOT fixed at build time, so this must be read at runtime rather
# than baked into an exec-form CMD. Default of 7860 only applies to a
# plain local `docker run` with no PORT set.
ENV PORT=7860
EXPOSE 7860

# exec-form CMD invoking `sh -c 'exec ...'`: the `exec` replaces the shell
# with uvicorn so uvicorn becomes PID 1 and receives SIGTERM directly on
# Render redeploys/restarts, instead of an intermediate shell swallowing it
# (a bare shell-form CMD would build and run fine but shut down uncleanly).
CMD ["sh", "-c", "exec uvicorn continuity.api.main:app --host 0.0.0.0 --port ${PORT}"]
