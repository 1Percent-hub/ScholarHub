"""
Advanced memory validation: scoring, sanitization, and quality checks for
user facts before they are stored. Used to reduce junk and improve recall quality.
"""
import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass

# Optional: use memory_utils if available
try:
    from memory_utils import (
        is_safe_to_store as _base_safe,
        looks_like_secret,
        word_count,
        is_reasonable_fact_length,
        strip_leading_that,
        clean_fact_value,
        FACT_INTRO_PHRASES,
        QUESTION_STARTS,
    )
except ImportError:
    def _base_safe(key: str, value: str) -> bool:
        return bool(key and value and len(value) < 500)
    def looks_like_secret(value: str) -> bool:
        return False
    def word_count(s: str) -> int:
        return len((s or "").split())
    def is_reasonable_fact_length(value: str) -> bool:
        return 1 <= word_count(value or "") <= 30
    def strip_leading_that(s: str) -> str:
        return (s or "").strip()
    def clean_fact_value(s: str) -> str:
        return (s or "").strip()[:500]
    FACT_INTRO_PHRASES = ()
    QUESTION_STARTS = ()


# ---------------------------------------------------------------------------
# Validation result type
# ---------------------------------------------------------------------------

@dataclass
class ValidationResult:
    """Result of validating a candidate fact."""
    valid: bool
    score: float  # 0.0 .. 1.0
    reason: str
    sanitized_value: Optional[str] = None


# ---------------------------------------------------------------------------
# Allowed fact keys (whitelist)
# ---------------------------------------------------------------------------

ALLOWED_FACT_KEYS = frozenset({
    "name", "location", "likes", "dislikes", "favorite", "favourite",
    "note", "has", "interested_in", "birthday", "work_or_study", "role",
    "pet", "friend", "school", "job", "born_in", "email", "color", "food",
    "movie", "sport", "hobby", "language", "goal", "custom",
})


def is_allowed_fact_key(key: str) -> bool:
    """True if this key is allowed for storage."""
    if not key or not isinstance(key, str):
        return False
    k = key.strip().lower()
    return k in ALLOWED_FACT_KEYS or k.startswith("custom_")


# ---------------------------------------------------------------------------
# Value sanitization
# ---------------------------------------------------------------------------

# Characters we strip from fact values
STRIP_CHARS = "\n\r\t\u200b\u200c\u200d\ufeff"
MAX_VALUE_LEN = 500


def sanitize_value(value: str) -> str:
    """Remove control chars and normalize whitespace."""
    if not value:
        return ""
    for c in STRIP_CHARS:
        value = value.replace(c, "")
    value = re.sub(r"\s+", " ", value.strip())
    return value[:MAX_VALUE_LEN]


def sanitize_name(name: str) -> str:
    """Extra sanitization for name: capitalize, no digits in the middle."""
    if not name:
        return ""
    s = sanitize_value(name)
    # Remove trailing/leading digits
    s = re.sub(r"^\d+|\d+$", "", s).strip()
    return s[:80]


# ---------------------------------------------------------------------------
# Scoring: how likely is this message to contain a storable fact?
# ---------------------------------------------------------------------------

def score_message_as_fact(message: str) -> float:
    """
    Score 0.0 .. 1.0: how much does this message look like a self-disclosure
    we should store? (Used to avoid storing "what is the capital of France" as a fact.)
    """
    if not message or len(message) < 2:
        return 0.0
    m = message.lower().strip()
    # Question-like -> low score
    for start in QUESTION_STARTS:
        if m.startswith(start):
            return 0.0
    # Ends with ? and short -> likely question
    if m.endswith("?") and len(m) < 60:
        return 0.1
    # Contains fact-intro phrase -> high score
    for phrase in FACT_INTRO_PHRASES:
        if phrase in m:
            return 0.9
    # Medium: could be a statement
    if len(m) > 10 and not m.endswith("?"):
        return 0.5
    return 0.3


def score_key_value_pair(key: str, value: str) -> float:
    """
    Score 0.0 .. 1.0 for a (key, value) fact candidate.
    Considers key validity, value length, and safety.
    """
    if not is_allowed_fact_key(key):
        return 0.0
    if not value or not value.strip():
        return 0.0
    if not _base_safe(key, value):
        return 0.0
    if looks_like_secret(value):
        return 0.0
    score = 0.5
    if is_reasonable_fact_length(value):
        score += 0.3
    if len(value) >= 2 and len(value) <= 200:
        score += 0.1
    # Names: prefer 2–4 words
    if key == "name":
        w = word_count(value)
        if 1 <= w <= 4:
            score += 0.1
        elif w > 6:
            score -= 0.2
    return min(1.0, max(0.0, score))


# ---------------------------------------------------------------------------
# Full validation pipeline
# ---------------------------------------------------------------------------

