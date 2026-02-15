"""
Helper functions for building and enriching chatbot responses.
Used to keep app.py thin and centralise reply logic.
"""
from typing import List, Optional


def truncate_for_display(text: str, max_len: int = 2000) -> str:
    """Ensure reply is not excessively long for the UI."""
    if not text or len(text) <= max_len:
        return text or ""
    return text[: max_len - 3].rstrip() + "..."


def ensure_non_empty_suggestions(suggested: List[str], min_count: int = 3) -> List[str]:
    """Return a list with at least min_count items by duplicating if needed (caller should pass enough)."""
    if not suggested:
        return []
    result = list(suggested)
    while len(result) < min_count and result:
        result.extend(result[: min_count - len(result)])
    return result[: min_count + 5]


def strip_reply(reply: str) -> str:
    """Remove leading/trailing whitespace and collapse internal newlines to spaces for consistency."""
    if not reply:
        return ""
    return " ".join(reply.strip().split())


def format_suggested_questions(questions: List[str], max_questions: int = 6) -> List[str]:
    """Take a list of suggested questions and return up to max_questions, trimmed."""
    if not questions:
        return []
    out = []
    seen = set()
    for q in questions:
        if len(out) >= max_questions:
            break
        s = (q or "").strip()
        if not s or len(s) > 120:
            continue
        key = s.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(s)
    return out


def fallback_message(topic_hint: Optional[str] = None) -> str:
    """Default message when no knowledge match is found."""
    base = (
        "I'm not sure about that. Try asking about space, Earth, animals, "
        "the human body, science, technology, history, geography, health, "
        "music, sports, maths, or ask for a fun fact or a joke!"
    )
    if topic_hint:
        return base + " You could try: " + topic_hint
    return base


def sanitise_reply_for_json(text: str) -> str:
    """Ensure the reply string is safe for JSON (no control characters)."""
    if not text:
        return ""
    return "".join(c for c in text if ord(c) >= 32 or c in "\n\t")


def clamp_suggestion_count(suggested: List[str], min_c: int = 2, max_c: int = 8) -> List[str]:
    """Return a sublist of suggested with length between min_c and max_c."""
    if not suggested:
        return []
    n = len(suggested)
    if n <= max_c and n >= min_c:
        return list(suggested)
    if n < min_c:
        return list(suggested) + (suggested * (min_c - n))[: min_c - n]
    return list(suggested[:max_c])
