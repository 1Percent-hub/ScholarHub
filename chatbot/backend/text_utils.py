"""
Text utilities for the chatbot: query normalization, synonym expansion,
autocorrect (Google-like spell fix), and common misspellings.
"""
import re
from typing import List, Set

# Optional: Google-like autocorrect using pyspellchecker (install with: pip install pyspellchecker)
_spell_checker = None


def _get_spell_checker():
    """Lazy-load spell checker so the bot works if pyspellchecker isn't installed."""
    global _spell_checker
    if _spell_checker is not None:
        return _spell_checker
    try:
        from spellchecker import SpellChecker
        _spell_checker = SpellChecker()
        return _spell_checker
    except ImportError:
        _spell_checker = False
        return False


def autocorrect(text: str) -> str:
    """
    Auto-correct spelling in the message (Google-style) so the bot can match
    e.g. 'capitol of france' -> 'capital of france'. Uses pyspellchecker if
    installed; otherwise returns text unchanged.
    """
    if not text or not isinstance(text, str) or len(text.strip()) < 2:
        return text or ""
    checker = _get_spell_checker()
    if checker is False:
        return text
    words = text.split()
    corrected = []
    for word in words:
        # Keep numbers, very short tokens, and words that look like abbreviations
        clean = re.sub(r"[^a-zA-Z]", "", word)
        if len(clean) <= 2 or clean.isdigit():
            corrected.append(word)
            continue
        # If the word is known (correct), keep it; otherwise use best correction
        if checker.known([clean.lower()]):
            corrected.append(word)
            continue
        best = checker.correction(clean.lower())
        if best and best != clean.lower():
            # Preserve original casing pattern (capital first letter etc.)
            if word and word[0].isupper():
                best = best.capitalize()
            corrected.append(word.replace(clean, best) if clean else word)
        else:
            corrected.append(word)
    return " ".join(corrected)

# Common substitutions so "what's" and "what is" both match "what is", etc.
CONTRACTIONS = {
    "what's": "what is",
    "whats": "what is",
    "who's": "who is",
    "whos": "who is",
    "where's": "where is",
    "wheres": "where is",
    "how's": "how is",
    "hows": "how is",
    "that's": "that is",
    "thats": "that is",
    "it's": "it is",
    "its": "it is",
    "there's": "there is",
    "theres": "there is",
    "here's": "here is",
    "heres": "here is",
    "they're": "they are",
    "theyre": "they are",
    "we're": "we are",
    "were": "we are",
    "you're": "you are",
    "youre": "you are",
    "you've": "you have",
    "youve": "you have",
    "i've": "i have",
    "ive": "i have",
    "we've": "we have",
    "weve": "we have",
    "they've": "they have",
    "theyve": "they have",
    "i'm": "i am",
    "im": "i am",
    "don't": "do not",
    "dont": "do not",
    "doesn't": "does not",
    "doesnt": "does not",
    "isn't": "is not",
    "isnt": "is not",
    "aren't": "are not",
    "arent": "are not",
    "wasn't": "was not",
    "wasnt": "was not",
    "weren't": "were not",
    "werent": "were not",
    "haven't": "have not",
    "havent": "have not",
    "hasn't": "has not",
    "hasnt": "has not",
    "hadn't": "had not",
    "hadnt": "had not",
    "won't": "will not",
    "wont": "will not",
    "wouldn't": "would not",
    "wouldnt": "would not",
    "couldn't": "could not",
    "couldnt": "could not",
    "shouldn't": "should not",
    "shouldnt": "should not",
    "can't": "cannot",
    "cant": "cannot",
    "cannot": "can not",
}


def expand_contractions(text: str) -> str:
    """Replace common contractions with full forms for better keyword matching."""
    if not text:
        return ""
    result = text.lower().strip()
    for short, long in CONTRACTIONS.items():
        result = re.sub(r"\b" + re.escape(short) + r"\b", long, result, flags=re.IGNORECASE)
    return result


