"""Basic tests for the PawPal+ core classes."""

from pawpal_system import Pet, Task, Priority, Recurrence


def make_task() -> Task:
    return Task("Walk", 30, Priority.HIGH, "exercise", Recurrence.DAILY)


def test_mark_complete_changes_status():
    """Calling mark_complete() flips the task from not-done to done."""
    task = make_task()
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_adding_task_increases_pet_task_count():
    """Adding a task to a Pet increases its task count by one."""
    pet = Pet("Rex", "dog", "Labrador")
    assert len(pet.get_tasks()) == 0
    pet.add_task(make_task())
    assert len(pet.get_tasks()) == 1
