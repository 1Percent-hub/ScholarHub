"""
Memory-aware reply engine: wraps the knowledge engine with persistent memory,
fact extraction, memory commands, and personalized responses.
"""
import re
from typing import Tuple, List, Optional

from knowledge_engine import get_reply as get_reply_from_knowledge

from memory import (
    detect_memory_command,
    get_memory_reply_for_command,
    get_facts,
    update_facts_from_message,
    add_recent,
    get_recent,
    get_last_topic,
)

try:
    from memory_personalize import apply_all_personalization, get_personalized_suggestions
except ImportError:
    def apply_all_personalization(reply: str, session_id: str, **kwargs) -> str:
        return reply
    def get_personalized_suggestions(session_id: str, base: List[str]) -> List[str]:
        return base

try:
    from memory_suggestions import (
        get_suggested_prompts,
        get_remember_hint,
        get_welcome_sentence_if_new,
    )
except ImportError:
    def get_suggested_prompts(session_id: str, max_count: int = 3) -> List[str]:
        return []
    def get_remember_hint(session_id: str) -> Optional[str]:
        return None
    def get_welcome_sentence_if_new(session_id: str) -> Optional[str]:
        return None


# Greeting-style replies that we can personalize with the user's name
GREETING_STARTS = (
    "hey!",
    "hey ",
    "hi there!",
    "hi there ",
    "hello!",
    "hello ",
    "hi!",
    "hi ",
    "howdy!",
    "howdy ",
    "good morning!",
    "good morning ",
    "good afternoon!",
    "good afternoon ",
    "good evening!",
    "good evening ",
    "i'm doing great",
    "all good on my end",
    "glad that helped",
    "sure thing",
    "go ahead!",
    "of course!",
    "yes!",
    "welcome back!",
    "nice to meet you",
)


def _personalize_reply(reply: str, session_id: str) -> str:
    """
    If we have the user's name and the reply looks like a greeting or direct address,
    prepend their name or replace a generic greeting so it feels personal.
    """
    if not reply or not session_id:
        return reply
    facts = get_facts(session_id)
    name = facts.get("name")
    if not name or len(name) > 80:
        return reply
    name = name.strip()
    reply_lower = reply.lower()
    # Already mentions their name?
    if name.lower() in reply_lower:
        return reply
    # Greeting-style: "Hey! I'm Josiah..." -> "Hey Alex! I'm Josiah..."
    for start in GREETING_STARTS:
        if reply_lower.startswith(start):
            # Insert name after the greeting word(s)
            rest = reply[len(start):].lstrip()
            if not rest or rest[0].isupper():
                personalized = reply[: len(start)].rstrip()
                if not personalized.endswith("!"):
                    personalized = personalized.rstrip(",")
                if personalized:
                    return personalized + " " + name + "! " + rest
            break
    # "What can I do for you?" at start -> "What can I do for you, Alex?"
    if reply_lower.startswith("what can i do for you"):
        idx = reply.find("?")
        if idx != -1:
            return reply[: idx] + ", " + name + "?" + reply[idx + 1 :]
    return reply


def _topic_hint_from_message(message: str) -> Optional[str]:
    """Very simple topic hint from first few words for memory."""
    if not message:
        return None
    m = message.strip().lower()[:100]
    # Remove question words
    for w in ("what", "who", "where", "when", "why", "how", "is", "are", "the", "a", "an"):
        m = re.sub(r"\b" + w + r"\b", "", m)
    m = re.sub(r"\s+", " ", m).strip()
    return m[:80] if m else None


def get_reply_with_memory(
    message: str, session_id: str
) -> Tuple[str, List[str], Optional[str]]:
    """
    Get a reply using the knowledge engine, with advanced memory:
    - Handles memory commands (what do you remember, forget my name, clear memory).
    - Extracts and stores facts from the message (name, likes, etc.).
    - Personalizes replies with the user's name when appropriate.
    - Saves this exchange to recent conversation history.
    """
    session_id = (session_id or "default").strip() or "default"
    message = (message or "").strip()
    if not message:
        hint = get_remember_hint(session_id) or get_welcome_sentence_if_new(session_id)
        return "Please type something!", [], hint

    # 1) Memory command?
    cmd = detect_memory_command(message)
    if cmd is not None:
        reply = get_memory_reply_for_command(cmd, session_id)
        if reply:
            add_recent(session_id, message, reply, topic_hint="memory")
            sug = [
                "What is the capital of France?",
                "Tell me a fun fact",
                "How does the heart work?",
            ]
            hint = get_remember_hint(session_id)
            return reply, sug, hint
        # Fall through to normal reply

    # 2) Extract and save facts from this message
    update_facts_from_message(session_id, message)

    # 3) Get reply from knowledge engine
    reply, suggested = get_reply_from_knowledge(message)

    # 4) Personalize with name and optional last-topic
    reply = _personalize_reply(reply, session_id)
    reply = apply_all_personalization(reply, session_id, use_last_topic=True)
    try:
        from memory_context import inject_context_into_fallback
        reply = inject_context_into_fallback(reply, session_id)
    except ImportError:
        pass

    # 5) Optionally personalize suggested questions from memory
    suggested = get_personalized_suggestions(session_id, suggested)
    # 5b) If we have few facts, prepend memory-building prompts (e.g. "What's your name?")
    memory_prompts = get_suggested_prompts(session_id, max_count=2)
    for p in reversed(memory_prompts):
        if p and p not in suggested:
            suggested = [p] + suggested
    suggested = suggested[:6]  # cap total

    # 6) Save to recent history
    add_recent(session_id, message, reply, topic_hint=_topic_hint_from_message(message))

    # 7) Optional hint for new users ("You can say 'remember that...'")
    hint = get_remember_hint(session_id) or get_welcome_sentence_if_new(session_id)
    return reply, suggested, hint
