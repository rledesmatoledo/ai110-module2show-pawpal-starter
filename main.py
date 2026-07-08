"""Testing ground for PawPal+.

Builds a small owner/pet/task setup and prints today's schedule so the
core logic in pawpal_system.py can be verified from the terminal.
"""

from pawpal_system import Owner, Pet, Task, Scheduler, Priority, Recurrence


def main() -> None:
    # Create an owner with two pets.
    owner = Owner("Alex")
    rex = Pet("Rex", "dog", "Labrador")
    milo = Pet("Milo", "cat", "Tabby")
    owner.add_pet(rex)
    owner.add_pet(milo)

    # Add tasks deliberately OUT OF TIME ORDER so we can prove that
    # sort_by_time() actually reorders them (the raw lists stay as-added).
    rex.add_task(Task("Evening walk", 30, Priority.HIGH, "exercise", Recurrence.DAILY, time="18:30"))
    rex.add_task(Task("Morning walk", 30, Priority.HIGH, "exercise", Recurrence.DAILY, time="07:00"))
    rex.add_task(Task("Vet checkup", 60, Priority.LOW, "health", Recurrence.NONE, time="14:15"))
    milo.add_task(Task("Brush coat", 15, Priority.MEDIUM, "grooming", Recurrence.WEEKLY, time="12:00"))
    milo.add_task(Task("Feed", 10, Priority.HIGH, "food", Recurrence.DAILY, time="08:00"))

    # Deliberate conflicts, all at 08:00, to exercise find_conflicts():
    #   - Same pet:      Milo's "Give pill" overlaps Milo's "Feed"
    #   - Different pets: Rex's "Sunbathe" overlaps both of Milo's 08:00 tasks
    milo.add_task(Task("Give pill", 5, Priority.HIGH, "health", Recurrence.DAILY, time="08:00"))
    rex.add_task(Task("Sunbathe", 20, Priority.LOW, "leisure", Recurrence.NONE, time="08:00"))

    # --- Recurrence demo: completing a DAILY task regenerates itself ------
    print("=" * 44)
    print("Recurrence: completing Rex's DAILY 'Morning walk'")
    print("=" * 44)

    morning_walk = rex.tasks[1]  # the DAILY task added above
    print(f"  Before: Rex has {len(rex.get_tasks())} tasks")
    print(f"          Morning walk due {morning_walk.due_date}, completed={morning_walk.completed}")

    # complete_task() marks it done AND adds the next occurrence back in.
    next_walk = rex.complete_task(morning_walk)

    print(f"  After:  Rex has {len(rex.get_tasks())} tasks")
    print(f"          Morning walk completed={morning_walk.completed}")
    if next_walk is not None:
        print(f"          New occurrence auto-added, due {next_walk.due_date} "
              f"(completed={next_walk.completed})")

    scheduler = Scheduler()

    # --- Conflict detection demo ------------------------------------------
    # Map each task object to its pet's name so the warning can say whether a
    # clash is within one pet's day or across two pets.
    task_owner = {id(t): pet.name for pet in owner.get_pets() for t in pet.get_tasks()}

    print("\n" + "=" * 44)
    print("Conflict detection: overlapping time windows")
    print("=" * 44)
    conflicts = scheduler.find_conflicts(owner.get_all_tasks())
    if not conflicts:
        print("  No conflicts found.")
    else:
        for first, second in conflicts:
            pet_a, pet_b = task_owner[id(first)], task_owner[id(second)]
            scope = "same pet" if pet_a == pet_b else "different pets"
            print(
                f"  WARNING ({scope}): {pet_a}'s '{first.name}' @ {first.time} "
                f"(+{first.duration}m) overlaps {pet_b}'s '{second.name}' @ "
                f"{second.time} (+{second.duration}m)"
            )

    # --- Sorting demo: every task, earliest start time first ---------------
    print("=" * 44)
    print(f"All tasks for {owner.name}, sorted by time")
    print("=" * 44)
    for task in scheduler.sort_by_time(owner.get_all_tasks()):
        status = "done" if task.completed else "todo"
        print(f"  {task.time}  {task.name:<14} ({task.priority.value}, {status})")

    # --- Filtering demo: by pet name --------------------------------------
    print("\n" + "=" * 44)
    print("Filter: only Rex's tasks (sorted by time)")
    print("=" * 44)
    for task in scheduler.sort_by_time(owner.filter_tasks(pet_name="Rex")):
        print(f"  {task.time}  {task.name}")

    # --- Filtering demo: by completion status -----------------------------
    print("\n" + "=" * 44)
    print("Filter: only unfinished tasks (sorted by time)")
    print("=" * 44)
    for task in scheduler.sort_by_time(owner.filter_tasks(completed=False)):
        print(f"  {task.time}  {task.name}")

    # --- Scheduler still works on the filtered, time-sorted list ----------
    available_time = 60  # minutes
    todo_tasks = owner.filter_tasks(completed=False)
    plan = scheduler.generate_plan(todo_tasks, available_time)

    print("\n" + "=" * 44)
    print(f"Today's Schedule for {owner.name}")
    print(f"(Available time: {available_time} minutes)")
    print("=" * 44)

    print("\nScheduled (in time order):")
    for task in scheduler.sort_by_time(plan.scheduled_tasks):
        print(f"  {task.time}  {task.name} ({task.duration} min, {task.priority.value})")

    if plan.deferred_tasks:
        print("\nDeferred (didn't fit):")
        for task in plan.deferred_tasks:
            print(f"  - {task.name} ({task.duration} min, {task.priority.value})")

    if plan.conflicts:
        print("\nWARNING - overlapping tasks in the plan:")
        for first, second in plan.conflicts:
            print(f"  - '{first.name}' @ {first.time} overlaps '{second.name}' @ {second.time}")

    print(f"\nTotal time used: {plan.total_time} / {available_time} minutes")
    print(f"Reasoning: {plan.reasoning}")


if __name__ == "__main__":
    main()
