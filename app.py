from datetime import time

import streamlit as st

from pawpal_system import Owner, Pet, Task, Scheduler, Priority, Recurrence

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")


# --- Small display helpers -------------------------------------------------
def _to_minutes(hhmm: str) -> int:
    """Convert an 'HH:MM' string to minutes since midnight."""
    hours, minutes = hhmm.split(":")
    return int(hours) * 60 + int(minutes)


def _to_hhmm(minutes: int) -> str:
    """Convert minutes since midnight back to a zero-padded 'HH:MM' string."""
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


def _overlap_window(first: Task, second: Task) -> str:
    """Return the 'HH:MM–HH:MM' window where two tasks overlap in time."""
    start = max(_to_minutes(first.time), _to_minutes(second.time))
    end = min(
        _to_minutes(first.time) + first.duration,
        _to_minutes(second.time) + second.duration,
    )
    return f"{_to_hhmm(start)}–{_to_hhmm(end)}"


# Streamlit reruns this script top-to-bottom on every interaction. Store the
# Owner in st.session_state so it (and its pets/tasks) persists across reruns
# instead of being recreated empty each time.
if "owner" not in st.session_state:
    st.session_state.owner = Owner("Jordan")

owner = st.session_state.owner

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Owner")
owner_name = st.text_input("Owner name", value=owner.name)
owner.name = owner_name  # keep the persisted Owner in sync with the input

st.divider()

# --- Add a Pet -------------------------------------------------------------
st.subheader("Pets")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])
breed = st.text_input("Breed", value="")

if st.button("Add pet"):
    if pet_name in [p.name for p in owner.get_pets()]:
        st.warning(f"{pet_name} is already added.")
    else:
        owner.add_pet(Pet(pet_name, species, breed))  # Phase 2: Owner.add_pet
        st.success(f"Added {pet_name}.")

pets = owner.get_pets()
if pets:
    st.write("Current pets: " + ", ".join(p.name for p in pets))
else:
    st.info("No pets yet. Add one above.")

st.divider()

# --- Add a Task to a Pet ---------------------------------------------------
st.subheader("Tasks")
if not pets:
    st.info("Add a pet first, then you can give it tasks.")
else:
    target_pet_name = st.selectbox("Add task to which pet?", [p.name for p in pets])
    target_pet = next(p for p in pets if p.name == target_pet_name)

    col1, col2, col3 = st.columns(3)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col3:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

    col4, col5, col6 = st.columns(3)
    with col4:
        category = st.text_input("Category", value="general")
    with col5:
        recurs = st.selectbox("Recurs", ["none", "daily", "weekly"])
    with col6:
        # st.time_input returns a datetime.time; formatting it guarantees a
        # zero-padded "HH:MM" string, which is what sort_by_time expects.
        start_time = st.time_input("Start time", value=time(9, 0))

    if st.button("Add task"):
        task = Task(
            task_title,
            int(duration),
            Priority(priority),
            category,
            Recurrence(recurs),
            time=start_time.strftime("%H:%M"),
        )
        target_pet.add_task(task)  # Phase 2: Pet.add_task
        st.success(f"Added '{task_title}' to {target_pet.name}.")

    # Show each pet's current tasks, sorted by start time (not add order).
    scheduler = Scheduler()
    for pet in pets:
        pet_tasks = scheduler.sort_by_time(pet.get_tasks())  # Phase 4: Scheduler.sort_by_time
        if pet_tasks:
            st.write(f"**{pet.name}'s tasks:**")
            st.table(
                [
                    {
                        "time": t.time,
                        "title": t.name,
                        "duration (min)": t.duration,
                        "priority": t.priority.value,
                        "recurs": t.recurs.value,
                    }
                    for t in pet_tasks
                ]
            )

st.divider()

# --- Build the Schedule ----------------------------------------------------
st.subheader("Build Schedule")
available_time = st.number_input(
    "Available time today (minutes)", min_value=1, max_value=1440, value=60
)

if st.button("Generate schedule"):
    all_tasks = owner.get_all_tasks()  # Phase 2: Owner.get_all_tasks
    if not all_tasks:
        st.warning("No tasks yet. Add a pet and some tasks first.")
    else:
        plan = Scheduler().generate_plan(all_tasks, int(available_time))  # Phase 2

        st.markdown("### Today's Schedule")
        if plan.scheduled_tasks:
            st.table(
                [
                    {
                        "title": t.name,
                        "duration (min)": t.duration,
                        "priority": t.priority.value,
                    }
                    for t in plan.scheduled_tasks
                ]
            )
        st.write(f"**Total time used:** {plan.total_time} / {int(available_time)} minutes")

        if plan.deferred_tasks:
            st.markdown("#### Deferred (didn't fit)")
            st.table(
                [
                    {"title": t.name, "duration (min)": t.duration, "priority": t.priority.value}
                    for t in plan.deferred_tasks
                ]
            )

        # --- Conflict warnings (Phase 4: DailyPlan.conflicts) --------------
        st.markdown("#### Time Conflicts")
        if plan.conflicts:
            # Map each task object to its pet's name so we can tell the owner
            # exactly who is affected (same pet, or a clash across two pets).
            task_pet = {id(t): p.name for p in owner.get_pets() for t in p.get_tasks()}
            for first, second in plan.conflicts:
                pet_a = task_pet.get(id(first), "?")
                pet_b = task_pet.get(id(second), "?")
                whose = pet_a if pet_a == pet_b else f"{pet_a} & {pet_b}"
                st.warning(
                    f"⚠️ Conflict ({whose}): "
                    f"**{first.name}** ({pet_a} @ {first.time}) overlaps "
                    f"**{second.name}** ({pet_b} @ {second.time}) "
                    f"— both busy {_overlap_window(first, second)}. "
                    f"Reschedule one to resolve."
                )
        else:
            st.success("✅ No time conflicts — this schedule is conflict-free.")

        st.info(plan.reasoning)
