"""
Student Survival App — Phase 1
================================
IBM Cloud Code Engine Job

Reads student life variables from environment variables,
calculates a survival score, and prints a personalised
survival report with a funny verdict to stdout (Code Engine logs).

Environment Variables:
  STUDENT_NAME         – your name (default: "Student")
  COFFEE_CUPS          – cups of coffee consumed today (default: 0)
  SLEEP_HOURS          – hours of sleep last night (default: 7)
  ASSIGNMENTS_DUE      – number of assignments due this week (default: 0)
  EXAM_TOMORROW        – "yes" or "no" (default: "no")
  DAYS_SINCE_OUTSIDE   – days since you last went outside (default: 0)
  ENERGY_DRINK_CANS    – energy drink cans today (default: 0)
  GPA                  – current GPA out of 4.0 (default: 3.0)
  LAST_MEAL_HOURS      – hours since last real meal (default: 4)
"""

import os
import math
import random


# ── Helpers ────────────────────────────────────────────────────────────────────

def clamp(val, lo, hi):
    return max(lo, min(hi, val))


def env_float(key, default):
    try:
        return float(os.getenv(key, str(default)))
    except ValueError:
        return default


def env_str(key, default):
    return os.getenv(key, default).strip()


# ── Survival score engine ──────────────────────────────────────────────────────

def calculate_survival(inputs: dict) -> tuple[float, dict]:
    """
    Returns (survival_pct, breakdown_dict).
    Each category contributes a score from 0–100 that is weighted into the total.
    """
    scores = {}

    # --- Sleep score (most impactful) ---
    sleep = inputs["sleep_hours"]
    if sleep >= 8:
        scores["sleep"] = 100
    elif sleep >= 7:
        scores["sleep"] = 85
    elif sleep >= 6:
        scores["sleep"] = 65
    elif sleep >= 5:
        scores["sleep"] = 40
    elif sleep >= 4:
        scores["sleep"] = 20
    else:
        scores["sleep"] = max(0, sleep * 4)   # below 4h: basically 0

    # --- Caffeine score ---
    # Sweet spot: 1–2 cups. Too much tanks focus.
    coffee  = inputs["coffee_cups"]
    drinks  = inputs["energy_drink_cans"]
    total_caffeine = coffee + drinks * 2.5    # energy drinks hit harder

    if total_caffeine == 0:
        scores["caffeine"] = 60              # unoptimised but not destroyed
    elif total_caffeine <= 2:
        scores["caffeine"] = 100
    elif total_caffeine <= 4:
        scores["caffeine"] = 80
    elif total_caffeine <= 6:
        scores["caffeine"] = 50
    elif total_caffeine <= 8:
        scores["caffeine"] = 25
    else:
        scores["caffeine"] = max(0, 100 - total_caffeine * 10)  # you are vibrating

    # --- Academic pressure score ---
    assignments = inputs["assignments_due"]
    exam_tomorrow = inputs["exam_tomorrow"]

    pressure = assignments + (3 if exam_tomorrow else 0)

    if pressure == 0:
        scores["pressure"] = 100
    elif pressure <= 2:
        scores["pressure"] = 80
    elif pressure <= 4:
        scores["pressure"] = 55
    elif pressure <= 6:
        scores["pressure"] = 30
    else:
        scores["pressure"] = max(0, 100 - pressure * 12)

    # --- Outdoor / social score ---
    outside = inputs["days_since_outside"]

    if outside == 0:
        scores["outside"] = 100
    elif outside == 1:
        scores["outside"] = 80
    elif outside == 2:
        scores["outside"] = 60
    elif outside <= 4:
        scores["outside"] = 35
    else:
        scores["outside"] = max(0, 100 - outside * 15)

    # --- Nutrition score ---
    last_meal = inputs["last_meal_hours"]

    if last_meal <= 3:
        scores["nutrition"] = 100
    elif last_meal <= 6:
        scores["nutrition"] = 75
    elif last_meal <= 10:
        scores["nutrition"] = 40
    else:
        scores["nutrition"] = max(0, 100 - last_meal * 8)

    # --- GPA morale bonus ---
    gpa = clamp(inputs["gpa"], 0.0, 4.0)
    scores["morale"] = round((gpa / 4.0) * 100)

    # Weighted total
    weights = {
        "sleep":     0.30,
        "caffeine":  0.15,
        "pressure":  0.25,
        "outside":   0.10,
        "nutrition": 0.12,
        "morale":    0.08,
    }

    total = sum(scores[k] * weights[k] for k in scores)

    # Exam-tomorrow penalty (sudden drop)
    if exam_tomorrow:
        total *= 0.85

    return round(clamp(total, 1, 99), 1), scores


# ── Verdict engine ─────────────────────────────────────────────────────────────

