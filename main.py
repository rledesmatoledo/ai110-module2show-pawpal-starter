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

    # Add tasks with different durations and priorities.
    rex.add_task(Task("Morning walk", 30, Priority.HIGH, "exercise", Recurrence.DAILY))
    rex.add_task(Task("Vet checkup", 60, Priority.LOW, "health", Recurrence.NONE))
    milo.add_task(Task("Feed", 10, Priority.HIGH, "food", Recurrence.DAILY))
    milo.add_task(Task("Brush coat", 15, Priority.MEDIUM, "grooming", Recurrence.WEEKLY))

    # Gather every task across the owner's pets and build a plan.
    available_time = 60  # minutes
    all_tasks = owner.get_all_tasks()
    plan = Scheduler().generate_plan(all_tasks, available_time)

    # Print today's schedule.
    print("=" * 40)
    print(f"Today's Schedule for {owner.name}")
    print(f"(Available time: {available_time} minutes)")
    print("=" * 40)

    print("\nScheduled:")
    for task in plan.scheduled_tasks:
        print(f"  - {task.name} ({task.duration} min, {task.priority.value})")

    if plan.deferred_tasks:
        print("\nDeferred (didn't fit):")
        for task in plan.deferred_tasks:
            print(f"  - {task.name} ({task.duration} min, {task.priority.value})")

    print(f"\nTotal time used: {plan.total_time} / {available_time} minutes")
    print(f"Reasoning: {plan.reasoning}")


if __name__ == "__main__":
    main()
