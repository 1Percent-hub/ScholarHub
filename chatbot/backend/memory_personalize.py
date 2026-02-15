"""
Personalization rules and templates: use stored facts to tailor replies
so the bot feels like it remembers the user (name, likes, last topic).
"""
import re
from typing import Optional, Dict, List

from memory import get_facts, get_last_topic, get_recent


def personalize_greeting(reply: str, session_id: str) -> str:
    """
    If the reply is a generic greeting and we have the user's name,
    insert their name so it reads "Hey Alex!" instead of "Hey!".
    """
    if not reply or not session_id:
        return reply
    facts = get_facts(session_id)
    name = facts.get("name")
    if not name or len(name) > 80:
        return reply
    name = name.strip()
    r = reply.strip()
    r_lower = r.lower()
    # Already has their name?
    if name.lower() in r_lower:
        return reply
    # "Hey! I'm Josiah..." -> "Hey Alex! I'm Josiah..."
    for prefix in ("hey! ", "hey! i'm", "hi there! ", "hi there! i'm", "hello! ", "hello! i'm", "hi! ", "hi! i'm"):
        if r_lower.startswith(prefix):
            insert_pos = len(prefix) - len(" i'm") if " i'm" in prefix else len(prefix)
            head = r[: insert_pos].rstrip()
            if not head.endswith("!"):
                head = head.rstrip(",")
            tail = r[insert_pos:].lstrip()
            return head + " " + name + "! " + tail
    # "Hey! What can I do..." -> "Hey Alex! What can I do..."
    for prefix in ("hey! what", "hi! what", "hello! what", "hey! how", "hi! how"):
        if r_lower.startswith(prefix):
            head = prefix.split("!")[0] + "!"
            tail = r[len(head):].lstrip()
            return head + " " + name + "! " + tail
    return reply


def personalize_signoff(reply: str, session_id: str) -> str:
    """Add a personal touch at the end, e.g. ', Alex' after 'What can I do for you?'"""
    if not reply or not session_id:
        return reply
    facts = get_facts(session_id)
    name = facts.get("name")
    if not name or len(name) > 80:
        return reply
    name = name.strip()
    r_lower = reply.lower()
    if "what can i do for you?" in r_lower and name.lower() not in reply.lower():
        return reply.replace("?", ", " + name + "?", 1)
    if "what would you like to know?" in r_lower and name.lower() not in reply.lower():
        return reply.replace("?", ", " + name + "?", 1)
    return reply


def inject_last_topic(reply: str, session_id: str) -> str:
    """
    If we have a last topic and the reply is a fallback ("I'm not sure..."),
    optionally prepend "Last time you asked about X. " for continuity.
    """
    if not reply or not session_id:
        return reply
    last = get_last_topic(session_id)
    if not last or len(last) < 2:
        return reply
    if "not sure" not in reply.lower() and "try asking" not in reply.lower():
        return reply
    # Don't repeat every time; only if it adds value
    if last in reply:
        return reply
    return "Last time you asked about something like \"" + last + "\". " + reply


def apply_all_personalization(reply: str, session_id: str, *, use_last_topic: bool = False) -> str:
    """
    Run all personalization steps: greeting, signoff, and optionally last-topic.
    """
    if not reply:
        return reply
    r = personalize_greeting(reply, session_id)
    r = personalize_signoff(r, session_id)
    if use_last_topic:
        r = inject_last_topic(r, session_id)
    return r


# ---------------------------------------------------------------------------
# Reply templates that can include {{name}} or other facts
# ---------------------------------------------------------------------------

PERSONALIZED_TEMPLATES = {
    "welcome_back": "Welcome back, {{name}}! What would you like to know?",
    "ask_again": "Sure, {{name}}. What's your question?",
    "thanks_name": "You're welcome, {{name}}!",
    "anything_else_name": "Anything else, {{name}}?",
}


def fill_template(template: str, session_id: str) -> str:
    """Replace {{name}}, {{likes}}, etc. with stored facts."""
    if "{{" not in template:
        return template
    facts = get_facts(session_id)
    result = template
    for key, value in facts.items():
        if value and isinstance(value, str):
            result = result.replace("{{" + key + "}}", value)
    # Remove any unfilled placeholders
    result = re.sub(r"\s*\{\{[^}]+\}\}\s*", " ", result)
    return re.sub(r"\s+", " ", result).strip()


def get_personalized_suggestions(session_id: str, base_suggestions: List[str]) -> List[str]:
    """
    Optionally reorder or add suggestions based on memory (e.g. if they like space,
    put space questions higher). For now just returns base_suggestions unchanged.
    """
    facts = get_facts(session_id)
    if not facts:
        return base_suggestions
    likes = facts.get("likes", "").lower()
    interested = facts.get("interested_in", "").lower()
    # If they mentioned an interest, we could prepend a suggestion about it
    if interested and len(base_suggestions) > 0:
        # e.g. "Tell me more about " + interested
        extra = "Tell me more about " + interested
        if extra not in base_suggestions:
            return [extra] + base_suggestions[:5]
    return base_suggestions