def remove_punctuation_for_match(text: str) -> str:
    """Remove punctuation that might break phrase matching (keep apostrophes for now)."""
    if not text:
        return ""
    return re.sub(r"[?!.,;:()\[\]{}]", " ", text)


def collapse_whitespace(text: str) -> str:
    """Collapse multiple spaces/newlines to a single space."""
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()


def fix_common_typos(text: str) -> str:
    """Replace common misspellings with correct form (word-boundary aware)."""
    if not text:
        return ""
    result = text.lower()
    for typo, correct in COMMON_TYPOS.items():
        if typo == correct:
            continue
        result = re.sub(r"\b" + re.escape(typo) + r"\b", correct, result)
    return result


def normalize_for_matching(text: str) -> str:
    """Full pipeline: expand contractions, fix typos, remove punctuation, collapse space."""
    t = expand_contractions(text)
    t = fix_common_typos(t)
    t = remove_punctuation_for_match(t)
    t = collapse_whitespace(t)
    return t.lower()


# Common misspellings -> correct form (applied during normalize so matching still works)
COMMON_TYPOS = {
    "teh": "the", "taht": "that", "becuase": "because", "becasue": "because",
    "recieve": "receive", "recieved": "received", "occured": "occurred",
    "seperate": "separate", "definately": "definitely", "accomodate": "accommodate",
    "occassion": "occasion", "neccessary": "necessary", "goverment": "government",
    "enviroment": "environment", "calender": "calendar", "wierd": "weird",
    "thier": "their", "adn": "and", "waht": "what", "taht": "that",
    "whcih": "which", "whihc": "which", "liek": "like", "taek": "take",
    "reponse": "response", "responce": "response", "anser": "answer",
    "quesiton": "question", "questoin": "question", "sciene": "science",
    "sience": "science", "recomend": "recommend", "reccomend": "recommend",
    "occured": "occurred", "happend": "happened", "begining": "beginning",
    "realy": "really", "realyl": "really", "probly": "probably", "probaly": "probably",
    "experiance": "experience", "experiment": "experiment", "occuring": "occurring",
    "refered": "referred", "refering": "referring", "occurence": "occurrence",
    "existance": "existence", "persistant": "persistent", "dependance": "dependence",
    "maintainance": "maintenance", "performence": "performance", "appearance": "appearance",
    "goverment": "government", "enviroment": "environment", "temperture": "temperature",
    "litrature": "literature", "seperately": "separately", "guarentee": "guarantee",
    "arguement": "argument", "judgement": "judgment", "developement": "development",
    "equiptment": "equipment", "achieve": "achieve", "acheive": "achieve",
    "freind": "friend", "freinds": "friends", "beleive": "believe", "recieve": "receive",
    "concieve": "conceive", "percieve": "perceive", "wierd": "weird", "thier": "their",
    "teh": "the", "taht": "that", "adn": "and", "waht": "what", "whcih": "which",
    "caluclate": "calculate", "mathmatics": "mathematics", "sciense": "science",
    "bioligy": "biology", "chemisty": "chemistry", "physic": "physics",
    "geography": "geography", "histroy": "history",
    "infromation": "information", "availible": "available", "sucess": "success",
    "comunicate": "communicate", "occure": "occur", "persue": "pursue", "tommorrow": "tomorrow",
    "buisness": "business", "enviroment": "environment", "goverment": "government",
    "libary": "library", "relly": "really", "untill": "until", "wensday": "wednesday",
    "febuary": "february", "january": "january", "recieve": "receive", "acheive": "achieve",
    "seperate": "separate", "occured": "occurred", "commited": "committed",
    "adress": "address", "embarass": "embarrass", "harass": "harass", "millenium": "millennium",
    "referance": "reference", "prefered": "preferred", "transfered": "transferred",
    "sucessful": "successful", "occassion": "occasion", "neccessary": "necessary",
}

