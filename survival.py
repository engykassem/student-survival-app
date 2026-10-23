"""
Student Survival App — Phase 2 (Web Application)
==================================================
IBM Cloud Code Engine Application

A Flask web app with sliders and dropdowns.
Fill in your student life variables, hit Submit,
and your Survival Rate appears on the same page.

No environment variables needed — everything is entered
through the web interface.
"""

from flask import Flask, render_template, request
import math
import random

app = Flask(__name__)


# ── Survival score engine ──────────────────────────────────────────────────────

def clamp(val, lo, hi):
    return max(lo, min(hi, val))


def calculate_survival(inputs: dict) -> tuple:
    scores = {}

    # Sleep
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
        scores["sleep"] = max(0, sleep * 4)

    # Caffeine
    coffee = inputs["coffee_cups"]
    drinks = inputs["energy_drink_cans"]
    total_caffeine = coffee + drinks * 2.5

    if total_caffeine == 0:
        scores["caffeine"] = 60
    elif total_caffeine <= 2:
        scores["caffeine"] = 100
    elif total_caffeine <= 4:
        scores["caffeine"] = 80
    elif total_caffeine <= 6:
        scores["caffeine"] = 50
    elif total_caffeine <= 8:
        scores["caffeine"] = 25
    else:
        scores["caffeine"] = max(0, 100 - total_caffeine * 10)

    # Academic pressure
    assignments  = inputs["assignments_due"]
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

    # Outside
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

    # Nutrition
    last_meal = inputs["last_meal_hours"]
    if last_meal <= 3:
        scores["nutrition"] = 100
    elif last_meal <= 6:
        scores["nutrition"] = 75
    elif last_meal <= 10:
        scores["nutrition"] = 40
    else:
        scores["nutrition"] = max(0, 100 - last_meal * 8)

    # GPA morale
    gpa = clamp(inputs["gpa"], 0.0, 4.0)
    scores["morale"] = round((gpa / 4.0) * 100)

    weights = {
        "sleep":     0.30,
        "caffeine":  0.15,
        "pressure":  0.25,
        "outside":   0.10,
        "nutrition": 0.12,
        "morale":    0.08,
    }

    total = sum(scores[k] * weights[k] for k in scores)
    if exam_tomorrow:
        total *= 0.85

    return round(clamp(total, 1, 99), 1), scores


def get_verdict(survival_pct, inputs):
    name  = inputs["name"]
    sleep = inputs["sleep_hours"]
    coffee = inputs["coffee_cups"]
    drinks = inputs["energy_drink_cans"]
    exam   = inputs["exam_tomorrow"]

    if survival_pct >= 85:
        status  = "THRIVING"
        color   = "#198038"
        emoji   = "🌟"
        messages = [
            "Somehow you have your life together. Suspicious.",
            "Are you actually a student or just cosplaying as one?",
            "You slept, you ate, you went outside. This is illegal.",
            "Your future self is proud. Annoyingly proud.",
        ]
    elif survival_pct >= 70:
        status  = "STABLE"
        color   = "#0f62fe"
        emoji   = "😐"
        messages = [
            "Not thriving, not dying. The student sweet spot.",
            "You're like a browser with 47 tabs. Functional. For now.",
            "GPA intact. Sanity: pending review.",
            "You could use more sleep but honestly who couldn't.",
        ]
    elif survival_pct >= 50:
        status  = "AT RISK"
        color   = "#f1c21b"
        emoji   = "😰"
        messages = [
            "You're running on caffeine and sheer stubbornness.",
            "Your body is a temple. A haunted one.",
            "Sleep is not optional. This is a threat.",
            f"{'Exam tomorrow and ' if exam else ''}your eyes have given up blinking voluntarily.",
        ]
    elif survival_pct >= 30:
        status  = "CRITICAL"
        color   = "#ff832b"
        emoji   = "😵"
        messages = [
            f"You've had {coffee} coffees and {drinks} energy drinks. Your heart is filing a formal complaint.",
            f"You haven't been outside in {inputs['days_since_outside']} days. Plants need sunlight. So do you.",
            "The assignments are due. The assignments are ALWAYS due.",
            "Your survival rate is lower than your Wi-Fi signal at 2am.",
        ]
    else:
        status  = "SEND HELP"
        color   = "#da1e28"
        emoji   = "💀"
        messages = [
            f"Only {survival_pct}% survival. That's not a grade, that's a medical reading.",
            f"You slept {sleep}h, drank {coffee + drinks} caffeinated things, and somehow opened this app. Respect.",
            "At this point you are not a student. You are a warning label.",
            "Please eat something. Drink water. Touch grass. In that order.",
        ]

    return status, color, emoji, random.choice(messages)


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.route("/", methods=["GET", "POST"])
def index():
    result = None

    if request.method == "POST":
        inputs = {
            "name":               request.form.get("name", "Student"),
            "coffee_cups":        float(request.form.get("coffee_cups", 0)),
            "sleep_hours":        float(request.form.get("sleep_hours", 7)),
            "assignments_due":    float(request.form.get("assignments_due", 0)),
            "exam_tomorrow":      request.form.get("exam_tomorrow") == "yes",
            "days_since_outside": float(request.form.get("days_since_outside", 0)),
            "energy_drink_cans":  float(request.form.get("energy_drink_cans", 0)),
            "gpa":                float(request.form.get("gpa", 3.0)),
            "last_meal_hours":    float(request.form.get("last_meal_hours", 4)),
        }

        survival_pct, scores = calculate_survival(inputs)
        status, color, emoji, message = get_verdict(survival_pct, inputs)

        result = {
            "name":         inputs["name"],
            "survival_pct": survival_pct,
            "status":       status,
            "color":        color,
            "emoji":        emoji,
            "message":      message,
            "scores":       scores,
            "inputs":       inputs,
        }

    return render_template("index.html", result=result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
