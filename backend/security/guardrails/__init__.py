"""
security/guardrails/__init__.py
────────────────────────────────
Unified guardrail entry point.

Chains:
  1. PII scan      → redact and warn, but allow through (non-blocking by default)
  2. Injection check → block if detected

Usage:
    from security.guardrails import run_guardrails, GuardResult
    result = run_guardrails(query, user="alice")
    if result.blocked:
        # return early with result.block_reason
    query = result.safe_query   # PII-redacted version
"""

from dataclasses import dataclass, field
from .pii_filter       import scan_pii
from .injection_filter import check_injection


@dataclass
class GuardResult:
    blocked:      bool
    block_reason: str         = ""
    block_stage:  str         = ""     # "pattern" | "llm"
    safe_query:   str         = ""     # PII-redacted query
    pii_findings: list = field(default_factory=list)
    pii_detected: bool        = False


def run_guardrails(query: str, user: str = "unknown") -> GuardResult:
    """
    Run the full guardrail pipeline on a user query.

    Steps:
      1. PII Scan — redact PII from query (non-blocking, always runs).
      2. Injection Check — block if jailbreak/injection detected.

    Returns a GuardResult. If blocked=True, the caller should abort
    the request and return the block_reason to the user.
    """
    import logging
    logger = logging.getLogger("ai_assistant")

    # ── Step 1: PII scan ──────────────────────────────────────────────────────
    pii = scan_pii(query)
    safe_query = pii.redacted_text

    if pii.has_pii:
        from observability.audit_service import log_pii_redaction
        log_pii_redaction(user, pii.findings)
        logger.warning(f"[Guardrail] PII detected for user={user}: {pii.findings}")

    # ── Step 2: Injection check ───────────────────────────────────────────────
    injection = check_injection(safe_query)

    if injection.blocked:
        from observability.audit_service import log_guardrail_block
        log_guardrail_block(user, injection.reason, injection.stage)
        return GuardResult(
            blocked      = True,
            block_reason = injection.reason,
            block_stage  = injection.stage,
            safe_query   = safe_query,
            pii_findings = pii.findings,
            pii_detected = pii.has_pii,
        )

    # ── All clear ─────────────────────────────────────────────────────────────
    return GuardResult(
        blocked      = False,
        safe_query   = safe_query,
        pii_findings = pii.findings,
        pii_detected = pii.has_pii,
    )
