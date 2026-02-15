"""
AI Response Enhancer: improves reply quality by adding structure,
examples, and length adaptation based on context and user intent.
"""
import re
from typing import List, Optional, Tuple

try:
    from ai_reasoning import detect_intent, IntentCategory
except ImportError:
    def detect_intent(msg): return type('D', (), {'category': 'unknown', 'confidence': 0})()
    class IntentCategory:
        QUESTION_HOW = "question_how"
        QUESTION_WHY = "question_why"
        MATH_REQUEST = "math_request"
        UNKNOWN = "unknown"


# Phrases that suggest the user wants a short answer
SHORT_INDICATORS = ["quick", "brief", "short", "simple", "in one sentence", "tl dr", "tldr", "summarize", "summary"]

# Phrases that suggest the user wants detail
DETAIL_INDICATORS = ["explain", "detail", "detailed", "more", "full", "complete", "how does", "why does", "tell me about"]


def wants_short_answer(message: str) -> bool:
    """Heuristic: does the user seem to want a brief reply?"""
    if not message:
        return False
    m = message.strip().lower()
    return any(p in m for p in SHORT_INDICATORS)


def wants_detail(message: str) -> bool:
    """Heuristic: does the user seem to want a detailed reply?"""
    if not message:
        return False
    m = message.strip().lower()
    return any(p in m for p in DETAIL_INDICATORS)


def shorten_reply(reply: str, max_sentences: int = 2) -> str:
    """Keep only the first max_sentences sentences."""
    if not reply or max_sentences < 1:
        return reply or ""
    sentences = re.split(r"(?<=[.!?])\s+", reply.strip())
    if len(sentences) <= max_sentences:
        return reply.strip()
    return " ".join(sentences[:max_sentences]).strip()


def add_example_hint(reply: str, topic: str) -> str:
    """Optionally append a one-line example hint if the reply is conceptual."""
    if not reply or len(reply) > 800:
        return reply
    topic_lower = topic.lower()
    if "formula" in topic_lower or "equation" in topic_lower:
        return reply.rstrip() + " For example: 2x + 3 = 7 → x = 2."
    if "percent" in topic_lower or "percentage" in topic_lower:
        return reply.rstrip() + " For example: 10% of 50 = 5."
    return reply


def ensure_friendly_close(reply: str, intent_category: str) -> str:
    """If the reply is short and not a greeting/thanks, optionally add a brief offer to help."""
    if not reply or len(reply) < 200:
        return reply
    if "?" in reply[-20:]:
        return reply  # Already ends with question
    if any(x in reply.lower() for x in ["ask me", "just ask", "what else", "anything else"]):
        return reply
    # Don't add for math/calculation replies
    if intent_category == "math_request":
        return reply
    return reply.rstrip() + " Want to know more? Just ask!"


def enhance_reply(
    reply: str,
    user_message: str,
    apply_short: bool = True,
    apply_example: bool = False,
    apply_close: bool = False,
) -> str:
    """
    Apply shortening, example hint, or friendly close based on user message and intent.
    """
    if not reply:
        return reply
    try:
        intent = detect_intent(user_message)
        cat = getattr(intent, "category", None)
        cat_value = getattr(cat, "value", str(cat)) if hasattr(cat, "value") else str(cat)
    except Exception:
        cat_value = "unknown"

    out = reply
    if apply_short and wants_short_answer(user_message):
        out = shorten_reply(out, 2)
    if apply_example:
        out = add_example_hint(out, user_message)
    if apply_close:
        out = ensure_friendly_close(out, cat_value)
    return out


def suggest_follow_ups(reply: str, user_message: str, existing_suggestions: List[str]) -> List[str]:
    """
    Optionally add or reorder follow-up suggestions based on reply content and intent.
    """
    if not existing_suggestions:
        return []
    try:
        intent = detect_intent(user_message)
        cat = getattr(intent, "category", None)
        cat_value = getattr(cat, "value", str(cat)) if hasattr(cat, "value") else str(cat)
    except Exception:
        return existing_suggestions[:6]
    # Cap at 6
    return list(existing_suggestions)[:6]
