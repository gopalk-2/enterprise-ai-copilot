"""
observability/tracing.py
─────────────────────────
Initialises the OpenTelemetry SDK and exports traces to a local Jaeger
instance via OTLP gRPC.

Usage (call once at application start, e.g. in api/main.py):

    from observability.tracing import init_tracing, get_tracer
    init_tracing()
    tracer = get_tracer()

Context managers:
    with tracer.start_as_current_span("my-operation") as span:
        span.set_attribute("user", username)
        ...

Graceful degradation: if Jaeger is unreachable or OTEL vars are missing,
tracing silently disables itself (NoOpTracer) — the app never crashes.
"""

import os
import logging

logger = logging.getLogger("ai_assistant")

# ── Global tracer (NoOp by default until init_tracing() is called) ──────────
_tracer = None


def init_tracing() -> None:
    """Initialise OpenTelemetry SDK. Safe to call multiple times (idempotent)."""
    global _tracer
    if _tracer is not None:
        return

    endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "")
    service  = os.getenv("OTEL_SERVICE_NAME", "enterprise-ai-assistant")

    if not endpoint:
        logger.info("[Tracing] OTEL_EXPORTER_OTLP_ENDPOINT not set — tracing disabled (NoOp).")
        _tracer = _noop_tracer()
        return

    try:
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
        from opentelemetry.sdk.resources import Resource

        resource = Resource.create({"service.name": service})
        provider = TracerProvider(resource=resource)

        exporter = OTLPSpanExporter(endpoint=endpoint, insecure=True)
        provider.add_span_processor(BatchSpanProcessor(exporter))

        trace.set_tracer_provider(provider)
        _tracer = trace.get_tracer(service)

        logger.info(f"[Tracing] OpenTelemetry initialised → {endpoint} (service: {service})")

    except Exception as exc:
        logger.warning(f"[Tracing] Failed to initialise OTel ({exc}) — falling back to NoOp.")
        _tracer = _noop_tracer()


def get_tracer():
    """Return the active tracer (initialise with NoOp if never called)."""
    global _tracer
    if _tracer is None:
        init_tracing()
    return _tracer


# ── NoOp tracer shim ─────────────────────────────────────────────────────────

class _NoOpSpan:
    """Minimal span shim — drop-in when OTel is disabled."""
    def set_attribute(self, *a, **kw): pass
    def record_exception(self, *a, **kw): pass
    def set_status(self, *a, **kw): pass
    def __enter__(self): return self
    def __exit__(self, *a): pass


class _NoOpTracer:
    def start_as_current_span(self, name, **kw):
        return _NoOpSpan()
    def start_span(self, name, **kw):
        return _NoOpSpan()


def _noop_tracer() -> _NoOpTracer:
    return _NoOpTracer()
