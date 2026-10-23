# Lab Phase 1 — Student Survival Calculator
IBM Cloud Code Engine

---

## What This Does

You fill in your real student-life variables as Code Engine environment
variables, run the job, and read your **Survival Rate %** and a personalised
verdict in the job logs.

No external services. No API keys. Pure Python — stdlib only.

---

## Variables

| Variable | What it means | Example |
|---|---|---|
| `STUDENT_NAME` | Your first name | `Engy` |
| `COFFEE_CUPS` | Cups of coffee today | `3` |
| `SLEEP_HOURS` | Hours of sleep last night | `5` |
| `ASSIGNMENTS_DUE` | Assignments due this week | `2` |
| `EXAM_TOMORROW` | Exam tomorrow? | `yes` or `no` |
| `DAYS_SINCE_OUTSIDE` | Days since you left your room | `1` |
| `ENERGY_DRINK_CANS` | Energy drinks today | `1` |
| `GPA` | Current GPA (out of 4.0) | `3.2` |
| `LAST_MEAL_HOURS` | Hours since your last real meal | `6` |

---

## Project Structure

```
student-survival-app/
├── survival.py        # Survival calculator
├── requirements.txt   # No dependencies (stdlib only)
├── Dockerfile         # Container definition
└── README.md          # This file
```

---

## Deployment Guide

### Step 1 — Push to GitHub

1. Create a new **public** repository on GitHub called `student-survival-app`
2. Push these three files to it:

```bash
git init
git add survival.py requirements.txt Dockerfile
git commit -m "Phase 1: Student Survival App"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/student-survival-app.git
git push -u origin main
```

---

### Step 2 — Log in to IBM Cloud

```bash
ibmcloud login --sso
```

Follow the browser prompt, paste the one-time code back into the terminal.

---

### Step 3 — Set Up IBM Container Registry

```bash
# Install the plugin if you haven't already
ibmcloud plugin install container-registry

# Point at the global registry
ibmcloud cr region-set global

# Create your namespace (pick a unique name)
ibmcloud cr namespace-add YOUR_NAMESPACE

# Log Docker in
ibmcloud cr login
```

---

### Step 4 — Build and Push the Docker Image

```bash
# Clone your repo (or just cd into the folder)
git clone https://github.com/YOUR_USERNAME/student-survival-app.git
cd student-survival-app

# Build
docker build -t icr.io/YOUR_NAMESPACE/student-survival:latest .

# Push
docker push icr.io/YOUR_NAMESPACE/student-survival:latest
```

---

### Step 5 — Select Your Code Engine Project

```bash
ibmcloud plugin install code-engine

# Select the project you created in Lab 1
ibmcloud ce project select --name my-first-ce-project
```

---

### Step 6 — Create the Job

```bash
ibmcloud ce job create \
  --name student-survival \
  --image icr.io/YOUR_NAMESPACE/student-survival:latest \
  --env STUDENT_NAME="Your Name" \
  --env COFFEE_CUPS=3 \
  --env SLEEP_HOURS=5 \
  --env ASSIGNMENTS_DUE=2 \
  --env EXAM_TOMORROW=yes \
  --env DAYS_SINCE_OUTSIDE=1 \
  --env ENERGY_DRINK_CANS=1 \
  --env GPA=3.1 \
  --env LAST_MEAL_HOURS=6
```

> Edit the values to match **your actual day** before running.

---

### Step 7 — Run It

```bash
ibmcloud ce jobrun submit --job student-survival --name survival-run-1
```

---

### Step 8 — Read Your Results

```bash
# Check the run completed
ibmcloud ce jobrun get --name survival-run-1

# Read your survival report
ibmcloud ce jobrun logs --instance survival-run-1-0-0
```

Or open the IBM Cloud console:
**Code Engine → Jobs → student-survival → survival-run-1 → Instances → Logs**

---

## Example Output

```
══════════════════════════════════════════════════════════
  🎓  STUDENT SURVIVAL CALCULATOR
  Saskatchewan Polytechnic — Code Engine Lab
══════════════════════════════════════════════════════════

  Student : Alex
  Status  : CRITICAL

  SURVIVAL RATE
  ──────────────────────────────────────────────────────────
  [░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░] 32.4%

  Alex, please sit down.
  "You've had 3 coffees and 1 energy drinks.
   Your heart is filing a formal complaint."

  BREAKDOWN
  ──────────────────────────────────────────────────────────
  😴  Sleep                ★★☆☆☆  (40/100)  ← 5h sleep
  ☕  Caffeine             ★★★☆☆  (50/100)  ← 3 coffee, 1 energy drinks
  📚  Academic Load        ★★☆☆☆  (30/100)  ← 2 assignments + exam tomorrow!
  🌿  Touch Grass          ★★★★☆  (80/100)  ← 1 day(s) indoors
  🍕  Nutrition            ★★★☆☆  (50/100)  ← 6h since last meal
  🎓  GPA Morale           ★★★★☆  (78/100)  ← GPA 3.1

  ──────────────────────────────────────────────────────────
  ⚠  Disclaimer: This app is not responsible for failed
     exams, caffeine overdoses, or existential crises.
     Please drink water.
══════════════════════════════════════════════════════════
```

---

## Re-run With Different Variables

To update your variables and run again:

```bash
# Update an env var on the existing job
ibmcloud ce job update \
  --name student-survival \
  --env SLEEP_HOURS=8 \
  --env COFFEE_CUPS=1 \
  --env EXAM_TOMORROW=no

# Submit a new run
ibmcloud ce jobrun submit --job student-survival --name survival-run-2

# Read new results
ibmcloud ce jobrun logs --instance survival-run-2-0-0
```

---

## Cleanup

```bash
ibmcloud ce job delete --name student-survival --force
ibmcloud ce jobrun delete --name survival-run-1 --force
ibmcloud cr image-rm icr.io/YOUR_NAMESPACE/student-survival:latest
```

---

## Up Next — Phase 2

In Phase 2 you will build a web page with sliders and dropdowns. When you
submit the form, it calls Code Engine and the page updates live with your
survival rate — no terminal required.

---

*Cloud Computing Lab Series*
