"""
Memory utilities: word lists and patterns to detect when the user is sharing
information about themselves (so we can store it) vs asking a general question.
Used to improve fact extraction and avoid storing irrelevant phrases.
"""
import re
from typing import List, Set, Tuple, Optional

# Words that often indicate the user is talking about themselves (first person)
SELF_INDICATORS = {
    "i", "my", "me", "i'm", "im", "i've", "ive", "i'll", "ill", "myself",
    "we", "our", "us", "we're", "weve", "we'll",
}

# Words that often precede a fact (name, place, preference)
NAME_LEADERS = {"name", "called", "call", "named", "call me", "known as"}
LOCATION_LEADERS = {"from", "live", "living", "born", "grew up", "located", "address"}
LIKES_LEADERS = {"like", "love", "enjoy", "into", "favorite", "favourite", "prefer"}
DISLIKES_LEADERS = {"hate", "dislike", "don't like", "dont like", "can't stand"}

# Words that suggest "remember this"
REMEMBER_LEADERS = {"remember", "save", "store", "don't forget", "dont forget", "recall", "note"}

# Words that suggest a memory command (question to the bot)
MEMORY_QUESTION_STARTS = {
    "what do you remember", "what did you remember", "what have you got",
    "do you remember me", "who am i", "what do you know about me",
    "forget my name", "clear memory", "wipe memory", "reset memory",
}

# Common words we should not store as fact values (too generic)
STOP_WORDS_FACT = {
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "must", "can", "to", "of", "in", "for", "on",
    "with", "at", "by", "from", "as", "into", "through", "during",
    "and", "or", "but", "if", "then", "so", "that", "this", "it", "its",
}

# Minimum length for a fact value to be worth storing
MIN_FACT_VALUE_LEN = 2
MAX_FACT_VALUE_LEN = 500


def is_likely_self_disclosure(text: str) -> bool:
    """
    Quick check: does the message look like the user is sharing info about themselves
    (e.g. "my name is X", "I like Y") rather than asking a general question?
    """
    if not text or len(text) < 5:
        return False
    t = text.lower().strip()
    tokens = set(re.findall(r"[a-z']+", t))
    if not (tokens & SELF_INDICATORS):
        return False
    # Could still be "I wonder what..." (question). Check for question marks or question words at start.
    if t.startswith(("what ", "who ", "where ", "when ", "why ", "how ", "is ", "are ", "can ", "could ", "would ", "do ", "does ")):
        if "?" in t or not any(w in t for w in ("my ", "i'm ", "i am ", "i like ", "i love ", "my name ", "call me ")):
            return False
    return True


def is_likely_memory_command(text: str) -> bool:
    """True if the message looks like a request to recall/forget/clear memory."""
    if not text:
        return False
    t = text.lower().strip()
    for start in MEMORY_QUESTION_STARTS:
        if t.startswith(start) or start in t[:60]:
            return True
    return False


def clean_fact_value(raw: str) -> Optional[str]:
    """
    Clean and validate a candidate fact value. Return None if it's not worth storing.
    """
    if not raw or not isinstance(raw, str):
        return None
    s = re.sub(r"\s+", " ", raw.strip())
    if len(s) < MIN_FACT_VALUE_LEN or len(s) > MAX_FACT_VALUE_LEN:
        return None
    words = s.lower().split()
    if all(w in STOP_WORDS_FACT for w in words):
        return None
    return s


def extract_capital_of_phrase(text: str) -> Optional[str]:
    """
    If the user said something like "capital of france", return "france".
    Used so we don't store "france" as a user fact when they're asking a question.
    """
    m = re.search(r"(?:capital|capitals?)\s+of\s+([a-z][a-z0-9\s\-']{0,40})", text, re.I)
    if m:
        return m.group(1).strip()
    return None


def extract_what_is_phrase(text: str) -> Optional[str]:
    """If the user asked 'what is X', return X so we don't store X as a fact."""
    m = re.search(r"what\s+is\s+(?:the\s+)?([a-z][a-z0-9\s\-']{0,50})", text, re.I)
    if m:
        return m.group(1).strip()
    return None


def extract_who_is_phrase(text: str) -> Optional[str]:
    """If the user asked 'who is X', return X."""
    m = re.search(r"who\s+is\s+(?:the\s+)?([a-z][a-z0-9\s\-']{0,50})", text, re.I)
    if m:
        return m.group(1).strip()
    return None


def should_skip_storing(message: str) -> bool:
    """
    Return True if we should NOT try to extract/store facts from this message.
    E.g. "What is the capital of France?" is a question, not "my name is France".
    """
    if not message or len(message) < 3:
        return True
    t = message.lower().strip()
    # Obvious question patterns
    if re.match(r"^(what|who|where|when|why|how)\s+(is|are|was|were|did|do|does|can|could|would)\b", t):
        return True
    if t.startswith(("tell me ", "give me ", "explain ", "define ", "list ")):
        return True
    if "?" in t and not is_likely_self_disclosure(t):
        return True
    return False