def get_verdict(survival_pct: float, inputs: dict) -> tuple[str, str, str]:
    """Returns (status_label, headline, funny_message)."""

    name  = inputs["name"]
    sleep = inputs["sleep_hours"]
    coffee = inputs["coffee_cups"]
    drinks = inputs["energy_drink_cans"]
    exam   = inputs["exam_tomorrow"]

    # Build a personalised funny message based on worst stat
    if survival_pct >= 85:
        status   = "THRIVING"
        headline = f"{name}, you are built different."
        messages = [
            "Somehow you have your life together. Suspicious.",
            "Are you actually a student or just cosplaying as one?",
            "You slept, you ate, you're outside. This is illegal.",
            "Your future self is proud. Annoyingly proud.",
        ]

    elif survival_pct >= 70:
        status   = "STABLE"
        headline = f"{name}, you're holding it together. Barely."
        messages = [
            "Not thriving, not dying. The student sweet spot.",
            "You're like a browser with 47 tabs. Functional. For now.",
            "GPA intact. Sanity: pending review.",
            "You could use more sleep but honestly who couldn't.",
        ]

    elif survival_pct >= 50:
        status   = "AT RISK"
        headline = f"{name}, the cracks are showing."
        messages = [
            "You're running on caffeine and sheer stubbornness.",
            "Your body is a temple. A haunted one.",
            "Sleep is not optional. This is a threat.",
            f"{'You have an exam tomorrow and ' if exam else ''}"
            "your eyes have given up blinking voluntarily.",
        ]

    elif survival_pct >= 30:
        status   = "CRITICAL"
        headline = f"{name}, please sit down."
        messages = [
            f"You've had {coffee} coffees and {drinks} energy drinks. "
            "Your heart is filing a formal complaint.",
            f"You haven't been outside in {inputs['days_since_outside']} days. "
            "Plants need sunlight. So do you.",
            "The assignments are due. The assignments are ALWAYS due.",
            "Your survival rate is lower than your Wi-Fi signal at 2am.",
        ]

    else:
        status   = "SEND HELP"
        headline = f"{name}... we need to talk."
        messages = [
            f"Only {survival_pct}% survival. That's not a grade, "
            "that's a medical reading.",
            f"You slept {sleep} hours, drank {coffee + drinks} caffeinated "
            "things, and somehow opened this app. Respect.",
            "At this point you are not a student. You are a warning label.",
            "Please eat something. Drink water. Touch grass. In that order.",
        ]

    return status, headline, random.choice(messages)


# ── ASCII survival bar ─────────────────────────────────────────────────────────

def survival_bar(pct: float, width: int = 40) -> str:
    filled = round(pct / 100 * width)
    empty  = width - filled

    if pct >= 70:
        char = "█"
        colour = "▓"
    elif pct >= 40:
        char = "▓"
        colour = "░"
    else:
        char = "░"
        colour = " "

    bar = char * filled + "░" * empty
    return f"[{bar}] {pct:.1f}%"


# ── Score breakdown display ────────────────────────────────────────────────────

def score_row(label: str, score: float, note: str = "") -> str:
    stars = round(score / 20)           # 0–5 stars
    filled = "★" * stars
    empty  = "☆" * (5 - stars)
    note_str = f"  ← {note}" if note else ""
    return f"  {label:<22} {filled}{empty}  ({score:.0f}/100){note_str}"


def build_breakdown(scores: dict, inputs: dict) -> str:
    lines = []

    sleep_note  = f"{inputs['sleep_hours']}h sleep"
    caff_note   = f"{inputs['coffee_cups']} coffee, {inputs['energy_drink_cans']} energy drinks"
    press_note  = f"{inputs['assignments_due']} assignments" + (" + exam tomorrow!" if inputs['exam_tomorrow'] else "")
    out_note    = f"{inputs['days_since_outside']} day(s) indoors"
    meal_note   = f"{inputs['last_meal_hours']}h since last meal"
    gpa_note    = f"GPA {inputs['gpa']:.1f}"

    lines.append(score_row("😴  Sleep",          scores["sleep"],    sleep_note))
    lines.append(score_row("☕  Caffeine",        scores["caffeine"], caff_note))
    lines.append(score_row("📚  Academic Load",  scores["pressure"], press_note))
    lines.append(score_row("🌿  Touch Grass",    scores["outside"],  out_note))
    lines.append(score_row("🍕  Nutrition",      scores["nutrition"],meal_note))
    lines.append(score_row("🎓  GPA Morale",     scores["morale"],   gpa_note))

    return "\n".join(lines)


# ── Main report ────────────────────────────────────────────────────────────────

def print_report(inputs: dict, survival_pct: float, scores: dict):
    status, headline, message = get_verdict(survival_pct, inputs)
    bar     = survival_bar(survival_pct)
    details = build_breakdown(scores, inputs)

    sep  = "═" * 58
    sep2 = "─" * 58

    print(f"""
{sep}
  🎓  STUDENT SURVIVAL CALCULATOR
  Saskatchewan Polytechnic — Code Engine Lab
{sep}

  Student : {inputs['name']}
  Status  : {status}

  SURVIVAL RATE
  {sep2}
  {bar}

  {headline}
  "{message}"

  BREAKDOWN
  {sep2}
{details}

  {sep2}
  ⚠  Disclaimer: This app is not responsible for failed
     exams, caffeine overdoses, or existential crises.
     Please drink water.
{sep}
""")


# ── Entry point ────────────────────────────────────────────────────────────────

def main():
    inputs = {
        "name":               env_str  ("STUDENT_NAME",       "Student"),
        "coffee_cups":        env_float("COFFEE_CUPS",        0),
        "sleep_hours":        env_float("SLEEP_HOURS",        7),
        "assignments_due":    env_float("ASSIGNMENTS_DUE",    0),
        "exam_tomorrow":      env_str  ("EXAM_TOMORROW",      "no").lower() == "yes",
        "days_since_outside": env_float("DAYS_SINCE_OUTSIDE", 0),
        "energy_drink_cans":  env_float("ENERGY_DRINK_CANS",  0),
        "gpa":                env_float("GPA",                3.0),
        "last_meal_hours":    env_float("LAST_MEAL_HOURS",    4),
    }

    survival_pct, scores = calculate_survival(inputs)
    print_report(inputs, survival_pct, scores)


if __name__ == "__main__":
    main()
