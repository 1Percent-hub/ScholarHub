"""
AI Reasoning Layer: intent detection, multi-step reasoning, clarification,
and query understanding to make Josiah smarter and more context-aware.
"""
import re
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum


class IntentCategory(Enum):
    GREETING = "greeting"
    FAREWELL = "farewell"
    QUESTION_FACT = "question_fact"
    QUESTION_HOW = "question_how"
    QUESTION_WHY = "question_why"
    QUESTION_WHAT = "question_what"
    QUESTION_WHO = "question_who"
    QUESTION_WHEN = "question_when"
    QUESTION_WHERE = "question_where"
    MATH_REQUEST = "math_request"
    ENGLISH_WRITING = "english_writing"
    SCIENCE_QUESTION = "science_question"
    STUDY_HELP = "study_help"
    OPINION_REQUEST = "opinion_request"
    CLARIFICATION = "clarification"
    THANKS = "thanks"
    PRAISE = "praise"
    COMPLAINT = "complaint"
    CHITCHAT = "chitchat"
    UNKNOWN = "unknown"


@dataclass
class DetectedIntent:
    category: IntentCategory
    confidence: float
    entities: Dict[str, Any]
    sub_intent: Optional[str] = None


# Patterns for intent detection
GREETING_PATTERNS = [
    r"^(hi|hey|hello|howdy|yo|sup|greetings|good\s+(morning|afternoon|evening)|g'day)\b",
    r"^(what'?s\s+up|wassup|how\s+are\s+you|how\s+you\s+doing|how\s+do\s+you\s+do)\b",
    r"^(nice\s+to\s+meet\s+you|pleased\s+to\s+meet\s+you)\b",
    r"^(good\s+to\s+see\s+you|long\s+time\s+no\s+see)\b",
]

FAREWELL_PATTERNS = [
    r"\b(bye|goodbye|see\s+ya|see\s+you|later|take\s+care|good\s+night)\b$",
    r"\b(thanks\s+bye|thank\s+you\s+bye)\b$",
    r"^(i'?m\s+done|that'?s\s+all|nothing\s+else)\b",
]

MATH_INDICATORS = [
    "calculate", "compute", "solve", "equation", "formula", "percent", "percentage",
    "fraction", "decimal", "multiply", "divide", "add", "subtract", "square root",
    "pi", "algebra", "geometry", "trigonometry", "derivative", "integral", "sum",
    "product", "factor", "quadratic", "linear", "angle", "area", "volume", "radius",
]

ENGLISH_INDICATORS = [
    "grammar", "spell", "spelling", "write", "writing", "essay", "sentence",
    "paragraph", "vocabulary", "synonym", "antonym", "define", "definition",
    "punctuation", "comma", "verb", "noun", "adjective", "adverb", "tense",
    "proofread", "revise", "thesis", "conclusion", "introduction",
]

SCIENCE_INDICATORS = [
    "physics", "chemistry", "biology", "experiment", "hypothesis", "theory",
    "molecule", "atom", "cell", "reaction", "force", "energy", "gravity",
    "evolution", "photosynthesis", "periodic table", "element", "compound",
]

STUDY_INDICATORS = [
    "study", "learn", "memorize", "flashcard", "exam", "test", "quiz",
    "remember", "recall", "notes", "review", "practice", "homework",
    "schedule", "focus", "concentration", "pomodoro",
]


def _normalize_for_intent(text: str) -> str:
    if not text or not isinstance(text, str):
        return ""
    t = text.strip().lower()
    t = re.sub(r"\s+", " ", t)
    return t


def _tokenize(text: str) -> List[str]:
    return re.findall(r"[a-z0-9]+", text.lower()) if text else []