# Synonym groups so "biggest" matches "largest", "tell me" intent matches "give me", etc.
SYNONYM_GROUPS = [
    {"big", "large", "huge", "biggest", "largest", "major", "massive"},
    {"small", "tiny", "little", "smallest", "minor"},
    {"fast", "quick", "speed", "quickly", "rapid"},
    {"old", "ancient", "age", "older", "oldest", "elder"},
    {"new", "modern", "recent", "newest", "latest"},
    {"good", "great", "best", "nice", "fine", "awesome"},
    {"bad", "worst", "poor", "terrible"},
    {"many", "much", "lots", "number", "how many", "amount", "count"},
    {"first", "1st", "original", "initial"},
    {"last", "final", "latest", "end"},
    {"tell", "say", "give", "show", "explain", "teach"},
    {"want", "like", "need", "would like", "love"},
    {"know", "learn", "understand", "find out", "figure out"},
    {"ask", "asking", "asked", "question", "questions"},
    {"help", "assist", "support", "aid"},
    {"make", "makes", "made", "creating", "create"},
    {"work", "works", "working", "function", "functions"},
    {"get", "got", "getting", "obtain", "have"},
    {"way", "ways", "method", "how"},
    {"thing", "things", "stuff", "something"},
    {"person", "people", "human", "someone", "who"},
    {"place", "places", "where", "location"},
    {"time", "when", "moment", "day"},
    {"reason", "why", "cause", "because"},
    {"same", "similar", "like", "alike"},
    {"different", "difference", "differ", "other"},
    {"right", "correct", "true", "yes"},
    {"wrong", "incorrect", "false", "no"},
    {"run", "runs", "running", "ran"},
    {"go", "goes", "going", "went"},
    {"think", "thinks", "thinking", "thought", "thoughts"},
    {"eat", "eats", "eating", "ate", "eaten", "food"},
    {"see", "sees", "seeing", "saw", "seen", "sight", "look", "looks", "looking"},
    {"use", "uses", "using", "used", "usage"},
    {"live", "lives", "living", "lived", "life", "alive"},
    {"come", "comes", "coming", "came"},
    {"start", "starts", "starting", "started", "begin", "begins", "beginning", "began"},
    {"end", "ends", "ending", "ended", "finish", "finishes", "finished"},
    {"change", "changes", "changing", "changed"},
    {"call", "calls", "calling", "called", "name", "named"},
    {"try", "tries", "trying", "tried"},
    {"leave", "leaves", "leaving", "left"},
    {"keep", "keeps", "keeping", "kept"},
    {"let", "lets", "letting"},
    {"begin", "begins", "beginning", "began", "begun", "start"},
    {"seem", "seems", "seeming", "seemed"},
    {"help", "helps", "helping", "helped", "assist", "support"},
    {"talk", "talks", "talking", "talked", "speak", "speaks", "speaking", "spoke"},
    {"turn", "turns", "turning", "turned"},
    {"show", "shows", "showing", "showed", "shown"},
    {"hear", "hears", "hearing", "heard"},
    {"play", "plays", "playing", "played"},
    {"move", "moves", "moving", "moved", "movement"},
    {"believe", "believes", "believing", "believed"},
    {"bring", "brings", "bringing", "brought"},
    {"happen", "happens", "happening", "happened"},
    {"write", "writes", "writing", "wrote", "written"},
    {"provide", "provides", "providing", "provided"},
    {"sit", "sits", "sitting", "sat"},
    {"stand", "stands", "standing", "stood"},
    {"lose", "loses", "losing", "lost"},
    {"pay", "pays", "paying", "paid"},
    {"meet", "meets", "meeting", "met"},
    {"include", "includes", "including", "included"},
    {"continue", "continues", "continuing", "continued"},
    {"set", "sets", "setting"},
    {"learn", "learns", "learning", "learned", "learnt"},
    {"lead", "leads", "leading", "led"},
    {"watch", "watches", "watching", "watched"},
    {"stop", "stops", "stopping", "stopped"},
    {"follow", "follows", "following", "followed"},
    {"create", "creates", "creating", "created", "creation"},
    {"remember", "remembers", "remembering", "remembered"},
    {"understand", "understands", "understanding", "understood"},
    {"consider", "considers", "considering", "considered"},
    {"appear", "appears", "appearing", "appeared"},
    {"buy", "buys", "buying", "bought"},
    {"wait", "waits", "waiting", "waited"},
    {"serve", "serves", "serving", "served"},
    {"die", "dies", "dying", "died", "dead", "death"},
    {"send", "sends", "sending", "sent"},
    {"expect", "expects", "expecting", "expected"},
    {"build", "builds", "building", "built"},
    {"stay", "stays", "staying", "stayed"},
    {"fall", "falls", "falling", "fell", "fallen"},
    {"cut", "cuts", "cutting"},
    {"reach", "reaches", "reaching", "reached"},
    {"kill", "kills", "killing", "killed"},
    {"remain", "remains", "remaining", "remained"},
    {"suggest", "suggests", "suggesting", "suggested"},
    {"raise", "raises", "raising", "raised"},
    {"pass", "passes", "passing", "passed"},
    {"sell", "sells", "selling", "sold"},
    {"require", "requires", "requiring", "required"},
    {"report", "reports", "reporting", "reported"},
    {"decide", "decides", "deciding", "decided"},
    {"pull", "pulls", "pulling", "pulled"},
    {"offer", "offers", "offering", "offered"},
    {"accept", "accepts", "accepting", "accepted"},
    {"support", "supports", "supporting", "supported"},
    {"hit", "hits", "hitting"},
    {"produce", "produces", "producing", "produced"},
    {"eat", "eats", "eating", "ate", "eaten"},
    {"cover", "covers", "covering", "covered"},
    {"catch", "catches", "catching", "caught"},
    {"draw", "draws", "drawing", "drew", "drawn"},
    {"choose", "chooses", "choosing", "chose", "chosen"},
    {"grow", "grows", "growing", "grew", "grown"},
    {"break", "breaks", "breaking", "broke", "broken"},
    {"hold", "holds", "holding", "held"},
    {"carry", "carries", "carrying", "carried"},
    {"seek", "seeks", "seeking", "sought"},
    {"plan", "plans", "planning", "planned"},
    {"pick", "picks", "picking", "picked"},
    {"wish", "wishes", "wishing", "wished"},
    {"fight", "fights", "fighting", "fought"},
    {"win", "wins", "winning", "won"},
    {"beat", "beats", "beating", "beaten"},
    {"question", "questions", "ask", "asking", "query"},
    {"answer", "answers", "reply", "replies", "response"},
    {"study", "studying", "studied", "learn", "learning", "learned"},
    {"read", "reads", "reading", "read"},
    {"write", "writes", "writing", "wrote", "written"},
    {"discover", "discovered", "discovery", "find", "found"},
    {"invent", "invented", "invention", "create", "created"},
    {"animal", "animals", "creature", "creatures", "pet", "pets"},
    {"plant", "plants", "flower", "flowers", "tree", "trees"},
    {"food", "foods", "eat", "eating", "eaten"},
    {"drink", "drinks", "drinking", "drank", "drunk"},
    {"body", "bodies", "human", "humans", "health"},
    {"earth", "world", "planet", "planets", "globe"},
    {"space", "universe", "cosmos", "astronomy", "star", "stars"},
    {"country", "countries", "nation", "nations", "state"},
    {"city", "cities", "town", "towns", "place", "places"},
    {"year", "years", "date", "dates", "time", "times"},
    {"number", "numbers", "count", "counting", "amount"},
    {"part", "parts", "piece", "pieces", "section"},
    {"kind", "kinds", "type", "types", "sort", "sorts"},
    {"problem", "problems", "issue", "issues", "trouble"},
    {"idea", "ideas", "thought", "thoughts", "concept"},
    {"fact", "facts", "true", "truth", "real"},
    {"example", "examples", "instance", "instances"},
    {"reason", "reasons", "cause", "causes", "why"},
    {"result", "results", "effect", "effects", "outcome"},
    {"change", "changes", "changing", "changed"},
    {"important", "importance", "significant", "key"},
    {"possible", "possibility", "maybe", "might"},
    {"different", "difference", "differ", "differs"},
    {"same", "similar", "alike", "like"},
    {"best", "better", "good", "great"},
    {"worst", "worse", "bad", "poor"},
    {"capital", "capitals", "city", "cities", "main city"},
    {"invent", "invented", "invention", "inventor", "create", "created"},
    {"discover", "discovered", "discovery", "find", "found"},
    {"largest", "biggest", "big", "large", "greatest"},
    {"smallest", "tiniest", "small", "little"},
    {"fastest", "quickest", "fast", "quick", "speed"},
    {"oldest", "old", "ancient", "age", "how old"},
    {"longest", "long", "length"},
    {"highest", "high", "tall", "tallest"},
    {"deepest", "deep", "depth"},
    {"hot", "hottest", "heat", "warm"},
    {"cold", "coldest", "cool", "freezing"},
    {"famous", "well-known", "known", "popular"},
    {"important", "significant", "major", "key"},
    {"first", "first", "original", "beginning"},
    {"last", "last", "final", "end"},
    {"number", "numbers", "how many", "count", "amount"},
    {"distance", "far", "how far", "away"},
    {"formula", "formulas", "equation", "chemical"},
    {"element", "elements", "chemical", "atom"},
    {"planet", "planets", "solar system", "space"},
    {"country", "countries", "nation", "nations"},
    {"river", "rivers", "stream", "water"},
    {"mountain", "mountains", "peak", "summit"},
    {"ocean", "oceans", "sea", "seas"},
    {"animal", "animals", "creature", "species"},
    {"president", "presidents", "leader", "ruler"},
    {"war", "wars", "battle", "conflict"},
    {"book", "books", "author", "wrote"},
    {"painting", "paintings", "painted", "artist"},
    {"composer", "composers", "music", "composed"},
]


