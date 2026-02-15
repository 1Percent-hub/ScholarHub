"""
AI Study Coach: study strategies, memorization techniques, time management,
and exam preparation to help students learn better.
"""
import re
import random
from typing import List, Optional, Dict


STUDY_STRATEGIES = {
    "pomodoro": "The Pomodoro Technique: work for 25 minutes, then take a 5-minute break. After four cycles, take a longer break (15–30 min). This helps focus and prevents burnout.",
    "spaced repetition": "Spaced repetition means reviewing material at increasing intervals—e.g. after 1 day, then 3 days, then a week. It's one of the best ways to move information into long-term memory.",
    "flashcards": "Use flashcards for facts and definitions. Put one question or term per card. Review often and separate cards into 'know' and 'need practice' piles. Apps like Anki use spaced repetition.",
    "active recall": "Active recall means testing yourself instead of just re-reading. Close the book and try to explain or write what you know. It's more effective than passive reading.",
    "feynman technique": "The Feynman Technique: explain the topic in simple terms as if teaching someone else. When you get stuck, go back to your notes. Simplifying reveals gaps in your understanding.",
    "mind map": "Mind maps help organize ideas. Put the main topic in the centre and branch out with key points and sub-points. Use colours and images to make connections visual.",
    "summarize": "After reading a section, summarize it in your own words in a few sentences. This forces you to process the material and check if you really understood.",
    "practice test": "Practice tests and past papers are powerful. They show what you don't know and get you used to exam format. Do them under timed conditions when possible.",
    "study group": "Study groups work when everyone prepares and stays on task. Explain concepts to each other and quiz one another. Teaching is one of the best ways to learn.",
    "sleep": "Sleep is when the brain consolidates memory. Cramming all night often hurts performance. Aim for 7–9 hours; review before bed and again in the morning.",
    "environment": "Find a quiet, well-lit place with few distractions. Put your phone away. Same place and time each day can help your brain get into 'study mode.'",
    "goals": "Set specific goals: 'I will read chapter 5 and make 10 flashcards' instead of 'I will study.' Small, clear goals are easier to complete and track.",
    "breaks": "Take regular breaks. Your brain needs rest to stay focused. Stand up, stretch, or walk. Short breaks improve overall productivity.",
    "note taking": "Good notes capture main ideas and key details, not every word. Use headings, bullets, and abbreviations. Review and tidy notes soon after class.",
    "mnemonics": "Mnemonics help memory: acronyms (ROY G BIV for rainbow colours), rhymes, or silly sentences. For example, 'My Very Easy Method Just Speeds Up Naming Planets' for the order of planets.",
}


EXAM_TIPS = [
    "Read all questions first and budget time. Do easier ones first to build confidence.",
    "Underline key words in the question so you answer what's actually asked.",
    "Show your work in math and science—partial credit can save you.",
    "If you're stuck, move on and come back. Don't let one question eat all your time.",
    "Review your answers if you have time. Check for careless mistakes.",
]

MEMORY_TIPS = [
    "Connect new information to something you already know. Analogies and examples help.",
    "Use multiple senses: read aloud, draw diagrams, act it out. More connections = better recall.",
    "Chunk information into small groups (e.g. phone numbers as 3-3-4).",
    "Practice retrieving: quiz yourself instead of only re-reading. Retrieval strengthens memory.",
]


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower()) if text else ""


def get_study_advice(query: str) -> Optional[str]:
    """Return study or exam advice based on query."""
    q = _normalize(query)
    for key, advice in STUDY_STRATEGIES.items():
        if key in q or key.replace(" ", "") in q:
            return advice
    if "exam" in q or "test" in q or "quiz" in q:
        return "Here are some exam tips: " + " ".join(f"• {t}" for t in EXAM_TIPS[:3])
    if "memor" in q or "remember" in q:
        return "Memory tips: " + " ".join(f"• {t}" for t in MEMORY_TIPS[:3])
    return None


def process_study_message(message: str) -> Optional[str]:
    """Handle study-related questions."""
    if not message:
        return None
    return get_study_advice(message)