def detect_intent(message: str) -> DetectedIntent:
    """
    Analyze user message and return the most likely intent category
    with confidence and any extracted entities.
    """
    msg = _normalize_for_intent(message)
    tokens = set(_tokenize(msg))
    entities: Dict[str, Any] = {}

    # Greeting
    for pat in GREETING_PATTERNS:
        if re.search(pat, msg):
            return DetectedIntent(IntentCategory.GREETING, 0.95, entities)

    # Farewell
    for pat in FAREWELL_PATTERNS:
        if re.search(pat, msg):
            return DetectedIntent(IntentCategory.FAREWELL, 0.9, entities)

    # Thanks / praise
    if re.search(r"^(thanks|thank\s+you|thx|ty|appreciate)", msg) or "thank you" in msg:
        return DetectedIntent(IntentCategory.THANKS, 0.9, entities)
    if any(w in tokens for w in ("awesome", "great", "cool", "amazing", "helpful", "perfect")):
        return DetectedIntent(IntentCategory.PRAISE, 0.85, entities)

    # Question-type detection
    if msg.startswith("who "):
        return DetectedIntent(IntentCategory.QUESTION_WHO, 0.85, entities)
    if msg.startswith("what ") or msg.startswith("whats ") or msg.startswith("what's "):
        return DetectedIntent(IntentCategory.QUESTION_WHAT, 0.85, entities)
    if msg.startswith("when "):
        return DetectedIntent(IntentCategory.QUESTION_WHEN, 0.85, entities)
    if msg.startswith("where "):
        return DetectedIntent(IntentCategory.QUESTION_WHERE, 0.85, entities)
    if msg.startswith("why "):
        return DetectedIntent(IntentCategory.QUESTION_WHY, 0.85, entities)
    if msg.startswith("how "):
        return DetectedIntent(IntentCategory.QUESTION_HOW, 0.85, entities)

    # Domain-specific
    if any(m in msg for m in MATH_INDICATORS):
        return DetectedIntent(IntentCategory.MATH_REQUEST, 0.8, entities)
    if any(e in msg for e in ENGLISH_INDICATORS):
        return DetectedIntent(IntentCategory.ENGLISH_WRITING, 0.8, entities)
    if any(s in msg for s in SCIENCE_INDICATORS):
        return DetectedIntent(IntentCategory.SCIENCE_QUESTION, 0.8, entities)
    if any(s in msg for s in STUDY_INDICATORS):
        return DetectedIntent(IntentCategory.STUDY_HELP, 0.75, entities)

    # Generic fact question (what is X, tell me about X)
    if re.search(r"^(what\s+is|whats\s+|what's\s+|tell\s+me\s+about|explain\s+|define\s+)", msg):
        return DetectedIntent(IntentCategory.QUESTION_FACT, 0.8, entities)

    # Chitchat / unclear
    if len(tokens) <= 3 and not msg.endswith("?"):
        return DetectedIntent(IntentCategory.CHITCHAT, 0.6, entities)

    return DetectedIntent(IntentCategory.UNKNOWN, 0.3, entities)


def get_intent_specific_suggestions(intent: DetectedIntent) -> List[str]:
    """Return follow-up suggestions tailored to the detected intent."""
    if intent.category == IntentCategory.GREETING:
        return [
            "What can you help me with?",
            "Tell me a fun fact",
            "I have a question about science",
        ]
    if intent.category == IntentCategory.MATH_REQUEST:
        return [
            "How do I solve quadratic equations?",
            "What is the quadratic formula?",
            "Explain percentages",
        ]
    if intent.category == IntentCategory.ENGLISH_WRITING:
        return [
            "How do I write a good thesis?",
            "What's the difference between its and it's?",
            "How do I structure an essay?",
        ]
    if intent.category == IntentCategory.SCIENCE_QUESTION:
        return [
            "How does photosynthesis work?",
            "What is Newton's first law?",
            "Explain the water cycle",
        ]
    if intent.category == IntentCategory.STUDY_HELP:
        return [
            "How can I memorize better?",
            "What's the best way to study for a test?",
            "Give me study tips",
        ]
    if intent.category == IntentCategory.QUESTION_WHAT:
        return [
            "What is the capital of France?",
            "What is photosynthesis?",
            "What is gravity?",
        ]
    if intent.category == IntentCategory.QUESTION_HOW:
        return [
            "How does the heart work?",
            "How do I calculate percentage?",
            "How do airplanes fly?",
        ]
    return [
        "Tell me more",
        "Can you explain that differently?",
        "What else should I know?",
    ]


