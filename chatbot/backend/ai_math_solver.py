"""
AI Math Solver: arithmetic, percentages, basic algebra, geometry,
and word-problem parsing to give Josiah strong math capabilities.
"""
import re
import math
from typing import List, Tuple, Optional, Dict, Any
from fractions import Fraction, Decimal


def _clean_number(s: str) -> Optional[float]:
    """Parse a string to float; return None if invalid."""
    if not s:
        return None
    s = s.strip().replace(",", "")
    try:
        return float(s)
    except ValueError:
        return None


def _extract_numbers(text: str) -> List[float]:
    """Extract all numbers from text (integers and decimals)."""
    pattern = r"-?\d+\.?\d*"
    return [_clean_number(m) for m in re.findall(pattern, text) if _clean_number(m) is not None]


def solve_arithmetic_expression(expr: str) -> Optional[Tuple[float, str]]:
    """
    Safely evaluate a simple arithmetic expression.
    Returns (result, explanation) or None if invalid.
    Supports +, -, *, /, %, and parentheses for grouping.
    """
    if not expr or not isinstance(expr, str):
        return None
    expr = expr.strip().replace(" ", "").replace("×", "*").replace("÷", "/")
    # Only allow digits, operators, parentheses, and one decimal point per number
    if not re.match(r"^[\d+\-*/().%\s]+$", expr):
        return None
    try:
        # Handle % as modulo
        expr_eval = expr.replace("%", "%")
        result = eval(expr_eval)
        if isinstance(result, float) and (math.isnan(result) or math.isinf(result)):
            return None
        return (float(result), f"The result is {result}.")
    except Exception:
        return None


def solve_percentage_question(text: str) -> Optional[Tuple[float, str]]:
    """
    Answer "what is X% of Y?" or "Y is X% of what?" or "X is what percent of Y?"
    Returns (answer, explanation).
    """
    text_lower = text.lower().strip()
    numbers = _extract_numbers(text)

    # "what is 15% of 80" or "15 percent of 80" or "what is 20 percent of 80"
    m = re.search(r"(?:what\s+is\s+)?(\d+(?:\.\d+)?)\s*%\s*(?:of\s+)?(\d+(?:\.\d+)?)", text_lower)
    if m:
        p, whole = float(m.group(1)), float(m.group(2))
        result = (p / 100) * whole
        return (result, f"{p}% of {whole} = {p/100} × {whole} = {result}. So the answer is {result}.")
    m = re.search(r"(?:what\s+is\s+)?(\d+(?:\.\d+)?)\s*percent\s+of\s+(\d+(?:\.\d+)?)", text_lower)
    if m:
        p, whole = float(m.group(1)), float(m.group(2))
        result = (p / 100) * whole
        return (result, f"{p}% of {whole} = {p/100} × {whole} = {result}. So the answer is {result}.")

    # "80 is 15% of what"
    m = re.search(r"(\d+(?:\.\d+)?)\s+is\s+(\d+(?:\.\d+)?)\s*%\s+of\s+what", text_lower)
    if m:
        part, p = float(m.group(1)), float(m.group(2))
        if p == 0:
            return None
        whole = part / (p / 100)
        return (whole, f"If {part} is {p}% of a number, then that number = {part} ÷ ({p}/100) = {part} ÷ {p/100} = {whole}.")

    # "what percent of 80 is 20"
    m = re.search(r"what\s+percent\s+of\s+(\d+(?:\.\d+)?)\s+is\s+(\d+(?:\.\d+)?)", text_lower)
    if m:
        whole, part = float(m.group(1)), float(m.group(2))
        if whole == 0:
            return None
        p = (part / whole) * 100
        return (p, f"{part} ÷ {whole} × 100 = {p}%. So the answer is {p}%.")

    if len(numbers) >= 2 and "%" in text:
        # Heuristic: "X% of Y"
        idx = text_lower.find("%")
        before = text_lower[:idx]
        after = text_lower[idx:]
        nums_before = _extract_numbers(before)
        nums_after = _extract_numbers(after)
        if nums_before and nums_after:
            p, whole = nums_before[-1], nums_after[0]
            result = (p / 100) * whole
            return (result, f"{p}% of {whole} = {result}.")

    return None


