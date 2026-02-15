"""
Smart matching: question-type detection and related-term boosting
so the bot prefers answers that fit how the user asked (who/what/where/when/why/how).
"""
import re
from typing import List, Set, Tuple

# Question words that hint at the type of answer expected.
WHO_WORDS = {"who", "whom", "whose", "person", "people", "invented", "discovered", "created", "wrote", "painted", "made"}
WHAT_WORDS = {"what", "which", "something", "thing", "definition", "mean", "means", "meaning"}
WHERE_WORDS = {"where", "place", "location", "country", "city", "capital", "located", "find", "find it"}
WHEN_WORDS = {"when", "time", "date", "year", "day", "how long", "duration", "ago", "started", "ended", "happened"}
WHY_WORDS = {"why", "reason", "cause", "because", "explain", "purpose"}
HOW_WORDS = {"how", "way", "method", "work", "works", "does", "do", "can", "possible", "happen", "happens"}

# Each question type maps to keywords that often appear in the right kind of answer.
QUESTION_TYPE_KEYWORDS = {
    "who": ["who", "invented", "discovered", "created", "wrote", "person", "people", "name", "founder"],
    "what": ["what", "definition", "mean", "is a", "are", "type", "kind", "thing"],
    "where": ["where", "place", "capital", "located", "country", "city", "find", "address"],
    "when": ["when", "year", "date", "time", "ago", "started", "ended", "history"],
    "why": ["why", "because", "reason", "cause", "explain", "purpose"],
    "how": ["how", "work", "works", "do", "does", "step", "process", "way", "method"],
}


def get_question_type(text: str) -> str:
    """
    Detect primary question type from user text (who/what/where/when/why/how).
    Returns one of: "who", "what", "where", "when", "why", "how", or "any".
    """
    if not text or not isinstance(text, str):
        return "any"
    normalized = text.lower().strip()
    tokens = set(re.findall(r"[a-z0-9]+", normalized))
    scores = {}
    if tokens & WHO_WORDS or "who" in normalized[:20]:
        scores["who"] = len(tokens & WHO_WORDS) + (2 if "who" in normalized[:25] else 0)
    if tokens & WHAT_WORDS or "what" in normalized[:20]:
        scores["what"] = len(tokens & WHAT_WORDS) + (2 if "what" in normalized[:25] else 0)
    if tokens & WHERE_WORDS or "where" in normalized[:20]:
        scores["where"] = len(tokens & WHERE_WORDS) + (2 if "where" in normalized[:25] else 0)
    if tokens & WHEN_WORDS or "when" in normalized[:20]:
        scores["when"] = len(tokens & WHEN_WORDS) + (2 if "when" in normalized[:25] else 0)
    if tokens & WHY_WORDS or "why" in normalized[:20]:
        scores["why"] = len(tokens & WHY_WORDS) + (2 if "why" in normalized[:25] else 0)
    if tokens & HOW_WORDS or "how" in normalized[:20]:
        scores["how"] = len(tokens & HOW_WORDS) + (2 if "how" in normalized[:25] else 0)
    if not scores:
        return "any"
    return max(scores, key=scores.get)


def entry_keywords_contain_type(keywords: List[str], qtype: str) -> bool:
    """Return True if any keyword phrase suggests this entry fits the question type."""
    if qtype == "any" or not keywords:
        return False
    preferred = set(QUESTION_TYPE_KEYWORDS.get(qtype, []))
    text = " ".join(kw.lower() for kw in keywords)
    tokens = set(re.findall(r"[a-z0-9]+", text))
    return bool(tokens & preferred)


def compute_question_type_boost(user_text: str, keywords: List[str]) -> int:
    """
    If the user asked a who/what/where/when/why/how question and this entry
    matches that type, add a score boost so we prefer the right kind of answer.
    """
    qtype = get_question_type(user_text)
    if qtype == "any":
        return 0
    if entry_keywords_contain_type(keywords, qtype):
        return 15
    return 0


def get_related_terms(text: str) -> Set[str]:
    """
    Expand the query with related terms people often use when they mean the same thing.
    E.g. "dog" -> keep "dog", add "dogs", "puppy"; "run" -> "running", "runs".
    """
    if not text or not isinstance(text, str):
        return set()
    tokens = re.findall(r"[a-z0-9]+", text.lower())
    out = set(tokens)
    for t in tokens:
        if len(t) <= 2:
            continue
        if t.endswith("s") and len(t) > 3:
            out.add(t[:-1])
        elif len(t) > 2 and not t.endswith("s"):
            out.add(t + "s")
        if t.endswith("ing") and len(t) > 4:
            base = t[:-3]
            out.add(base)
            out.add(base + "e")
        elif t.endswith("ed") and len(t) > 3:
            base = t[:-2]
            out.add(base)
            if len(base) > 1 and base[-1] == base[-2]:
                out.add(base[:-1])
    return out


# Topic hints: if user and entry share a topic, boost the score.
TOPIC_SETS = {
    "space": {"space", "planet", "moon", "sun", "star", "galaxy", "mars", "earth", "orbit", "asteroid", "comet", "black hole", "solar", "nasa", "astronaut", "universe", "neptune", "uranus", "jupiter", "saturn", "venus", "mercury", "pluto"},
    "animal": {"animal", "animals", "dog", "cat", "bird", "fish", "lion", "tiger", "bear", "elephant", "whale", "dolphin", "snake", "insect", "pet", "species", "mammal", "reptile", "amphibian"},
    "body": {"body", "heart", "brain", "blood", "bone", "muscle", "health", "disease", "virus", "vaccine", "medicine", "doctor", "sick", "organ", "cell", "dna", "gene"},
    "science": {"science", "atom", "molecule", "gravity", "energy", "force", "physics", "chemistry", "biology", "experiment", "element", "reaction", "formula"},
    "geo": {"country", "capital", "city", "ocean", "mountain", "river", "continent", "map", "geography", "desert", "forest", "lake"},
    "history": {"history", "war", "invented", "discovered", "ancient", "century", "year", "emperor", "empire", "president", "king", "queen"},
    "tech": {"computer", "internet", "phone", "robot", "code", "program", "digital", "wifi", "ai", "software"},
    "food": {"food", "eat", "fruit", "vegetable", "recipe", "cook", "drink", "water", "vitamin", "protein", "calorie"},
    "math": {"math", "maths", "number", "equation", "percent", "fraction", "geometry", "algebra", "pi"},
}


