# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
# e.g.:
# Daily plan for Biscuit (Golden Retriever):
#   08:00 — Morning walk (30 min) [priority: high]
#   09:00 — Feeding (10 min) [priority: high]
#   ...
```

## 🧪 Testing PawPal+
The suite covers 22 tests across five behaviors: sorting tasks by time, filtering by pet and status, recurring task regeneration, conflict detection, and scheduling logic that fits or defers tasks based on available time.

python3 -m pytest
========================================================================================= test session starts =========================================================================================
platform darwin -- Python 3.9.6, pytest-8.4.2, pluggy-1.6.0
rootdir: /Users/robertoledesma/ai110-module2show-pawpal-starter
collected 22 items                                                                                                                                                                                    

tests/test_pawpal.py ......................                                                                                                                                                     [100%]

========================================================================================= 22 passed in 0.02s ==========================================================================================
Confidence level 4/5 stars 
## ✨ Features

- **Sort by time** — puts a pet's tasks in order from earliest to latest (`Scheduler.sort_by_time`).
- **Filter tasks** — show just one pet's tasks, or just the ones that aren't done yet (`Owner.filter_tasks`).
- **Daily & weekly recurrence** — finish a recurring task and the next one is created automatically, a day or a week later (`Task.mark_complete`, `Pet.complete_task`).
- **Conflict warnings** — flags two tasks whose times overlap, for the same pet or across pets (`Scheduler.find_conflicts`).
- **Daily plan** — fits the most important tasks into the time you have, defers the rest, and explains the result (`Scheduler.generate_plan`).

One thing to know: conflict warnings only look at the time of day, not the date, so a daily task and tomorrow's copy at the same time can show a harmless conflict (see `reflection.md`, 2b).

## 🎬 Demo Walkthrough

Run the app with `streamlit run app.py`. You can set the owner's name, add pets, give each pet tasks (title, duration, priority, recurrence, and a start time), and then build a daily schedule from the time you have available.

A typical run looks like this:

1. Add a pet — say coco the bully.
2. Add a couple of tasks, like a 07:00 walk and a 14:15 vet visit.
3. Enter how many minutes you have today and generate the schedule.
4. See what fit, what got deferred, and any conflict warnings.

Along the way the scheduler sorts tasks by time, filters them by pet or status, regenerates recurring tasks when you complete them, and warns you when two tasks overlap.

### Sample CLI output

`main.py` runs the same logic in the terminal. `python3 main.py` prints:

```text
============================================
Conflict detection: overlapping time windows
============================================
  WARNING (same pet): Milo's 'Feed' @ 08:00 (+10m) overlaps Milo's 'Give pill' @ 08:00 (+5m)
  WARNING (different pets): Coco's 'Sunbathe' @ 08:00 (+20m) overlaps Milo's 'Feed' @ 08:00 (+10m)

============================================
Today's Schedule for Alex
(Available time: 60 minutes)
============================================

Scheduled (in time order):
  07:00  Morning walk (30 min, high)
  18:30  Evening walk (30 min, high)

Deferred (didn't fit):
  - Feed (10 min, high)
  - Vet checkup (60 min, low)

Total time used: 60 / 60 minutes
Reasoning: Scheduled 2 of 7 task(s) in priority order, using 60 of 60 available minutes. Deferred 5 task(s) that did not fit.
```