def solve_simple_algebra(text: str) -> Optional[Tuple[float, str]]:
    """
    Solve very simple linear equations like "2x + 5 = 15" or "3x = 12".
    Returns (value of x, explanation).
    """
    text_lower = text.lower().replace(" ", "")
    # 3x = 12
    m = re.search(r"(\d+(?:\.\d+)?)\s*x\s*=\s*(\d+(?:\.\d+)?)", text_lower)
    if m:
        a, b = float(m.group(1)), float(m.group(2))
        if a == 0:
            return None
        x = b / a
        return (x, f"Divide both sides by {a}: x = {b}/{a} = {x}. So x = {x}.")

    # x + 5 = 15
    m = re.search(r"x\s*\+\s*(\d+(?:\.\d+)?)\s*=\s*(\d+(?:\.\d+)?)", text_lower)
    if m:
        c, b = float(m.group(1)), float(m.group(2))
        x = b - c
        return (x, f"Subtract {c} from both sides: x = {b} - {c} = {x}. So x = {x}.")

    # 2x + 5 = 15
    m = re.search(r"(\d+(?:\.\d+)?)\s*x\s*\+\s*(\d+(?:\.\d+)?)\s*=\s*(\d+(?:\.\d+)?)", text_lower)
    if m:
        a, c, b = float(m.group(1)), float(m.group(2)), float(m.group(3))
        if a == 0:
            return None
        x = (b - c) / a
        return (x, f"First subtract {c}: {a}x = {b - c}. Then divide by {a}: x = {(b - c)}/{a} = {x}. So x = {x}.")

    return None


def solve_quadratic_formula(a: float, b: float, c: float) -> Optional[Tuple[Optional[float], Optional[float], str]]:
    """
    Solve ax² + bx + c = 0. Returns (x1, x2, explanation) or None if invalid.
    """
    if a == 0:
        return None
    disc = b * b - 4 * a * c
    if disc < 0:
        return (None, None, "The discriminant is negative, so there are no real solutions (only complex ones).")
    sqrt_d = math.sqrt(disc)
    x1 = (-b + sqrt_d) / (2 * a)
    x2 = (-b - sqrt_d) / (2 * a)
    expl = f"Using the quadratic formula: x = (-b ± √(b²-4ac)) / (2a). Here a={a}, b={b}, c={c}. Discriminant = {disc}. So x = {x1} or x = {x2}."
    return (x1, x2, expl)


def detect_quadratic_question(text: str) -> Optional[Tuple[float, float, float, str]]:
    """Try to extract a, b, c from 'solve x^2 + 5x + 6 = 0' or similar. Returns (a, b, c, explanation)."""
    text_lower = text.lower().replace(" ", "")
    # x^2 + 5x + 6 = 0
    m = re.search(r"x\^2\s*\+\s*(\d+(?:\.\d+)?)\s*x\s*\+\s*(\d+(?:\.\d+)?)\s*=\s*0", text_lower)
    if m:
        b, c = float(m.group(1)), float(m.group(2))
        return (1.0, b, c, f"Equation: x² + {b}x + {c} = 0, so a=1, b={b}, c={c}.")

    # 2x^2 - 4x + 2 = 0
    m = re.search(r"(\d+(?:\.\d+)?)\s*x\^2\s*([+-])\s*(\d+(?:\.\d+)?)\s*x\s*([+-])\s*(\d+(?:\.\d+)?)\s*=\s*0", text_lower)
    if m:
        a = float(m.group(1))
        b_sign = 1 if m.group(2) == "+" else -1
        b = b_sign * float(m.group(3))
        c_sign = 1 if m.group(4) == "+" else -1
        c = c_sign * float(m.group(5))
        return (a, b, c, f"Equation: {a}x² + ({b})x + ({c}) = 0.")

    return None