def needs_clarification(message: str, intent: DetectedIntent) -> Optional[str]:
    """
    If the message is too vague, return a clarifying question.
    Otherwise return None.
    """
    msg = _normalize_for_intent(message)
    tokens = _tokenize(msg)

    if len(tokens) <= 2 and intent.category == IntentCategory.UNKNOWN:
        return "Could you give me a bit more detail? What would you like to know?"
    if intent.category == IntentCategory.MATH_REQUEST and len(tokens) < 4:
        return "What would you like me to calculate? For example: 'What is 15% of 80?' or 'Solve 2x + 5 = 15'"
    if intent.category == IntentCategory.QUESTION_WHAT and "what" in msg and len(tokens) < 5:
        return "What topic are you curious about? For example: 'What is the capital of Japan?' or 'What is DNA?'"
    return None


def expand_query_for_reasoning(message: str) -> List[str]:
    """
    Generate alternative phrasings of the user query to improve matching.
    Returns the original plus variations.
    """
    msg = _normalize_for_intent(message)
    variations = [msg]

    # "what is X" -> "define X", "X definition"
    m = re.match(r"^what\s+is\s+(?:the\s+)?(.+)$", msg)
    if m:
        topic = m.group(1).strip()
        if topic and len(topic) > 1:
            variations.append("define " + topic)
            variations.append(topic + " definition")

    # "how do I X" -> "how to X", "X steps"
    m = re.match(r"^how\s+do\s+i\s+(.+)$", msg)
    if m:
        rest = m.group(1).strip()
        if rest:
            variations.append("how to " + rest)
            variations.append(rest + " steps")

    return variations


def get_reasoning_context_prompt(message: str, intent: DetectedIntent) -> Optional[str]:
    """
    Build an internal context string that can be used by response generators
    to tailor the answer (e.g. "user asked a how-question, prefer step-by-step").
    """
    parts = []
    parts.append(f"intent:{intent.category.value}")
    parts.append(f"confidence:{intent.confidence:.2f}")
    if intent.category == IntentCategory.QUESTION_HOW:
        parts.append("prefer:steps")
    if intent.category == IntentCategory.QUESTION_WHY:
        parts.append("prefer:causes")
    if intent.category == IntentCategory.QUESTION_WHAT:
        parts.append("prefer:definition")
    if intent.category == IntentCategory.MATH_REQUEST:
        parts.append("prefer:calculation")
    return " ".join(parts)


def should_use_deep_reasoning(message: str, intent: DetectedIntent) -> bool:
    """Decide whether to invoke deeper reasoning (math solver, etc.)."""
    if intent.category == IntentCategory.MATH_REQUEST:
        return True
    if intent.category == IntentCategory.ENGLISH_WRITING and len(message) > 20:
        return True
    if intent.confidence < 0.5:
        return False
    return False


# --- Response templates for intents when no knowledge match ---
INTENT_FALLBACKS = {
    IntentCategory.GREETING: "Hey! I'm Josiah. Ask me anything—science, math, history, writing tips, or how things work!",
    IntentCategory.FAREWELL: "Bye! Come back anytime you have questions.",
    IntentCategory.THANKS: "You're welcome! If you have more questions, just ask.",
    IntentCategory.PRAISE: "Glad I could help! What else would you like to know?",
    IntentCategory.MATH_REQUEST: "I can help with math! Try asking something like 'What is 20% of 150?' or 'How do I solve 2x + 3 = 9?'",
    IntentCategory.ENGLISH_WRITING: "I can help with writing and grammar! Ask me about essay structure, grammar rules, or word meanings.",
    IntentCategory.SCIENCE_QUESTION: "I love science questions! Ask about physics, chemistry, biology, or how things work.",
    IntentCategory.STUDY_HELP: "I can give study tips! Ask about memorization, note-taking, or how to prepare for a test.",
}


def get_intent_fallback_reply(intent: DetectedIntent) -> Optional[str]:
    """Return a friendly fallback reply for this intent when no knowledge match."""
    return INTENT_FALLBACKS.get(intent.category)
