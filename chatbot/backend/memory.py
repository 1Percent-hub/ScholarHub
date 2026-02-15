"""
Advanced memory for the chatbot: persistent user facts, conversation history,
and personalization. Uses a JSON file for storage (no database required).
"""
import os
import re
import json
import threading
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple

# Path to the memory file (in backend folder)
MEMORY_DIR = os.path.dirname(os.path.abspath(__file__))
MEMORY_FILE = os.path.join(MEMORY_DIR, "chatbot_memory.json")
_LOCK = threading.Lock()

# Max recent exchanges to keep per session
MAX_RECENT = 50
# Max facts per session
MAX_FACTS = 100
# Max length of a stored fact value
MAX_FACT_VALUE_LEN = 500


def _load_all() -> Dict[str, Any]:
    """Load full memory store from disk."""
    with _LOCK:
        if not os.path.exists(MEMORY_FILE):
            return {"sessions": {}, "meta": {"version": 1}}
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"sessions": {}, "meta": {"version": 1}}


def _save_all(data: Dict[str, Any]) -> None:
    """Write full memory store to disk."""
    with _LOCK:
        data.setdefault("meta", {})["last_updated"] = datetime.utcnow().isoformat()
        try:
            with open(MEMORY_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception:
            pass


def _get_session(data: Dict[str, Any], session_id: str) -> Dict[str, Any]:
    """Get or create session dict."""
    sessions = data.setdefault("sessions", {})
    if session_id not in sessions:
        sessions[session_id] = {
            "facts": {},
            "recent": [],
            "topics": [],
            "created": datetime.utcnow().isoformat(),
            "updated": datetime.utcnow().isoformat(),
        }
    return sessions[session_id]


# ---------------------------------------------------------------------------
# Fact extraction: detect "my name is X", "I like Y", etc.
# ---------------------------------------------------------------------------

EXTRACT_PATTERNS = [
    # (regex, fact_key, group_index or None to use full match)
    (r"\b(?:my name is|i'm called|call me|name is|i am)\s+([a-z][a-z\s\-']{0,48})", "name", 1),
    (r"\b(?:i'm|i am)\s+([a-z][a-z\s\-']{0,48}?)(?:\s*\.|,|\s+and\s+|$)", "name", 1),
    (r"\b(?:i (?:am from|live in|live at)|from)\s+([a-z][a-z0-9\s,\-']{0,48})", "location", 1),
    (r"\b(?:i (?:like|love|enjoy)|i'm into)\s+([a-z][a-z0-9\s,&\-']{0,48})", "likes", 1),
    (r"\b(?:i (?:don't like|hate|dislike))\s+([a-z][a-z0-9\s,&\-']{0,48})", "dislikes", 1),
    (r"\b(?:i (?:am|'m) a)\s+([a-z][a-z0-9\s\-']{0,48})", "role", 1),
    (r"\b(?:my (?:favorite|favourite) (?:is|thing is))\s+([a-z][a-z0-9\s\-']{0,48})", "favorite", 1),
    (r"\b(?:my (?:favorite|favourite))\s+([a-z][a-z0-9\s\-']{0,48})\s+is", "favorite", 1),
    (r"\b(?:remember that|don't forget)\s+(.+?)(?:\.|$)", "note", 1),
    (r"\b(?:i (?:have|got) a)\s+([a-z][a-z0-9\s\-']{0,30})", "has", 1),
    (r"\b(?:i'm (?:interested in|curious about))\s+([a-z][a-z0-9\s,&\-']{0,48})", "interested_in", 1),
    (r"\b(?:my (?:birthday|bday) is)\s+([a-z0-9\s\-\/]{3,30})", "birthday", 1),
    (r"\b(?:i (?:work|study) (?:at|in))\s+([a-z][a-z0-9\s\-']{0,48})", "work_or_study", 1),
    (r"\b(?:my (?:mom|mother|dad|father) (?:is|name is))\s+([a-z][a-z\s\-']{0,40})", "family", 1),
    (r"\b(?:my (?:dog|cat|pet) (?:is named|is called)|(?:dog|cat|pet) name)\s+([a-z][a-z0-9\s\-']{0,30})", "pet_name", 1),
]


def _normalize_for_extract(text: str) -> str:
    """Lowercase and collapse space for pattern matching."""
    if not text:
        return ""
    return re.sub(r"\s+", " ", text.strip().lower())


def extract_facts(message: str) -> Dict[str, str]:
    """
    Extract memory-worthy facts from a user message.
    Returns a dict of fact_key -> value (e.g. {"name": "Alex", "likes": "dogs"}).
    """
    if not message or len(message) > 2000:
        return {}
    text = _normalize_for_extract(message)
    if len(text) < 3:
        return {}
    facts = {}
    for pattern, key, group_idx in EXTRACT_PATTERNS:
        try:
            m = re.search(pattern, text, re.IGNORECASE)
            if m:
                val = m.group(group_idx).strip() if group_idx is not None else m.group(0).strip()
                val = re.sub(r"\s+", " ", val)[:MAX_FACT_VALUE_LEN]
                if len(val) >= 2:
                    facts[key] = val
        except (IndexError, AttributeError):
            continue
    # "remember X" / "store that X" style
    for prefix in ("remember ", "store ", "save ", "don't forget "):
        if text.startswith(prefix):
            rest = text[len(prefix):].strip()
            if len(rest) >= 2 and len(rest) <= MAX_FACT_VALUE_LEN:
                facts["note"] = rest
            break
    return facts


# ---------------------------------------------------------------------------
# Memory commands: "what do you remember", "forget my name", "clear memory"
# ---------------------------------------------------------------------------

MEMORY_COMMAND_PATTERNS = [
    (r"^(?:what (?:do you |did you )?remember|what (?:have you )?got (?:stored|saved)|recall|your memory)\??\s*$", "recall"),
    (r"^(?:forget (?:my )?name|clear my name|remove my name)\??\s*$", "forget_name"),
    (r"^(?:forget (?:that |what you know |everything about me)|clear (?:my )?memory|wipe (?:my )?memory|reset memory)\??\s*$", "clear_all"),
    (r"^(?:forget (?:that i (?:like|love)|my (?:likes?|favorites?))\??\s*$)", "forget_likes"),
    (r"^(?:do you remember me|remember me\??)\s*$", "remember_me"),
    (r"^(?:who am i|what do you know about me)\??\s*$", "who_am_i"),
    (r"^(?:what (?:did you |do you )?remember about me)\??\s*$", "recall"),
    (r"^(?:show (?:me )?(?:my )?memory|display memory|list (?:my )?facts)\??\s*$", "recall"),
    (r"^(?:erase (?:my )?name|delete my name)\??\s*$", "forget_name"),
    (r"^(?:erase (?:my )?memory|delete (?:my )?memory|clear (?:my )?data)\??\s*$", "clear_all"),
    (r"^(?:do you know (?:my )?name|remember my name)\??\s*$", "remember_me"),
    (r"^(?:what (?:is )?my name|who (?:am )?i (?:again)?)\??\s*$", "who_am_i"),
]


def detect_memory_command(message: str) -> Optional[str]:
    """If the message is a memory-related command, return the command id; else None."""
    if not message:
        return None
    text = _normalize_for_extract(message)
    for pattern, cmd in MEMORY_COMMAND_PATTERNS:
        if re.match(pattern, text, re.IGNORECASE):
            return cmd
    return None


# ---------------------------------------------------------------------------
# Public API: get/set facts, recent, and handle commands
# ---------------------------------------------------------------------------

def get_facts(session_id: str) -> Dict[str, str]:
    """Return all stored facts for this session."""
    data = _load_all()
    session = _get_session(data, session_id)
    return dict(session.get("facts", {}))


def set_fact(session_id: str, key: str, value: str) -> None:
    """Set one fact. Key should be lowercase; value is trimmed and length-limited."""
    if not key or not isinstance(value, str):
        return
    key = key.strip().lower()[:100]
    if not key:
        return
    try:
        from memory_validation import validate_and_sanitize
        value = validate_and_sanitize(key, value)
        if value is None:
            return
    except ImportError:
        value = value.strip()[:MAX_FACT_VALUE_LEN]
    data = _load_all()
    session = _get_session(data, session_id)
    facts = session.setdefault("facts", {})
    facts[key] = value
    while len(facts) > MAX_FACTS:
        # Remove oldest by deleting first key (dict order is insertion order in Py3)
        k = next(iter(facts))
        del facts[k]
    session["updated"] = datetime.utcnow().isoformat()
    _save_all(data)


def update_facts_from_message(session_id: str, message: str) -> Dict[str, str]:
    """
    Extract facts from the message and save them. Returns the facts that were saved.
    Skips if the message looks like a general question (e.g. "what is the capital of X").
    """
    try:
        from memory_utils import should_skip_storing, is_safe_to_store, clean_fact_value
        if should_skip_storing(message):
            return {}
    except ImportError:
        pass
    extracted = extract_facts(message)
    if not extracted:
        return {}
    try:
        from memory_utils import is_safe_to_store, clean_fact_value
        extracted = {k: clean_fact_value(v) or v for k, v in extracted.items() if v}
        extracted = {k: v for k, v in extracted.items() if is_safe_to_store(k, v)}
        if not extracted:
            return {}
    except ImportError:
        pass
    data = _load_all()
    session = _get_session(data, session_id)
    facts = session.setdefault("facts", {})
    for k, v in extracted.items():
        facts[k] = v
    while len(facts) > MAX_FACTS:
        k = next(iter(facts))
        del facts[k]
    session["updated"] = datetime.utcnow().isoformat()
    _save_all(data)
    return extracted


def add_recent(session_id: str, user_message: str, bot_reply: str, topic_hint: Optional[str] = None) -> None:
    """Append one exchange to recent conversation history."""
    if not session_id:
        return
    data = _load_all()
    session = _get_session(data, session_id)
    recent = session.setdefault("recent", [])
    recent.append({
        "user": (user_message or "")[:500],
        "bot": (bot_reply or "")[:1000],
        "topic": (topic_hint or "")[:100],
        "at": datetime.utcnow().isoformat(),
    })
    while len(recent) > MAX_RECENT:
        recent.pop(0)
    if topic_hint:
        topics = session.setdefault("topics", [])
        topics.append(topic_hint[:80])
        while len(topics) > 20:
            topics.pop(0)
    session["updated"] = datetime.utcnow().isoformat()
    _save_all(data)


def get_recent(session_id: str, n: int = 10) -> List[Dict[str, str]]:
    """Get the last n exchanges (each has 'user', 'bot', 'topic', 'at')."""
    data = _load_all()
    session = _get_session(data, session_id)
    recent = session.get("recent", [])
    return list(recent[-n:]) if recent else []


def get_last_topic(session_id: str) -> Optional[str]:
    """Get the last topic the user asked about (if we stored it)."""
    data = _load_all()
    session = _get_session(data, session_id)
    topics = session.get("topics", [])
    return topics[-1] if topics else None


def clear_all_facts(session_id: str) -> None:
    """Remove all facts for this session."""
    data = _load_all()
    session = _get_session(data, session_id)
    session["facts"] = {}
    session["updated"] = datetime.utcnow().isoformat()
    _save_all(data)


def forget_fact(session_id: str, key: str) -> bool:
    """Remove one fact. Returns True if it existed."""
    data = _load_all()
    session = _get_session(data, session_id)
    facts = session.get("facts", {})
    key = key.strip().lower()
    if key in facts:
        del facts[key]
        session["updated"] = datetime.utcnow().isoformat()
        _save_all(data)
        return True
    return False


def format_facts_for_display(facts: Dict[str, str]) -> str:
    """Turn facts dict into a short human-readable summary."""
    if not facts:
        return "I don't have anything stored about you yet. Tell me your name, what you like, or say \"remember that ...\" and I'll remember!"
    labels = {
        "name": "Name",
        "location": "From / live",
        "likes": "Likes",
        "dislikes": "Dislikes",
        "favorite": "Favourite",
        "role": "Role",
        "note": "Note",
        "interested_in": "Interested in",
        "birthday": "Birthday",
        "work_or_study": "Work / study",
        "family": "Family",
        "pet_name": "Pet's name",
        "has": "Has",
        "friend_name": "Friend's name",
        "school": "School",
        "job": "Job",
        "born_in": "Born in",
        "email": "Email",
        "favorite_color": "Favourite colour",
        "favorite_food": "Favourite food",
        "favorite_movie": "Favourite movie",
        "favorite_sport": "Favourite sport",
        "pet": "Pet",
        "hobby": "Hobby",
        "language": "Language",
        "goal": "Goal",
    }
    parts = []
    for k, v in facts.items():
        label = labels.get(k, k.replace("_", " ").title())
        parts.append(f"{label}: {v}")
    return "Here's what I remember: " + "; ".join(parts) + "."


def get_conversation_summary(session_id: str, max_turns: int = 5) -> str:
    """
    Build a short text summary of the last few exchanges for context.
    Used so the bot could (in future) refer to recent conversation.
    """
    recent = get_recent(session_id, max_turns)
    if not recent:
        return ""
    parts = []
    for ex in recent:
        u = (ex.get("user") or "").strip()[:80]
        if u:
            parts.append("User: " + u)
    return " | ".join(parts) if parts else ""


def get_context_for_reply(session_id: str) -> Dict[str, Any]:
    """
    Gather all memory context (facts, last topic, recent summary) for use in reply generation.
    """
    facts = get_facts(session_id)
    last_topic = get_last_topic(session_id)
    recent = get_recent(session_id, 3)
    summary = get_conversation_summary(session_id, 5)
    return {
        "facts": facts,
        "name": facts.get("name"),
        "last_topic": last_topic,
        "recent": recent,
        "summary": summary,
    }


def merge_fact_into_reply(reply: str, session_id: str, fact_key: str, template: str) -> str:
    """
    If we have a fact and the reply contains a placeholder, replace it.
    template e.g. "Hey {{name}}, ..." -> "Hey Alex, ..."
    """
    facts = get_facts(session_id)
    value = facts.get(fact_key)
    if not value or "{{" not in template:
        return reply
    placeholder = "{{" + fact_key + "}}"
    if placeholder in reply:
        return reply.replace(placeholder, value)
    return reply


# ---------------------------------------------------------------------------
# More extraction patterns: additional ways users share info
# ---------------------------------------------------------------------------

EXTRACT_PATTERNS_EXTRA = [
    (r"\b(?:my (?:best )?friend (?:is named|is called)|friend'?s name)\s+([a-z][a-z0-9\s\-']{0,30})", "friend_name", 1),
    (r"\b(?:i (?:go to|attend) (?:school|college|university at)?)\s+([a-z][a-z0-9\s\-']{0,48})", "school", 1),
    (r"\b(?:my (?:job|work) is)\s+([a-z][a-z0-9\s\-']{0,48})", "job", 1),
    (r"\b(?:i (?:was born in|grew up in))\s+([a-z][a-z0-9\s,\-']{0,48})", "born_in", 1),
    (r"\b(?:my (?:email|e-mail) is)\s+([a-z0-9@.\-]+)", "email", 1),
    (r"\b(?:my (?:favorite|favourite) (?:color|colour) is)\s+([a-z][a-z0-9\s\-']{0,20})", "favorite_color", 1),
    (r"\b(?:my (?:favorite|favourite) (?:food|meal) is)\s+([a-z][a-z0-9\s\-']{0,30})", "favorite_food", 1),
    (r"\b(?:my (?:favorite|favourite) (?:movie|film) is)\s+([a-z0-9][a-z0-9\s\-':&]{0,40})", "favorite_movie", 1),
    (r"\b(?:my (?:favorite|favourite) (?:sport|team) is)\s+([a-z][a-z0-9\s\-']{0,30})", "favorite_sport", 1),
    (r"\b(?:i (?:have|got) (?:a )?pet)\s+([a-z][a-z0-9\s\-']{0,30})", "pet", 1),
    (r"\b(?:my (?:hobby|hobbies) (?:is|are))\s+([a-z][a-z0-9\s,&\-']{0,48})", "hobby", 1),
    (r"\b(?:i (?:speak|know) (?:the )?language)\s+([a-z][a-z0-9\s\-']{0,30})", "language", 1),
    (r"\b(?:my (?:dream|goal) is to)\s+([a-z][a-z0-9\s\-']{0,48})", "goal", 1),
    (r"\b(?:remember (?:this|it):?)\s+(.+?)(?:\.|$)", "note", 1),
    (r"\b(?:save (?:this|that):?)\s+(.+?)(?:\.|$)", "note", 1),
    (r"\b(?:don't forget:?)\s+(.+?)(?:\.|$)", "note", 1),
]

# Merge extra patterns into EXTRACT_PATTERNS so extract_facts uses them
EXTRACT_PATTERNS.extend(EXTRACT_PATTERNS_EXTRA)


def get_memory_reply_for_command(command: str, session_id: str) -> Optional[str]:
    """
    Handle memory commands and return a reply string, or None if not a command / not handled.
    Uses memory_responses for varied natural-language replies when available.
    """
    # Perform forget/clear actions first, then get reply text
    if command == "forget_name":
        forget_fact(session_id, "name")
    elif command == "clear_all":
        clear_all_facts(session_id)
    elif command == "forget_likes":
        forget_fact(session_id, "likes")
        forget_fact(session_id, "favorite")
    try:
        from memory_responses import get_memory_command_reply
        reply = get_memory_command_reply(command, session_id)
        if reply is not None:
            return reply
    except ImportError:
        pass
    # Fallback if memory_responses not available
    if command == "recall":
        return format_facts_for_display(get_facts(session_id))
    if command == "forget_name":
        forget_fact(session_id, "name")
        return "I've forgotten your name. You can tell me again anytime."
    if command == "clear_all":
        clear_all_facts(session_id)
        return "I've cleared my memory about you. I won't remember anything from before."
    if command == "forget_likes":
        forget_fact(session_id, "likes")
        forget_fact(session_id, "favorite")
        return "I've forgotten what you like. Tell me again if you want me to remember."
    if command == "remember_me":
        facts = get_facts(session_id)
        if facts:
            return "Yes! " + format_facts_for_display(facts)
        return "I don't have anything stored yet. Tell me your name or something you like and I'll remember."
    if command == "who_am_i":
        facts = get_facts(session_id)
        name = facts.get("name")
        if name:
            rest = {k: v for k, v in facts.items() if k != "name"}
            if rest:
                return f"You're {name}. " + format_facts_for_display(rest)
            return f"You're {name}! Tell me more about yourself and I'll remember."
        return format_facts_for_display(facts)
    return None
