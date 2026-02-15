"""
AI Science Q&A: deep science knowledge, experiments, and concept explanations
for physics, chemistry, biology, and earth science.
"""
import re
from typing import List, Tuple, Optional, Dict

# Physics concepts and answers
PHYSICS_QA = {
    "newton first law": "Newton's first law says an object stays at rest or in constant motion unless a force acts on it. This is inertia—things keep doing what they're doing.",
    "newton second law": "Newton's second law: F = ma. Force equals mass times acceleration. So the harder you push (or the heavier the object), the more force you need to change its motion.",
    "newton third law": "Newton's third law: For every action there is an equal and opposite reaction. When you push a wall, the wall pushes back on you with the same force.",
    "gravity": "Gravity is the force that pulls objects with mass toward each other. On Earth it gives things weight and makes things fall. Newton described it; Einstein's general relativity describes it as curvature of space-time.",
    "friction": "Friction is a force that opposes motion between surfaces in contact. It comes from bumps and bonds between surfaces. Without friction we couldn't walk or drive.",
    "acceleration": "Acceleration is the rate of change of velocity—speeding up, slowing down, or changing direction. It's measured in m/s². F = ma links force to acceleration.",
    "velocity": "Velocity is speed in a given direction. So 50 km/h north is a velocity; 50 km/h is just speed. Change in velocity (including direction) means acceleration.",
    "momentum": "Momentum = mass × velocity. It's conserved in a closed system: total momentum before equals total momentum after a collision or interaction.",
    "energy conservation": "Energy cannot be created or destroyed, only changed from one form to another (kinetic, potential, heat, etc.). Total energy in a closed system stays constant.",
    "kinetic energy": "Kinetic energy is the energy of motion. KE = (1/2)mv². The faster or heavier something is, the more kinetic energy it has.",
    "potential energy": "Potential energy is stored energy due to position or condition. Gravitational PE = mgh (mass × g × height). A raised weight has potential energy that becomes kinetic when dropped.",
    "electricity": "Electricity is the flow of electric charge (usually electrons). Current is the rate of flow (amperes); voltage is the push (volts); resistance opposes flow (ohms). V = IR.",
    "magnet": "A magnet has a north and south pole. Like poles repel; opposite poles attract. Magnetic fields are produced by moving charges. Earth itself acts like a big magnet.",
    "light": "Light is electromagnetic radiation we can see. It travels in waves and also as particles (photons). It has a speed of about 300,000 km/s in a vacuum.",
    "sound": "Sound is a wave of pressure through a medium (air, water, etc.). It needs something to travel through—no sound in space. Pitch is frequency; loudness is amplitude.",
    "wave": "A wave is a disturbance that carries energy. Wavelength is the distance between peaks; frequency is how many pass per second. Speed = wavelength × frequency.",
    "reflection": "Reflection is when light or sound bounces off a surface. The angle of incidence equals the angle of reflection. Mirrors reflect light to form images.",
    "refraction": "Refraction is when light bends as it passes from one medium to another (e.g. air to water) because speed changes. That's why a straw looks bent in water.",
    "photosynthesis": "Photosynthesis is how plants make food. They use sunlight, water, and carbon dioxide to produce glucose and oxygen. It happens in chloroplasts, using chlorophyll.",
    "water cycle": "The water cycle: evaporation (water to vapour), condensation (vapour to clouds), precipitation (rain/snow), and runoff or infiltration. Water moves continuously through these stages.",
    "solar system": "The solar system has the Sun and everything that orbits it: eight planets (Mercury to Neptune), dwarf planets like Pluto, moons, asteroids, and comets. The Sun contains almost all the mass.",
    "black hole": "A black hole is a region where gravity is so strong that nothing, not even light, can escape. It forms when a massive star collapses. The boundary is the event horizon.",
    "atom": "An atom is the smallest unit of an element. It has a nucleus (protons and neutrons) and electrons around it. Different elements have different numbers of protons.",
    "molecule": "A molecule is two or more atoms bonded together. Water is H₂O—two hydrogen atoms and one oxygen. Molecules can be simple or very large like DNA.",
    "element": "An element is a substance made of one type of atom. There are about 118 elements on the periodic table. Examples: hydrogen, carbon, gold, oxygen.",
    "compound": "A compound is a substance made of two or more different elements in a fixed ratio. Water (H₂O) and salt (NaCl) are compounds.",
    "chemical reaction": "A chemical reaction is when substances change into new substances. Bonds break and form. Signs: colour change, gas produced, heat, or precipitate. Mass is conserved.",
    "periodic table": "The periodic table arranges elements by atomic number and properties. Rows are periods; columns are groups. Elements in the same group often have similar behaviour.",
    "acid base": "Acids donate protons (H⁺); bases accept them. pH measures acidity: below 7 is acid, 7 is neutral, above 7 is base. Vinegar is acidic; baking soda solution is basic.",
    "cell": "Cells are the basic units of life. They have a membrane, cytoplasm, and DNA. Plant cells have a cell wall and chloroplasts; animal cells don't.",
    "dna": "DNA (deoxyribonucleic acid) carries genetic information. It's a double helix of two strands. Sequences of bases (A, T, G, C) code for proteins and traits.",
    "evolution": "Evolution is the change in species over time through natural selection. Organisms with traits that help survival and reproduction pass those traits on. Over many generations, species can change.",
    "natural selection": "Natural selection means that organisms better suited to their environment tend to survive and reproduce more. Over time this can lead to new species.",
    "ecosystem": "An ecosystem includes all living things and their physical environment in an area. Energy flows (e.g. sun to plants to animals); nutrients cycle.",
    "food chain": "A food chain shows who eats whom: producer (plant) → herbivore → carnivore. Food webs show many interconnected chains in an ecosystem.",
    "climate change": "Climate change is long-term change in global temperatures and weather patterns. It's largely driven by more greenhouse gases (e.g. CO₂) from human activity, leading to warming and other effects.",
    "greenhouse effect": "The greenhouse effect is when gases in the atmosphere trap heat from the Sun. Some of it is natural and keeps Earth warm; extra greenhouse gases from human activity increase warming.",
}

