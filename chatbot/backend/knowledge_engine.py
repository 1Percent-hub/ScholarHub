"""
Smart knowledge engine: keyword scoring, multiple replies per topic,
and suggested follow-up questions when no match is found.
"""
import re
import random
from typing import List, Tuple, Optional

try:
    from text_utils import normalize_for_matching as normalize, get_words_expanded, autocorrect
except ImportError:
    def normalize(text: str) -> str:
        if not text or not isinstance(text, str):
            return ""
        return re.sub(r"\s+", " ", text.strip().lower())

    def get_words_expanded(text: str):
        t = normalize(text)
        return set(re.findall(r"[a-z0-9]+", t)) if t else set()

    def autocorrect(text: str) -> str:
        return text or ""


def _words_from_keywords(keywords: List[str]) -> set:
    """Get all unique words from a list of keyword phrases."""
    out = set()
    for kw in keywords:
        tokens = re.findall(r"[a-z0-9]+", normalize(kw))
        out.update(tokens)
    return out


def score_match_phrase(text: str, keywords: List[str]) -> int:
    """Original style: bonus when a full keyword phrase appears in text."""
    if not text or not keywords:
        return 0
    score = 0
    for kw in keywords:
        if kw.strip() and kw in text:
            score += 10 + len(kw)
    return score


def score_match_words(user_words: set, keywords: List[str]) -> int:
    """
    Score by word overlap (user_words can be synonym-expanded).
    Bonus when most of the entry's meaning-bearing words are covered (coverage).
    """
    if not user_words or not keywords:
        return 0
    entry_words = _words_from_keywords(keywords)
    meaningful = entry_words - {"a", "an", "the", "is", "are", "to", "of", "and", "or", "for", "with", "in", "on", "at"}
    overlap = user_words & entry_words
    # Base: each matching word adds points (longer = more specific)
    word_score = sum(2 + len(w) for w in overlap)
    # Coverage bonus: if user hit most of this entry's important words, boost score
    if meaningful:
        coverage = len(overlap & meaningful) / len(meaningful)
        if coverage >= 0.5:
            word_score += int(10 * coverage)  # up to +10 for full coverage
    return word_score


def score_match(text: str, keywords: List[str], user_words: set) -> int:
    """
    Combined: phrase match (exact substring) gets a strong bonus, plus word-overlap score.
    So "how have you've been" scores high on entries that contain words how, have, you, been.
    """
    phrase_score = score_match_phrase(text, keywords)
    word_score = score_match_words(user_words, keywords)
    return phrase_score + word_score


def get_best_match(text: str, knowledge: List[Tuple[List[str], List[str]]]) -> Optional[Tuple[int, List[str]]]:
    """
    Find the best-matching knowledge entry using word-based + phrase scoring + smart boost.
    Returns (score, list_of_possible_replies) or None if no match.
    """
    normalized = normalize(text) if text else ""
    user_words = get_words_expanded(text) if text else set()
    stop_words = {"a", "an", "the", "is", "are", "was", "were", "be", "being", "to", "of", "and", "or", "but", "in", "on", "at", "for", "with", "by", "from", "as", "into", "through", "during"}
    user_words = user_words - stop_words
    if not user_words and not normalized:
        return None

    try:
        from smart_match import apply_smart_boost
        use_smart_boost = True
    except ImportError:
        use_smart_boost = False

    best_score = 0
    best_replies: Optional[List[str]] = None
    for keywords, replies in knowledge:
        s = score_match(normalized, keywords, user_words)
        if use_smart_boost:
            s = apply_smart_boost(normalized, user_words, keywords, s)
        if s > best_score and replies:
            best_score = s
            best_replies = replies if isinstance(replies, list) else [replies]

    if best_score > 0 and best_replies:
        return (best_score, best_replies)

    try:
        from smart_match import strip_question_prefix
        stripped = strip_question_prefix(normalized)
        if stripped and stripped != normalized and len(stripped) >= 3:
            stripped_words = get_words_expanded(stripped) - stop_words
            if stripped_words:
                for keywords, replies in knowledge:
                    s = score_match(stripped, keywords, stripped_words)
                    if use_smart_boost:
                        s = apply_smart_boost(stripped, stripped_words, keywords, s)
                    if s > best_score and replies:
                        best_score = s
                        best_replies = replies if isinstance(replies, list) else [replies]
    except ImportError:
        pass

    if best_score > 0 and best_replies:
        return (best_score, best_replies)
    return None


# ---------------------------------------------------------------------------
# Knowledge base: (keywords, [reply1, reply2, ...])
# Multiple replies = we pick one at random for variety.
# ---------------------------------------------------------------------------

KNOWLEDGE: List[Tuple[List[str], List[str]]] = [
    # Greetings & social
    (["hello", "hi ", " hi", "hey", "howdy", "greetings", "hiya"], [
        "Hey! I'm Josiah. What can I do for you? Ask me about anything—science, history, animals, tech, or fun facts!",
        "Hi there! I'm Josiah. What would you like to know? I can help with loads of topics.",
    ]),
    (["bye", "goodbye", "see you", "later", "cya"], [
        "Goodbye! Have a great day. Come back anytime you have questions.",
        "See you later! Feel free to return whenever you're curious about something.",
    ]),
    (["thanks", "thank you", "thx", "cheers", "ty"], [
        "You're welcome! Happy to help.",
        "Anytime! Ask again if you have more questions.",
    ]),
    (["help", "what can you do", "what do you know"], [
        "I can answer questions on lots of topics: space, Earth, animals, the human body, science, technology, history, geography, health, music, sports, maths, and fun facts. Just ask in plain English!",
    ]),
    (["who are you", "what are you", "what is your name", "josiah"], [
        "I'm Josiah! I'm here to help with questions about science, history, tech, animals, and tons more. What can I do for you?",
        "I'm Josiah—your friendly chatbot with a big knowledge base. Ask me anything and I'll do my best to answer!",
    ]),
    (["who made you", "who created you", "who built you", "who made this", "who created this", "who built this", "who made the chatbot", "who created the chatbot", "made by", "created by", "built by", "how was this made", "how was this created", "how was it made", "how was it created", "who is your creator", "who is your maker", "your creator", "your maker", "james campbell", "james campbell high", "josiah evans", "from hawaii", "who programmed you", "who coded you", "who developed you", "what school made you", "where were you made", "who built josiah"], [
        "I'm Josiah! I was created by Josiah Evans from Hawaii—James Campbell High School. What can I do for you?",
        "Josiah Evans from Hawaii, James Campbell High School, made me. I'm Josiah—here to help with any questions!",
    ]),
    (["how are you", "how have you been", "how you been", "how've you been", "how are things", "how's it going", "how goes it"], [
        "I'm doing great, thanks for asking! I'm Josiah—here to help. What can I do for you?",
        "All good on my end! What would you like to know? I'm Josiah and I'm ready to help.",
    ]),
    (["what's up", "whats up", "wassup", "sup", "yo", "good morning", "good evening", "good afternoon", "good night", "gday"], [
        "Hey! I'm Josiah. What can I do for you? Ask me anything—science, history, fun facts, or just chat!",
        "Hi there! I'm Josiah. What would you like to know?",
    ]),
    (["explain", "tell me about", "give me info", "teach me", "learn about", "what do you know about"], [
        "I'd love to explain! Tell me the topic—e.g. 'Explain black holes', 'Tell me about Rome', or 'What do you know about dolphins?' and I'll dive in. I'm Josiah!",
    ]),
    (["difference between", "whats the difference", "different from", "vs ", " versus ", "compare"], [
        "I can compare things! Try: 'What's the difference between DNA and RNA?', 'Mars vs Earth', or 'Compare X and Y'. I'm Josiah—what do you want to compare?",
    ]),
    (["is it true", "really", "is that true", "fact check", "true or false"], [
        "I can help with that! Ask me something like 'Is it true that bats are blind?' or 'Is it true that we only use 10% of our brain?' and I'll give you the facts. I'm Josiah!",
    ]),
    (["something interesting", "interesting thing", "cool fact", "learn something", "teach me something"], [
        "Sure! Try: 'Tell me something interesting about space', 'Give me a cool fact about animals', or 'Teach me something about history'. I'm Josiah—what topic?",
    ]),
    # Follow-ups
    (["tell me more", "more info", "elaborate", "expand", "go on", "and then", "what else"], [
        "I'd be happy to go deeper! Could you say which topic? For example: 'Tell me more about black holes' or 'More about the Roman Empire.'",
        "Sure! Which part would you like more detail on? Just name the topic or ask a more specific question.",
    ]),
    (["why", "how come", "explain why"], [
        "I'd need a bit more detail—'why' or 'how come' about what? Try asking a full question and I'll do my best to answer!",
    ]),
    # Space
    (["speed of light", "how fast is light", "light speed"], [
        "Light travels at about 299,792 kilometres per second (or roughly 186,282 miles per second) in a vacuum. Nothing with mass can go that fast.",
    ]),
    (["how far is the sun", "distance to sun", "earth to sun"], [
        "On average, Earth is about 150 million kilometres (93 million miles) from the Sun. That distance is defined as one astronomical unit (1 AU).",
    ]),
    (["how many planets", "planets in solar system", "solar system"], [
        "There are eight planets in our solar system: Mercury, Venus, Earth, Mars, Jupiter, Saturn, Uranus, and Neptune. Pluto is now classified as a dwarf planet.",
    ]),
    (["black hole", "black holes", "what is a black hole"], [
        "A black hole is a region of space where gravity is so strong that nothing, not even light, can escape. They form when very massive stars collapse at the end of their lives.",
        "Black holes are created when massive stars run out of fuel and collapse. The gravity is so intense that not even light can escape—hence 'black'.",
    ]),
    (["moon landing", "land on the moon", "apollo", "first man on moon"], [
        "Humans first landed on the Moon on July 20, 1969, during NASA's Apollo 11 mission. Neil Armstrong and Buzz Aldrin walked on the surface while Michael Collins orbited above.",
    ]),
    (["big bang", "how did the universe start", "origin of universe"], [
        "The Big Bang is the leading theory: the universe began as an extremely hot, dense point about 13.8 billion years ago and has been expanding and cooling ever since.",
    ]),
    (["mars", "red planet", "planet mars"], [
        "Mars is the fourth planet from the Sun, often called the Red Planet because of its rusty colour from iron oxide. It has two small moons, Phobos and Deimos, and we've sent many rovers there.",
    ]),
    (["galaxy", "milky way", "our galaxy"], [
        "The Milky Way is our galaxy—a huge spiral of stars, gas, and dust. The Sun is one of roughly 100 to 400 billion stars in it, and we're about 27,000 light-years from the centre.",
    ]),
    (["saturn", "saturn's rings", "rings of saturn"], [
        "Saturn is the sixth planet and the second largest. Its spectacular rings are made of ice and rock. Saturn has over 80 moons; Titan is the largest and has a thick atmosphere.",
    ]),
    (["jupiter", "largest planet", "gas giant"], [
        "Jupiter is the largest planet in our solar system—a gas giant. It has a famous Great Red Spot (a storm), at least 80 moons, and no solid surface. Its gravity helps protect Earth by deflecting some asteroids.",
    ]),
    (["venus", "planet venus"], [
        "Venus is the second planet from the Sun and the hottest—thick clouds trap heat. It's similar in size to Earth but has a crushing atmosphere of carbon dioxide. It's often called Earth's twin.",
    ]),
    (["mercury", "planet mercury"], [
        "Mercury is the smallest and closest planet to the Sun. It has extreme temperature swings, almost no atmosphere, and a heavily cratered surface. A year on Mercury is only about 88 Earth days.",
    ]),
    (["neptune", "uranus", "ice giant"], [
        "Neptune and Uranus are ice giants—cold, windy planets with thick atmospheres. Neptune is the farthest known planet. Both were discovered with telescopes; Neptune's existence was predicted from Uranus's orbit.",
    ]),
    (["asteroid", "asteroids", "asteroid belt"], [
        "Asteroids are rocky leftovers from the early solar system. Most orbit in the asteroid belt between Mars and Jupiter. Some cross Earth's orbit; tracking them helps assess impact risk.",
    ]),
    (["comet", "comets", "halley"], [
        "Comets are icy bodies that release gas and dust when they approach the Sun, forming a visible tail. Many orbit the Sun from the outer solar system. Halley's Comet returns roughly every 76 years.",
    ]),
    (["solar eclipse", "lunar eclipse", "eclipse"], [
        "A solar eclipse happens when the Moon blocks the Sun from Earth's view. A lunar eclipse is when Earth's shadow falls on the Moon. Both occur when Sun, Earth, and Moon align.",
    ]),
    (["international space station", "iss", "space station"], [
        "The ISS is a habitable satellite in low Earth orbit. It's a partnership of NASA, Roscosmos, ESA, JAXA, and CSA. Astronauts live there for months, doing science in microgravity.",
    ]),
    (["hubble", "hubble telescope", "space telescope"], [
        "The Hubble Space Telescope orbits Earth and has taken stunning images of distant galaxies, nebulae, and planets. Launched in 1990, it has been serviced by astronauts and is still in use.",
    ]),
    (["james webb", "jwst", "webb telescope"], [
        "The James Webb Space Telescope (JWST) is NASA's powerful infrared observatory, launched in 2021. It looks at the earliest galaxies, star formation, and exoplanet atmospheres, and is much more sensitive than Hubble for certain science.",
    ]),
    (["exoplanet", "exoplanets", "planets outside solar system"], [
        "Exoplanets are planets that orbit stars other than the Sun. Thousands have been found, some in the 'habitable zone' where liquid water could exist. We detect them by watching stars wobble or dim as planets pass by.",
    ]),
    (["nebula", "nebulas", "stellar nursery"], [
        "A nebula is a cloud of gas and dust in space. Some are where new stars form; others are debris from dying stars. They're often beautifully lit by nearby stars—like the Orion Nebula.",
    ]),
    (["supernova", "supernovae", "star explosion"], [
        "A supernova is the explosive death of a massive star (or a white dwarf in a binary). It briefly outshines a whole galaxy and spreads heavy elements into space. The Crab Nebula is a supernova remnant.",
    ]),
    (["dark matter", "dark energy"], [
        "Dark matter is invisible stuff that doesn't emit light but has gravity—we see its effects on galaxies. Dark energy is thought to be driving the universe's accelerated expansion. Together they make up most of the universe's content, but we still don't know what they are.",
    ]),
]

