"""
security/guardrails/pii_filter.py
──────────────────────────────────
Fast regex-based PII scanner and redactor.

Detects: Email, Phone, SSN (US), Credit Card, Aadhaar (IN), PAN (IN),
         IP addresses, Passport numbers (basic).

Usage:
    from security.guardrails.pii_filter import scan_pii
    result = scan_pii("My SSN is 123-45-6789 and email is john@example.com")
    # result = {"has_pii": True, "redacted_text": "...", "findings": ["SSN", "EMAIL"]}
"""

import re
from dataclasses import dataclass, field

# ── PII Pattern Registry ──────────────────────────────────────────────────────

_PATTERNS: list[tuple[str, re.Pattern]] = [
    ("EMAIL",        re.compile(r'\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b')),
    ("PHONE_US",     re.compile(r'\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b')),
    ("SSN",          re.compile(r'\b\d{3}-\d{2}-\d{4}\b')),
    ("CREDIT_CARD",  re.compile(r'\b(?:\d{4}[-\s]?){3}\d{4}\b')),
    ("AADHAAR",      re.compile(r'\b\d{4}\s\d{4}\s\d{4}\b')),          # Indian Aadhaar
    ("PAN",          re.compile(r'\b[A-Z]{5}[0-9]{4}[A-Z]\b')),         # Indian PAN
    ("IP_ADDRESS",   re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')),
    ("PASSPORT",     re.compile(r'\b[A-Z]{1,2}\d{6,9}\b')),
]

_REDACT_PLACEHOLDER = "[REDACTED]"


@dataclass
class PIIResult:
    has_pii:      bool
    redacted_text: str
    findings:     list[str] = field(default_factory=list)


def scan_pii(text: str) -> PIIResult:
    """
    Scan text for PII patterns and return a redacted version.

    Args:
        text: The raw query or text to check.

    Returns:
        PIIResult with:
          - has_pii: True if at least one pattern matched.
          - redacted_text: text with PII tokens replaced by [REDACTED].
          - findings: list of PII type names that were found.
    """
    findings  = []
    redacted  = text

    for pii_type, pattern in _PATTERNS:
        matches = pattern.findall(redacted)
        if matches:
            if pii_type not in findings:
                findings.append(pii_type)
            redacted = pattern.sub(_REDACT_PLACEHOLDER, redacted)

    return PIIResult(
        has_pii       = bool(findings),
        redacted_text = redacted,
        findings      = findings,
    )