# ---------------------------------------------------------------------------
# Pattern lists for fact extraction (reference / future use)
# ---------------------------------------------------------------------------

PREFIXES_NAME = [
    "my name is", "i'm called", "call me", "name is", "i am", "i'm ", "people call me",
    "you can call me", "everyone calls me", "my friends call me",
]

PREFIXES_LOCATION = [
    "i'm from", "i am from", "i live in", "i live at", "i was born in", "i grew up in",
    "from", "living in", "based in",
]

PREFIXES_LIKES = [
    "i like", "i love", "i enjoy", "i'm into", "my favorite is", "my favourite is",
    "i prefer", "i'm interested in", "i'm curious about",
]

PREFIXES_DISLIKES = [
    "i don't like", "i dont like", "i hate", "i dislike", "i can't stand",
]

PREFIXES_REMEMBER = [
    "remember that", "remember this", "don't forget", "dont forget",
    "save this", "store that", "note that", "keep in mind",
]

# Suffixes that often end a fact (so we can trim)
FACT_END_MARKERS = [".", ",", "!", "?", " and ", " or ", " but "]


def truncate_at_marker(s: str, max_len: int = 200) -> str:
    """Truncate at a natural boundary (., and, or) and limit length."""
    if len(s) <= max_len:
        return s
    s = s[: max_len + 50]
    for m in FACT_END_MARKERS:
        idx = s.rfind(m)
        if idx > max_len // 2:
            return s[: idx + 1].strip()
    return s[:max_len].strip()


def normalize_name_candidate(s: str) -> str:
    """Clean a candidate 'name' value (capitalize, remove extra space)."""
    if not s:
        return ""
    s = re.sub(r"\s+", " ", s.strip())
    return s.title()[:80]


def infer_topic_from_user_message(message: str) -> Optional[str]:
    """
    Infer a short topic label from the user's message (e.g. "capital of france" -> "france capital").
    Used for conversation history / "last topic" feature.
    """
    if not message or len(message) < 2:
        return None
    t = message.lower().strip()
    # Remove question words
    for w in ("what", "who", "where", "when", "why", "how", "is", "are", "the", "a", "an", "can", "you", "tell", "me", "give", "explain"):
        t = re.sub(r"\b" + re.escape(w) + r"\b", "", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t[:80] if t else None


# ---------------------------------------------------------------------------
# Validation: avoid storing sensitive or junk
# ---------------------------------------------------------------------------

# Patterns that look like passwords or secrets (don't store)
SECRET_PATTERNS = [
    re.compile(r"\b\d{4,}\b"),  # long number
    re.compile(r"\b[a-z0-9]{20,}\b", re.I),  # long alphanumeric
]

# Keys we never overwrite with extracted data from "what is X" style questions
PROTECTED_KEYS = {"name", "email", "location"}


def looks_like_secret(value: str) -> bool:
    """True if the value looks like a password or token we shouldn't store."""
    if not value or len(value) < 10:
        return False
    for pat in SECRET_PATTERNS:
        if pat.search(value):
            return True
    return False


def is_safe_to_store(key: str, value: str) -> bool:
    """Check key/value before storing."""
    if not key or not value:
        return False
    if looks_like_secret(value):
        return False
    if key in PROTECTED_KEYS and len(value) > 100:
        return False
    return True


# ---------------------------------------------------------------------------
# Additional pattern lists for future extraction or scoring
# ---------------------------------------------------------------------------

# Phrases that often introduce a fact (for scoring "how likely is this a fact?")
FACT_INTRO_PHRASES = (
    "my name is", "i'm called", "call me", "i am", "i'm from", "i live in",
    "i like", "i love", "i enjoy", "i hate", "i dislike", "my favorite is",
    "my favourite is", "remember that", "don't forget", "save this",
    "i was born", "i grew up", "i work at", "i study at", "my job is",
    "my hobby is", "i'm interested in", "i'm curious about",
)

# Question starts that mean we should NOT store the rest as a fact
QUESTION_STARTS = (
    "what is", "what are", "who is", "who are", "where is", "when is",
    "why is", "how is", "how do", "how can", "can you", "could you",
    "tell me about", "give me", "explain", "define", "list", "name the",
)

# Minimum number of words for a fact value to be considered meaningful
MIN_WORDS_FACT = 1
MAX_WORDS_FACT = 30


def word_count(s: str) -> int:
    """Count words in a string."""
    if not s:
        return 0
    return len(s.split())


def is_reasonable_fact_length(value: str) -> bool:
    """True if value has a reasonable word count for a fact."""
    n = word_count(value)
    return MIN_WORDS_FACT <= n <= MAX_WORDS_FACT


def strip_leading_that(s: str) -> str:
    """Remove leading 'that' from a string (e.g. 'that dogs are cool' -> 'dogs are cool')."""
    if not s:
        return s
    t = s.strip()
    if t.lower().startswith("that "):
        return t[5:].strip()
    return t