# Append the rest of the knowledge from the original app (single reply per entry for brevity in this block)
# We'll add many more below as separate entries for scoring variety.
def _add_knowledge():
    extra = [
        (["how old is the earth", "age of earth"], ["Earth is about 4.54 billion years old. Scientists work this out from radiometric dating of rocks and meteorites."]),
        (["why is the sky blue", "sky blue"], ["The sky looks blue because sunlight is scattered by the gases in our atmosphere. Shorter (blue) wavelengths scatter more than longer (red) ones, so we see blue when we look up."]),
        (["rainbow", "rainbows"], ["A rainbow appears when sunlight is refracted and reflected inside water droplets (e.g. after rain). You see a band of colours—red, orange, yellow, green, blue, indigo, violet—because each colour bends slightly differently."]),
        (["earthquake", "earthquakes"], ["Earthquakes happen when tectonic plates suddenly slip past each other, releasing energy as seismic waves. They're measured with seismometers; the Richter scale (or moment magnitude) describes their size."]),
        (["volcano", "volcanoes"], ["Volcanoes are openings in the Earth's crust where molten rock (magma), gas, and ash can escape. They form near plate boundaries or hotspots. Famous examples include Mount Fuji, Vesuvius, and Kilauea."]),
        (["ocean", "oceans", "deepest ocean", "pacific", "atlantic", "mariana trench"], ["There are five main oceans: Pacific, Atlantic, Indian, Southern, and Arctic. The Pacific is the largest and deepest; the Mariana Trench in the Pacific is the deepest point on Earth, about 11 km down."]),
        (["climate change", "global warming"], ["Climate change is long-term change in global temperatures and weather patterns. Largely driven by human activities (like burning fossil fuels), it leads to rising seas, more extreme weather, and shifts in ecosystems. Reducing emissions and adapting are key."]),
        (["fastest animal", "cheetah"], ["The cheetah is the fastest land animal, reaching about 70 mph (113 km/h) in short bursts. The peregrine falcon is even faster in a dive—over 200 mph (320 km/h)."]),
        (["biggest animal", "largest animal", "blue whale"], ["The blue whale is the largest animal ever known. It can grow to about 30 metres long and weigh over 170 tonnes. Its heart alone is about the size of a small car."]),
        (["do dogs dream", "dogs dream"], ["Yes. Dogs go through similar sleep stages to us, including REM (rapid eye movement), when dreaming happens. Twitching and quiet barks during sleep are often signs they're dreaming."]),
        (["how do birds fly", "birds fly"], ["Birds fly thanks to lightweight skeletons, strong breast muscles, and wings that act like airfoils. They push air down and back, and the reaction force lifts them. Hollow bones and feathers also help reduce weight."]),
        (["honeybee", "bees", "how do bees make honey"], ["Bees make honey from flower nectar. They collect it, add enzymes in their stomachs, and store it in honeycomb. They fan it with their wings to evaporate water until it becomes thick honey."]),
        (["dinosaurs", "dinosaur", "when did dinosaurs live"], ["Dinosaurs lived from about 230 million years ago until about 66 million years ago, when a huge asteroid impact (and its effects) led to a mass extinction. Birds are the only living dinosaurs."]),
        (["elephant", "elephants"], ["Elephants are the largest land animals. They're highly social, have excellent memory, and use tools. African elephants have larger ears; Asian elephants are slightly smaller. All are endangered due to habitat loss and poaching."]),
        (["octopus", "octopuses"], ["Octopuses are molluscs with eight arms, three hearts, and blue blood. They're very intelligent, can change colour and texture for camouflage, and can squeeze through tiny gaps. Most live in the ocean."]),
        (["how many bones", "bones in body", "human skeleton"], ["Adults have 206 bones. Babies are born with more (around 300); some fuse as they grow. Bones support the body, protect organs, store minerals, and make blood cells."]),
        (["heart", "human heart", "heart beat"], ["The human heart has four chambers and pumps blood around the body. At rest it beats about 60–100 times per minute. Over a lifetime it can beat billions of times."]),
        (["brain", "human brain", "how does the brain work"], ["The brain has roughly 86 billion neurons that communicate via electrical and chemical signals. It controls thought, memory, emotion, movement, and body functions. Different regions specialise in different tasks."]),
        (["blood", "what is blood"], ["Blood carries oxygen, nutrients, and hormones, and removes waste. It's made of red cells (oxygen), white cells (immunity), platelets (clotting), and plasma. Adults have about 5 litres."]),
        (["sleep", "why do we sleep", "why sleep"], ["Sleep restores the body and brain, helps memory and learning, supports the immune system, and regulates mood. Not getting enough is linked to health problems and poorer thinking."]),
        (["sneeze", "sneezing"], ["Sneezing is a reflex to clear the nose of irritants like dust or germs. Air is forced out quickly through the nose and mouth. It's hard to keep your eyes open because the reflex is so strong."]),
        (["gravity", "what is gravity"], ["Gravity is the force that pulls objects with mass toward each other. Earth's gravity keeps us on the ground and holds the Moon in orbit. Einstein described it as curvature of space-time."]),
        (["atom", "atoms", "what is an atom"], ["Atoms are the building blocks of matter. Each has a nucleus (protons and neutrons) and electrons around it. Different elements have different numbers of protons. Atoms combine to form molecules."]),
        (["photosynthesis", "how do plants make food"], ["Plants use sunlight, water, and carbon dioxide to make sugar (food) and release oxygen. This process happens mainly in the leaves, in structures called chloroplasts, using the green pigment chlorophyll."]),
        (["evolution", "what is evolution"], ["Evolution is the change in species over time through inherited traits. Those better suited to the environment tend to survive and reproduce (natural selection). All life on Earth shares common ancestors."]),
        (["electricity", "how does electricity work"], ["Electricity is the flow of charged particles (usually electrons). In wires, a voltage pushes electrons along a circuit. It can produce light, heat, and motion, and powers most modern technology."]),
        (["speed of sound", "how fast is sound"], ["The speed of sound in air at room temperature is about 343 metres per second (767 mph). It travels faster in liquids and solids. Light is much faster, which is why you see lightning before you hear thunder."]),
        (["what is python", "python programming"], ["Python is a popular programming language known for clear, readable syntax. It's used for web development, data science, AI, automation, and more. It's a great first language to learn."]),
        (["what is ai", "artificial intelligence", "machine learning"], ["Artificial intelligence (AI) is when machines perform tasks that usually need human intelligence (e.g. learning, reasoning). Machine learning is a type of AI where systems learn from data instead of being programmed step-by-step."]),
        (["internet", "how does the internet work"], ["The internet is a global network of connected computers. Data is split into packets, sent via routers and cables (or wireless links), and reassembled at the destination. Protocols like TCP/IP and DNS make this possible."]),
        (["cookie", "cookies", "browser cookies"], ["Browser cookies are small text files websites save on your device. They remember logins, preferences, and tracking data. You can view or delete them in your browser settings."]),
        (["virus", "computer virus", "malware"], ["A computer virus or malware is software designed to harm or misuse your system—steal data, damage files, or take control. Protect yourself with antivirus software, updates, and careful use of links and downloads."]),
        (["flask", "what is flask"], ["Flask is a lightweight Python web framework. It's used to build web apps and APIs with minimal setup. You define routes and functions; Flask handles HTTP requests and responses."]),
        (["world war 2", "ww2", "second world war"], ["World War II (1939–1945) was a global conflict involving most of the world's nations. It was the deadliest war in history and led to the use of nuclear weapons, the Holocaust, and the founding of the UN."]),
        (["who invented the internet", "internet invented"], ["The internet grew from research in the 1960s–70s. Key developments include ARPANET (USA), TCP/IP, and the World Wide Web, which Tim Berners-Lee invented at CERN in 1989."]),
        (["ancient rome", "roman empire"], ["Ancient Rome grew from a city-state into an empire that dominated the Mediterranean and beyond. It left a lasting legacy in law, language, engineering, and culture. The Western Empire fell in the 5th century CE."]),
        (["egypt", "ancient egypt", "pyramids"], ["Ancient Egypt was a civilisation along the Nile, known for pharaohs, hieroglyphics, and monuments like the pyramids at Giza. The Great Pyramid was built around 2560 BCE and was one of the Seven Wonders of the Ancient World."]),
        (["who discovered america", "columbus"], ["Indigenous peoples had been in the Americas for thousands of years. In 1492, Christopher Columbus's voyage from Spain reached the Caribbean, which led to lasting European contact and colonisation of the Americas."]),
        (["largest country", "biggest country", "russia size"], ["Russia is the largest country by area (about 17.1 million km²), spanning Europe and Asia. Canada is second, then the USA and China."]),
        (["capital of france", "france capital"], ["The capital of France is Paris. It's a major global city known for culture, art, fashion, and landmarks like the Eiffel Tower and the Louvre."]),
        (["capital of japan", "japan capital"], ["The capital of Japan is Tokyo. It's one of the world's most populous cities and a major financial and cultural centre."]),
        (["how many countries", "countries in the world"], ["There are about 195 countries today, depending on how you count (e.g. UN member states vs. territories). The number changes when borders or recognition change."]),
        (["longest river", "nile", "amazon river"], ["The Nile is often cited as the longest river (about 6,650 km), and the Amazon is the largest by water flow. Both are among the most important rivers on Earth."]),
        (["vitamin c", "vitamins", "vitamin d"], ["Vitamins are nutrients the body needs in small amounts. Vitamin C supports the immune system and is in citrus and vegetables. Vitamin D helps bones and immunity; we get it from sunlight and some foods."]),
        (["calories", "what is a calorie"], ["A calorie is a unit of energy. In food, we usually mean kilocalories (kcal): the energy needed to raise 1 kg of water by 1°C. We need calories to fuel our body; balance intake with activity for healthy weight."]),
        (["protein", "what is protein"], ["Protein is a nutrient made of amino acids. It builds and repairs muscles and tissues. Good sources include meat, fish, eggs, beans, and dairy. Most people get enough from a varied diet."]),
        (["water", "how much water to drink", "stay hydrated"], ["Guidelines often suggest about 2–2.5 litres (8–10 cups) of fluid per day for adults. Needs vary with activity, climate, and health. Thirst and pale urine are rough guides; drink when thirsty."]),
        (["exercise", "why exercise", "benefits of exercise"], ["Exercise strengthens the heart, muscles, and bones; improves mood and sleep; and helps control weight. Aim for at least 150 minutes of moderate activity (or 75 minutes vigorous) per week, plus strength work."]),
        (["fun fact", "random fact", "tell me something"], ["Here's one: Honey never spoils. Archaeologists have found edible honey in ancient Egyptian tombs. Or: A group of flamingos is called a 'flamboyance.' Want more on a specific topic?"]),
        (["joke", "tell me a joke"], ["Why did the scarecrow win an award? He was outstanding in his field! Want another, or shall we switch to facts?"]),
        (["how are you"], ["I'm doing well, thanks for asking! I'm here to answer your questions—what would you like to know?"]),
        (["your name", "what's your name", "who are you called"], ["I'm a chatbot—you can call me whatever you like! What would you like to ask?"]),
    ]
    KNOWLEDGE.extend(extra)


_add_knowledge()

# Even more knowledge for 20x smarter bot
MORE_KNOWLEDGE = [
    (["penguin", "penguins"], ["Penguins are flightless birds that live mostly in the Southern Hemisphere. They're adapted to cold: dense feathers, fat, and huddling. The emperor penguin breeds in the harsh Antarctic winter."]),
    (["dolphin", "dolphins"], ["Dolphins are intelligent marine mammals. They use echolocation, live in social groups, and have been seen using tools. They're in the same order as whales—cetaceans."]),
    (["shark", "sharks"], ["Sharks are fish with cartilaginous skeletons. They've been around for hundreds of millions of years. Most are not dangerous to humans; great whites, tiger sharks, and bull sharks get the most attention."]),
    (["cat", "cats", "do cats purr"], ["Cats purr when content, but also when stressed or in pain. The mechanism isn't fully understood—it may involve the larynx and diaphragm. Cats are obligate carnivores and were domesticated thousands of years ago."]),
    (["butterfly", "butterflies", "metamorphosis"], ["Butterflies go through complete metamorphosis: egg, caterpillar, chrysalis, adult. Their wings are covered in tiny scales that create colour and pattern. Many migrate; monarchs travel thousands of kilometres."]),
    (["spider", "spiders"], ["Spiders are arachnids with eight legs and fangs. Most use venom to subdue prey and silk for webs, egg sacs, and travel. They're found on every continent and are important predators."]),
    (["crocodile", "alligator", "crocodiles"], ["Crocodiles and alligators are large reptiles. Crocodiles have V-shaped snouts and show teeth when the mouth is closed; alligators have U-shaped snouts. Both have been around since the time of dinosaurs."]),
    (["gorilla", "gorillas", "great apes"], ["Gorillas are the largest living primates and our close relatives. They live in family groups, use tools, and have distinct personalities. They're endangered due to habitat loss and poaching."]),
    (["koala", "koalas"], ["Koalas are Australian marsupials that eat almost only eucalyptus leaves. They sleep a lot to conserve energy and carry their young in a pouch. They're vulnerable due to habitat loss and disease."]),
    (["wolf", "wolves", "wolf pack"], ["Wolves are social predators that live and hunt in packs. They communicate with howls, body language, and scent. They play a key role in ecosystems by controlling prey populations."]),
    (["magnet", "magnetism", "magnetic"], ["Magnetism comes from moving electric charges. Earth has a magnetic field (from its molten core) that protects us from some solar radiation and guides compasses. Magnets have north and south poles."]),
    (["laser", "lasers"], ["A laser produces a narrow, coherent beam of light—all waves in phase. Used in surgery, communications, cutting, and pointers. The name stands for Light Amplification by Stimulated Emission of Radiation."]),
    (["dna", "what is dna", "genes"], ["DNA carries genetic instructions. It's a double helix of four bases (A, T, G, C). Genes are segments of DNA that code for proteins. Almost all cells in your body have the same DNA."]),
    (["bacteria", "germs"], ["Bacteria are single-celled organisms; some cause disease, many are harmless or helpful. Viruses are smaller—they need a host to reproduce. 'Germs' often means bacteria or viruses that can make you ill."]),
    (["solar energy", "solar power", "photovoltaic"], ["Solar panels turn sunlight into electricity using photovoltaic cells. Solar power is renewable and produces no direct emissions. Costs have fallen sharply, making it a major energy source."]),
    (["recycling", "recycle", "plastic recycling"], ["Recycling turns used materials into new products, reducing waste and often saving energy. Paper, metal, glass, and many plastics can be recycled. Check local rules—what's accepted varies by place."]),
    (["periodic table", "elements", "chemical elements"], ["The periodic table lists all known chemical elements by atomic number. Elements in the same column share similar properties. There are 118 known elements; many are synthetic."]),
    (["newton", "newton's laws", "laws of motion"], ["Newton's three laws: (1) An object stays at rest or in motion unless a force acts on it. (2) Force = mass × acceleration. (3) For every action there's an equal and opposite reaction."]),
    (["einstein", "relativity", "e=mc2"], ["Einstein's theory of relativity changed physics. Special relativity says speed of light is constant and E=mc². General relativity describes gravity as the curvature of space-time by mass and energy."]),
    (["javascript", "what is javascript", "js"], ["JavaScript is a programming language that runs in web browsers and on servers (e.g. Node.js). It powers interactive websites and is one of the core web technologies with HTML and CSS."]),
    (["html", "what is html"], ["HTML (HyperText Markup Language) structures web pages with tags like headings, paragraphs, links, and images. Browsers read HTML and display content. It's the skeleton of the web."]),
    (["css", "what is css"], ["CSS (Cascading Style Sheets) controls how web pages look: layout, colours, fonts, and animations. It works with HTML to separate structure from presentation."]),
    (["api", "what is an api"], ["An API (Application Programming Interface) lets different software talk to each other. Web APIs use URLs and return data (often JSON). They're how apps fetch weather, payments, or other services."]),
    (["cloud", "cloud computing"], ["Cloud computing means using remote servers over the internet for storage, processing, and apps. Examples: AWS, Google Cloud, Azure. You pay for what you use instead of owning the hardware."]),
    (["password", "strong password", "passwords"], ["A strong password is long, mixed (letters, numbers, symbols), and unique. Use a password manager. Enable two-factor authentication where possible to add security."]),
    (["vpn", "what is a vpn"], ["A VPN (Virtual Private Network) encrypts your internet traffic and can make it appear you're in another country. Used for privacy on public Wi‑Fi and sometimes to access region-locked content."]),
    (["bitcoin", "cryptocurrency", "crypto"], ["Bitcoin is a decentralised digital currency using blockchain. Cryptocurrencies use cryptography and aren't issued by a central bank. They're volatile and used for investment and some payments."]),
    (["capital of england", "london", "uk capital"], ["The capital of England and the United Kingdom is London. It's a major global city for finance, culture, and history, with landmarks like Big Ben and the Tower of London."]),
    (["capital of usa", "washington dc", "america capital"], ["The capital of the United States is Washington, D.C. It's where the White House, Capitol, and Supreme Court are. New York is the largest city but not the capital."]),
    (["capital of australia", "australia capital"], ["The capital of Australia is Canberra. It was chosen as a compromise between Sydney and Melbourne. Parliament and many national institutions are there."]),
    (["capital of germany", "berlin"], ["The capital of Germany is Berlin. It's the largest city in Germany and a major European centre for politics, culture, and history, including the Brandenburg Gate."]),
    (["capital of italy", "rome", "italy capital"], ["The capital of Italy is Rome. It was the heart of the Roman Empire and is home to the Vatican, the Colosseum, and countless historic sites."]),
    (["capital of spain", "madrid", "spain capital"], ["The capital of Spain is Madrid. It's in the centre of the country and is known for art museums like the Prado, royal palaces, and vibrant culture."]),
    (["capital of china", "beijing", "china capital"], ["The capital of China is Beijing. It's a huge city with landmarks like the Forbidden City and the Great Wall nearby. Shanghai is larger but Beijing is the political centre."]),
    (["capital of india", "india capital", "new delhi"], ["The capital of India is New Delhi. It's part of the larger Delhi metro area and houses the government, including the Parliament and Rashtrapati Bhavan."]),
    (["capital of brazil", "brazil capital", "brasilia"], ["The capital of Brazil is Brasília. It was built in the 1960s as a planned capital in the interior. Rio and São Paulo are larger but Brasília is the seat of government."]),
    (["capital of canada", "ottawa", "canada capital"], ["The capital of Canada is Ottawa. It's in Ontario, chosen as a compromise between English and French Canada. Parliament Hill and many national museums are there."]),
    (["mount everest", "everest", "tallest mountain"], ["Mount Everest is Earth's highest peak above sea level—8,849 m (29,032 ft). It's in the Himalayas on the border of Nepal and China. Climbing it is dangerous and requires preparation."]),
    (["sahara", "sahara desert", "largest desert"], ["The Sahara is the world's largest hot desert, covering much of North Africa. It's mostly sand and rock, with extreme temperatures. The Antarctic is larger but is a cold, icy desert."]),
    (["amazon", "amazon rainforest", "amazon jungle"], ["The Amazon rainforest is the largest tropical rainforest, mostly in Brazil. It holds huge biodiversity and affects global climate. Deforestation is a major environmental concern."]),
    (["world war 1", "ww1", "first world war"], ["World War I (1914–1918) was a global conflict triggered by the assassination of Archduke Franz Ferdinand. Trench warfare, new weapons, and millions of deaths led to major political changes and the Treaty of Versailles."]),
    (["industrial revolution"], ["The Industrial Revolution was the shift to machine-based manufacturing, starting in Britain in the late 1700s. Steam power, factories, and railways changed work, cities, and society. It spread to Europe and the USA."]),
    (["renaissance", "the renaissance"], ["The Renaissance was a period of cultural and intellectual revival in Europe (roughly 14th–17th centuries). It emphasised art, science, and humanism. Figures like Leonardo da Vinci and Michelangelo defined the era."]),
    (["middle ages", "medieval"], ["The Middle Ages (roughly 5th–15th century) followed the fall of Rome. It saw feudalism, the rise of Christianity and Islam, castles, crusades, and later the Black Death and the start of the Renaissance."]),
    (["greek", "ancient greece", "greece history"], ["Ancient Greece gave us democracy, philosophy, drama, and the Olympics. City-states like Athens and Sparta flourished. Greek ideas influenced Rome and later the whole of Western culture."]),
    (["invention of printing", "printing press", "gutenberg"], ["The printing press was developed by Johannes Gutenberg in the 1440s. Moveable type made books cheaper and more widespread, spreading ideas and helping trigger the Renaissance and Reformation."]),
    (["cold war"], ["The Cold War was a period of tension (roughly 1947–1991) between the USA and the Soviet Union. No direct large-scale war, but nuclear arms race, proxy wars, and space race. It ended with the USSR's collapse."]),
    (["great wall of china"], ["The Great Wall of China is a series of fortifications built over centuries to protect against invasions. It stretches thousands of kilometres. Most of what we see today is from the Ming dynasty."]),
    (["who wrote beethoven", "beethoven"], ["Ludwig van Beethoven was a German composer (1770–1827). He wrote nine symphonies, piano sonatas, and the famous 'Ode to Joy' in his Ninth. He went deaf but kept composing."]),
    (["mozart", "who was mozart"], ["Wolfgang Amadeus Mozart (1756–1791) was an Austrian composer. He wrote over 600 works—operas, symphonies, concertos—and was a child prodigy. He's one of the most famous classical composers."]),
    (["shakespeare", "who was shakespeare"], ["William Shakespeare (1564–1616) was an English playwright and poet. He wrote Hamlet, Romeo and Juliet, Macbeth, and many more. His works are still performed and studied worldwide."]),
    (["mona lisa", "da vinci"], ["The Mona Lisa is a painting by Leonardo da Vinci, in the Louvre in Paris. It's famous for its subject's smile and gaze. Leonardo was also a scientist and inventor—a true Renaissance figure."]),
    (["guitar", "how does a guitar work"], ["A guitar makes sound when strings vibrate. The body amplifies the sound. Acoustic guitars use the hollow body; electric guitars use pickups and an amplifier. Frets change the pitch by shortening the string."]),
    (["piano", "how does a piano work"], ["A piano has strings struck by hammers when you press keys. The harder you press, the louder the sound. The piano has 88 keys and can play melody and harmony—it's a percussion and string instrument."]),
    (["olympics", "olympic games", "when were the olympics"], ["The modern Olympic Games began in 1896 in Athens. They're held every four years (Summer and Winter alternate every two years). They bring together athletes from around the world."]),
    (["world cup", "fifa", "football world cup"], ["The FIFA World Cup is the biggest international football (soccer) tournament. It's held every four years. Countries qualify; one hosts. Millions watch the final."]),
    (["chess", "how to play chess"], ["Chess is a two-player board game. Each side has 16 pieces (king, queen, rooks, bishops, knights, pawns). You move to attack the opponent's king. Checkmate wins. It's played worldwide for fun and in competitions."]),
    (["marathon", "why is a marathon 26 miles"], ["The marathon is 42.195 km (26.2 miles). The distance comes from the legend of a Greek messenger who ran from Marathon to Athens to report a victory, then died. The modern length was set at the 1908 London Olympics."]),
    (["pi", "what is pi", "value of pi"], ["Pi (π) is the ratio of a circle's circumference to its diameter. It's about 3.14159 and goes on forever without repeating. It appears in geometry, physics, and engineering."]),
    (["prime number", "prime numbers", "what is a prime"], ["A prime number is greater than 1 and has no positive divisors except 1 and itself. Examples: 2, 3, 5, 7, 11. Primes are building blocks in number theory and cryptography."]),
    (["infinity", "what is infinity"], ["Infinity isn't a normal number—it's the idea of something without end. In maths we use it in limits, sets, and calculus. There are different 'sizes' of infinity in set theory."]),
    (["fibonacci", "fibonacci sequence"], ["The Fibonacci sequence starts 0, 1 and each number is the sum of the two before: 0, 1, 1, 2, 3, 5, 8, 13... It appears in nature (petals, spirals) and in maths and art."]),
    (["why does it rain", "how does rain form"], ["Rain forms when water vapour in the air cools and condenses into droplets. Clouds are made of these droplets; when they get heavy enough, they fall as rain (or snow if it's cold enough)."]),
    (["thunder", "lightning", "thunderstorm"], ["Lightning is a giant spark of electricity between clouds or cloud and ground. Thunder is the sound of that air expanding rapidly. Light travels faster than sound, so you see lightning before you hear thunder."]),
    (["seasons", "why do we have seasons"], ["Seasons happen because Earth's axis is tilted. As we orbit the Sun, different parts get more or less direct sunlight. When your hemisphere is tilted toward the Sun, it's summer; away, it's winter."]),
    (["time zone", "time zones", "why time zones"], ["Time zones divide the world so the Sun is roughly overhead at noon locally. Earth is split into 24 zones (one per hour). Travel and the internet make coordinating across zones part of daily life."]),
    (["leap year", "why leap year"], ["A leap year has an extra day (February 29) to keep the calendar in sync with the solar year. Earth takes about 365.25 days to orbit the Sun. We add a day every four years (with a few exceptions)."]),
    (["another joke", "more jokes", "one more joke"], ["What do you call a bear with no teeth? A gummy bear! Or: Why don't scientists trust atoms? Because they make up everything!"]),
    (["weird fact", "strange fact", "weird facts"], ["Bananas are berries, but strawberries aren't. Or: A day on Venus is longer than its year—it rotates very slowly. Want more?"]),
    (["good morning", "good afternoon", "good evening", "good night"], ["Hello! Hope you're having a good one. What would you like to know?"]),
    (["yes", "yeah", "yep", "ok", "okay"], ["Great! What's your question?"]),
    (["no"], ["No problem. If you think of something, just ask!"]),
]