def _entry_words(keywords: List[str]) -> Set[str]:
    """All words from keyword phrases."""
    out = set()
    for kw in keywords:
        out.update(re.findall(r"[a-z0-9]+", kw.lower()))
    return out


def compute_topic_boost(user_words: Set[str], keywords: List[str]) -> int:
    """If user and entry share a topic (space, animal, body, etc.), add a boost."""
    entry_w = _entry_words(keywords)
    boost = 0
    for topic_name, topic_words in TOPIC_SETS.items():
        if (user_words & topic_words) and (entry_w & topic_words):
            boost += 8
    return min(boost, 16)


def apply_smart_boost(
    user_text: str,
    user_words: Set[str],
    keywords: List[str],
    base_score: int,
) -> int:
    """
    Apply question-type boost, topic boost, and optional related-term bonus.
    Returns enhanced score for this (user_text, knowledge_entry) pair.
    """
    score = base_score
    score += compute_question_type_boost(user_text, keywords)
    score += compute_topic_boost(user_words, keywords)
    related = get_related_terms(user_text)
    entry_words = _entry_words(keywords)
    extra_overlap = related & entry_words
    if extra_overlap and not (user_words & extra_overlap):
        score += len(extra_overlap) * 2
    return score


def strip_question_prefix(text: str) -> str:
    """
    Remove leading question words so "what is the capital of France"
    becomes "capital of France" for a second-pass match.
    """
    if not text or not isinstance(text, str):
        return text or ""
    t = text.lower().strip()
    prefixes = [
        r"^\s*what\s+is\s+the\s+",
        r"^\s*what\s+are\s+the\s+",
        r"^\s*what\s+is\s+a\s+",
        r"^\s*what\s+is\s+",
        r"^\s*what\s+are\s+",
        r"^\s*who\s+is\s+the\s+",
        r"^\s*who\s+is\s+a\s+",
        r"^\s*who\s+is\s+",
        r"^\s*where\s+is\s+the\s+",
        r"^\s*where\s+is\s+",
        r"^\s*when\s+did\s+the\s+",
        r"^\s*when\s+did\s+",
        r"^\s*when\s+was\s+the\s+",
        r"^\s*when\s+was\s+",
        r"^\s*why\s+do\s+",
        r"^\s*why\s+does\s+",
        r"^\s*why\s+is\s+the\s+",
        r"^\s*why\s+is\s+",
        r"^\s*how\s+do\s+you\s+",
        r"^\s*how\s+do\s+we\s+",
        r"^\s*how\s+does\s+",
        r"^\s*how\s+do\s+",
        r"^\s*how\s+can\s+i\s+",
        r"^\s*how\s+can\s+you\s+",
        r"^\s*how\s+many\s+",
        r"^\s*how\s+much\s+",
        r"^\s*can\s+you\s+tell\s+me\s+",
        r"^\s*could\s+you\s+tell\s+me\s+",
        r"^\s*tell\s+me\s+about\s+",
        r"^\s*tell\s+me\s+",
        r"^\s*give\s+me\s+",
        r"^\s*explain\s+",
        r"^\s*define\s+",
        r"^\s*do\s+you\s+know\s+",
        r"^\s*i\s+want\s+to\s+know\s+",
        r"^\s*i\s+wanna\s+know\s+",
        r"^\s*can\s+you\s+explain\s+",
        r"^\s*could\s+you\s+explain\s+",
        r"^\s*what\s+does\s+",
        r"^\s*what\s+do\s+",
        r"^\s*where\s+are\s+",
        r"^\s*when\s+was\s+",
        r"^\s*when\s+is\s+",
        r"^\s*why\s+are\s+",
        r"^\s*why\s+do\s+",
        r"^\s*how\s+are\s+",
        r"^\s*is\s+it\s+true\s+that\s+",
        r"^\s*is\s+it\s+true\s+",
        r"^\s*tell\s+me\s+why\s+",
        r"^\s*give\s+me\s+info\s+on\s+",
        r"^\s*info\s+on\s+",
        r"^\s*learn\s+about\s+",
        r"^\s*teach\s+me\s+about\s+",
        r"^\s*what\s+is\s+the\s+",
        r"^\s*what\s+are\s+",
        r"^\s*who\s+was\s+",
        r"^\s*who\s+were\s+",
        r"^\s*where\s+did\s+",
        r"^\s*when\s+was\s+",
        r"^\s*why\s+did\s+",
        r"^\s*how\s+did\s+",
        r"^\s*i\s+need\s+to\s+know\s+",
        r"^\s*just\s+curious\s+",
        r"^\s*quick\s+question\s+",
        r"^\s*random\s+question\s+",
        r"^\s*one\s+question\s+",
        r"^\s*can\s+you\s+answer\s+",
        r"^\s*could\s+you\s+answer\s+",
        r"^\s*please\s+tell\s+me\s+",
        r"^\s*i\s+was\s+wondering\s+",
        r"^\s*curious\s+about\s+",
    ]
    for pat in prefixes:
        t = re.sub(pat, "", t, count=1, flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", t).strip() or text