def area_of_circle(radius: float) -> Tuple[float, str]:
    """Area = πr²."""
    r = float(radius)
    area = math.pi * r * r
    return (area, f"Area of a circle = πr² = π × {r}² = {area:.4f} (using π ≈ 3.14159).")


def circumference_of_circle(radius: float) -> Tuple[float, str]:
    """Circumference = 2πr."""
    r = float(radius)
    c = 2 * math.pi * r
    return (c, f"Circumference = 2πr = 2 × π × {r} = {c:.4f}.")


def area_of_rectangle(length: float, width: float) -> Tuple[float, str]:
    """Area = length × width."""
    a = length * width
    return (a, f"Area of a rectangle = length × width = {length} × {width} = {a}.")


def area_of_triangle(base: float, height: float) -> Tuple[float, str]:
    """Area = (1/2) × base × height."""
    a = 0.5 * base * height
    return (a, f"Area of a triangle = (1/2) × base × height = 0.5 × {base} × {height} = {a}.")


def volume_of_sphere(radius: float) -> Tuple[float, str]:
    """Volume = (4/3)πr³."""
    r = float(radius)
    v = (4 / 3) * math.pi * (r ** 3)
    return (v, f"Volume of a sphere = (4/3)πr³ = (4/3) × π × {r}³ = {v:.4f}.")


def volume_of_cylinder(radius: float, height: float) -> Tuple[float, str]:
    """Volume = πr²h."""
    r, h = float(radius), float(height)
    v = math.pi * r * r * h
    return (v, f"Volume of a cylinder = πr²h = π × {r}² × {h} = {v:.4f}.")


def pythagorean_theorem(a: float, b: float, find: str) -> Optional[Tuple[float, str]]:
    """a² + b² = c². find is 'c' or 'a' or 'b'."""
    a, b = float(a), float(b)
    if find.lower() == "c":
        c = math.sqrt(a * a + b * b)
        return (c, f"By Pythagoras: c² = a² + b² = {a}² + {b}² = {a*a + b*b}, so c = √{a*a + b*b} = {c:.4f}.")
    return None


def process_math_message(message: str) -> Optional[Tuple[str, bool]]:
    """
    Try to interpret the message as a math question, solve it, and return (reply, used_math).
    If not a math question or cannot solve, return None.
    """
    if not message or len(message) < 2:
        return None
    text = message.strip().lower()

    # Percentage
    result = solve_percentage_question(message)
    if result is not None:
        ans, expl = result
        return (expl, True)

    # Quadratic
    quad = detect_quadratic_question(message)
    if quad is not None:
        a, b, c, _ = quad
        sol = solve_quadratic_formula(a, b, c)
        if sol is not None:
            x1, x2, expl = sol
            if x1 is not None and x2 is not None:
                return (expl, True)
            return (expl, True)

    # Simple algebra
    result = solve_simple_algebra(message)
    if result is not None:
        _, expl = result
        return (expl, True)

    # "area of circle radius 5"
    m = re.search(r"area\s+of\s+(?:a\s+)?circle\s+(?:with\s+)?radius\s+(\d+(?:\.\d+)?)", text)
    if m:
        r = float(m.group(1))
        _, expl = area_of_circle(r)
        return (expl, True)

    m = re.search(r"circumference\s+of\s+(?:a\s+)?circle\s+(?:with\s+)?radius\s+(\d+(?:\.\d+)?)", text)
    if m:
        r = float(m.group(1))
        _, expl = circumference_of_circle(r)
        return (expl, True)

    # "volume of sphere radius 3"
    m = re.search(r"volume\s+of\s+(?:a\s+)?sphere\s+(?:with\s+)?radius\s+(\d+(?:\.\d+)?)", text)
    if m:
        r = float(m.group(1))
        _, expl = volume_of_sphere(r)
        return (expl, True)

    # Simple arithmetic: "what is 3 + 5" or "calculate 10 * 7"
    m = re.search(r"(?:what\s+is|calculate|compute|solve)\s+([\d\s+\-*/().]+)", text)
    if m:
        expr = m.group(1).strip()
        res = solve_arithmetic_expression(expr)
        if res is not None:
            _, expl = res
            return (expl, True)

    # Bare expression "3 + 5 * 2"
    if re.match(r"^[\d\s+\-*/().]+$", text.replace(" ", "")):
        res = solve_arithmetic_expression(text)
        if res is not None:
            _, expl = res
            return (expl, True)

    return None


