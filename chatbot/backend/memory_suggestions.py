"""
Suggest prompts or follow-ups based on what we have (or don't have) in memory.
E.g. if we don't have a name yet, we can suggest "What's your name?" in the UI or reply.
"""
from typing import List, Optional

from memory import get_facts


# Questions we can suggest to learn more about the user
SUGGESTIONS_BY_MISSING_KEY = {
    "name": [
        "What's your name?",
        "Tell me your name and I'll remember it.",
        "You can say \"My name is ...\" and I'll remember.",
    ],
    "location": [
        "Where are you from?",
        "You can tell me where you live and I'll remember.",
    ],
    "likes": [
        "What do you like?",
        "Tell me something you're into!",
        "You can say \"I like ...\" and I'll remember.",
    ],
    "favorite": [
        "What's your favourite thing?",
        "Do you have a favourite movie or book?",
    ],
    "interested_in": [
        "What are you interested in?",
        "What would you like to learn about?",
    ],
}


def get_missing_fact_keys(session_id: str) -> List[str]:
    """Return list of fact keys we don't have yet (from a preferred set)."""
    facts = get_facts(session_id)
    preferred = ["name", "location", "likes", "favorite", "interested_in"]
    return [k for k in preferred if not facts.get(k)]


def get_suggested_prompts(session_id: str, max_count: int = 3) -> List[str]:
    """
    Suggest prompts to ask the user so we can fill in missing facts.
    E.g. if we don't have name, suggest "What's your name?"
    """
    missing = get_missing_fact_keys(session_id)
    if not missing:
        return []
    out = []
    for key in missing[:max_count]:
        options = SUGGESTIONS_BY_MISSING_KEY.get(key, [])
        if options:
            out.append(options[0])  # First suggestion per key
    return out[:max_count]


def get_welcome_sentence_if_new(session_id: str) -> Optional[str]:
    """
    If we have no facts yet, return a sentence to encourage the user to share.
    E.g. "Tell me your name or what you like and I'll remember!"
    """
    facts = get_facts(session_id)
    if facts:
        return None
    return "Tell me your name or what you like and I'll remember for next time!"


def should_suggest_remember(session_id: str) -> bool:
    """True if we have few facts and could suggest the user share more."""
    facts = get_facts(session_id)
    return len(facts) < 3


def get_remember_hint(session_id: str) -> Optional[str]:
    """
    If we have little stored, return a short hint like "You can say 'remember that ...' and I'll save it."
    """
    if not should_suggest_remember(session_id):
        return None
    return "You can say \"remember that ...\" or \"my name is ...\" and I'll remember."
