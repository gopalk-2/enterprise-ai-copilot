from .logger import logger
from observability.tracing import get_tracer
import time
import json


# ── Helpers ──────────────────────────────────────────────────────────────────

def _structured(event: str, **fields) -> str:
    """Emit a structured JSON log line for machine-readable parsing."""
    return json.dumps({"event": event, **fields})


# ── Original API (unchanged) ─────────────────────────────────────────────────

def log_query(user: str, query: str):
    logger.info(_structured("query", user=user, query=query[:300]))


def log_response(user: str, response: str):
    logger.info(_structured("response", user=user, preview=response[:200]))


def log_error(user: str, error: str):
    logger.error(_structured("error", user=user, error=error))


def measure_time(start_time: float):
    duration = round(time.time() - start_time, 3)
    logger.info(_structured("latency", duration_s=duration))


def log_cache_hit(user: str, query: str):
    logger.info(_structured("cache", user=user, hit=True, query=query[:100]))


def log_cache_miss(user: str, query: str):
    logger.info(_structured("cache", user=user, hit=False, query=query[:100]))


def log_redis_error(error: str):
    logger.warning(_structured("redis_error", error=str(error)))


# ── Extended LLM / Route / Tool metrics (new) ────────────────────────────────

def log_llm_call(
    model: str,
    latency_ms: float,
    prompt_tokens: int = 0,
    completion_tokens: int = 0,
):
    """
    Log an LLM invocation with token and latency metrics.
    Also attaches attributes to the current OTel span (if active).
    """
    data = {
        "model": model,
        "latency_ms": round(latency_ms, 1),
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": prompt_tokens + completion_tokens,
    }
    logger.info(_structured("llm_call", **data))

    # Attach to the active OTel span if one exists
    try:
        from opentelemetry import trace
        span = trace.get_current_span()
        if span.is_recording():
            for k, v in data.items():
                span.set_attribute(f"llm.{k}", v)
    except Exception:
        pass


def log_route(user: str, route: str, latency_ms: float):
    """Log the result of semantic routing and attach it to the active span."""
    logger.info(_structured("route", user=user, route=route, latency_ms=round(latency_ms, 1)))
    try:
        from opentelemetry import trace
        span = trace.get_current_span()
        if span.is_recording():
            span.set_attribute("rag.route", route)
            span.set_attribute("rag.route_latency_ms", round(latency_ms, 1))
    except Exception:
        pass


def log_tool_failure(tool_name: str, error: str):
    """Log a tool invocation failure with high severity."""
    logger.error(_structured("tool_failure", tool=tool_name, error=str(error)[:400]))
    try:
        from opentelemetry import trace
        from opentelemetry.trace import StatusCode
        span = trace.get_current_span()
        if span.is_recording():
            span.set_attribute("tool.failed", tool_name)
            span.set_attribute("tool.error", str(error)[:200])
            span.set_status(StatusCode.ERROR, str(error)[:100])
    except Exception:
        pass


def log_guardrail_block(user: str, reason: str, stage: str):
    """Log when a query is blocked by the guardrail layer."""
    logger.warning(_structured("guardrail_block", user=user, reason=reason, stage=stage))
    try:
        from opentelemetry import trace
        span = trace.get_current_span()
        if span.is_recording():
            span.set_attribute("guardrail.blocked", True)
            span.set_attribute("guardrail.stage", stage)
            span.set_attribute("guardrail.reason", reason)
    except Exception:
        pass


def log_pii_redaction(user: str, findings: list):
    """Log when PII is detected and redacted from a query."""
    logger.warning(_structured("pii_redacted", user=user, pii_types=findings))