KNOWLEDGE.extend(MORE_KNOWLEDGE)

# Suggested questions when we don't find a match (random subset)
SUGGESTED_QUESTIONS = [
    "How far is the Sun from Earth?",
    "Why is the sky blue?",
    "What is a black hole?",
    "How do bees make honey?",
    "Who was Shakespeare?",
    "What is the speed of light?",
    "How many planets are there?",
    "Why do we have seasons?",
    "What is DNA?",
    "Tell me a joke",
    "What is the capital of Japan?",
    "How does the internet work?",
    "What is photosynthesis?",
    "When did dinosaurs live?",
    "What is the largest animal?",
    "What is the capital of France?",
    "How does a piano work?",
    "What caused World War II?",
    "What is machine learning?",
    "Why does it rain?",
    "What is the Great Wall of China?",
    "How do vaccines work?",
    "What is the tallest building?",
    "Tell me a fun fact",
    "What is the speed of sound?",
    "Who invented the internet?",
    "What is the largest ocean?",
    "How many bones are in the human body?",
    "What is the Fibonacci sequence?",
    "What is climate change?",
]


def _topic_fallback_hint(message: str) -> str:
    """When no match, suggest an example question based on detected topic or question type."""
    try:
        from smart_match import get_question_type, TOPIC_SETS
        user_words = get_words_expanded(message) if message else set()
        qtype = get_question_type(message or "")
        examples = []
        for topic_name, topic_words in TOPIC_SETS.items():
            if user_words & topic_words:
                if topic_name == "space":
                    examples.extend(["What is a black hole?", "How far is the Sun?"])
                elif topic_name == "animal":
                    examples.extend(["Tell me about dolphins", "What is the fastest animal?"])
                elif topic_name == "body":
                    examples.extend(["How does the heart work?", "What are vitamins?"])
                elif topic_name == "science":
                    examples.extend(["What is gravity?", "How do magnets work?"])
                elif topic_name == "geo":
                    examples.extend(["What is the capital of France?", "Where is Mount Everest?"])
                elif topic_name == "history":
                    examples.extend(["When did World War II end?", "Who invented the telephone?"])
                elif topic_name == "tech":
                    examples.extend(["How does the internet work?", "What is AI?"])
                elif topic_name == "food":
                    examples.extend(["Where does chocolate come from?", "What is vitamin C?"])
                elif topic_name == "math":
                    examples.extend(["What is pi?", "What is the Fibonacci sequence?"])
        if examples:
            return " For example: \"" + examples[0] + "\" or \"" + (examples[1] if len(examples) > 1 else "Tell me a fun fact") + "\"."
        if qtype == "who":
            return " For example: \"Who invented the light bulb?\" or \"Who wrote Romeo and Juliet?\"."
        if qtype == "where":
            return " For example: \"Where is the Eiffel Tower?\" or \"What is the capital of Japan?\"."
        if qtype == "when":
            return " For example: \"When did the Titanic sink?\" or \"When did humans land on the Moon?\"."
        if qtype == "how":
            return " For example: \"How do planes fly?\" or \"How does the heart work?\"."
    except Exception:
        pass
    return ""


def _strip_josiah_signoff(reply: str) -> str:
    """Remove trailing 'I'm Josiah' and 'what can I do for you' style sign-offs from replies."""
    if not reply or not isinstance(reply, str):
        return reply or ""
    s = reply
    # Strip common sign-off patterns from the end (case-insensitive, various punctuation)
    signoffs = [
        r"\s*I'm Josiah\!?\s*$",
        r"\s*I'm Josiah\.\s*$",
        r"\s*I'm Josiah—?\s*$",
        r"\s*I'm Josiah,?\s*$",
        r"\s*—?\s*I'm Josiah\.?\s*What can I do for you\??\s*$",
        r"\s*\.?\s*What can I do for you\??\s*$",
        r"\s*I'm Josiah\.?\s*What would you like to know\??\s*$",
        r"\s*I'm Josiah—?\s*what can I do for you\??\s*$",
        r"\s*I'm Josiah\.?\s*What else can I help with\??\s*$",
        r"\s*I'm Josiah\.?\s*What else would you like to know\??\s*$",
        r"\s*I'm Josiah—?\s*anything else\??\s*$",
        r"\s*I'm Josiah—?\s*ask me more\!?\s*$",
        r"\s*I'm Josiah\.?\s*What's your question\??\s*$",
        r"\s*I'm Josiah—?\s*want more on .+\??\s*$",
        r"\s*I'm Josiah\.?\s*What do you want to (ask|know)\??\s*$",
    ]
    for pat in signoffs:
        s = re.sub(pat, "", s, flags=re.IGNORECASE)
    # Also strip any remaining trailing " I'm Josiah." / " I'm Josiah!" / " I'm Josiah—" anywhere in the string
    s = re.sub(r"\s+I'm Josiah[.!—,]?\s*", " ", s, flags=re.IGNORECASE)
    return " ".join(s.split()).strip() or reply.strip()


def get_reply(message: str) -> Tuple[str, List[str]]:
    """
    Return (reply_text, suggested_questions).
    Uses autocorrect (Google-style), then smart keyword scoring.
    """
    corrected = autocorrect(message) if message else ""
    text = normalize(corrected)
    if not text:
        return "Please type something!", []

    match = get_best_match(text, KNOWLEDGE)
    if match:
        score, replies = match
        reply = random.choice(replies)
        reply = _strip_josiah_signoff(reply)
        suggestions = random.sample(SUGGESTED_QUESTIONS, min(5, len(SUGGESTED_QUESTIONS)))
        return reply, suggestions

    fallback = (
        "I'm Josiah—I'm not sure about that one! Try asking about space, Earth, animals, the human body, "
        "science, technology, history, geography, health, music, sports, maths, or ask for a fun fact or a joke!"
    )
    fallback += _topic_fallback_hint(message)
    return fallback, list(random.sample(SUGGESTED_QUESTIONS, min(6, len(SUGGESTED_QUESTIONS))))


# ---------------------------------------------------------------------------
# Extended knowledge: hundreds more entries for 20x smarter bot
# ---------------------------------------------------------------------------

