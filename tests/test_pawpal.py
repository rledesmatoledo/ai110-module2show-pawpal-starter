"""Tests for the PawPal+ core classes and Scheduler logic."""

from datetime import date

from pawpal_system import (
    Owner,
    Pet,
    Task,
    Scheduler,
    Priority,
    Recurrence,
)


def make_task(
    name: str = "Walk",
    duration: int = 30,
    priority: Priority = Priority.HIGH,
    category: str = "exercise",
    recurs: Recurrence = Recurrence.DAILY,
    time: str = "09:00",
    due_date: date = date(2026, 1, 1),
) -> Task:
    """Build a Task with sensible defaults; override only what a test cares about."""
    return Task(name, duration, priority, category, recurs, time=time, due_date=due_date)


# --- Existing tests --------------------------------------------------------

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


# --- 1. Sorting correctness ------------------------------------------------

def test_sort_by_time_returns_chronological_order():
    """Tasks added out of order come back earliest-time-first."""
    scheduler = Scheduler()
    tasks = [
        make_task(name="Evening", time="18:30"),
        make_task(name="Morning", time="07:00"),
        make_task(name="Afternoon", time="14:15"),
    ]
    ordered = scheduler.sort_by_time(tasks)
    assert [t.name for t in ordered] == ["Morning", "Afternoon", "Evening"]


def test_sort_by_time_nonpadded_time_breaks_chronological_order():
    """Documents the zero-padding contract: sort_by_time compares "HH:MM"
    strings directly, so a non-padded "7:00" sorts AFTER "14:15" because
    the character "7" > "1". This asserts the current (string-based)
    behavior so the contract is explicit -- callers must zero-pad times.
    """
    scheduler = Scheduler()
    tasks = [
        make_task(name="Padded", time="14:15"),
        make_task(name="NonPadded", time="7:00"),
    ]
    ordered = scheduler.sort_by_time(tasks)
    # If times were parsed numerically, "7:00" would come first; with string
    # sorting it lands last. That's the limitation we're pinning down.
    assert [t.name for t in ordered] == ["Padded", "NonPadded"]


# --- 2. Filtering ----------------------------------------------------------

def _owner_with_two_pets() -> Owner:
    """Owner 'Alex' with Rex (2 tasks, one done) and Milo (1 task)."""
    owner = Owner("Alex")
    rex = Pet("Rex", "dog", "Labrador")
    milo = Pet("Milo", "cat", "Tabby")
    rex.add_task(make_task(name="Walk"))
    done = make_task(name="Vet")
    done.mark_complete()  # mark one of Rex's tasks complete
    rex.add_task(done)
    milo.add_task(make_task(name="Feed"))
    owner.add_pet(rex)
    owner.add_pet(milo)
    return owner


def test_filter_tasks_by_pet_name():
    """filter_tasks(pet_name=...) returns only that pet's tasks."""
    owner = _owner_with_two_pets()
    rex_tasks = owner.filter_tasks(pet_name="Rex")
    assert {t.name for t in rex_tasks} == {"Walk", "Vet"}
    assert all(t.name != "Feed" for t in rex_tasks)  # Milo's task excluded


def test_filter_tasks_by_completion_status():
    """filter_tasks(completed=False) hides finished tasks."""
    owner = _owner_with_two_pets()
    unfinished = owner.filter_tasks(completed=False)
    # The one Vet task was marked complete, so it should be excluded.
    assert all(t.completed is False for t in unfinished)
    assert "Vet" not in {t.name for t in unfinished}


def test_filter_tasks_unknown_pet_returns_empty_list():
    """A pet name that doesn't exist yields [] rather than crashing."""
    owner = _owner_with_two_pets()
    assert owner.filter_tasks(pet_name="Ghost") == []


def test_filter_tasks_owner_with_no_pets_returns_empty_list():
    """An owner with no pets filters to an empty list, not an error."""
    owner = Owner("Nobody")
    assert owner.filter_tasks() == []
    assert owner.filter_tasks(completed=False) == []


# --- 3. Recurrence logic ---------------------------------------------------

def test_completing_daily_task_creates_next_day_occurrence():
    """A DAILY task, when completed, returns a fresh task due one day later."""
    task = make_task(recurs=Recurrence.DAILY, due_date=date(2026, 1, 1))
    nxt = task.mark_complete()
    assert task.completed is True             # original is now done
    assert nxt is not None
    assert nxt.due_date == date(2026, 1, 2)   # +1 day
    assert nxt.completed is False             # the new occurrence starts fresh


def test_completing_weekly_task_creates_occurrence_seven_days_later():
    """A WEEKLY task advances the due date by 7 days."""
    task = make_task(recurs=Recurrence.WEEKLY, due_date=date(2026, 1, 1))
    nxt = task.mark_complete()
    assert nxt is not None
    assert nxt.due_date == date(2026, 1, 8)   # +7 days


def test_completing_non_recurring_task_returns_none():
    """A NONE task just marks done and returns None (no new occurrence)."""
    task = make_task(recurs=Recurrence.NONE)
    nxt = task.mark_complete()
    assert task.completed is True
    assert nxt is None


