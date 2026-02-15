"""
AI English Helper: grammar tips, writing structure, vocabulary,
and common writing questions to make Josiah a strong writing assistant.
"""
import re
from typing import List, Tuple, Optional, Dict


# Common grammar rules and explanations
GRAMMAR_RULES = {
    "its it's": "Its (no apostrophe) is possessive: 'The dog wagged its tail.' It's (with apostrophe) means 'it is' or 'it has': 'It's raining.' If you can say 'it is' in place, use it's.",
    "their there they're": "Their = belonging to them. There = a place or in 'there is.' They're = they are. Example: They're going over there to get their books.",
    "your you're": "Your = belonging to you. You're = you are. So 'You're going to love your new bike.'",
    "whose who's": "Whose = belonging to whom. Who's = who is or who has. 'Whose book is this?' vs 'Who's coming?'",
    "affect effect": "Affect is usually a verb (to influence): 'The weather affects my mood.' Effect is usually a noun (a result): 'The effect was surprising.'",
    "then than": "Then = time or sequence ('First this, then that.'). Than = comparison ('She is taller than him.').",
    "accept except": "Accept = to agree or receive. Except = excluding. 'I accept all except the last one.'",
    "capitalization": "Capitalize the first word of a sentence, proper nouns (names, places), and the pronoun I. Titles of works capitalize major words.",
    "comma": "Use commas to separate items in a list, after introductory phrases, before conjunctions joining two independent clauses, and around non-essential clauses.",
    "apostrophe": "Use an apostrophe for possessives (the dog's tail) and contractions (don't, it's). Never use it for plurals (wrong: apple's for more than one apple).",
    "semicolon": "A semicolon joins two closely related independent clauses without a conjunction. It can also separate items in a list when those items contain commas.",
    "colon": "Use a colon to introduce a list, a quote, or an explanation. What follows should complete the thought started before the colon.",
    "subject verb agreement": "The verb must match the subject in number. 'The dog runs' (singular) vs 'The dogs run' (plural). Watch for phrases between subject and verb: 'The list of items is long.'",
    "run on sentence": "A run-on is two or more independent clauses joined without proper punctuation or a conjunction. Fix with a period, semicolon, or comma plus conjunction (and, but, so).",
    "fragment": "A sentence fragment is missing a subject or a main verb, so it doesn't express a complete thought. Add the missing part or attach it to another sentence.",
    "passive voice": "In passive voice, the subject is acted upon: 'The ball was thrown by her.' In active voice: 'She threw the ball.' Active is usually clearer and more direct.",
    "thesis statement": "A thesis statement is one or two sentences that state the main idea of your essay. It should be specific, arguable, and appear usually at the end of your introduction.",
    "topic sentence": "A topic sentence states the main idea of a paragraph. It usually comes at the beginning and tells the reader what the paragraph will be about.",
    "introduction paragraph": "An introduction hooks the reader, gives background, and ends with a thesis statement. It sets up what the rest of the essay will do.",
    "conclusion paragraph": "A conclusion restates the thesis in new words, summarizes main points, and often ends with a broader thought or call to action. Don't introduce new arguments.",
    "paragraph structure": "A strong paragraph has a topic sentence, supporting sentences with details or examples, and sometimes a concluding sentence that ties back to the main idea.",
    "essay structure": "A typical essay has an introduction (with thesis), body paragraphs (each with one main idea and evidence), and a conclusion that reinforces the thesis.",
    "evidence": "Evidence supports your claims. It can be facts, statistics, quotes, or examples. Always explain how your evidence supports your point.",
    "transition words": "Use transition words to connect ideas: however, therefore, furthermore, for example, in addition, on the other hand, finally. They help the reader follow your logic.",
    "plagiarism": "Plagiarism is using someone else's words or ideas without giving credit. Always cite sources and put direct quotes in quotation marks.",
    "citation": "When you use someone else's idea or words, cite the source. Common styles are MLA, APA, and Chicago. Include author, title, and publication info.",
}