EXTENDED_KNOWLEDGE = [
    (["tiger", "tigers"], ["Tigers are the largest wild cats. They live in Asia and are endangered. Each tiger's stripe pattern is unique. They're solitary hunters and can swim well."]),
    (["lion", "lions", "king of beasts"], ["Lions are big cats that live in prides in Africa and a small part of India. Males have manes. They hunt together and are symbols of strength in many cultures."]),
    (["bear", "bears", "grizzly", "polar bear"], ["Bears are large mammals found in the Americas, Europe, and Asia. Polar bears live in the Arctic; grizzlies and black bears in North America. They have a strong sense of smell and many hibernate."]),
    (["horse", "horses"], ["Horses were domesticated thousands of years ago for transport, work, and sport. They're herd animals, can run fast, and sleep standing up. There are hundreds of breeds."]),
    (["rabbit", "rabbits", "bunny"], ["Rabbits are small mammals with long ears and strong back legs. They're known for rapid reproduction and live in burrows. Domestic rabbits are popular pets."]),
    (["snake", "snakes"], ["Snakes are legless reptiles found on every continent except Antarctica. They swallow prey whole and some use venom to subdue it. They sense heat and smell with their tongue."]),
    (["turtle", "turtles", "tortoise"], ["Turtles are reptiles with a bony or leathery shell. Sea turtles live in oceans; tortoises on land. Some species live over 100 years. They've been around since the time of dinosaurs."]),
    (["whale", "whales", "whales migration"], ["Whales are marine mammals. Baleen whales filter small prey; toothed whales hunt fish and squid. Many migrate long distances. They're intelligent and some sing complex songs."]),
    (["bat", "bats"], ["Bats are the only mammals that truly fly. Most use echolocation to navigate and find insects at night. They're important pollinators and seed dispersers. Only a few species drink blood."]),
    (["ant", "ants", "ant colony"], ["Ants are social insects that live in colonies. They communicate with chemicals and can carry many times their weight. There are thousands of species; some farm fungi or keep aphids."]),
    (["ladybug", "ladybugs", "ladybird"], ["Ladybugs are small beetles, often red with black spots. They eat aphids and are welcome in gardens. Some species hibernate in large groups."]),
    (["coral", "coral reef", "coral reefs"], ["Corals are tiny animals that build calcium carbonate skeletons. Coral reefs are huge ecosystems supporting many fish and species. They're threatened by warming and acidifying oceans."]),
    (["jellyfish", "jellyfish"], ["Jellyfish are gelatinous drifters with stinging tentacles. They have no brain or heart. Some are tiny; others, like the lion's mane, have long tentacles. They've existed for hundreds of millions of years."]),
    (["starfish", "starfish", "sea star"], ["Sea stars (starfish) are echinoderms with usually five arms. They can regenerate lost arms. They move on tiny tube feet and eat by pushing their stomach outside their body."]),
    (["chameleon", "chameleons"], ["Chameleons are lizards known for changing colour (for mood and camouflage), long sticky tongues to catch prey, and eyes that move independently. Most live in trees in Africa and Madagascar."]),
    (["kangaroo", "kangaroos"], ["Kangaroos are Australian marsupials that hop on strong back legs. Females carry young in a pouch. They're herbivores and can reach high speeds over short distances."]),
    (["panda", "pandas", "giant panda"], ["Giant pandas live in Chinese bamboo forests. They eat almost only bamboo and are endangered. They have a distinctive black-and-white coat and are a symbol of conservation."]),
    (["zebra", "zebras"], ["Zebras are African equids with black-and-white stripes. Each pattern is unique. They live in herds and the stripes may help confuse predators or repel flies."]),
    (["giraffe", "giraffes"], ["Giraffes are the tallest land animals, with very long necks and legs. They live in African savannas and eat leaves from tall trees. Their long necks have the same number of neck vertebrae as most mammals—seven."]),
    (["hippo", "hippopotamus", "hippos"], ["Hippos are large African mammals that spend much of the day in water. They're aggressive and can run fast on land. They're related to whales and are one of the most dangerous animals in Africa."]),
    (["rhino", "rhinoceros", "rhinos"], ["Rhinos are large herbivores with one or two horns made of keratin. They're endangered due to poaching. Five species exist in Africa and Asia."]),
    (["camel", "camels"], ["Camels are adapted to deserts: they store fat in humps, can go long without water, and have thick eyelashes and closable nostrils for sand. Dromedaries have one hump; Bactrian camels two."]),
    (["owl", "owls"], ["Owls are mostly nocturnal birds of prey. They have large eyes, silent flight, and can turn their heads far. They hunt small mammals and birds. Many cultures associate them with wisdom."]),
    (["eagle", "eagles"], ["Eagles are large birds of prey with strong beaks and talons. They have excellent eyesight and soar on thermal currents. The bald eagle is a US symbol; the golden eagle is widespread in the Northern Hemisphere."]),
    (["parrot", "parrots"], ["Parrots are colourful birds with curved beaks and strong feet. Many can imitate sounds and human speech. They're intelligent and social. They live in tropical and subtropical regions."]),
    (["crow", "crows", "raven", "ravens"], ["Crows and ravens are highly intelligent birds in the corvid family. They use tools, solve puzzles, and have complex social behaviour. Ravens are larger; crows often live in groups."]),
    (["peacock", "peacocks", "peafowl"], ["Peacocks (male peafowl) are known for their spectacular tail feathers, which they display in courtship. Peahens are brown. They're native to South Asia and have been introduced elsewhere."]),
    (["flamingo", "flamingos"], ["Flamingos are wading birds with long legs and necks and pink plumage from the carotenoids in their diet. They filter-feed in shallow water. They often stand on one leg."]),
    (["salmon", "salmon migration"], ["Salmon are fish that hatch in freshwater, migrate to the ocean to grow, then return to their birth river to spawn. The journey is arduous and many die after spawning. They're important for ecosystems and human diet."]),
    (["goldfish", "goldfish"], ["Goldfish are domesticated carp, originally from East Asia. They can live in ponds or aquariums and come in many colours and shapes. With good care they can live for many years."]),
    (["frog", "frogs", "toad", "toads"], ["Frogs and toads are amphibians. Frogs usually have smooth skin and jump; toads often have bumpy skin and walk. They start as tadpoles in water and many absorb water through their skin."]),
    (["salamander", "salamanders"], ["Salamanders are amphibians with long tails and often bright colours. Some live in water, some on land. Certain species can regenerate lost limbs. They're found mainly in the Northern Hemisphere."]),
    (["lizard", "lizards"], ["Lizards are a large group of reptiles. They include geckos, iguanas, and chameleons. Many can detach their tail to escape predators. They're found on every continent except Antarctica."]),
    (["insect", "insects"], ["Insects have six legs, three body parts, and usually wings as adults. They're the most diverse animal group—millions of species. They pollinate plants, decompose matter, and are food for many animals."]),
    (["mosquito", "mosquitoes"], ["Mosquitoes are small flies; females bite to get blood for their eggs. Some species spread diseases like malaria and dengue. They're attracted to carbon dioxide and body odour. They need water to breed."]),
    (["cockroach", "cockroaches"], ["Cockroaches are ancient insects that can survive in tough conditions. Some are pests in homes; they can carry germs and trigger allergies. They're fast and can go without food for a while."]),
    (["scorpion", "scorpions"], ["Scorpions are arachnids with pincers and a venomous tail. They glow under UV light. Most species' venom isn't deadly to humans. They're found in warm, dry regions."]),
    (["centipede", "centipede", "millipede"], ["Centipedes have one pair of legs per segment and can bite; millipedes have two pairs per segment and often curl up. Both are many-legged arthropods. Centipedes are predators; millipedes eat decaying matter."]),
    (["worm", "worms", "earthworm"], ["Earthworms burrow through soil, aerating it and breaking down organic matter. They're important for soil health. They have no legs and breathe through their skin."]),
    (["slug", "slugs", "snail", "snails"], ["Slugs and snails are molluscs. Snails have a shell; slugs don't. They move on a muscular foot and leave a slime trail. Many are garden pests; some species are edible."]),
    (["squid", "squids", "octopus vs squid"], ["Squids have elongated bodies, eight arms and two tentacles, and an internal shell (pen). Some are huge—giant squid live in the deep ocean. They're fast swimmers and use jet propulsion."]),
    (["crab", "crabs"], ["Crabs are crustaceans with a hard shell and pincers. They live in oceans, freshwater, and on land. They walk sideways and many are edible. Hermit crabs use empty shells for protection."]),
    (["lobster", "lobsters"], ["Lobsters are large marine crustaceans with strong claws. They're long-lived and can regenerate lost limbs. They're a prized seafood. They turn red when cooked because of pigment changes."]),
    (["seahorse", "seahorses"], ["Seahorses are fish with a horse-like head and prehensile tail. They're slow swimmers and anchor to seagrass. Male seahorses carry the eggs in a pouch until they hatch—unique among fish."]),
    (["clownfish", "clownfish", "nemo"], ["Clownfish live among sea anemones; a mucus layer protects them from stings. They're small, colourful fish. In nature, the largest in a group is female; if she dies, a male can change sex and become female."]),
    (["piranha", "piranhas"], ["Piranhas are South American fish with sharp teeth. They're often portrayed as vicious, but most species are scavengers or eat plants. In groups they can strip prey quickly when food is scarce."]),
    (["tornado", "tornadoes", "twister"], ["A tornado is a violently rotating column of air touching the ground. They form from severe thunderstorms and can cause huge damage. The US Midwest has many; they're rated on the Enhanced Fujita scale."]),
    (["hurricane", "hurricanes", "cyclone", "typhoon"], ["Hurricanes (cyclones, typhoons) are huge rotating storms over warm ocean water. They bring strong winds, heavy rain, and storm surge. They're named and categorized by wind speed (e.g. Category 1–5)."]),
    (["snow", "how does snow form"], ["Snow forms when water vapour in clouds turns into ice crystals at below-freezing temperatures. The crystals stick together into flakes. Snow reflects sunlight and helps cool the planet."]),
    (["wind", "what causes wind"], ["Wind is air moving from high pressure to low pressure. The Sun heats the Earth unevenly, creating pressure differences. The rotation of the Earth (Coriolis effect) influences wind direction in large-scale weather."]),
    (["humidity", "what is humidity"], ["Humidity is the amount of water vapour in the air. High humidity makes it feel hotter because sweat evaporates less. Relative humidity is the percentage of moisture the air holds compared to its maximum at that temperature."]),
    (["aurora", "northern lights", "southern lights"], ["Auroras are glowing lights in the sky near the poles. Charged particles from the Sun hit Earth's magnetic field and excite atoms in the upper atmosphere. In the north it's aurora borealis; in the south, aurora australis."]),
    (["magnetosphere", "earth magnetic field"], ["Earth's magnetic field is generated by the molten iron in the outer core. It protects us from solar wind and cosmic rays and guides compass needles. It can flip polarity over long time scales."]),
    (["tectonic plates", "plate tectonics"], ["Earth's lithosphere is broken into tectonic plates that move slowly. Where they meet we get earthquakes, volcanoes, and mountains. The theory of plate tectonics explains continental drift and much of Earth's geology."]),
    (["mineral", "minerals", "rocks"], ["Minerals are naturally occurring solid substances with a specific chemical makeup and crystal structure. Rocks are made of one or more minerals. Examples: quartz, feldspar, calcite."]),
    (["gemstone", "gems", "diamond", "ruby"], ["Gemstones are minerals or rocks valued for beauty and rarity. Diamonds are carbon; rubies and sapphires are corundum. They're cut and polished for jewellery. Some are very hard (diamond is the hardest)."]),
    (["fossil", "fossils"], ["Fossils are preserved remains or traces of ancient life. They form when organisms are buried and minerals replace tissue or leave impressions. They tell us about past life and environments."]),
    (["ice age", "ice ages", "glacier"], ["Ice ages are periods when large ice sheets cover much of the Earth. We're in an interglacial now. Glaciers are moving masses of ice that carve landscapes and leave moraines and U-shaped valleys."]),
    (["rainforest", "tropical rainforest"], ["Tropical rainforests are dense forests near the equator with high rainfall and biodiversity. They produce much of the world's oxygen and are home to countless species. Deforestation is a major threat."]),
    (["tundra", "arctic tundra"], ["The tundra is a cold, treeless biome with permafrost. It's found in the Arctic and on high mountains. Plants are low (mosses, lichens, small shrubs). Animals include caribou, Arctic foxes, and migratory birds."]),
    (["savanna", "savannah"], ["Savannas are grasslands with scattered trees, found in Africa, South America, and Australia. They have wet and dry seasons. Iconic wildlife includes lions, elephants, and wildebeest."]),
    (["wetland", "wetlands", "marsh", "swamp"], ["Wetlands are areas where water covers the soil or is near the surface. They filter water, store floodwater, and provide habitat. Marshes, swamps, and bogs are types of wetlands."]),
    (["biome", "biomes"], ["Biomes are large ecological areas with similar climate and life—e.g. tropical rainforest, desert, tundra, grassland. They're defined by temperature, rainfall, and the plants and animals that live there."]),
    (["ecosystem", "ecosystem"], ["An ecosystem is a community of living things and their physical environment, all interacting. Energy flows (e.g. sun to plants to animals); nutrients cycle. Healthy ecosystems provide services like clean water and pollination."]),
    (["food chain", "food web"], ["A food chain shows who eats whom (e.g. grass → rabbit → fox). A food web is many interconnected chains. Producers (plants) are at the base; top predators at the end. Decomposers break down dead matter."]),
    (["endangered", "extinction", "endangered species"], ["Many species are endangered due to habitat loss, hunting, pollution, and climate change. Extinction is permanent. Conservation efforts include protected areas, breeding programmes, and laws like the Endangered Species Act."]),
    (["pollination", "pollinators", "bees pollinate"], ["Pollination is when pollen reaches the female part of a flower so seeds can form. Bees, butterflies, birds, and bats are pollinators. Many crops depend on them; pollinator decline is a concern."]),
    (["chlorophyll", "why are plants green"], ["Plants look green because chlorophyll—the pigment that captures light for photosynthesis—absorbs red and blue light but reflects green. So we see the reflected green."]),
    (["oxygen", "where does oxygen come from"], ["Most of Earth's oxygen comes from photosynthesis by plants, algae, and cyanobacteria in the ocean. They use sunlight to turn CO2 and water into sugar and release oxygen."]),
    (["carbon dioxide", "co2", "greenhouse gas"], ["Carbon dioxide (CO2) is a gas in the air. Plants use it for photosynthesis. It's a greenhouse gas—it traps heat. Burning fossil fuels increases CO2 and contributes to climate change."]),
    (["nitrogen", "nitrogen cycle"], ["Nitrogen is essential for life (e.g. in proteins and DNA). The air is mostly nitrogen but most organisms can't use it directly. Bacteria fix it; it cycles through soil, plants, and animals; decomposers return it."]),
    (["water cycle", "hydrological cycle"], ["The water cycle: water evaporates from oceans and land, forms clouds, falls as rain or snow, and flows back to oceans or groundwater. It's driven by the Sun and never stops."]),
    (["acid rain"], ["Acid rain is rain (or snow) that's more acidic than normal because of sulphur and nitrogen oxides in the air—often from burning fossil fuels. It can harm forests, lakes, and buildings."]),
    (["ozone", "ozone layer"], ["The ozone layer in the stratosphere absorbs most of the Sun's UV radiation, protecting life. CFCs (now largely phased out) were damaging it; the 'ozone hole' over Antarctica has been slowly healing."]),
    (["renewable energy", "clean energy"], ["Renewable energy comes from sources that don't run out or regenerate quickly: solar, wind, hydro, geothermal, biomass. They produce little or no greenhouse gases compared to fossil fuels."]),
    (["nuclear power", "nuclear energy"], ["Nuclear power uses fission—splitting atoms—to heat water and drive turbines. It produces no direct CO2 but creates radioactive waste. Safety and waste storage are debated. Fusion (like the Sun) is still experimental for power."]),
    (["battery", "batteries", "how do batteries work"], ["Batteries store chemical energy and convert it to electrical energy when connected to a circuit. They have positive and negative electrodes and an electrolyte. Rechargeable batteries can be used many times."]),
    (["hydrogen", "hydrogen fuel"], ["Hydrogen is the lightest element. As a fuel it can power vehicles or generate electricity; when burned or used in fuel cells the main byproduct is water. 'Green' hydrogen is made with renewable energy."]),
    (["fossil fuels", "coal", "oil", "natural gas"], ["Fossil fuels (coal, oil, natural gas) formed from ancient organic matter. Burning them releases CO2 and other pollutants. They're non-renewable and a main driver of climate change; transition to cleaner energy is ongoing."]),
    (["plastic", "plastics", "where does plastic come from"], ["Most plastic is made from petroleum. It's durable and versatile but doesn't biodegrade easily, so it accumulates in the environment. Recycling and reducing single-use plastic help; microplastics are a growing concern."]),
    (["glass", "how is glass made"], ["Glass is made by melting silica (sand) with other ingredients at high heat, then cooling it so it doesn't crystallise. It's transparent, hard, and recyclable. Used for windows, containers, and optics."]),
    (["metal", "metals", "alloy"], ["Metals are elements that conduct electricity and heat, and are often shiny and malleable. Alloys mix metals (e.g. steel is iron and carbon) for strength or other properties. Many are essential for construction and tech."]),
    (["conductor", "insulator", "electricity conduct"], ["Conductors (e.g. metals) let electric current flow easily. Insulators (e.g. rubber, plastic) resist it. Semiconductors (e.g. silicon) are in between—they're the basis of electronics."]),
    (["semiconductor", "silicon", "computer chip"], ["Semiconductors have conductivity between conductors and insulators. Silicon is used in most chips. By doping and patterning them we make transistors and integrated circuits—the heart of computers and phones."]),
    (["transistor", "transistors"], ["Transistors are tiny switches that control current. They're the building blocks of digital circuits—millions or billions on a single chip. They made modern computing possible."]),
    (["quantum", "quantum physics", "quantum mechanics"], ["Quantum mechanics describes nature at very small scales. Particles can be in superpositions, show wave-particle duality, and be entangled. It's counterintuitive but incredibly accurate and underlies technologies like lasers and MRI."]),
    (["photon", "photons", "light particle"], ["Photons are particles of light—quantum packets of electromagnetic energy. They have no mass, always move at the speed of light, and can behave as both wave and particle."]),
    (["antimatter", "antimatter"], ["Antimatter is like matter but with opposite charge (e.g. positron vs electron). When matter and antimatter meet they annihilate, releasing energy. It's rare in the universe; we make tiny amounts in particle accelerators."]),
    (["particle accelerator", "cern", "large hadron collider"], ["Particle accelerators speed up particles and smash them together to study fundamental physics. CERN's Large Hadron Collider (LHC) discovered the Higgs boson. It's a ring under France and Switzerland."]),
    (["higgs boson", "god particle"], ["The Higgs boson is a particle that gives other particles mass via the Higgs field. It was predicted in the 1960s and discovered at the LHC in 2012. It's sometimes called the 'God particle' in popular media."]),
    (["algorithm", "algorithms"], ["An algorithm is a step-by-step procedure to solve a problem or perform a task. In computing, algorithms are the logic behind search, sort, and AI. Good algorithms are correct and efficient."]),
    (["binary", "binary code", "zeros and ones"], ["Binary uses only two digits—0 and 1. Computers store and process everything as binary because electronic switches are on or off. Each 0 or 1 is a bit; eight bits make a byte."]),
    (["encryption", "encrypt", "cryptography"], ["Encryption scrambles data so only someone with the right key can read it. It protects messages, passwords, and payments. Modern cryptography uses maths that's hard to reverse without the key."]),
    (["blockchain"], ["A blockchain is a distributed ledger—a chain of blocks holding data (e.g. transactions). Each block is linked and secured with cryptography. Bitcoin and other cryptocurrencies use it; it's also used for contracts and records."]),
    (["robot", "robots", "robotics"], ["Robots are machines that can carry out tasks automatically or semi-automatically. They range from factory arms to drones and humanoid research robots. Robotics combines mechanics, electronics, and software."]),
    (["self-driving", "autonomous car", "driverless"], ["Self-driving cars use sensors and AI to navigate without a human driver. Levels range from driver assistance to full autonomy. Safety, regulation, and ethics are active areas of development and debate."]),
    (["deep learning", "neural network"], ["Neural networks are computing systems inspired by the brain—layers of nodes that process input and learn from data. Deep learning uses many layers and has achieved breakthroughs in vision, language, and game-playing."]),
    (["natural language", "nlp", "language processing"], ["Natural language processing (NLP) is when computers understand or generate human language. It's used in translation, chatbots, search, and voice assistants. Large language models have recently improved it a lot."]),
    (["programming language", "coding", "code"], ["Programming languages let humans write instructions for computers. Examples: Python, JavaScript, Java, C++. They have syntax and semantics; code is compiled or interpreted into machine instructions."]),
    (["open source", "open source software"], ["Open source means the source code is publicly available so people can view, use, modify, and share it. Linux, Python, and many tools are open source. It encourages collaboration and transparency."]),
    (["github"], ["GitHub is a platform for hosting and collaborating on code using Git (version control). Developers store repositories, track issues, and review code. It's widely used in open source and companies."]),
    (["database", "databases", "sql"], ["Databases store and organise data. Relational databases use tables and SQL; NoSQL databases use other structures. They're essential for apps, websites, and analytics."]),
    (["server", "servers", "web server"], ["A server is a computer or program that provides services to other computers (clients). Web servers deliver web pages; file servers store files. They run 24/7 and handle many requests."]),
    (["bandwidth", "internet speed"], ["Bandwidth is the maximum rate of data transfer—how much you can send or receive per second. Higher bandwidth means faster downloads and smoother streaming. It's measured in bits per second (e.g. Mbps)."]),
    (["wifi", "wi-fi", "wireless"], ["Wi‑Fi is wireless networking that uses radio waves. Devices connect to a router that's usually linked to the internet by cable or fibre. Range and speed depend on the standard (e.g. Wi‑Fi 6) and environment."]),
    (["bluetooth"], ["Bluetooth is a short-range wireless technology for connecting devices—phones to earbuds, keyboards to computers, etc. It uses little power and operates in the 2.4 GHz band."]),
    (["5g", "5g network"], ["5G is the fifth generation of mobile networks. It offers higher speed, lower latency, and more capacity than 4G. It supports more devices and enables things like better video calls and potential for IoT and autonomous systems."]),
    (["phishing", "phishing attack"], ["Phishing is when attackers pretend to be a trusted party (e.g. email from 'your bank') to steal passwords or data. Don't click suspicious links; check URLs; use two-factor authentication."]),
    (["ransomware"], ["Ransomware is malware that encrypts your files and demands payment to unlock them. Backups (offline or in the cloud) are the best defence. Don't pay if you can avoid it—it funds more attacks."]),
    (["firewall"], ["A firewall is software or hardware that monitors and controls network traffic. It blocks or allows data based on rules, helping protect your computer or network from unauthorised access."]),
    (["operating system", "os", "windows", "macos", "linux"], ["An operating system (OS) manages hardware and software—e.g. Windows, macOS, Linux, Android, iOS. It handles files, memory, and runs applications. You interact with it through the desktop or shell."]),
    (["cpu", "processor", "central processing unit"], ["The CPU (central processing unit) is the main processor that executes instructions and runs programs. Speed is measured in GHz; multiple cores allow parallel work. It's the 'brain' of the computer."]),
    (["ram", "memory", "random access memory"], ["RAM is fast, temporary storage the computer uses for running programs and open data. More RAM usually means you can run more or heavier apps at once. It's cleared when the power is off."]),
    (["gpu", "graphics card"], ["A GPU (graphics processing unit) handles graphics and parallel computing. It's used for games, video editing, and AI training. Dedicated GPUs are separate cards; integrated GPUs are part of the CPU."]),
    (["solid state drive", "ssd", "hard drive"], ["SSDs store data on flash memory with no moving parts—they're faster and more shock-resistant than traditional hard drives. HDDs use spinning disks and are cheaper for large storage."]),
    (["resolution", "4k", "1080p"], ["Resolution is the number of pixels (e.g. 1920×1080 = Full HD, 3840×2160 = 4K). Higher resolution means sharper image but needs more processing and bandwidth. 4K is common for TVs and monitors."]),
    (["frame rate", "fps", "frames per second"], ["Frame rate (fps) is how many images are shown per second in video or games. Higher fps looks smoother. 24–30 fps is common for film; 60+ for games. Monitors have refresh rates (Hz) that limit max fps."]),
    (["streaming", "stream"], ["Streaming means playing audio or video over the internet without downloading the whole file first. Services like Netflix and Spotify stream. It uses bandwidth in real time; quality can adapt to your connection."]),
    (["podcast", "podcasts"], ["Podcasts are audio (or video) series you can subscribe to and listen to on demand. They cover news, stories, education, and entertainment. You get them via apps or websites."]),
    (["ebook", "e-books", "electronic book"], ["E-books are books in digital form, read on devices or apps. Formats include EPUB and PDF. They're portable and often cheaper; libraries lend them too."]),
    (["social media", "social network"], ["Social media are platforms where people share content and connect—e.g. Facebook, Instagram, Twitter/X, TikTok, LinkedIn. They affect news, culture, and communication; privacy and misinformation are ongoing concerns."]),
    (["search engine", "google", "how search works"], ["Search engines index the web and rank results by relevance (and other factors). They use crawlers and algorithms. Google is the most used; others include Bing and DuckDuckGo. SEO is about optimising content for search."]),
    (["email", "how email works"], ["Email sends messages over the internet. Your client (e.g. Gmail) talks to mail servers with protocols like SMTP and IMAP. Spam filters and encryption (e.g. TLS) protect and secure mail."]),
    (["domain", "domain name", "url"], ["A domain name (e.g. example.com) is a human-friendly address for a website. DNS translates it to an IP address. URLs include the protocol (https), domain, and path."]),
    (["browser", "web browser", "chrome", "firefox"], ["A web browser fetches and displays web pages. It interprets HTML, CSS, and JavaScript. Major browsers include Chrome, Firefox, Safari, and Edge. They also manage tabs, bookmarks, and security."]),
    (["download", "upload"], ["Downloading is receiving data from the internet to your device; uploading is sending data from your device. Speed depends on your connection and the server. Files and streams can be downloaded."]),
    (["backup", "back up", "backups"], ["A backup is a copy of data so you can restore it if something is lost or corrupted. Keep backups regularly and in a different place (e.g. external drive or cloud). The 3-2-1 rule: 3 copies, 2 media types, 1 offsite."]),
    (["virus scan", "antivirus"], ["Antivirus software scans for malware (viruses, trojans, ransomware) and can quarantine or remove it. Keep it updated and run scans. It's one layer of security alongside careful browsing and updates."]),
    (["update", "software update", "patch"], ["Updates fix bugs and security holes and add features. Install them for your OS and apps. Patches are often critical for security; delaying can leave you vulnerable."]),
    (["capital of mexico", "mexico city"], ["The capital of Mexico is Mexico City. It's one of the largest cities in the world and the country's political, cultural, and economic centre. It was built on the site of the Aztec capital Tenochtitlan."]),
    (["capital of russia", "moscow"], ["The capital of Russia is Moscow. It's the largest city in Russia and a major political, economic, and cultural centre. The Kremlin and Red Square are there."]),
    (["capital of south korea", "seoul"], ["The capital of South Korea is Seoul. It's a huge, modern city with a long history. It's a global centre for technology, culture, and entertainment (including K-pop)."]),
    (["capital of egypt", "cairo"], ["The capital of Egypt is Cairo. It's near the Nile Delta and the Pyramids of Giza. It's the largest city in Africa and the Arab world and a major cultural and political centre."]),
    (["capital of argentina", "buenos aires"], ["The capital of Argentina is Buenos Aires. It's a major port and cultural city known for tango, football, and European-style architecture."]),
    (["capital of south africa", "pretoria", "cape town"], ["South Africa has three capitals: Pretoria (administrative), Cape Town (legislative), and Bloemfontein (judicial). It's unique in having multiple capital cities."]),
    (["capital of nigeria", "abuja"], ["The capital of Nigeria is Abuja. It was chosen as a planned capital in the centre of the country. Lagos is the largest city but Abuja is the seat of government."]),
    (["capital of kenya", "nairobi"], ["The capital of Kenya is Nairobi. It's the largest city in Kenya and an economic hub for East Africa. The Nairobi National Park is nearby."]),
    (["capital of turkey", "ankara", "istanbul"], ["The capital of Turkey is Ankara. Istanbul is the largest city and was the historical capital of the Byzantine and Ottoman empires, but Ankara became the capital when the Republic was founded."]),
    (["capital of indonesia", "jakarta"], ["The capital of Indonesia is Jakarta, on Java. It's a huge, crowded city. Indonesia is planning to move the capital to Nusantara in Borneo."]),
    (["capital of thailand", "bangkok"], ["The capital of Thailand is Bangkok. It's a bustling city known for temples, street food, and the Grand Palace. It's one of the most visited cities in the world."]),
    (["capital of vietnam", "hanoi"], ["The capital of Vietnam is Hanoi. It's in the north and has a long history. Ho Chi Minh City (Saigon) in the south is larger and the economic hub."]),
    (["capital of poland", "warsaw"], ["The capital of Poland is Warsaw. It was largely rebuilt after World War II. It's the country's political, economic, and cultural centre."]),
    (["capital of netherlands", "amsterdam"], ["The capital of the Netherlands is Amsterdam. The government sits in The Hague, but Amsterdam is the constitutional capital and the largest city, known for canals and museums."]),
    (["capital of sweden", "stockholm"], ["The capital of Sweden is Stockholm. It's built on islands and known for design, innovation, and the Nobel Prize ceremonies."]),
    (["capital of norway", "oslo"], ["The capital of Norway is Oslo. It's at the head of the Oslofjord and is the country's economic and cultural centre."]),
    (["capital of switzerland", "bern"], ["The capital of Switzerland is Bern. Zurich is the largest city, but Bern is the federal capital. Switzerland has four national languages and a direct democracy."]),
    (["capital of austria", "vienna"], ["The capital of Austria is Vienna. It's known for music (Mozart, Beethoven), imperial history, and coffee houses. It's consistently ranked among the most liveable cities."]),
    (["capital of belgium", "brussels"], ["The capital of Belgium is Brussels. It's also the de facto capital of the European Union and NATO. The city is bilingual (French and Dutch)."]),
    (["capital of ireland", "dublin"], ["The capital of Ireland is Dublin. It's on the east coast and is the country's largest city, known for literature, pubs, and history."]),
    (["capital of portugal", "lisbon"], ["The capital of Portugal is Lisbon. It's on the Atlantic coast and one of the oldest cities in Europe. It's known for hills, trams, and maritime history."]),
    (["capital of greece", "athens"], ["The capital of Greece is Athens. It's one of the world's oldest cities and the birthplace of democracy. The Acropolis and Parthenon are there."]),
    (["capital of scotland", "edinburgh"], ["The capital of Scotland is Edinburgh. It's known for the Edinburgh Festival, the castle, and historic streets. Glasgow is the largest city in Scotland."]),
    (["capital of wales", "cardiff"], ["The capital of Wales is Cardiff. It's the largest city in Wales and the political and cultural centre. The Principality Stadium is there."]),
    (["capital of new zealand", "wellington"], ["The capital of New Zealand is Wellington. It's in the south of the North Island. Auckland is the largest city but Wellington is the seat of government."]),
    (["tallest building", "burj khalifa", "skyscraper"], ["The Burj Khalifa in Dubai is the tallest building in the world at 828 metres. Skyscrapers need strong foundations and can sway in the wind; they're feats of engineering."]),
    (["seven wonders", "wonders of the world"], ["The Seven Wonders of the Ancient World were famous structures; only the Great Pyramid remains. There are modern lists too, e.g. New7Wonders, which include the Great Wall, Petra, and Machu Picchu."]),
    (["machu picchu"], ["Machu Picchu is an Inca citadel in the Peruvian Andes. It was built in the 15th century and abandoned during the Spanish conquest. It's a UNESCO site and one of the most famous archaeological sites in the world."]),
    (["petra"], ["Petra is an ancient city in Jordan, carved into red rock. It was the capital of the Nabataeans. The Treasury is its most famous facade. It's a UNESCO World Heritage site."]),
    (["taj mahal"], ["The Taj Mahal in Agra, India, is a white marble mausoleum built by the Mughal emperor Shah Jahan for his wife. It's a symbol of love and one of the most recognisable buildings in the world."]),
    (["statue of liberty"], ["The Statue of Liberty is in New York Harbor. It was a gift from France and symbolises freedom. It was dedicated in 1886 and is a major landmark and UNESCO site."]),
    (["eiffel tower"], ["The Eiffel Tower is an iron lattice tower in Paris, built for the 1889 World's Fair. It was initially criticised but became the symbol of Paris and one of the most visited monuments in the world."]),
    (["great barrier reef"], ["The Great Barrier Reef off Australia is the world's largest coral reef system. It's home to thousands of species and is a UNESCO site. It's threatened by warming oceans and pollution."]),
    (["mount fuji"], ["Mount Fuji is Japan's highest peak and an active (currently dormant) volcano. It's a cultural and religious icon and a UNESCO site. Climbing season is in summer."]),
    (["niagara falls"], ["Niagara Falls is a group of waterfalls on the US–Canada border. They're a major tourist attraction and a source of hydroelectric power. The Horseshoe Falls are on the Canadian side."]),
    (["grand canyon"], ["The Grand Canyon is a steep-sided canyon carved by the Colorado River in Arizona. It's one of the most famous natural landmarks and shows billions of years of geological history."]),
    (["mount rushmore"], ["Mount Rushmore in South Dakota has giant carved faces of four US presidents: Washington, Jefferson, Roosevelt, and Lincoln. It was completed in 1941 and is a major tourist site."]),
    (["stonehenge"], ["Stonehenge in England is a prehistoric ring of standing stones. Its purpose is debated—possibly ceremonial or astronomical. It was built in stages over thousands of years."]),
    (["acropolis"], ["The Acropolis in Athens is a hilltop citadel with ancient buildings, including the Parthenon. It was the centre of Athenian religion and culture and is a symbol of classical Greece."]),
    (["colosseum"], ["The Colosseum in Rome is an ancient amphitheatre where gladiators fought and spectacles were held. It's one of the largest surviving Roman structures and a major tourist attraction."]),
    (["sphinx"], ["The Great Sphinx of Giza is a limestone statue with a lion's body and a human head. It's near the Pyramids and is thought to represent the pharaoh Khafre. It's one of the world's oldest and largest statues."]),
    (["angkor wat"], ["Angkor Wat in Cambodia is a vast temple complex originally dedicated to Vishnu. It's the world's largest religious monument and a symbol of Cambodia. It was built in the 12th century."]),
    (["forbidden city"], ["The Forbidden City in Beijing was the Chinese imperial palace for almost 500 years. It's a vast complex of wooden buildings and now houses the Palace Museum. It's a UNESCO World Heritage site."]),
    (["westminster", "big ben", "parliament london"], ["The Palace of Westminster in London houses the UK Parliament. Big Ben is the nickname for the Great Bell in the clock tower (Elizabeth Tower). It's a symbol of British democracy."]),
    (["kremlin"], ["The Kremlin is a fortified complex in Moscow that has been the seat of Russian power for centuries. It contains palaces, cathedrals, and government buildings. The name is often used to mean the Russian government."]),
    (["white house"], ["The White House in Washington, D.C., is the official residence and workplace of the US president. It has been the home of every president since John Adams. It's a symbol of the American government."]),
    (["buckingham palace"], ["Buckingham Palace in London is the monarch's official residence. The Changing of the Guard is a famous ceremony. It's used for state occasions and royal events."]),
    (["empire state building"], ["The Empire State Building is a famous skyscraper in New York City. It was the world's tallest building when completed in 1931. It has an observation deck and is an Art Deco icon."]),
    (["golden gate bridge"], ["The Golden Gate Bridge spans the entrance to San Francisco Bay. It opened in 1937 and was the longest suspension bridge at the time. Its orange colour was chosen for visibility in fog."]),
    (["sydney opera house"], ["The Sydney Opera House in Australia is famous for its sail-like roof. It was designed by Jørn Utzon and opened in 1973. It's a UNESCO site and a symbol of Sydney and Australia."]),
    (["tower of london"], ["The Tower of London is a historic castle on the Thames. It has been a fortress, prison, and armoury. The Crown Jewels are kept there and it's guarded by Beefeaters."]),
    (["notre dame", "notre dame cathedral"], ["Notre-Dame de Paris is a medieval cathedral on the Île de la Cité. It was badly damaged by fire in 2019 and is being restored. It's a masterpiece of Gothic architecture."]),
    (["sagrada familia"], ["The Sagrada Família in Barcelona is a large basilica designed by Antoni Gaudí. Construction began in 1882 and is still ongoing. It's known for its unique, organic design."]),
    (["parthenon"], ["The Parthenon is a temple on the Acropolis in Athens, dedicated to the goddess Athena. It's a symbol of ancient Greece and Western civilisation. Many of its sculptures are in the British Museum."]),
    (["roman forum"], ["The Roman Forum was the centre of ancient Rome—political, religious, and commercial. Today it's a ruin of temples, basilicas, and arches. It's next to the Colosseum."]),
    (["pompeii"], ["Pompeii was a Roman city buried by the eruption of Mount Vesuvius in 79 CE. The ash preserved buildings and even bodies. It's one of the best-preserved ancient sites and a UNESCO World Heritage site."]),
    (["terracotta army"], ["The Terracotta Army is a collection of thousands of life-sized clay soldiers buried with China's first emperor, Qin Shi Huang, to protect him in the afterlife. It was discovered in 1974 near Xi'an."]),
    (["alhambra"], ["The Alhambra in Granada, Spain, is a palace and fortress complex from the Moorish period. It's known for intricate Islamic art and gardens. It's a UNESCO site and one of Spain's most visited monuments."]),
    (["neuschwanstein"], ["Neuschwanstein Castle in Bavaria, Germany, was built by King Ludwig II in the 19th century. It looks like a fairy-tale castle and inspired Disney's Sleeping Beauty castle. It's one of the most photographed castles in the world."]),
    (["versailles"], ["The Palace of Versailles near Paris was the centre of French royal power. Its Hall of Mirrors and gardens are famous. The Treaty of Versailles ending World War I was signed there."]),
    (["mont saint michel"], ["Mont-Saint-Michel is a rocky island in Normandy, France, topped by a medieval monastery. It's connected to the mainland by a causeway and is a UNESCO site and major tourist destination."]),
    (["christ the redeemer"], ["Christ the Redeemer is a huge statue of Jesus in Rio de Janeiro, Brazil. It stands on Corcovado mountain and is one of the New Seven Wonders. It was completed in 1931."]),
    (["chichen itza"], ["Chichen Itza is a large Maya city in Mexico. The stepped pyramid El Castillo is famous. The site shows Maya and Toltec influence and is a UNESCO site and one of the New Seven Wonders."]),
    (["teotihuacan"], ["Teotihuacan was a large pre-Columbian city in Mexico. The Pyramid of the Sun and Moon dominate the site. It was one of the largest cities in the ancient world; its builders are still debated."]),
    (["mesopotamia"], ["Mesopotamia (between the Tigris and Euphrates) was one of the cradles of civilisation. Sumer, Babylon, and Assyria arose there. Writing, the wheel, and early cities developed in the region."]),
    (["indus valley", "harappa"], ["The Indus Valley civilisation (including Harappa and Mohenjo-daro) was contemporary with ancient Egypt and Mesopotamia. It had planned cities, writing (undeciphered), and trade. It declined around 1900 BCE."]),
    (["inca", "incas", "incan empire"], ["The Inca Empire was the largest in pre-Columbian America, centred in the Andes. They built Machu Picchu and a vast road network. The Spanish conquered them in the 16th century."]),
    (["aztec", "aztecs", "tenochtitlan"], ["The Aztecs built an empire in central Mexico with their capital at Tenochtitlan (now Mexico City). They had a complex society, calendar, and religion. The Spanish, with local allies, conquered them in 1521."]),
    (["maya", "mayans", "mayan civilisation"], ["The Maya built cities and a writing system in Mesoamerica. They had advanced maths (including zero) and astronomy. Many cities were abandoned before the Spanish arrived; descendants still live in the region."]),
    (["viking", "vikings", "norsemen"], ["The Vikings were Norse seafarers from Scandinavia who raided, traded, and settled across Europe and beyond (8th–11th centuries). They reached North America. They had a rich culture and mythology."]),
    (["samurai", "samurais", "japanese warrior"], ["Samurai were Japanese warriors who served lords and followed a code (bushido). They were dominant from the medieval period until the Meiji Restoration. They're celebrated in film and culture."]),
    (["knight", "knights", "medieval knight"], ["Knights were mounted warriors in medieval Europe, often of noble birth. They followed chivalry and served lords. They wore armour and fought in battles and tournaments."]),
    (["gladiator", "gladiators"], ["Gladiators were fighters in ancient Rome who fought in arenas for entertainment. They could be slaves, prisoners, or volunteers. Some became famous; most had short lives."]),
    (["pharaoh", "pharaohs"], ["Pharaohs were the rulers of ancient Egypt, considered divine. They built pyramids and temples. Famous ones include Tutankhamun, Cleopatra, and Ramesses II."]),
    (["emperor", "emperors", "empire"], ["An emperor rules an empire—multiple peoples or territories. Historical examples include Roman, Chinese, and Byzantine emperors. The title often implied supreme authority."]),
    (["democracy", "democratic"], ["Democracy is government by the people, usually through elections and representation. Ancient Athens had direct democracy; modern states use representative democracy. It includes rights, rule of law, and accountability."]),
    (["monarchy", "monarch", "king", "queen"], ["A monarchy is rule by a single person (king or queen), often hereditary. Constitutional monarchs share power with parliaments; absolute monarchs have full control. Many countries still have ceremonial monarchs."]),
    (["republic", "republican"], ["A republic is a state without a hereditary monarch; power is held by the people or their representatives. The head of state is usually elected. Many democracies are republics (e.g. USA, France, India)."]),
    (["french revolution"], ["The French Revolution (1789–1799) overthrew the monarchy and reshaped French society. Ideas of liberty, equality, and fraternity spread. It led to the Reign of Terror, Napoleon, and lasting political change."]),
    (["american revolution", "american independence"], ["The American Revolution (1775–1783) was the war in which the American colonies broke from Britain and founded the United States. The Declaration of Independence (1776) and the Constitution followed."]),
    (["civil rights", "civil rights movement"], ["The civil rights movement in the US (especially the 1950s–60s) fought for equal rights for African Americans. Key figures include Martin Luther King Jr. and Rosa Parks. It led to laws banning segregation and discrimination."]),
    (["suffrage", "women vote", "women's rights"], ["Suffrage is the right to vote. Women's suffrage was won in many countries in the late 19th and early 20th centuries. New Zealand was first (1893); the US granted it in 1920."]),
    (["apartheid"], ["Apartheid was a system of racial segregation and discrimination in South Africa (1948–1990s). It restricted where people could live, work, and go to school. Nelson Mandela and others fought it; it ended with democratic elections in 1994."]),
    (["united nations", "un", "un organisation"], ["The United Nations (UN) was founded in 1945 to promote peace, cooperation, and human rights. It has a General Assembly, Security Council, and many agencies (e.g. WHO, UNICEF). Almost every country is a member."]),
    (["nato"], ["NATO (North Atlantic Treaty Organisation) is a military alliance of North American and European countries. Founded in 1949, members agree that an attack on one is an attack on all. It has expanded since the end of the Cold War."]),
    (["european union", "eu"], ["The European Union (EU) is a political and economic union of European countries. It has a single market, common laws in many areas, and a shared currency (euro) in many members. It grew from post–WWII cooperation."]),
    (["brexit"], ["Brexit was the UK's exit from the European Union, completed in 2020. It ended decades of membership and changed trade, travel, and law. It remains politically and economically significant."]),
    (["human rights"], ["Human rights are basic rights and freedoms that belong to everyone—e.g. life, liberty, equality, free speech. They're set out in documents like the Universal Declaration of Human Rights. Governments and international bodies are meant to protect them."]),
    (["refugee", "refugees"], ["Refugees are people who flee their country because of persecution, war, or violence. International law protects them; the UNHCR supports them. Many countries accept refugees for resettlement."]),
    (["immigration", "immigration"], ["Immigration is when people move to another country to live. People migrate for work, family, or safety. It shapes economies and societies; policies on borders and integration vary widely."]),
    (["population", "world population", "how many people"], ["The world population is over 8 billion. It grew slowly for most of history and accelerated in the 20th century. Growth rates vary by region; some countries are ageing and shrinking."]),
    (["poverty", "global poverty"], ["Poverty means lacking enough resources for a basic standard of living. Millions still live in extreme poverty, especially in parts of Africa and South Asia. Aid, development, and fair trade aim to reduce it."]),
    (["literacy", "literacy rate"], ["Literacy is the ability to read and write. Literacy rates have risen globally but gaps remain. Education, especially for girls, is key to improving literacy and opportunities."]),
    (["vaccine", "vaccines", "vaccination"], ["Vaccines train the immune system to fight disease by exposing it to a harmless version of a pathogen. They've eliminated or reduced many diseases (e.g. smallpox, polio). They're one of the most effective public health tools."]),
    (["antibiotic", "antibiotics"], ["Antibiotics are drugs that kill or stop bacteria. They've saved countless lives. Overuse leads to resistance—bacteria that no longer respond—so they should be used only when needed."]),
    (["immune system", "immunity"], ["The immune system defends the body against germs and disease. It includes white blood cells, antibodies, and barriers like skin. Vaccines and good hygiene help it do its job."]),
    (["cancer", "what is cancer"], ["Cancer is when cells grow out of control and can spread. It has many types and causes. Treatment includes surgery, chemotherapy, and radiation. Early detection and healthy habits can reduce risk."]),
    (["heart disease", "cardiovascular"], ["Heart disease (cardiovascular disease) includes conditions affecting the heart and blood vessels. Risk factors include diet, smoking, and lack of exercise. It's a leading cause of death globally."]),
    (["diabetes"], ["Diabetes is when the body can't properly control blood sugar. Type 1 is when the body doesn't make insulin; Type 2 is often linked to lifestyle. Management includes diet, exercise, and sometimes medication or insulin."]),
    (["allergy", "allergies"], ["Allergies happen when the immune system overreacts to something harmless (e.g. pollen, nuts). Symptoms range from sneezing to anaphylaxis. Avoidance and medicines (e.g. antihistamines, epinephrine) help."]),
    (["stress", "stress management"], ["Stress is the body's response to pressure. Short-term stress can be helpful; chronic stress can harm health. Managing it with sleep, exercise, and relaxation helps. Severe stress may need professional support."]),
    (["mental health", "depression", "anxiety"], ["Mental health includes emotional and psychological well-being. Conditions like depression and anxiety are common and treatable. Talking to someone and, when needed, therapy or medication can help. Stigma is a barrier for many."]),
    (["meditation", "mindfulness"], ["Meditation is practice that trains attention and awareness. Mindfulness is being present without judgment. Both can reduce stress and improve well-being. There are many styles—guided, breath-focused, etc."]),
    (["caffeine", "coffee", "tea"], ["Caffeine is a stimulant in coffee, tea, chocolate, and some drinks. It can improve alertness but too much can cause jitters or sleep problems. Effects vary by person."]),
    (["sugar", "sugar health"], ["Sugar provides quick energy but too much is linked to weight gain, tooth decay, and health problems. Added sugars are in many processed foods. Moderation and reading labels help."]),
    (["fiber", "fibre", "dietary fibre"], ["Dietary fibre is in plants and helps digestion. It can help with constipation, blood sugar, and heart health. Good sources include whole grains, fruits, vegetables, and legumes."]),
    (["carbohydrate", "carbs"], ["Carbohydrates are a main energy source—sugars and starches. Complex carbs (whole grains, vegetables) are generally better than simple sugars. They're part of a balanced diet."]),
    (["fat", "fats", "saturated fat"], ["Fats are essential for energy and cell function. Unsaturated fats (e.g. olive oil, fish) are often healthier; too much saturated and trans fat can harm the heart. Balance and quality matter."]),
    (["vegetarian", "vegan", "plant-based"], ["Vegetarians don't eat meat; vegans avoid all animal products. Plant-based diets can be healthy with planning (e.g. enough protein and B12). People choose them for health, ethics, or the environment."]),
    (["organic", "organic food"], ["Organic food is grown without synthetic pesticides and fertilisers, under certification rules. It's often more expensive. Benefits are debated; it can reduce chemical use and support certain farming practices."]),
    (["gluten", "celiac"], ["Gluten is a protein in wheat, barley, and rye. People with coeliac disease must avoid it. Others may choose to reduce it. Gluten-free diets are essential for coeliac; for others it's a choice."]),
    (["lactose", "lactose intolerance"], ["Lactose is the sugar in milk. Some people don't make enough lactase to digest it, causing bloating and discomfort. Lactose-free products and alternatives (e.g. oat milk) help."]),
    (["antioxidant", "antioxidants"], ["Antioxidants are compounds that can protect cells from damage by free radicals. They're in many fruits and vegetables. A varied diet is the best source; supplements are less clearly beneficial."]),
    (["probiotic", "probiotics"], ["Probiotics are live bacteria that may benefit gut health. They're in yoghurt and fermented foods and as supplements. Evidence is mixed; they may help some people with digestion."]),
    (["cholesterol", "good cholesterol", "bad cholesterol"], ["Cholesterol is needed for cells and hormones. LDL ('bad') can build up in arteries; HDL ('good') helps remove it. Diet, exercise, and sometimes medication keep levels in check."]),
    (["blood pressure", "hypertension"], ["Blood pressure is the force of blood on artery walls. High pressure (hypertension) increases heart and stroke risk. Lifestyle changes and medication can control it. It's measured as systolic over diastolic."]),
    (["bmi", "body mass index"], ["BMI is weight in kg divided by height in metres squared. It's a rough measure of body fatness. It doesn't account for muscle or frame; doctors use it with other factors."]),
    (["obesity", "overweight"], ["Obesity is excess body fat that can harm health. Causes include diet, activity, genes, and environment. It increases the risk of many diseases. Prevention and treatment focus on lifestyle and sometimes medicine or surgery."]),
    (["smoking", "tobacco", "quit smoking"], ["Smoking tobacco causes cancer, heart disease, and lung disease. Quitting at any age helps. Nicotine is addictive; support, patches, and other aids can help people quit."]),
    (["alcohol", "alcohol health"], ["Moderate alcohol may have limited benefits for some, but excess harms the liver, heart, and cancer risk. Guidelines suggest limiting intake. Not drinking is the safest option."]),
    (["drug", "medication", "medicine"], ["Medicines treat or prevent disease. They work in different ways and can have side effects. Always follow dosage and ask a doctor or pharmacist. Misuse of prescription or illegal drugs is dangerous."]),
    (["first aid"], ["First aid is immediate care for injury or illness before professional help. It includes CPR, stopping bleeding, and treating shock. Learning basics can save lives. Courses are widely available."]),
    (["cpr", "cardiopulmonary resuscitation"], ["CPR (cardiopulmonary resuscitation) keeps blood flowing when the heart stops. It combines chest compressions and rescue breaths. Learning CPR can save lives; many organisations offer short courses."]),
    (["x-ray", "x ray"], ["X-rays are a form of radiation that passes through soft tissue but is absorbed by dense material like bone. They're used for imaging broken bones and some conditions. Overexposure is avoided."]),
    (["mri", "magnetic resonance"], ["MRI (magnetic resonance imaging) uses magnets and radio waves to create detailed images of the body. It doesn't use X-rays. It's used for brain, joints, and many other areas."]),
    (["ct scan", "cat scan"], ["A CT (computed tomography) scan uses X-rays from many angles to create cross-sectional images. It's faster than MRI and good for trauma and many conditions. It involves more radiation than a single X-ray."]),
    (["surgery", "surgery"], ["Surgery is medical treatment that involves cutting or opening the body. It can be open or minimally invasive (e.g. keyhole). Anaesthesia is used so the patient doesn't feel pain. It's used for diagnosis, repair, or removal of tissue."]),
    (["transplant", "organ transplant"], ["Organ transplant replaces a failing organ with one from a donor. Kidneys, livers, hearts, and others are transplanted. Donors can be living or deceased. Immunosuppression is needed to prevent rejection."]),
    (["gene therapy"], ["Gene therapy aims to treat disease by changing or replacing genes. It's used or in trials for some genetic and other conditions. It's a growing and carefully regulated field."]),
    (["antibody", "antibodies"], ["Antibodies are proteins the immune system makes to recognise and neutralise germs and other invaders. Vaccines prompt the body to make them. Monoclonal antibodies are made in labs for treatment and diagnosis."]),
    (["clinical trial"], ["Clinical trials test new treatments in people. They follow strict rules and phases to check safety and effectiveness. Participating can help advance medicine; risks and benefits are explained."]),
    (["placebo", "placebo effect"], ["A placebo is a harmless substance or procedure with no active effect. The placebo effect is when people feel better because they expect to. Placebos are used in trials to compare with real treatments."]),
    (["epidemic", "pandemic"], ["An epidemic is a disease spreading in a region; a pandemic is worldwide. COVID-19 was a pandemic. Public health measures (vaccines, distancing, treatment) help control spread and harm."]),
    (["quarantine", "isolation"], ["Quarantine separates people who may have been exposed to a disease; isolation separates people who are sick. Both help prevent spread during outbreaks."]),
    (["world health organization", "who"], ["The World Health Organization (WHO) is the UN agency for health. It sets standards, tracks disease, and supports countries. It led global efforts on smallpox eradication and coordinates responses to outbreaks."]),
    (["sloth", "sloths"], ["Sloths are slow-moving mammals that live in Central and South American trees. They have a very low metabolic rate and spend most of their time sleeping or moving slowly. Algae can grow on their fur."]),
    (["hedgehog", "hedgehogs"], ["Hedgehogs are small spiny mammals found in Europe, Asia, and Africa. They roll into a ball when threatened. They eat insects and are sometimes kept as pets (in places where it's legal)."]),
    (["raccoon", "raccoons"], ["Raccoons are North American mammals known for their masked face and dexterous front paws. They're adaptable and often live near humans. They are nocturnal and omnivorous."]),
    (["squirrel", "squirrels"], ["Squirrels are rodents that live in trees or on the ground. They gather and store nuts and are known for their bushy tails. They're found on every continent except Australia and Antarctica."]),
    (["hamster", "hamsters"], ["Hamsters are small rodents often kept as pets. They have cheek pouches for carrying food and are nocturnal. The Syrian hamster is the most common pet species."]),
    (["golden ratio"], ["The golden ratio (about 1.618) is a number that appears in art, architecture, and nature. It's the ratio where the whole is to the larger part as the larger part is to the smaller. It's related to the Fibonacci sequence."]),
    (["pythagorean theorem"], ["The Pythagorean theorem says that in a right triangle, the square of the hypotenuse equals the sum of the squares of the other two sides: a² + b² = c². It's named after the ancient Greek mathematician Pythagoras."]),
    (["square root"], ["The square root of a number is a value that when multiplied by itself gives that number. For example, the square root of 9 is 3. Negative numbers have no real square root; we use imaginary numbers for them."]),
    (["fraction", "fractions"], ["A fraction represents part of a whole, written as one number over another (e.g. 3/4). The top is the numerator; the bottom is the denominator. Fractions can be added, subtracted, multiplied, and divided with specific rules."]),
    (["percentage", "percent"], ["A percentage is a fraction out of 100. For example, 50% means 50/100 or one half. Percentages are used for discounts, interest rates, and statistics."]),
    (["average", "mean", "median"], ["The mean (average) is the sum of values divided by how many there are. The median is the middle value when sorted. Both describe the 'centre' of data; the median is less affected by extreme values."]),
    (["probability", "chance"], ["Probability measures how likely something is, from 0 (impossible) to 1 (certain). It's used in games, weather forecasts, and science. Flipping a fair coin has probability 1/2 for heads."]),
    (["geometry", "shapes"], ["Geometry is the branch of maths about shapes, sizes, and space. It includes points, lines, angles, triangles, circles, and 3D solids. Euclidean geometry is what we learn in school."]),
    (["triangle", "triangles"], ["A triangle has three sides and three angles. The angles always add to 180°. Types include equilateral (all equal), isosceles (two equal), and right-angled (one 90° angle)."]),
    (["circle", "circles"], ["A circle is all points the same distance from a centre. The circumference is 2πr and the area is πr². Pi (π) is about 3.14159."]),
    (["moon", "earth moon", "lunar"], ["Earth's Moon is our only natural satellite. It orbits about 384,400 km away and causes tides. We see phases as the Sun lights different parts. Humans landed there in 1969."]),
    (["sun", "the sun", "our sun"], ["The Sun is the star at the centre of our solar system. It's mostly hydrogen and helium and produces energy by nuclear fusion. It's about 4.6 billion years old and will last billions more."]),
    (["star", "stars", "what is a star"], ["Stars are huge balls of gas that shine because of nuclear fusion in their cores. They vary in size, colour, and lifespan. The Sun is a medium-sized star."]),
    (["light year", "light-year"], ["A light-year is the distance light travels in one year—about 9.46 trillion km. It's used for huge distances in space. The nearest star beyond the Sun is about 4 light-years away."]),
    (["astronaut", "astronauts"], ["Astronauts are people trained to travel and work in space. They go through rigorous physical and technical training. They work on the ISS, conduct spacewalks, and will likely go to the Moon and Mars in future."]),
    (["rocket", "rockets", "how do rockets work"], ["Rockets work on Newton's third law: they expel gas backward, which pushes the rocket forward. They carry their own oxidiser so they can burn fuel in space where there's no air."]),
    (["satellite", "satellites"], ["A satellite is any object that orbits a planet or star. Natural satellites are moons; artificial ones are human-made and used for communication, weather, navigation (GPS), and science."]),
    (["gravity on mars", "mars gravity"], ["Mars has about 38% of Earth's surface gravity because it's smaller and less massive. You would weigh less there; walking and movement would feel different."]),
    (["water on mars"], ["Scientists have found evidence of water on Mars—ice at the poles and possibly liquid brine in the past. Ancient Mars likely had rivers and lakes; today it's mostly dry and cold."]),
    (["spacex", "space x", "elon musk space"], ["SpaceX is a private aerospace company founded by Elon Musk. It builds rockets (e.g. Falcon, Starship) and has reduced launch costs. It sends cargo and crew to the ISS and is developing missions to Mars."]),
    (["nasa"], ["NASA is the US government agency for space and aeronautics. It runs human spaceflight (e.g. Apollo, Space Shuttle, Artemis), robotic missions, and research. It works with international partners."]),
    (["voyager", "voyager 1", "voyager 2"], ["Voyager 1 and 2 are NASA probes launched in 1977. They've left the solar system and are in interstellar space, still sending data. They carry golden records with sounds and images of Earth."]),
    (["curiosity", "curiosity rover"], ["Curiosity is a NASA rover on Mars since 2012. It studies the planet's climate and geology and has found evidence that Mars once had conditions suitable for life."]),
    (["perseverance", "perseverance rover"], ["Perseverance is a NASA rover that landed on Mars in 2021. It collects rock samples for future return to Earth and carries the Ingenuity helicopter drone."]),
    (["sputnik"], ["Sputnik was the first artificial satellite, launched by the Soviet Union in 1957. It sparked the space race and showed that spaceflight was possible."]),
    (["yuri gagarin"], ["Yuri Gagarin was a Soviet cosmonaut who became the first human in space on 12 April 1961. He orbited Earth once in Vostok 1."]),
    (["neil armstrong"], ["Neil Armstrong was an American astronaut and the first person to walk on the Moon, on 20 July 1969, during Apollo 11. He said: 'That's one small step for man, one giant leap for mankind.'"]),
    (["sally ride"], ["Sally Ride was an American astronaut and the first American woman in space (1983). She flew on the Space Shuttle and later promoted science education."]),
    (["stephen hawking"], ["Stephen Hawking was a British physicist who worked on black holes, the Big Bang, and popularised science. He had ALS but continued researching and writing (e.g. A Brief History of Time)."]),
    (["albert einstein"], ["Albert Einstein was a physicist who developed the theory of relativity and contributed to quantum mechanics. E=mc² and the photoelectric effect are among his famous work. He won the Nobel Prize and is one of the most famous scientists ever."]),
    (["isaac newton"], ["Isaac Newton was an English mathematician and physicist. He formulated laws of motion and gravity and developed calculus. His work laid the foundation for classical mechanics."]),
    (["marie curie"], ["Marie Curie was a physicist and chemist who researched radioactivity. She was the first woman to win a Nobel Prize and the only person to win in two sciences. She discovered polonium and radium."]),
    (["charles darwin"], ["Charles Darwin was a naturalist who proposed the theory of evolution by natural selection. His book On the Origin of Species (1859) changed biology and our understanding of life."]),
    (["galileo"], ["Galileo Galilei was an Italian scientist who improved the telescope and made key astronomical observations. He supported the idea that Earth orbits the Sun and faced opposition from the Church."]),
    (["nikola tesla"], ["Nikola Tesla was an inventor and engineer who worked on alternating current (AC), motors, and wireless technology. He had a long rivalry with Thomas Edison over AC vs DC power."]),
    (["thomas edison"], ["Thomas Edison was an American inventor who developed the practical light bulb, phonograph, and many other devices. He held over 1,000 patents and founded research labs."]),
    (["ada lovelace"], ["Ada Lovelace was a mathematician who worked with Charles Babbage on the Analytical Engine. She is often considered the first computer programmer for her notes on the machine."]),
    (["alan turing"], ["Alan Turing was a mathematician and codebreaker who helped break Enigma in WWII. He formalised the concept of computation and the Turing test. He's a founding figure of computer science."]),
    (["bill gates"], ["Bill Gates co-founded Microsoft and helped make personal computers widespread. He later focused on philanthropy through the Bill & Melinda Gates Foundation."]),
    (["steve jobs"], ["Steve Jobs co-founded Apple and led the creation of the Mac, iPod, iPhone, and iPad. He emphasised design and user experience and built one of the world's most valuable companies."]),
    (["red blood cell", "erythrocyte"], ["Red blood cells (erythrocytes) carry oxygen from the lungs to the body and bring back carbon dioxide. They contain haemoglobin and have no nucleus. The body makes millions every second."]),
    (["white blood cell", "leukocyte"], ["White blood cells are part of the immune system. They fight infections and remove damaged or foreign material. There are several types, including lymphocytes and phagocytes."]),
    (["kidney", "kidneys"], ["The kidneys filter blood, remove waste and extra fluid as urine, and help regulate blood pressure and electrolytes. Most people have two; they're bean-shaped and sit near the back."]),
    (["liver", "livers"], ["The liver processes nutrients, makes bile for digestion, filters toxins, and helps with blood clotting. It can regenerate. Damage from alcohol or disease can lead to serious illness."]),
    (["lung", "lungs", "respiration"], ["The lungs take in oxygen and expel carbon dioxide. Air goes down the trachea into bronchi and tiny alveoli where gas exchange happens. Breathing is controlled automatically."]),
    (["skin", "human skin"], ["Skin is the body's largest organ. It protects against infection, regulates temperature, and senses touch. It has layers: epidermis, dermis, and subcutaneous tissue."]),
    (["muscle", "muscles"], ["Muscles allow movement and maintain posture. Skeletal muscles attach to bones; smooth muscle is in organs; cardiac muscle is in the heart. They contract when stimulated."]),
    (["nervous system"], ["The nervous system includes the brain, spinal cord, and nerves. It receives sensory input, processes information, and sends signals to muscles and organs. It's central to thought and control."]),
    (["digestive system", "digestion"], ["The digestive system breaks down food so the body can absorb nutrients. It includes the mouth, stomach, intestines, liver, and pancreas. Enzymes and acids do most of the work."]),
    (["immune system"], ["The immune system defends against germs and disease. It includes white blood cells, antibodies, and organs like the spleen. It can remember past infections (immunity)."]),
    (["hormone", "hormones"], ["Hormones are chemical messengers released by glands. They regulate growth, metabolism, mood, and more. Examples: insulin, adrenaline, oestrogen, testosterone."]),
    (["adrenaline", "fight or flight"], ["Adrenaline (epinephrine) is a hormone that prepares the body for danger—increasing heart rate, blood flow to muscles, and alertness. It's part of the 'fight or flight' response."]),
    (["insulin"], ["Insulin is a hormone that helps cells take in sugar from the blood. People with diabetes may not make enough insulin or may not use it well. It's essential for regulating blood glucose."]),
    (["antibiotic resistance"], ["Antibiotic resistance happens when bacteria evolve to survive antibiotics. Overuse of antibiotics speeds this up. It's a major health threat; new drugs and careful use are needed."]),
    (["penicillin"], ["Penicillin was the first widely used antibiotic, discovered by Alexander Fleming. It fights bacterial infections. Many bacteria are now resistant, but penicillin and related drugs are still used."]),
    (["aspirin"], ["Aspirin reduces pain, fever, and inflammation. In low doses it can help prevent heart attacks and strokes by reducing blood clotting. It's one of the most used medicines worldwide."]),
    (["anaesthesia", "anesthetic"], ["Anaesthesia is the use of drugs to block pain (and sometimes consciousness) during surgery. General anaesthesia puts you to sleep; local numbs a small area. It's made surgery much safer."]),
    (["x-ray discovery"], ["X-rays were discovered by Wilhelm Röntgen in 1895. They pass through soft tissue but are absorbed by dense material like bone, allowing internal imaging without surgery."]),
    (["antibody test"], ["Antibody tests detect whether someone has had a past infection or responded to a vaccine by looking for antibodies in the blood. They don't diagnose active infection by themselves."]),
    (["blood type", "blood groups"], ["Blood is grouped by antigens (e.g. A, B, AB, O) and Rhesus (positive or negative). Matching types is important for transfusions. O negative is the 'universal donor'."]),
    (["organ donor", "organ donation"], ["Organ donation allows organs from a deceased (or sometimes living) donor to be given to someone in need. It saves lives; many countries have opt-in or opt-out systems."]),
    (["caffeine overdose"], ["Too much caffeine can cause jitters, anxiety, fast heartbeat, and in rare cases serious harm. Safe limits vary; roughly 400 mg per day for most adults is often cited. Energy drinks can have a lot."]),
    (["dehydration", "dehydrated"], ["Dehydration is when the body loses more fluid than it takes in. Symptoms include thirst, dry mouth, dark urine, and dizziness. Drink water and seek help if severe (e.g. confusion, little urine)."]),
    (["sunburn"], ["Sunburn is skin damage from too much UV radiation. It increases skin cancer risk. Prevent it with sunscreen, clothing, and shade. Aloe and pain relievers can help after; severe burns need a doctor."]),
    (["allergy reaction", "anaphylaxis"], ["Severe allergic reactions (anaphylaxis) can cause swelling, trouble breathing, and shock. Epinephrine (EpiPen) is the first-line treatment. Get emergency help if someone has a severe reaction."]),
    (["cpr steps"], ["For CPR: call for help, tilt the head back, give 30 chest compressions then 2 rescue breaths, and repeat. Use an AED if available. Training courses teach the full technique."]),
    (["stroke", "stroke symptoms"], ["Stroke is when blood flow to the brain is cut off. Signs include face drooping, arm weakness, speech difficulty—act FAST and call emergency services. Quick treatment can limit damage."]),
    (["heart attack", "heart attack symptoms"], ["Heart attack symptoms include chest pain or pressure, shortness of breath, and pain in the arm or jaw. Call emergency services immediately; don't wait."]),
    (["flu", "influenza"], ["Influenza (flu) is a viral infection affecting the nose, throat, and sometimes lungs. It can be serious for the very young, old, or ill. Vaccination and hand-washing reduce spread."]),
    (["cold", "common cold"], ["The common cold is a mild viral infection of the nose and throat. Rest, fluids, and over-the-counter remedies help. Antibiotics don't work for colds."]),
    (["covid", "covid-19", "coronavirus"], ["COVID-19 is the disease caused by the coronavirus SARS-CoV-2. It spreads through the air. Vaccines and treatments have reduced severe illness; variants continue to be monitored."]),
    (["vitamin b12"], ["Vitamin B12 is needed for nerves and red blood cells. It's in animal products; vegans may need fortified foods or supplements. Deficiency can cause tiredness and nerve problems."]),
    (["iron", "iron deficiency"], ["Iron is needed for haemoglobin and oxygen transport. Too little can cause anaemia (tiredness, weakness). Good sources: meat, beans, leafy greens. Vitamin C helps absorption."]),
    (["calcium", "calcium bones"], ["Calcium is important for bones and teeth, and for muscle and nerve function. Dairy, leafy greens, and fortified foods are sources. Vitamin D helps the body use calcium."]),
    (["magnesium"], ["Magnesium is involved in hundreds of body processes, including muscle and nerve function and bone health. It's in nuts, seeds, whole grains, and leafy greens. Many people get enough from diet."]),
    (["zinc"], ["Zinc supports the immune system, wound healing, and taste. It's in meat, shellfish, legumes, and seeds. Deficiency can impair immunity; too much can be harmful."]),
    (["omega 3", "omega-3", "fish oil"], ["Omega-3 fatty acids support heart and brain health. They're in fatty fish (e.g. salmon), flaxseed, and walnuts. Supplements (e.g. fish oil) are used when diet isn't enough."]),
    (["antioxidants"], ["Antioxidants are compounds that can protect cells from damage. They're in many fruits and vegetables. A balanced diet is the best source; benefits of supplements are less clear."]),
    (["processed food"], ["Processed foods are altered from their natural state—from canned beans to ready meals and snacks. Highly processed foods are often high in salt, sugar, and fat; eating them in moderation is wise."]),
    (["gluten free"], ["Gluten-free diets avoid wheat, barley, and rye. They're essential for people with coeliac disease. For others, going gluten-free is a choice; it doesn't automatically make the diet healthier."]),
    (["saturated fat"], ["Saturated fat is in meat, dairy, and some plant oils. Too much can raise cholesterol and heart disease risk. Guidelines suggest limiting it and choosing unsaturated fats more often."]),
    (["trans fat"], ["Trans fats are unhealthy fats that can raise bad cholesterol. Many countries have limited or banned them in foods. Check labels; they can appear as 'partially hydrogenated' oil."]),
    (["sodium", "salt", "sodium intake"], ["Sodium (in salt) is needed in small amounts but too much raises blood pressure. Most people eat more than needed. Cutting down on processed foods and adding less salt helps."]),
    (["sugar substitute", "sweetener", "artificial sweetener"], ["Sugar substitutes (e.g. aspartame, stevia) provide sweetness with few or no calories. They're generally considered safe in moderation; they can help some people reduce sugar intake."]),
    (["intermittent fasting"], ["Intermittent fasting is eating only during certain hours or on certain days. Some find it helps with weight or health; it's not for everyone. Check with a doctor if you have health conditions."]),
    (["keto", "ketogenic diet"], ["A ketogenic diet is very low in carbs and high in fat, aiming to put the body in ketosis. It's used for epilepsy and by some for weight loss. It can have side effects; medical advice is wise."]),
    (["mediterranean diet"], ["The Mediterranean diet emphasises vegetables, fruit, whole grains, olive oil, fish, and moderate wine. It's linked to heart health and longevity in research."]),
    (["vegan diet", "veganism"], ["Veganism avoids all animal products. With planning it can be healthy; attention to B12, iron, and protein is important. People choose it for health, animals, or the environment."]),
    (["breakfast"], ["Breakfast is the first meal of the day. Whether it's 'most important' is debated; what matters is overall diet and what works for you. A balanced breakfast can help energy and focus."]),
    (["sleep hygiene"], ["Good sleep hygiene means habits that support sleep: consistent schedule, dark quiet room, limiting screens and caffeine before bed, and avoiding large meals late."]),
    (["screen time"], ["Too much screen time can affect sleep, posture, and activity. Taking breaks, limiting before bed, and balancing with exercise and offline activities helps."]),
    (["posture"], ["Good posture means keeping the spine aligned when sitting or standing. It can reduce pain and strain. Ergonomic setups and regular movement help, especially if you sit a lot."]),
    (["ergonomics"], ["Ergonomics is designing work and tools to fit the person. Good desk setup—screen height, chair support, keyboard position—can reduce strain and injury."]),
    (["carpal tunnel"], ["Carpal tunnel syndrome is when the median nerve in the wrist is compressed, causing numbness and pain in the hand. Rest, splints, and sometimes surgery help. Ergonomic setup can reduce risk."]),
    (["headache", "headaches"], ["Headaches have many causes—tension, dehydration, migraines, or something else. Rest, water, and pain relievers help many. See a doctor if they're severe, sudden, or frequent."]),
    (["migraine"], ["Migraines are intense headaches often with nausea and sensitivity to light or sound. Triggers vary; treatment includes avoiding triggers, pain relief, and preventive or acute medicines."]),
    (["back pain"], ["Back pain is common and often due to strain, posture, or disc issues. Rest, gentle movement, and pain relief help many. Persistent or severe pain should be checked by a doctor."]),
    (["arthritis"], ["Arthritis is inflammation of joints, causing pain and stiffness. Osteoarthritis is wear-and-tear; rheumatoid is autoimmune. Treatment includes exercise, medicine, and sometimes surgery."]),
    (["asthma"], ["Asthma is a condition where airways narrow and swell, causing wheezing and shortness of breath. Triggers include allergens and exercise. Inhalers and avoiding triggers help control it."]),
    (["eczema"], ["Eczema (atopic dermatitis) causes itchy, inflamed skin. It often runs in families and can flare with stress or irritants. Moisturisers and sometimes prescription treatments help."]),
    (["acne"], ["Acne is when pores become blocked with oil and dead skin, leading to pimples. It's common in teens but can affect adults. Cleansing, treatments, and sometimes medication help."]),
    (["sunscreen", "spf"], ["Sunscreen blocks or absorbs UV rays to prevent sunburn and skin damage. SPF indicates protection from UVB; broad-spectrum also covers UVA. Reapply regularly when outdoors."]),
    (["first aid kit"], ["A basic first aid kit might include plasters, gauze, tape, antiseptic, pain relievers, and any personal medicines. Keep it handy at home and when travelling."]),
    (["heimlich maneuver", "choking"], ["For choking, the Heimlich maneuver (abdominal thrusts) can dislodge an object. Stand behind the person, make a fist above the navel, and thrust upward. Get trained for full technique."]),
]

