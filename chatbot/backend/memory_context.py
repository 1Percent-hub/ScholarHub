"""
Build context strings from memory (facts + recent conversation) for use in
reply generation or future features (e.g. "You asked about X last time").
"""
from typing import Dict, List, Optional, Any

from memory import get_facts, get_recent, get_last_topic


def build_facts_context(session_id: str) -> str:
    """
    Build a one-line summary of stored facts for internal use.
    E.g. "User name: Alex. Likes: dogs. From: Hawaii."
    """
    facts = get_facts(session_id)
    if not facts:
        return ""
    parts = []
    key_order = ["name", "location", "likes", "dislikes", "favorite", "role", "interested_in"]
    for k in key_order:
        if k in facts and facts[k]:
            parts.append(f"{k}: {facts[k]}")
    for k, v in facts.items():
        if k not in key_order and v:
            parts.append(f"{k}: {v}")
    return " | ".join(parts)[:500] if parts else ""


def build_recent_context(session_id: str, max_turns: int = 5) -> str:
    """
    Build a short summary of recent user messages (not bot replies) for context.
    """
    recent = get_recent(session_id, max_turns)
    if not recent:
        return ""
    parts = []
    for ex in recent:
        u = (ex.get("user") or "").strip()
        if u and len(u) < 100:
            parts.append(u)
    return " | ".join(parts)[:400] if parts else ""


def get_last_topic_sentence(session_id: str) -> Optional[str]:
    """
    If we have a last topic, return a sentence like "Last time you asked about X."
    Otherwise None.
    """
    topic = get_last_topic(session_id)
    if not topic or len(topic) < 2:
        return None
    return f"Last time you asked about something like \"{topic}\"."


def should_prepend_last_topic(reply: str, session_id: str) -> bool:
    """
    Decide whether to prepend a "Last time you asked about X" to the reply.
    Only for fallback / unsure replies to avoid clutter.
    """
    if not reply or "not sure" not in reply.lower():
        return False
    if "try asking" not in reply.lower():
        return False
    topic = get_last_topic(session_id)
    return bool(topic and len(topic) > 2)


def inject_context_into_fallback(reply: str, session_id: str) -> str:
    """
    If the reply is a fallback ("I'm not sure..."), optionally prepend
    a sentence about last topic for continuity.
    """
    if not should_prepend_last_topic(reply, session_id):
        return reply
    sentence = get_last_topic_sentence(session_id)
    if sentence:
        return sentence + " " + reply
    return reply


def get_personalization_hints(session_id: str) -> Dict[str, Any]:
    """
    Return a dict of hints for personalization: name, has_name, has_likes, etc.
    Used by memory_engine or memory_personalize to decide how to tailor the reply.
    """
    facts = get_facts(session_id)
    name = facts.get("name")
    likes = facts.get("likes") or facts.get("favorite")
    return {
        "name": name,
        "has_name": bool(name),
        "has_likes": bool(likes),
        "likes": likes,
        "location": facts.get("location"),
        "all_facts": facts,
    }


def format_recent_for_display(session_id: str, max_turns: int = 5) -> str:
    """
    Format recent conversation for display (e.g. in a "recent" panel or debug).
    """
    recent = get_recent(session_id, max_turns)
    if not recent:
        return "No recent conversation."
    lines = []
    for i, ex in enumerate(recent[-max_turns:], 1):
        u = ex.get("user", "")
        b = (ex.get("bot", "") or "")[:80]
        if b:
            b = b + "..." if len(ex.get("bot", "")) > 80 else b
        lines.append(f"{i}. You: {u[:60]}")
        if b:
            lines.append(f"   Josiah: {b}")
    return "\n".join(lines)


def context_summary(session_id: str) -> str:
    """
    Full context summary: facts + last topic + count of recent exchanges.
    For logging or future model-based reply generation.
    """
    facts = get_facts(session_id)
    topic = get_last_topic(session_id)
    recent = get_recent(session_id, 10)
    parts = []
    if facts:
        parts.append("Facts: " + build_facts_context(session_id))
    if topic:
        parts.append("Last topic: " + topic)
    if recent:
        parts.append(f"Recent exchanges: {len(recent)}")
    return " | ".join(parts) if parts else "No context."