def _normalize_query(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower()) if text else ""


def get_grammar_help(query: str) -> Optional[str]:
    """Match user question to a grammar rule and return explanation."""
    q = _normalize_query(query)
    for key, explanation in GRAMMAR_RULES.items():
        key_words = key.replace("'", "").split()
        if all(w in q for w in key_words):
            return explanation
        if key in q or key.replace(" ", "") in q.replace(" ", ""):
            return explanation
    return None


# Writing tips by topic
WRITING_TIPS = {
    "essay": [
        "Start with a clear thesis statement that your whole essay supports.",
        "Each body paragraph should have one main idea and evidence to back it up.",
        "Use transition words between paragraphs so the reader can follow your argument.",
        "End the introduction with your thesis and the conclusion by restating it in new words.",
    ],
    "thesis": [
        "A good thesis is specific—not too broad or vague.",
        "It should be something you can argue, not just a fact.",
        "Put it at the end of your introduction so the reader knows what to expect.",
    ],
    "paragraph": [
        "Start with a topic sentence that states the main idea.",
        "Add 3–5 sentences that explain or give examples.",
        "Keep one main idea per paragraph; start a new one when the idea changes.",
    ],
    "proofread": [
        "Read your work out loud to catch awkward phrasing.",
        "Check for common mistakes: its/it's, their/there/they're, your/you're.",
        "Look at one thing at a time: first punctuation, then spelling, then clarity.",
    ],
    "introduction": [
        "Hook the reader with a question, quote, or interesting fact.",
        "Give a little background so the reader understands the topic.",
        "End with your thesis statement.",
    ],
    "conclusion": [
        "Restate your thesis in different words.",
        "Summarize your main points briefly.",
        "End with a final thought, recommendation, or question—don't introduce new arguments.",
    ],
}


def get_writing_tips(topic: str) -> Optional[List[str]]:
    """Return a list of tips for the given writing topic."""
    q = _normalize_query(topic)
    for key, tips in WRITING_TIPS.items():
        if key in q:
            return tips
    return None


# Synonyms and vocabulary hints (simple)
VOCAB_SIMPLE = {
    "big": "large, huge, enormous, massive, vast",
    "small": "tiny, little, compact, slight",
    "good": "great, excellent, fine, positive, beneficial",
    "bad": "poor, negative, harmful, terrible",
    "said": "stated, remarked, announced, declared, replied",
    "happy": "glad, pleased, joyful, content, delighted",
    "sad": "unhappy, sorrowful, down, gloomy, miserable",
    "important": "significant, major, key, critical, essential",
    "interesting": "fascinating, engaging, compelling, intriguing",
    "different": "distinct, various, diverse, alternative",
    "beautiful": "lovely, pretty, attractive, stunning, gorgeous",
    "smart": "intelligent, clever, bright, sharp, wise",
    "fast": "quick, rapid, swift, speedy",
    "slow": "sluggish, gradual, unhurried, delayed",
}


def get_synonym_suggestion(word: str) -> Optional[str]:
    """Suggest synonyms for a common word."""
    w = word.strip().lower()
    if w in VOCAB_SIMPLE:
        return f"Some synonyms for '{word}' are: {VOCAB_SIMPLE[w]}."
    return None


def process_english_message(message: str) -> Optional[str]:
    """
    If the message is about grammar, writing, or vocabulary, return a helpful reply.
    Otherwise return None.
    """
    if not message or len(message) < 3:
        return None
    q = _normalize_query(message)

    # Grammar
    reply = get_grammar_help(message)
    if reply:
        return reply

    # Writing tips
    tips = get_writing_tips(message)
    if tips:
        return "Here are some tips: " + " ".join(f"• {t}" for t in tips)

    # Synonym
    words = re.findall(r"[a-z]+", q)
    for w in words:
        if len(w) > 2:
            syn = get_synonym_suggestion(w)
            if syn:
                return syn

    return None
