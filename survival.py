import os
import random


def clamp(val, lo, hi):
    return max(lo, min(hi, val))


def env_float(key, default):
    try:
        return float(os.getenv(key, str(default)))
    except ValueError:
        return default



def env_str(key, default):
    return os.getenv(key, default).strip()


def calculate_survival(inputs):
    scores = {}

    sleep = inputs["sleep_hours"]
    if sleep >= 8:    scores["sleep"] = 100
    elif sleep >= 7:  scores["sleep"] = 85
    elif sleep >= 6:  scores["sleep"] = 65
    elif sleep >= 5:  scores["sleep"] = 40
    elif sleep >= 4:  scores["sleep"] = 20
    else:             scores["sleep"] = max(0, sleep * 4)

    coffee = inputs["coffee_cups"]
    if coffee == 0:       scores["caffeine"] = 60
    elif coffee <= 2:     scores["caffeine"] = 100
    elif coffee <= 4:     scores["caffeine"] = 70
    elif coffee <= 6:     scores["caffeine"] = 35
    else:                 scores["caffeine"] = max(0, 100 - coffee * 10)

    pressure = inputs["assignments_due"] + (3 if inputs["exam_tomorrow"] else 0)
    if pressure == 0:    scores["pressure"] = 100
    elif pressure <= 2:  scores["pressure"] = 80
    elif pressure <= 4:  scores["pressure"] = 55
    elif pressure <= 6:  scores["pressure"] = 30
    else:                scores["pressure"] = max(0, 100 - pressure * 12)

    outside = inputs["days_since_outside"]
    if outside == 0:    scores["outside"] = 100
    elif outside == 1:  scores["outside"] = 80
    elif outside == 2:  scores["outside"] = 60
    elif outside <= 4:  scores["outside"] = 35
    else:               scores["outside"] = max(0, 100 - outside * 15)

    last_meal = inputs["last_meal_hours"]
    if last_meal <= 3:    scores["nutrition"] = 100
    elif last_meal <= 6:  scores["nutrition"] = 75
    elif last_meal <= 10: scores["nutrition"] = 40
    else:                 scores["nutrition"] = max(0, 100 - last_meal * 8)

    weights = {
        "sleep":     0.35,
        "caffeine":  0.20,
        "pressure":  0.25,
        "outside":   0.10,
        "nutrition": 0.10,
    }

    total = sum(scores[k] * weights[k] for k in scores)
    if inputs["exam_tomorrow"]:
        total *= 0.85

    return round(clamp(total, 1, 99), 1), scores


def get_verdict(pct, inputs):
    sleep  = inputs["sleep_hours"]
    coffee = inputs["coffee_cups"]

    if pct >= 85:
        status = "THRIVING"
        msgs = [
            "Somehow you have your life together. Suspicious.",
            "Are you actually a student or just cosplaying as one?",
            "You slept, you ate, you went outside. This is illegal.",
        ]
    elif pct >= 70:
        status = "STABLE"
        msgs = [
            "Not thriving, not dying. The student sweet spot.",
            "You're like a browser with 47 tabs. Functional. For now.",
            "Could use more sleep but honestly who couldn't.",
        ]
    elif pct >= 50:
        status = "AT RISK"
        msgs = [
            "Running on caffeine and sheer stubbornness.",
            "Your body is a temple. A haunted one.",
            "Sleep is not optional. This is a threat.",
        ]
    elif pct >= 30:
        status = "CRITICAL"
        msgs = [
            "You've had " + str(coffee) + " coffees today. Your heart is filing a formal complaint.",
            "You haven't been outside in " + str(inputs["days_since_outside"]) + " days. Plants need sunlight. So do you.",
            "Your survival rate is lower than your Wi-Fi at 2am.",
        ]
    else:
        status = "SEND HELP"
        msgs = [
            "Only " + str(pct) + "% survival. That is not a grade, that is a medical reading.",
            "You slept " + str(sleep) + "h and somehow opened this app. Respect.",
            "At this point you are not a student. You are a warning label.",
        ]

    return status, random.choice(msgs)


def main():
    inputs = {
        "name":               env_str  ("STUDENT_NAME",       "Student"),
        "coffee_cups":        env_float("COFFEE_CUPS",        0),
        "sleep_hours":        env_float("SLEEP_HOURS",        7),
        "assignments_due":    env_float("ASSIGNMENTS_DUE",    0),
        "exam_tomorrow":      env_str  ("EXAM_TOMORROW",      "no").lower() == "yes",
        "days_since_outside": env_float("DAYS_SINCE_OUTSIDE", 0),
        "last_meal_hours":    env_float("LAST_MEAL_HOURS",    4),
    }

    pct, scores  = calculate_survival(inputs)
    status, msg  = get_verdict(pct, inputs)

    filled   = round(pct / 100 * 40)
    bar      = "[" + "#" * filled + "-" * (40 - filled) + "] " + str(pct) + "%"
    exam_note = " + exam tomorrow!" if inputs["exam_tomorrow"] else ""
    sep      = "=" * 55
    sep2     = "-" * 55

    report = (
        "\n" + sep + "\n"
        "  STUDENT SURVIVAL CALCULATOR\n"
        "  Saskatchewan Polytechnic - Code Engine Lab\n"
        + sep + "\n"
        "\n"
        "  Student      : " + inputs["name"] + "\n"
        "  Status       : " + status + "\n"
        "\n"
        "  SURVIVAL RATE\n"
        "  " + sep2 + "\n"
        "  " + bar + "\n"
        "\n"
        '  "' + msg + '"\n'
        "\n"
        "  BREAKDOWN\n"
        "  " + sep2 + "\n"
        "  Sleep         : " + str(round(scores["sleep"]))    + "/100  (" + str(inputs["sleep_hours"])        + "h slept)\n"
        "  Caffeine      : " + str(round(scores["caffeine"])) + "/100  (" + str(inputs["coffee_cups"])        + " cups)\n"
        "  Academic Load : " + str(round(scores["pressure"])) + "/100  (" + str(inputs["assignments_due"])    + " assignments" + exam_note + ")\n"
        "  Touch Grass   : " + str(round(scores["outside"]))  + "/100  (" + str(inputs["days_since_outside"]) + " day(s) inside)\n"
        "  Nutrition     : " + str(round(scores["nutrition"]))+ "/100  (" + str(inputs["last_meal_hours"])    + "h since last meal)\n"
        "\n"
        "  " + sep2 + "\n"
        "  Disclaimer: This app is not responsible for failed exams,\n"
        "  caffeine overdoses, or existential crises. Drink water.\n"
        + sep + "\n"
    )

    print(report)


if __name__ == "__main__":
    main()