def expand_with_synonyms(tokens: List[str]) -> Set[str]:
    """Given a list of tokens, return a set that includes synonym alternatives."""
    result = set(tokens)
    for group in SYNONYM_GROUPS:
        if result & group:
            result |= group
    return result


def tokenize_for_synonyms(text: str) -> List[str]:
    """Simple tokenization: split on non-alphanumeric."""
    return re.findall(r"[a-z0-9]+", text.lower())


def get_words(text: str) -> Set[str]:
    """Normalize text and return set of words (for word-based matching)."""
    normalized = normalize_for_matching(text)
    tokens = tokenize_for_synonyms(normalized)
    return set(tokens) if tokens else set()


def _simple_word_forms(word: str) -> Set[str]:
    """Return word plus common variants (plural/singular, -ing/-ed base) for fuzzier matching."""
    if not word or len(word) < 2:
        return {word} if word else set()
    out = {word}
    if word.endswith("s") and len(word) > 3 and not word.endswith("ss"):
        out.add(word[:-1])
    elif not word.endswith("s"):
        out.add(word + "s")
    if word.endswith("ing") and len(word) > 4:
        base = word[:-3]
        out.add(base)
        if len(base) > 1 and base[-1] == base[-2]:
            out.add(base[:-1])
    if word.endswith("ed") and len(word) > 3:
        base = word[:-2]
        out.add(base)
    if word.endswith("er") and len(word) > 3:
        out.add(word[:-2])
    if word.endswith("ly") and len(word) > 3:
        out.add(word[:-2])
    return out


def get_words_expanded(text: str) -> Set[str]:
    """Words + synonym expansion + simple word forms so 'largest' matches 'biggest', 'running' matches 'run', etc."""
    words = get_words(text)
    expanded = expand_with_synonyms(list(words))
    for w in list(expanded):
        expanded |= _simple_word_forms(w)
    return expanded


def query_variants(text: str) -> List[str]:
    """
    Produce variant forms of the query for matching:
    - normalized form
    - with synonyms expanded (as extra tokens we could search for)
    Returns a list of strings to try matching against.
    """
    normalized = normalize_for_matching(text)
    variants = [normalized]
    tokens = tokenize_for_synonyms(normalized)
    expanded = expand_with_synonyms(tokens)
    if expanded != set(tokens):
        variants.append(" ".join(sorted(expanded)))
    return variants