# Experiment ideas (short)
EXPERIMENT_IDEAS = [
    "Vinegar and baking soda: mix them to see a fizzy reaction (CO₂ gas). Safe and easy.",
    "Plant growth: grow two plants—one in light, one in dark—to see how light affects growth.",
    "Density: float an egg in salt water vs fresh water to see how salt changes density.",
    "Static electricity: rub a balloon on your hair and stick it to a wall.",
    "Magnet and paper clips: see how many paper clips a magnet can hold; try different magnets.",
    "Dissolving: see how fast sugar dissolves in hot vs cold water.",
    "Volcano: baking soda + vinegar in a model volcano for a safe 'eruption.'",
]


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower()) if text else ""


def get_science_reply(query: str) -> Optional[str]:
    """Return a science explanation if the query matches a known topic."""
    q = _normalize(query)
    for key, answer in PHYSICS_QA.items():
        key_words = key.split()
        if all(w in q for w in key_words):
            return answer
        if key in q:
            return answer
    return None


def get_experiment_suggestion(query: str) -> Optional[str]:
    """If user asks for an experiment idea, return one."""
    q = _normalize(query)
    if any(w in q for w in ["experiment", "science project", "try at home", "easy science"]):
        return "Here's an idea you can try: " + (EXPERIMENT_IDEAS[0] if EXPERIMENT_IDEAS else "Mix vinegar and baking soda to see a safe chemical reaction.")
    return None


def process_science_message(message: str) -> Optional[str]:
    """Handle science-related questions. Return reply or None."""
    if not message:
        return None
    reply = get_science_reply(message)
    if reply:
        return reply
    reply = get_experiment_suggestion(message)
    if reply:
        return reply
    return None