def test_pet_complete_task_readds_recurring_occurrence():
    """Pet.complete_task adds the regenerated task back into the pet's list."""
    pet = Pet("Rex", "dog", "Labrador")
    task = make_task(recurs=Recurrence.DAILY)
    pet.add_task(task)
    assert len(pet.get_tasks()) == 1
    nxt = pet.complete_task(task)
    # The next occurrence must actually re-enter the list, not be dropped.
    assert len(pet.get_tasks()) == 2
    assert nxt in pet.get_tasks()


def test_pet_complete_task_non_recurring_does_not_grow_list():
    """Completing a NONE task leaves the task count unchanged."""
    pet = Pet("Rex", "dog", "Labrador")
    task = make_task(recurs=Recurrence.NONE)
    pet.add_task(task)
    nxt = pet.complete_task(task)
    assert nxt is None
    assert len(pet.get_tasks()) == 1


# --- 4. Conflict detection -------------------------------------------------

def test_overlapping_tasks_are_flagged():
    """Two tasks whose windows overlap produce exactly one conflict pair."""
    scheduler = Scheduler()
    a = make_task(name="A", time="08:00", duration=30)  # 08:00-08:30
    b = make_task(name="B", time="08:15", duration=30)  # 08:15-08:45 (overlaps)
    conflicts = scheduler.find_conflicts([a, b])
    assert len(conflicts) == 1


def test_back_to_back_tasks_are_not_flagged():
    """Touching windows must NOT conflict: this pins the half-open [) boundary
    (using `<`, not `<=`). Task A ends exactly when Task B starts.
    """
    scheduler = Scheduler()
    a = make_task(name="A", time="08:00", duration=10)  # 08:00-08:10
    b = make_task(name="B", time="08:10", duration=10)  # 08:10-08:20
    assert scheduler.find_conflicts([a, b]) == []


def test_same_time_tasks_are_flagged():
    """Two tasks starting at the exact same time overlap and are flagged."""
    scheduler = Scheduler()
    a = make_task(name="A", time="08:00", duration=15)
    b = make_task(name="B", time="08:00", duration=5)
    assert len(scheduler.find_conflicts([a, b])) == 1


def test_no_conflicts_for_empty_or_single_task():
    """Empty and single-task lists have nothing to conflict with."""
    scheduler = Scheduler()
    assert scheduler.find_conflicts([]) == []
    assert scheduler.find_conflicts([make_task(time="08:00")]) == []


def test_cross_day_same_time_is_flagged_known_limitation():
    """KNOWN LIMITATION (documented tradeoff, not a bug): find_conflicts only
    compares time-of-day and ignores due_date, so two tasks at the same time
    on different days are still reported as conflicting. This asserts the
    current behavior on purpose; if we later group by due_date, flip this to
    expect zero conflicts.
    """
    scheduler = Scheduler()
    today = make_task(name="Today", time="08:00", duration=30, due_date=date(2026, 1, 1))
    tomorrow = make_task(name="Tomorrow", time="08:00", duration=30, due_date=date(2026, 1, 2))
    assert len(scheduler.find_conflicts([today, tomorrow])) == 1


# --- 5. Scheduler fitting / deferring --------------------------------------

def test_scheduler_schedules_tasks_that_fit():
    """Tasks whose durations fit within the available time are scheduled."""
    scheduler = Scheduler()
    tasks = [
        make_task(name="A", duration=20, priority=Priority.HIGH),
        make_task(name="B", duration=15, priority=Priority.MEDIUM),
    ]
    plan = scheduler.generate_plan(tasks, available_time=60)
    assert {t.name for t in plan.scheduled_tasks} == {"A", "B"}
    assert plan.deferred_tasks == []
    assert plan.total_time == 35


def test_scheduler_defers_task_that_is_too_large():
    """A task longer than the whole budget is deferred, not scheduled."""
    scheduler = Scheduler()
    small = make_task(name="Small", duration=20, priority=Priority.HIGH)
    huge = make_task(name="Huge", duration=90, priority=Priority.LOW)
    plan = scheduler.generate_plan([small, huge], available_time=60)
    assert "Small" in {t.name for t in plan.scheduled_tasks}
    assert "Huge" in {t.name for t in plan.deferred_tasks}


def test_scheduler_empty_task_list_does_not_crash():
    """An empty task list returns an empty plan with zero time used."""
    scheduler = Scheduler()
    plan = scheduler.generate_plan([], available_time=60)
    assert plan.scheduled_tasks == []
    assert plan.deferred_tasks == []
    assert plan.total_time == 0


def test_scheduler_zero_available_time_defers_everything():
    """With zero minutes available, every task is deferred (no crash)."""
    scheduler = Scheduler()
    tasks = [make_task(name="A", duration=10), make_task(name="B", duration=5)]
    plan = scheduler.generate_plan(tasks, available_time=0)
    assert plan.scheduled_tasks == []
    assert len(plan.deferred_tasks) == 2
    assert plan.total_time == 0
