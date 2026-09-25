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

EXPOSE 7860
ENV PORT=7860

CMD ["uvicorn", "continuity.api.main:app", "--host", "0.0.0.0", "--port", "7860"]
