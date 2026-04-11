# ─────────────────────────────────────────────────────────────────────────────
# Stage 1 — Builder: install Python deps into an isolated venv
# ─────────────────────────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /build

# System deps needed for some Python packages (e.g. numpy, sentence-transformers)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Create venv
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install deps (layer-cached unless requirements.txt changes)
COPY backend/requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt


# ─────────────────────────────────────────────────────────────────────────────
# Stage 2 — Runtime: lean image with only what's needed to run
# ─────────────────────────────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

WORKDIR /app

# Security: non-root user
RUN useradd -m -u 1001 appuser

# Copy venv from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application source
COPY backend/ .

# Pre-create data directories so SQLite / logs have a home
RUN mkdir -p /app/data /app/data/logs && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

# 2 workers for baseline horizontal throughput. Tune via UVICORN_WORKERS env var.
CMD ["sh", "-c", "uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers ${UVICORN_WORKERS:-2}"]