# --- Math concept explanations (for when we don't solve but explain) ---
MATH_CONCEPT_REPLIES = {
    "quadratic formula": "The quadratic formula solves ax² + bx + c = 0. It is x = (-b ± √(b²-4ac)) / (2a). The part under the square root, b²-4ac, is called the discriminant. If it's positive, there are two real solutions; if zero, one; if negative, no real solutions.",
    "pythagorean theorem": "The Pythagorean theorem says that in a right triangle, the square of the hypotenuse (the side opposite the right angle) equals the sum of the squares of the other two sides: a² + b² = c². You can use it to find any side if you know the other two.",
    "area of circle": "The area of a circle is πr², where r is the radius. So if the radius is 5, the area is π × 25 ≈ 78.54 square units.",
    "circumference of circle": "The circumference (distance around) a circle is 2πr, where r is the radius. So for radius 5, circumference = 2 × π × 5 ≈ 31.42.",
    "volume of sphere": "The volume of a sphere is (4/3)πr³. So for radius 3, volume = (4/3) × π × 27 ≈ 113.1 cubic units.",
    "percentage": "To find X% of Y, multiply Y by X/100. For example, 20% of 80 = 0.20 × 80 = 16. To find what percent X is of Y, do (X/Y) × 100.",
    "fraction": "A fraction is a part of a whole, written as a/b. You can add fractions with a common denominator, multiply by multiplying numerators and denominators, and divide by multiplying by the reciprocal.",
    "decimal": "Decimals are a way to write numbers with a fractional part using a decimal point. The first place after the point is tenths, then hundredths, and so on.",
    "square root": "The square root of a number n is a number that when multiplied by itself gives n. For example, √9 = 3 because 3×3 = 9. Negative numbers don't have real square roots.",
    "exponent": "An exponent means repeated multiplication. For example, 2³ = 2×2×2 = 8. Rules: aⁿ × aᵐ = aⁿ⁺ᵐ, aⁿ ÷ aᵐ = aⁿ⁻ᵐ, (aⁿ)ᵐ = aⁿᵐ.",
    "algebra": "Algebra uses letters (like x) to stand for unknown numbers. You solve equations by doing the same thing to both sides until the unknown is alone. For example, 2x + 3 = 9 → subtract 3 → 2x = 6 → divide by 2 → x = 3.",
    "geometry": "Geometry is the study of shapes, angles, and space. Key ideas include area (for 2D shapes), volume (for 3D shapes), and the Pythagorean theorem for right triangles.",
    "pi": "Pi (π) is the ratio of a circle's circumference to its diameter. It's approximately 3.14159 and is used in formulas for circles and spheres. It has infinitely many decimal places.",
    "mean average": "The mean (average) of a set of numbers is the sum of all the numbers divided by how many there are. For example, the mean of 4, 8, and 12 is (4+8+12)/3 = 8.",
    "median": "The median is the middle value when numbers are arranged in order. If there's an even count, it's the average of the two middle values.",
    "mode": "The mode is the value that appears most often in a set of numbers. A set can have one mode, more than one, or no mode.",
}


def get_math_concept_reply(query: str) -> Optional[str]:
    """If the query asks about a math concept, return an explanation."""
    q = query.lower().strip()
    for key, reply in MATH_CONCEPT_REPLIES.items():
        if key in q:
            return reply
    return None