def validate_fact(key: str, value: str) -> ValidationResult:
    """
    Run full validation on a candidate fact. Returns ValidationResult with
    valid=True only if we should store it.
    """
    if not key:
        return ValidationResult(False, 0.0, "missing key", None)
    if not value:
        return ValidationResult(False, 0.0, "missing value", None)
    if not is_allowed_fact_key(key):
        return ValidationResult(False, 0.0, "key not allowed", None)
    sanitized = sanitize_value(value)
    if key == "name":
        sanitized = sanitize_name(sanitized)
    else:
        sanitized = clean_fact_value(sanitized)
    if not sanitized:
        return ValidationResult(False, 0.0, "empty after sanitization", None)
    if not _base_safe(key, sanitized):
        return ValidationResult(False, 0.0, "unsafe to store", None)
    if looks_like_secret(sanitized):
        return ValidationResult(False, 0.0, "looks like secret", None)
    sc = score_key_value_pair(key, sanitized)
    if sc < 0.3:
        return ValidationResult(False, sc, "score too low", sanitized)
    return ValidationResult(True, sc, "ok", sanitized)


# ---------------------------------------------------------------------------
# Batch validation for multiple extracted facts
# ---------------------------------------------------------------------------

def validate_facts(candidates: Dict[str, str]) -> Dict[str, str]:
    """
    Given a dict of key -> value candidates, return a dict of key -> sanitized value
    for only those that pass validation. Duplicate keys are not expected; we take the first.
    """
    result = {}
    for key, value in candidates.items():
        vr = validate_fact(key, value)
        if vr.valid and vr.sanitized_value:
            result[key] = vr.sanitized_value
    return result


# ---------------------------------------------------------------------------
# Quality checks for existing stored data (e.g. periodic cleanup)
# ---------------------------------------------------------------------------

def check_stored_fact_quality(key: str, value: Any) -> Tuple[bool, str]:
    """
    Check an already-stored fact for quality. Returns (ok, reason).
    Used by maintenance or export to flag low-quality entries.
    """
    if not isinstance(value, str):
        return False, "not a string"
    if not key:
        return False, "no key"
    if not is_allowed_fact_key(key):
        return False, "key not allowed"
    if len(value) > MAX_VALUE_LEN:
        return False, "value too long"
    if looks_like_secret(value):
        return False, "looks like secret"
    if not value.strip():
        return False, "empty"
    return True, "ok"


def filter_quality_facts(facts: Dict[str, str]) -> Dict[str, str]:
    """Return only facts that pass check_stored_fact_quality."""
    out = {}
    for k, v in facts.items():
        ok, _ = check_stored_fact_quality(k, v)
        if ok:
            out[k] = v
    return out


# ---------------------------------------------------------------------------
# Regex-based value checks (no PII, no URLs if desired)
# ---------------------------------------------------------------------------

# Optional: don't store values that look like URLs
URL_PATTERN = re.compile(
    r"https?://[^\s]+|www\.[^\s]+|[a-z0-9-]+\.(?:com|org|net|io)\b",
    re.I
)


def contains_url(value: str) -> bool:
    """True if value looks like it contains a URL."""
    return bool(value and URL_PATTERN.search(value))


def contains_email(value: str) -> bool:
    """True if value looks like an email (simple check)."""
    if not value:
        return False
    return bool(re.search(r"[a-z0-9_.+-]+@[a-z0-9-]+\.[a-z0-9-.]+", value, re.I))


# Policy: allow email only for key "email"
def should_reject_value_for_key(key: str, value: str) -> Optional[str]:
    """
    If we should reject this (key, value), return reason string; else None.
    """
    if contains_url(value) and key != "note":
        return "contains URL"
    if contains_email(value) and key not in ("email", "note"):
        return "contains email"
    return None


# ---------------------------------------------------------------------------
# Length limits per key (optional stricter limits)
# ---------------------------------------------------------------------------

MAX_LEN_BY_KEY = {
    "name": 80,
    "email": 120,
    "location": 100,
    "likes": 200,
    "favorite": 100,
    "note": 500,
    "birthday": 30,
    "work_or_study": 100,
    "goal": 200,
}


def apply_key_length_limit(key: str, value: str) -> str:
    """Truncate value to key-specific max length if defined."""
    if not value:
        return value
    max_len = MAX_LEN_BY_KEY.get(key.lower(), MAX_VALUE_LEN)
    return value[:max_len] if len(value) > max_len else value


# ---------------------------------------------------------------------------
# Export for use by memory.py: validate before set_fact
# ---------------------------------------------------------------------------

def validate_and_sanitize(key: str, value: str) -> Optional[str]:
    """
    One-shot: validate (key, value) and return sanitized value to store, or None to skip.
    """
    vr = validate_fact(key, value)
    if not vr.valid or not vr.sanitized_value:
        return None
    reject = should_reject_value_for_key(key, vr.sanitized_value)
    if reject:
        return None
    return apply_key_length_limit(key, vr.sanitized_value)
