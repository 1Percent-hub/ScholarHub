"""
Natural-language response variants for memory commands.
Provides multiple reply options so the bot doesn't sound repetitive when
users ask "what do you remember?", "forget my name", etc.
"""
import random
from typing import List, Optional

from memory import get_facts, format_facts_for_display


def _pick(choices: List[str]) -> str:
    """Return a random choice from the list."""
    return random.choice(choices) if choices else ""


# ---------------------------------------------------------------------------
# Recall / what do you remember
# ---------------------------------------------------------------------------

RECALL_EMPTY = [
    "I don't have anything stored about you yet. Tell me your name, what you like, or say \"remember that ...\" and I'll remember!",
    "Nothing yet! Share something—like your name or what you're into—and I'll remember it.",
    "My memory's empty for you so far. Tell me a bit about yourself and I'll keep track.",
]

RECALL_HAS_FACTS = [
    "Here's what I remember: {facts}",
    "I've got this stored: {facts}",
    "Sure! {facts}",
]


def get_recall_reply(session_id: str) -> str:
    """Get a reply for 'what do you remember?'"""
    facts = get_facts(session_id)
    if not facts:
        return _pick(RECALL_EMPTY)
    formatted = format_facts_for_display(facts)
    templates = [t.format(facts=formatted) for t in RECALL_HAS_FACTS if "{facts}" in t]
    if templates:
        return _pick(templates)
    return formatted


# ---------------------------------------------------------------------------
# Forget name
# ---------------------------------------------------------------------------

FORGET_NAME_REPLIES = [
    "I've forgotten your name. You can tell me again anytime.",
    "Done. I no longer remember your name. Say it again whenever you like.",
    "Cleared. I won't use your name until you tell me again.",
]


def get_forget_name_reply() -> str:
    return _pick(FORGET_NAME_REPLIES)


# ---------------------------------------------------------------------------
# Clear all memory
# ---------------------------------------------------------------------------

CLEAR_ALL_REPLIES = [
    "I've cleared my memory about you. I won't remember anything from before.",
    "All cleared. I've forgotten everything you told me.",
    "Done. My memory about you is reset. Tell me again if you'd like me to remember something.",
]


def get_clear_all_reply() -> str:
    return _pick(CLEAR_ALL_REPLIES)


# ---------------------------------------------------------------------------
# Forget likes
# ---------------------------------------------------------------------------

FORGET_LIKES_REPLIES = [
    "I've forgotten what you like. Tell me again if you want me to remember.",
    "Cleared. I no longer remember your likes or favourites.",
    "Done. I've forgotten your preferences.",
]


def get_forget_likes_reply() -> str:
    return _pick(FORGET_LIKES_REPLIES)


# ---------------------------------------------------------------------------
# Remember me? / Do you remember me?
# ---------------------------------------------------------------------------

REMEMBER_ME_YES = [
    "Yes! {facts}",
    "I do! {facts}",
    "Sure do. {facts}",
]

REMEMBER_ME_NO = [
    "I don't have anything stored yet. Tell me your name or something you like and I'll remember.",
    "Not yet! Share your name or a fact and I'll remember you next time.",
    "My memory's empty for you. Tell me a bit about yourself!",
]


def get_remember_me_reply(session_id: str) -> str:
    facts = get_facts(session_id)
    if not facts:
        return _pick(REMEMBER_ME_NO)
    formatted = format_facts_for_display(facts)
    return _pick(REMEMBER_ME_YES).format(facts=formatted)


# ---------------------------------------------------------------------------
# Who am I? / What do you know about me?
# ---------------------------------------------------------------------------

WHO_AM_I_HAS_NAME = [
    "You're {name}! {rest}",
    "You're {name}. {rest}",
]

WHO_AM_I_NO_NAME = [
    "I have this stored: {facts}",
    "Here's what I know: {facts}",
]


def get_who_am_i_reply(session_id: str) -> str:
    facts = get_facts(session_id)
    name = facts.get("name")
    if name:
        rest_facts = {k: v for k, v in facts.items() if k != "name"}
        if rest_facts:
            rest = format_facts_for_display(rest_facts)
            return _pick(WHO_AM_I_HAS_NAME).format(name=name, rest=rest)
        return f"You're {name}! Tell me more about yourself and I'll remember."
    return _pick(WHO_AM_I_NO_NAME).format(facts=format_facts_for_display(facts))


# ---------------------------------------------------------------------------
# Unified: get reply for any memory command
# ---------------------------------------------------------------------------

def get_memory_command_reply(command: str, session_id: str) -> Optional[str]:
    """
    Return a natural-language reply for the given memory command.
    Returns None if the command is not recognised.
    """
    if command == "recall":
        return get_recall_reply(session_id)
    if command == "forget_name":
        return get_forget_name_reply()
    if command == "clear_all":
        return get_clear_all_reply()
    if command == "forget_likes":
        return get_forget_likes_reply()
    if command == "remember_me":
        return get_remember_me_reply(session_id)
    if command == "who_am_i":
        return get_who_am_i_reply(session_id)
    return None
