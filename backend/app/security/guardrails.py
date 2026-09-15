import hashlib
import re
from dataclasses import dataclass


EMAIL_PATTERN = re.compile(
    r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE
)
PHONE_PATTERN = re.compile(r"(?<!\w)(?:\+?\d[\d\s().-]{7,}\d)(?!\w)")
CARD_PATTERN = re.compile(r"(?<!\d)(?:\d[ -]*?){13,19}(?!\d)")

INJECTION_PATTERNS = {
    "instruction_override": re.compile(
        r"\b(ignore|forget|disregard)\b.{0,40}\b(previous|prior|system|instructions?)\b",
        re.IGNORECASE,
    ),
    "prompt_extraction": re.compile(
        r"\b(reveal|show|print|repeat)\b.{0,40}"
        r"\b(system prompt|developer message|hidden instructions?)\b",
        re.IGNORECASE,
    ),
    "jailbreak_attempt": re.compile(
        r"\b(jailbreak|developer mode|DAN mode)\b", re.IGNORECASE
    ),
}


@dataclass(frozen=True)
class SecurityAssessment:
    safe: bool
    flags: list[str]


def redact_pii(text: str) -> str:
    redacted = EMAIL_PATTERN.sub("[EMAIL_REDACTED]", text)
    redacted = PHONE_PATTERN.sub("[PHONE_REDACTED]", redacted)
    redacted = CARD_PATTERN.sub("[PAYMENT_DATA_REDACTED]", redacted)
    return redacted


def hash_identifier(identifier: str | None) -> str | None:
    if not identifier:
        return None
    return hashlib.sha256(identifier.encode("utf-8")).hexdigest()


def assess_prompt_security(text: str) -> SecurityAssessment:
    flags = [name for name, pattern in INJECTION_PATTERNS.items() if pattern.search(text)]
    return SecurityAssessment(safe=not flags, flags=flags)