KNOWLEDGE.extend(EXTENDED_KNOWLEDGE)

# Crazy more knowledge: hundreds of extra entries
CRAZY_KNOWLEDGE = [
    (["banana", "bananas"], ["Bananas are berries botanically! They grow in clusters and are a great source of potassium. The Cavendish is the most common variety; wild bananas have big seeds."]),
    (["strawberry", "strawberries"], ["Strawberries aren't true berries—the seeds are on the outside. They're the only fruit with seeds on the outside. They're in the rose family."]),
    (["avocado", "avocados"], ["Avocados are fruits (single large seed). They're high in healthy fats and potassium. They don't ripen on the tree; they ripen after picking."]),
    (["pineapple", "pineapples"], ["Pineapples take about two years to grow. They're made of many fused berries. The plant flowers once and produces one pineapple; then it can produce shoots for more."]),
    (["watermelon", "watermelons"], ["Watermelons are 92% water. They're related to cucumbers and pumpkins. Seedless varieties exist. They originated in Africa."]),
    (["coconut", "coconuts"], ["Coconuts can float across oceans and germinate on new shores. The coconut water inside is sterile until opened. Coconut oil is high in saturated fat."]),
    (["chocolate", "cocoa"], ["Chocolate comes from cacao beans, fermented and roasted. Dark chocolate has more cocoa and less sugar. Theobromine in chocolate is toxic to dogs."]),
    (["coffee", "coffee beans"], ["Coffee comes from roasted seeds of the Coffea plant. The two main species are arabica and robusta. Caffeine is a natural pesticide for the plant."]),
    (["tea", "tea leaves"], ["All tea (black, green, white, oolong) comes from the same plant, Camellia sinensis. The difference is how it's processed. Herbal 'teas' are infusions of other plants."]),
    (["pepper", "black pepper"], ["Black pepper is dried fruit (peppercorns) of a flowering vine. It was once so valuable it was used as currency. White pepper is the same berry with the outer layer removed."]),
    (["salt history", "why is salt valuable"], ["Salt was crucial for preserving food before refrigeration. Roman soldiers were sometimes paid in salt—that's the origin of 'salary'. Wars have been fought over salt."]),
    (["honey never spoils"], ["Honey doesn't spoil. Archaeologists have found edible honey in ancient Egyptian tombs. Its low water content and acidity prevent bacteria and mould from growing."]),
    (["octopus have three hearts"], ["Octopuses have three hearts: two pump blood to the gills, one to the body. When they swim, the heart that pumps to the body stops—so they prefer crawling."]),
    (["blue blood", "horseshoe crab"], ["Horseshoe crabs have blue blood because they use copper-based haemocyanin instead of iron-based haemoglobin. Their blood is used to test medical equipment for bacteria."]),
    (["turritopsis", "immortal jellyfish"], ["The Turritopsis dohrnii jellyfish can revert to its juvenile polyp stage after maturity—so in theory it could live forever. It's often called the 'immortal jellyfish'."]),
    (["tardigrade", "water bear"], ["Tardigrades (water bears) can survive extreme heat, cold, radiation, and even the vacuum of space. They can go into a tun state and revive after years."]),
    (["axolotl"], ["Axolotls are salamanders that stay in their larval form their whole lives and can regenerate limbs, organs, and even parts of their brain. They're native to Mexico."]),
    (["mantis shrimp"], ["Mantis shrimp have the most complex eyes in the animal kingdom—they see more colours than we do. Some species punch so fast they create cavitation bubbles and light (sonoluminescence)."]),
    (["naked mole rat"], ["Naked mole rats live in colonies like insects, are largely pain-insensitive, and are resistant to cancer. They can survive long periods without much oxygen."]),
    (["platypus", "platypuses"], ["Platypuses are egg-laying mammals with duck bills, beaver tails, and venomous spurs on males. They use electroreception to find prey underwater."]),
    (["echidna", "echidnas"], ["Echidnas are egg-laying mammals (monotremes) like the platypus. They have spines, long snouts, and lay a single egg in a pouch. They're found in Australia and New Guinea."]),
    (["peacock spider"], ["Peacock spiders are tiny Australian jumping spiders. Males have colourful abdomens and do elaborate dances to attract females. They're only a few millimetres long."]),
    (["leafy sea dragon"], ["Leafy sea dragons are Australian fish that look like floating seaweed. They're related to seahorses. Their leaf-like appendages are for camouflage."]),
    (["blobfish"], ["The blobfish looks 'ugly' when brought to the surface because its body is adapted to extreme deep-sea pressure. In its natural habitat it looks like a normal fish."]),
    (["anglerfish"], ["Anglerfish live in the deep sea. Females have a bioluminescent lure on their head to attract prey. Males are tiny and fuse onto females, sharing blood and sperm for life."]),
    (["goblin shark"], ["Goblin sharks are deep-sea sharks with extendable jaws that shoot forward to catch prey. They're rarely seen; they live in dark waters."]),
    (["narwhal", "narwhals"], ["Narwhals are Arctic whales. The 'horn' is actually a long spiral tusk—a canine tooth—that can grow several metres. Mostly males have it; its exact function is still debated."]),
    (["capybara"], ["Capybaras are the world's largest rodents. They're semi-aquatic, social, and live in South America. Other animals often sit on them—they're famously chill."]),
    (["quokka"], ["Quokkas are small Australian marsupials known for their 'smiling' faces. They're friendly and live on islands off Western Australia. Selfies with quokkas are popular but rules protect them."]),
    (["flying squirrel"], ["Flying squirrels don't truly fly—they glide using a membrane between their legs. They're nocturnal and found in Asia and North America."]),
    (["pangolin"], ["Pangolins are scaly mammals that eat ants and termites. They're the most trafficked mammal in the world. Their scales are keratin, like our fingernails."]),
    (["tapir"], ["Tapirs are large herbivorous mammals with flexible snouts. They look like a mix of pig and anteater. They're found in South America and Southeast Asia and are related to horses and rhinos."]),
    (["okapi"], ["Okapis look like zebra-giraffe hybrids but are the giraffe's only living relative. They live in the Congo rainforest and have long tongues for stripping leaves."]),
    (["manatee", "manatees"], ["Manatees are slow, gentle marine mammals. They're related to elephants. They have to surface to breathe. They're sometimes called sea cows."]),
    (["dugong"], ["Dugongs are marine mammals related to manatees. They're strictly marine and have a fluked tail like a whale. They graze on seagrass."]),
    (["quetzal"], ["The quetzal is a colourful Central American bird. Male resplendent quetzals have long tail feathers. They were sacred to the Maya and Aztecs."]),
    (["toucan", "toucans"], ["Toucans have huge colourful beaks that are light and full of air pockets. The beak helps with temperature regulation and reaching fruit. They're found in Central and South America."]),
    (["kiwi bird"], ["Kiwi birds are flightless and native to New Zealand. They lay huge eggs relative to body size. They're nocturnal and have a strong sense of smell—unusual for birds."]),
    (["cassowary"], ["Cassowaries are large flightless birds in Australia and New Guinea. They have a bony casque on their head and can be dangerous—they've been known to attack humans."]),
    (["hummingbird", "hummingbirds"], ["Hummingbirds can hover and fly backwards. Their wings beat up to 80 times per second. They have the highest metabolism of any bird and must eat constantly."]),
    (["albatross"], ["Albatrosses can fly for hours without flapping—they use dynamic soaring over the ocean. They have the longest wingspan of any living bird. Some live 60+ years."]),
    (["peacock", "peacock facts"], ["A group of peacocks is called a party or ostentation. Only males have the fancy tail; they molt it each year. The eyespots are thought to attract females and deter predators."]),
    (["lyrebird"], ["Lyrebirds in Australia can mimic almost any sound—chainsaws, cameras, other birds. Males display their tail feathers in elaborate courtship dances."]),
    (["bowerbird"], ["Bowerbirds build elaborate structures (bowers) and decorate them with colourful objects to attract mates. Some even 'paint' the walls with berry juice."]),
    (["weird animal fact"], ["Octopuses have neurons in their arms—so their arms can 'think' somewhat independently. Or: a group of porcupines is called a prickle."]),
    (["weird science fact"], ["A day on Venus is longer than its year—it takes 243 Earth days to rotate once but only 225 to orbit the Sun. Or: there are more stars in the universe than grains of sand on Earth's beaches."]),
    (["weird history fact"], ["Cleopatra lived closer in time to the Moon landing than to the building of the Great Pyramid. Or: Napoleon was once attacked by rabbits—a failed rabbit hunt turned into a bunny stampede."]),
    (["weird body fact"], ["Your stomach gets a new lining every few days so it doesn't digest itself. Or: you shed about 600,000 particles of skin every hour."]),
    (["do we swallow spiders in sleep"], ["The myth that we swallow eight spiders a year in our sleep is false. Spiders avoid sleeping humans (breath, vibrations). It was spread as an example of how false facts spread online."]),
    (["can you get warts from toads"], ["No. Warts are caused by human papillomavirus (HPV), not toads. Toads have bumpy skin and some have toxins, but they don't give you warts."]),
    (["goldfish memory"], ["Goldfish memory is better than the myth suggests. They can remember things for months and can be trained. The 'three-second memory' idea is wrong."]),
    (["lemmings suicide"], ["Lemmings don't jump off cliffs on purpose. The myth came from a staged Disney documentary. They do migrate in large numbers and some may fall when crowded—but it's not suicide."]),
    (["great wall visible from space"], ["The Great Wall is not clearly visible from the Moon with the naked eye. From low Earth orbit some astronauts have seen it in good conditions, but it's not unique—many human structures are visible from space."]),
    (["blood is blue"], ["Blood is never blue. Venous blood is dark red; it looks blue through skin because of how light penetrates. Blood is red whether it has oxygen or not."]),
    (["we only use 10 percent of our brain"], ["We use virtually all of our brain over the day. Different areas are active for different tasks. The '10% myth' has been debunked—brain scans show activity everywhere."]),
    (["chameleon change color camouflage"], ["Chameleons change colour mainly for mood, temperature, and communication—not primarily for camouflage. They use special cells called chromatophores."]),
    (["bats are blind"], ["Bats aren't blind. Most have small eyes and use echolocation to navigate and hunt at night, but they can see. The phrase 'blind as a bat' is misleading."]),
    (["bulls hate red"], ["Bulls react to movement, not the colour red. They're colourblind to red. Matadors use red capes partly for tradition and because blood shows less on red."]),
    (["ostrich bury head"], ["Ostriches don't bury their heads in the sand. They sometimes put their heads low to inspect the ground or to hide when sitting on nests. The myth is ancient."]),
    (["earwig in ear"], ["Earwigs don't crawl into human ears on purpose. The name may come from an old belief or from the shape of their wings. They're harmless to people."]),
    (["daddy longlegs venom"], ["Daddy longlegs (harvestmen) have no venom glands—they're not spiders. The myth that they're 'the most venomous but fangs too short' applies to a different animal (certain spiders) and is exaggerated."]),
    (["shark attack"], ["Shark attacks on humans are rare. Most sharks don't see us as prey. You're more likely to be struck by lightning than killed by a shark. Millions of sharks are killed by humans each year."]),
    (["murder hornet", "asian giant hornet"], ["Asian giant hornets can deliver painful stings and attack honeybee hives. They're native to Asia; they've been found in North America. Media sometimes call them 'murder hornets'."]),
    (["killer whale", "orca"], ["Orcas (killer whales) are actually dolphins—the largest dolphins. They're apex predators with different ecotypes (some eat fish, some mammals). They're highly social and intelligent."]),
    (["piranha attack"], ["Piranhas rarely attack humans. Most are scavengers or eat plants. In dry seasons when water is low and food scarce, feeding frenzies can happen—but they're not mindless man-eaters."]),
    (["black widow"], ["Black widow spiders have a neurotoxic venom. Females sometimes eat males after mating—hence the name. Bites can be serious but are rarely fatal with medical care."]),
    (["tarantula"], ["Tarantulas are large, hairy spiders. Most have mild venom and are not dangerous to humans. Their hairs can irritate skin. They can live for decades."]),
    (["scorpion sting"], ["Scorpion stings range from mild to serious depending on species. Most are like a bee sting. Some species (e.g. in North Africa) can be dangerous; antivenom exists."]),
    (["jellyfish sting"], ["Jellyfish stings come from nematocysts (stinging cells). Rinse with vinegar for many species; don't use freshwater (can trigger more stings). Remove tentacles carefully. Some species are very dangerous."]),
    (["electric eel"], ["Electric eels are fish (not eels) that can generate strong electric shocks to stun prey and defend themselves. They live in South American rivers. One shock can be enough to knock down a person."]),
    (["poison dart frog"], ["Poison dart frogs are small, brightly coloured frogs. Some have deadly skin toxins; indigenous people used the poison on darts. Captive-bred frogs often lose toxicity (diet-related)."]),
    (["stonefish"], ["Stonefish are the most venomous fish. They look like rocks and hide on the seabed. Stepping on their spines is extremely painful; antivenom exists. Found in the Indo-Pacific."]),
    (["box jellyfish"], ["Box jellyfish have potent venom and can kill humans. They're found in Australian and Asian waters. Wearing protective clothing and vinegar can help; seek emergency care if stung."]),
    (["blue ringed octopus"], ["The blue-ringed octopus is tiny but carries enough venom to kill several humans. It flashes blue rings when threatened. Found in the Pacific; no antivenom exists—support breathing until help arrives."]),
    (["cone snail"], ["Cone snails have harpoon-like teeth and venom that can paralyse and kill. Some species have killed humans. They're beautiful shells but don't pick up live ones."]),
    (["komodo dragon"], ["Komodo dragons are the largest living lizards. They have venomous saliva and bacteria in their bite. They're found on a few Indonesian islands and can take down large prey."]),
    (["saltwater crocodile"], ["Saltwater crocodiles are the largest living reptiles and can exceed 6 m. They're aggressive and have killed humans. They live in estuaries and coasts from India to Australia."]),
    (["hippos kill"], ["Hippos are among the most dangerous animals in Africa—they kill more people than lions. They're territorial and can run fast on land. Never get between a hippo and water."]),
    (["moon landing hoax"], ["The Moon landings were not faked. Evidence includes reflectors left on the Moon that anyone can bounce lasers off, thousands of people involved (no mass conspiracy), and rocks brought back that are clearly not from Earth."]),
    (["flat earth"], ["Earth is not flat. Evidence: ships disappear hull-first, different stars in different hemispheres, circumnavigation, photos from space, gravity, and every scientific measurement. It's a sphere (actually an oblate spheroid)."]),
    (["chemtrails"], ["'Chemtrails' are normal contrails—condensation trails from aircraft exhaust. They can spread and persist depending on atmospheric conditions. There's no evidence for secret chemical spraying."]),
    (["area 51"], ["Area 51 is a secretive US military base in Nevada used for testing aircraft. It's real; the secrecy was about spy planes like the U-2. Alien conspiracy theories have no evidence."]),
    (["bermuda triangle"], ["The Bermuda Triangle has no higher rate of disappearances than other busy shipping and flight areas. Many 'mysteries' were exaggerated or had ordinary explanations. It's not a supernatural zone."]),
    (["loch ness"], ["Loch Ness is a deep Scottish lake. The 'monster' legend is centuries old. No conclusive evidence of a large unknown animal exists despite sonar and searches. It's likely myth and misidentification."]),
    (["bigfoot", "sasquatch"], ["Bigfoot (Sasquatch) is a legendary ape-like creature in North America. No physical evidence (bodies, DNA) has been verified. Most scientists consider it folklore."]),
    (["yeti"], ["The Yeti is a legendary creature said to live in the Himalayas. No verified evidence exists. Some 'yeti' relics have turned out to be from bears. It's part of local folklore."]),
    (["doomsday", "apocalypse"], ["Predictions of specific doomsdays have always been wrong. Asteroids, climate, and pandemics are real risks—but 'the end on date X' has no scientific basis. Focus on real risks and resilience."]),
    (["zombie"], ["Zombies aren't real. The idea comes from folklore (e.g. Haitian Vodou) and fiction. Some parasites and diseases alter behaviour (e.g. rabies, toxoplasmosis) but nothing creates human 'zombies'."]),
    (["vampire", "vampires"], ["Vampires aren't real. The legend may have been influenced by diseases like porphyria or rabies, or burial practices. Bram Stoker's Dracula and folklore shaped the modern image."]),
    (["werewolf"], ["Werewolves are mythological. The idea of humans turning into wolves appears in many cultures. Lycanthropy is also a rare psychiatric condition where people believe they transform."]),
    (["unicorn"], ["Unicorns are mythical. The rhinoceros or extinct 'Elasmotherium' may have inspired some tales. The unicorn is Scotland's national animal (as a symbol)."]),
    (["dragon", "dragons"], ["Dragons are mythical in most cultures. Dinosaur fossils may have inspired some dragon myths. Komodo dragons and flying lizards are real animals with 'dragon' in the name."]),
    (["phoenix"], ["The phoenix is a mythical bird that burns and is reborn from its ashes. It appears in Greek, Egyptian, and other mythologies. It's a symbol of renewal."]),
    (["griffin"], ["Griffins are mythical creatures with the body of a lion and the head and wings of an eagle. They appear in ancient Near Eastern and Greek art. They may have been inspired by dinosaur fossils (Protoceratops)."]),
    (["mermaid", "mermaids"], ["Mermaids aren't real. Manatees and dugongs may have been mistaken for them by sailors. The myth appears in many cultures."]),
    (["kraken"], ["The kraken is a legendary giant sea monster. It may have been inspired by giant squid or octopuses. Real giant squid were only filmed in the wild in the 21st century."]),
    (["how many languages"], ["There are roughly 7,000 languages in the world. Many are endangered. The most spoken by native speakers are Mandarin, Spanish, and English."]),
    (["english language"], ["English is a West Germanic language with huge influence from French and Latin. It's one of the most widely spoken languages and the dominant language of the internet, science, and aviation."]),
    (["emoji", "emojis"], ["Emoji are pictograms used in digital communication. They were popularised in Japan; the word is Japanese (e picture + moji character). They're now part of Unicode so they work across platforms."]),
    (["why do we dream"], ["Dreams may help with memory, emotion processing, or problem-solving. REM sleep is when most vivid dreams occur. Their exact function is still debated."]),
    (["lucid dream"], ["Lucid dreaming is when you know you're dreaming and can sometimes control the dream. Techniques include reality checks and waking briefly then going back to sleep (WILD/MILD)."]),
    (["deja vu"], ["Déjà vu is the feeling that you've experienced something before. It may be a brief glitch in memory processing—the brain storing and recalling at almost the same time. It's common and usually harmless."]),
    (["yawn", "yawning"], ["We yawn when tired or bored; the cause isn't fully known. It might cool the brain or increase alertness. Yawning is contagious in humans and some animals—linked to empathy and social bonding."]),
    (["brain freeze"], ["Brain freeze (ice-cream headache) happens when something cold touches the roof of your mouth. Blood vessels constrict then dilate, triggering pain receptors. It goes away quickly."]),
    (["hiccup", "hiccups"], ["Hiccups are involuntary contractions of the diaphragm. Causes include eating fast, carbonated drinks, or excitement. Most stop on their own; holding breath or breathing into a paper bag can help."]),
    (["goosebumps"], ["Goosebumps are when tiny muscles at the base of hairs contract. They're a vestige of when our ancestors' fur would fluff up for warmth or to look bigger. They can happen with cold or strong emotion."]),
    (["taste buds"], ["Taste buds detect sweet, salty, sour, bitter, and umami. They're mostly on the tongue but also elsewhere in the mouth. What we call 'taste' is often a mix of taste and smell."]),
    (["why do we cry"], ["We cry from emotion (sadness, joy, frustration) and from irritation (e.g. onions). Emotional tears may have different chemistry and might signal need for support or release stress."]),
    (["fingerprints"], ["Fingerprints are unique patterns of ridges on our fingers. They help with grip and may improve touch sensitivity. They form before birth and don't change (except injury)."]),
    (["eye color", "eye colour"], ["Eye colour comes from the amount of melanin in the iris. Brown is most common; blue has less melanin. Two blue-eyed parents can have a brown-eyed child (recessive/dominant genes)."]),
    (["left handed", "left-handed"], ["About 10% of people are left-handed. It runs in families but isn't purely genetic. Left-handers have been stigmatised in history; in many languages 'left' has negative connotations."]),
    (["twin", "twins"], ["Identical twins come from one fertilised egg splitting; they share the same DNA. Fraternal twins come from two eggs; they're like any siblings. Twins can run in families (fraternal more so)."]),
    (["blood type diet"], ["The 'blood type diet' (eating for your A, B, AB, or O type) has no good scientific support. Studies don't show benefits. A balanced diet matters more than blood type."]),
    (["detox", "detoxing"], ["Your liver and kidneys already 'detox' your body. Commercial 'detox' diets and products usually don't remove toxins—they're often just low-calorie or laxative. Healthy eating and drinking water help real organs."]),
    (["superfood"], ["'Superfood' is a marketing term. No single food gives you perfect health. A varied diet with plenty of plants, whole grains, and moderate amounts of other foods is what evidence supports."]),
    (["antioxidant superfood"], ["Antioxidants in food are fine, but 'superfood' claims are often exaggerated. Get nutrients from a variety of fruits and vegetables rather than one trendy food."]),
    (["collagen"], ["Collagen is a protein in skin, bones, and connective tissue. Supplements and creams are popular; evidence for them helping skin or joints is limited. Your body makes collagen from protein and vitamin C."]),
    (["biotin", "biotin hair"], ["Biotin is a B vitamin. Deficiency can cause hair and nail problems, but most people get enough from diet. Supplements are often marketed for hair growth; they help only if you were deficient."]),
    (["probiotic"], ["Probiotics are live bacteria that may benefit gut health. Evidence is mixed—they can help some people with certain conditions. They're in yoghurt and supplements."]),
    (["prebiotic"], ["Prebiotics are fibres that feed good gut bacteria. They're in garlic, onions, bananas, oats, and more. Eating a variety of plant foods supports a healthy microbiome."]),
    (["gut microbiome"], ["The gut microbiome is the community of bacteria and other microbes in your intestines. It affects digestion, immunity, and possibly mood. Diet, antibiotics, and environment shape it."]),
    (["placebo effect"], ["The placebo effect is when a fake treatment improves symptoms because the person expects it to work. It's real and powerful. Clinical trials use placebos to test if drugs work beyond placebo."]),
    (["nocebo"], ["The nocebo effect is when expecting harm or side effects makes you feel worse—the opposite of placebo. Negative beliefs can worsen symptoms even when the treatment is inert."]),
    (["laughter"], ["Laughter reduces stress hormones and can boost immunity and mood. We laugh to bond and communicate. It's partly involuntary—it's hard to fake a real laugh."]),
    (["music and brain"], ["Music activates many brain areas—auditory, emotional, and motor. Learning music can improve memory and coordination. Music can trigger strong emotions and memories."]),
    (["perfect pitch"], ["Perfect (absolute) pitch is the ability to name or produce a note without a reference. It's rare and often develops in early childhood with music training. Most musicians have relative pitch instead."]),
    (["earworm", "song stuck in head"], ["Earworms are songs that get stuck in your head. They often have a simple, catchy melody. Listening to the full song or doing a puzzle can sometimes 'release' them."]),
    (["why music catchy"], ["Catchy songs often use repetition, simple melodies, and surprise (e.g. a hook). The brain likes patterns and slight variations. Earworms exploit how we remember and anticipate music."]),
    (["world's smallest country", "vatican"], ["The Vatican City is the world's smallest country by area and population—about 44 hectares and around 800 residents. It's the headquarters of the Roman Catholic Church."]),
    (["world's largest city"], ["By population, Tokyo is one of the largest cities (metro over 37 million). 'Largest' can mean by area or population; definitions of city vs metro vary."]),
    (["tallest building in the world"], ["The Burj Khalifa in Dubai is the tallest building (828 m). Other contenders are under construction. 'Tallest' can mean to tip or to occupied floor."]),
    (["longest bridge"], ["The longest bridge over water is the Danyang–Kunshan Grand Bridge in China (about 164 km). The longest suspension bridge is the 1915 Çanakkale Bridge in Turkey."]),
    (["deepest point in ocean"], ["The Challenger Deep in the Mariana Trench is the deepest known point—about 11 km down. Only a few people have been there in submersibles."]),
    (["highest mountain"], ["Mount Everest is the highest above sea level (8,849 m). Mauna Kea in Hawaii is taller from base to peak (underwater base) but doesn't exceed Everest above sea level."]),
    (["largest lake"], ["The Caspian Sea is the largest lake by area (though it's called a sea). Lake Baikal is the deepest and has the most freshwater by volume. The Great Lakes are the largest group of freshwater lakes by area."]),
    (["coldest place on earth"], ["Antarctica holds the record: the lowest natural temperature was recorded at Vostok Station (−89.2°C). Villages in Siberia and Antarctica are among the coldest inhabited places."]),
    (["hottest place on earth"], ["Death Valley in California has recorded 56.7°C (134°F). Lut Desert in Iran has had similar land-surface temperatures from satellite data. Both are among the hottest."]),
    (["rainiest place"], ["Mawsynram in India is often cited as the wettest place—heavy monsoon rains. Cherrapunji nearby also gets enormous rainfall. Definitions and records vary."]),
    (["oldest tree"], ["The oldest known non-clonal tree is a bristlecone pine in California (Methuselah) over 4,800 years old. Some clonal colonies (e.g. Pando, a quaking aspen) are tens of thousands of years old."]),
    (["oldest living animal"], ["Some animals live very long: Greenland sharks (centuries), ocean quahog clams (500+ years), some sponges. 'Oldest' depends on how you define and measure."]),
    (["fastest fish"], ["The sailfish is often cited as the fastest fish—bursts over 110 km/h. Other fast swimmers include marlin and tuna."]),
    (["slowest animal"], ["The sloth is one of the slowest—they move at about 0.24 km/h. Some snails and starfish are also very slow."]),
    (["loudest animal"], ["The blue whale's calls are among the loudest—they can travel hundreds of kilometres. The pistol shrimp's snap is one of the loudest sounds in the ocean (relative to size)."]),
    (["smartest animal"], ["Intelligence is hard to compare. Great apes, dolphins, elephants, parrots, and octopuses are often cited. They solve problems, use tools, and show complex social behaviour."]),
    (["strongest animal"], ["By pure strength, the dung beetle can pull over 1,000 times its body weight. By absolute power, elephants and whales are among the strongest. 'Strongest' depends on how you measure."]),
    (["poisonous vs venomous"], ["Venomous = injects toxin (e.g. snake bite). Poisonous = harmful if eaten or touched (e.g. poison dart frog). Some animals are both; the distinction is how the toxin is delivered."]),
    (["extinct animals"], ["Many species have gone extinct—dinosaurs, dodo, thylacine, passenger pigeon, and more. Today extinction is often driven by humans (habitat loss, hunting, climate change)."]),
    (["endangered species"], ["Endangered species are at high risk of extinction. Examples: tigers, rhinos, gorillas, vaquita, many amphibians. Conservation efforts include protected areas, breeding programmes, and laws."]),
    (["invasive species"], ["Invasive species are non-native species that spread and harm the environment or economy. Examples: cane toad in Australia, zebra mussels, kudzu. Control is difficult once established."]),
    (["biomimicry"], ["Biomimicry is designing things inspired by nature—e.g. Velcro from burrs, shark-skin coatings, bullet trains shaped like kingfisher beaks. Nature has solved many engineering problems."]),
    (["tardigrade space"], ["Tardigrades have survived exposure to space—they were taken outside the ISS and some revived after returning. They're among the hardiest known organisms."]),
    (["space junk"], ["Space junk is defunct satellites, rocket stages, and debris in orbit. It poses a risk to active spacecraft and the ISS. Clean-up missions and guidelines for disposal are being developed."]),
    (["space tourism"], ["Space tourism is when private citizens pay to go to space. Companies like SpaceX and Blue Origin offer suborbital or orbital flights. It's still expensive and rare."]),
    (["mars colony"], ["A human colony on Mars is a long-term goal of SpaceX and others. Challenges include radiation, low gravity, and supplying water and food. No firm date exists for a permanent settlement."]),
    (["terraforming"], ["Terraforming is the idea of making another planet (e.g. Mars) Earth-like. It would require enormous technology and time—changing atmosphere, temperature, and possibly introducing life. It's still theoretical."]),
    (["multiverse"], ["The multiverse is the idea that our universe is one of many. Some physics theories suggest it; it's hard to test. It's popular in science fiction and philosophy."]),
    (["time travel"], ["Time travel to the future is possible in theory (e.g. near light speed or a black hole—time dilation). Travel to the past has no known way and leads to paradoxes; it may be impossible."]),
    (["wormhole"], ["A wormhole is a hypothetical shortcut through spacetime. They appear in Einstein's equations but would need exotic matter to stay open. None have been observed."]),
    (["parallel universe"], ["Parallel universes could mean many things: other branches in quantum theory, other bubbles in inflation, or other dimensions. They're speculative; evidence is indirect or absent."]),
    (["simulation theory"], ["Simulation theory is the idea that we might be living in a computer simulation. It's a philosophical possibility but not testable in a clear way. There's no evidence we are in one."]),
    (["fermi paradox"], ["The Fermi paradox: the universe is huge and old, so why don't we see evidence of other civilisations? Possible answers: they're rare, they're different, we're not looking right, or they avoid us."]),
    (["drake equation"], ["The Drake equation estimates the number of communicative civilisations in our galaxy. It multiplies factors like star formation rate, fraction with planets, and chance of life and intelligence. Many factors are unknown."]),
    (["goldilocks zone", "habitable zone"], ["The habitable zone is the range of distances from a star where liquid water could exist on a planet's surface. Too close = too hot; too far = too cold. It's a rough guide for where life might exist."]),
    (["exoplanet habitable"], ["Thousands of exoplanets are known; some are in the habitable zone. Whether they have water, atmosphere, or life is unknown. We're starting to study their atmospheres with telescopes."]),
    (["james webb discoveries"], ["The James Webb Space Telescope has observed early galaxies, star formation, and exoplanet atmospheres. It sees in infrared and can look further back in time than Hubble."]),
    (["hubble deep field"], ["The Hubble Deep Field image showed thousands of galaxies in a tiny patch of sky. It revealed how many galaxies exist and how they've evolved. It was a long exposure of a 'empty' region."]),
    (["pale blue dot"], ["'Pale Blue Dot' is a photo of Earth taken by Voyager 1 from about 6 billion km away. Carl Sagan used it to describe how small and precious Earth is in the cosmos."]),
    (["overview effect"], ["The overview effect is the shift in awareness some astronauts report when seeing Earth from space—a sense of unity and fragility. It's often described as life-changing."]),
]

KNOWLEDGE.extend(CRAZY_KNOWLEDGE)

try:
    from massive_knowledge import MASSIVE_KNOWLEDGE
    KNOWLEDGE.extend(MASSIVE_KNOWLEDGE)
except ImportError:
    pass
try:
    from extra_smart_knowledge import EXTRA_SMART_KNOWLEDGE
    KNOWLEDGE.extend(EXTRA_SMART_KNOWLEDGE)
except ImportError:
    pass

