"""
AI Orchestrator: runs intent detection, specialty handlers (math, English, science, study),
and falls back to the main knowledge engine so Josiah is smarter and more capable.
"""
from typing import List, Tuple, Optional

try:
    from knowledge_engine import get_reply as get_reply_from_knowledge
except ImportError:
    def get_reply_from_knowledge(message: str) -> Tuple[str, List[str]]:
        return "I'm not sure about that. Try asking something else!", []

try:
    from ai_reasoning import (
        detect_intent,
        get_intent_specific_suggestions,
        needs_clarification,
        get_intent_fallback_reply,
        IntentCategory,
    )
except ImportError:
    def detect_intent(message: str):
        class Dummy:
            category = "unknown"
            confidence = 0.0
            entities = {}
        return Dummy()
    def get_intent_specific_suggestions(intent): return []
    def needs_clarification(msg, intent): return None
    def get_intent_fallback_reply(intent): return None
    class IntentCategory:
        UNKNOWN = "unknown"

try:
    from ai_math_solver import process_math_message, get_math_concept_reply
except ImportError:
    def process_math_message(message: str): return None
    def get_math_concept_reply(query: str): return None

try:
    from ai_english_helper import process_english_message
except ImportError:
    def process_english_message(message: str): return None

try:
    from ai_science_qa import process_science_message
except ImportError:
    def process_science_message(message: str): return None

try:
    from ai_study_coach import process_study_message
except ImportError:
    def process_study_message(message: str): return None


def get_reply_smart(message: str) -> Tuple[str, List[str]]:
    """
    Smarter reply pipeline:
    1. Intent detection
    2. Clarification if needed
    3. Math solver (calculations, percentages, algebra, geometry)
    4. English helper (grammar, writing, vocabulary)
    5. Science QA (physics, chemistry, biology)
    6. Study coach (study tips, exam prep)
    7. Math concept explanations (if math intent but no calculation)
    8. Intent-based fallback (friendly prompt for math/english/science/study)
    9. Main knowledge engine
    """
    message = (message or "").strip()
    if not message:
        return "Please type something! I'm Josiah—ask me about math, science, writing, study tips, or anything else.", []

    intent = detect_intent(message)

    # Clarification
    clarification = needs_clarification(message, intent)
    if clarification:
        sugs = get_intent_specific_suggestions(intent)
        return clarification, sugs[:5] if sugs else []

    # Math (calculations and concepts)
    math_result = process_math_message(message)
    if math_result is not None:
        reply, _ = math_result
        return reply, [
            "How do I solve a quadratic equation?",
            "What is the Pythagorean theorem?",
            "Explain percentages again",
        ]
    math_concept = get_math_concept_reply(message)
    if math_concept:
        return math_concept, ["Solve 2x + 5 = 15", "What is 20% of 80?", "Area of a circle with radius 5"]

    # English
    english_reply = process_english_message(message)
    if english_reply:
        return english_reply, [
            "How do I write a thesis statement?",
            "What's the difference between its and it's?",
            "Give me writing tips",
        ]

    # Science
    science_reply = process_science_message(message)
    if science_reply:
        return science_reply, [
            "How does photosynthesis work?",
            "What is Newton's first law?",
            "Tell me an easy science experiment",
        ]

    # Study
    study_reply = process_study_message(message)
    if study_reply:
        return study_reply, [
            "How can I memorize better?",
            "What's the Pomodoro technique?",
            "Give me exam tips",
        ]

    # Intent fallback when we have a strong intent but no specialty reply
    intent_fallback = get_intent_fallback_reply(intent)
    if intent_fallback:
        sugs = get_intent_specific_suggestions(intent)
        if sugs:
            return intent_fallback, sugs[:5]

    # Main knowledge engine
    return get_reply_from_knowledge(message)
