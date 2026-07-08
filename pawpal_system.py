"""PawPal+ system.

Core implementation of the four main classes (Task, Pet, Owner, Scheduler)
plus the DailyPlan result object and the Priority/Recurrence enums.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from enum import Enum


class Priority(Enum):
    """Task priority level."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Recurrence(Enum):
    """How often a task repeats."""
    DAILY = "daily"
    WEEKLY = "weekly"
    NONE = "none"


# Ranking used to order tasks (higher number = scheduled first).
_PRIORITY_RANK = {
    Priority.HIGH: 3,
    Priority.MEDIUM: 2,
    Priority.LOW: 1,
}


@dataclass
class Task:
    """A single pet-care task."""

    name: str
    duration: int          # minutes
    priority: Priority
    category: str
    recurs: Recurrence
    time: str = "00:00"    # 24-hour "HH:MM" start time
    due_date: date = field(default_factory=date.today)
    completed: bool = False

    def is_recurring(self) -> bool:
        """Return True if this task repeats (daily or weekly)."""
        return self.recurs != Recurrence.NONE

    def mark_complete(self) -> Task | None:
        """Mark this task done; if it recurs, return the next occurrence.

        For a DAILY/WEEKLY task, returns a fresh (not-yet-completed) Task
        identical to this one but with due_date advanced by 1 or 7 days.
        For a NONE task, just marks it done and returns None.
        """
        self.completed = True

        if not self.is_recurring():
            return None

        step = timedelta(days=1) if self.recurs == Recurrence.DAILY else timedelta(days=7)
        return Task(
            name=self.name,
            duration=self.duration,
            priority=self.priority,
            category=self.category,
            recurs=self.recurs,
            time=self.time,
            due_date=self.due_date + step,
        )


@dataclass
class Pet:
    """A pet owned by an Owner, with its own list of tasks."""

    name: str
    species: str
    breed: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a task from this pet's task list if present."""
        if task in self.tasks:
            self.tasks.remove(task)

    def get_tasks(self) -> list[Task]:
        """Return this pet's list of tasks."""
        return self.tasks

    def complete_task(self, task: Task) -> Task | None:
        """Mark one of this pet's tasks complete, handling recurrence.

        Delegates to Task.mark_complete(). If the task recurs, the returned
        next occurrence is added straight back into this pet's task list so
        the schedule stays populated. Returns the new Task (or None).
        """
        next_occurrence = task.mark_complete()
        if next_occurrence is not None:
            self.add_task(next_occurrence)
        return next_occurrence


@dataclass
class Owner:
    """A pet owner with one or more pets."""

    name: str
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        """Remove a pet from this owner if present."""
        if pet in self.pets:
            self.pets.remove(pet)

    def get_pets(self) -> list[Pet]:
        """Return this owner's list of pets."""
        return self.pets

    def get_all_tasks(self) -> list[Task]:
        """Return every task across all of this owner's pets."""
        all_tasks: list[Task] = []
        for pet in self.pets:
            all_tasks.extend(pet.get_tasks())
        return all_tasks

    def filter_tasks(
        self,
        pet_name: str | None = None,
        completed: bool | None = None,
    ) -> list[Task]:
        """Return tasks filtered by pet name and/or completion status.

        Both filters are optional; leaving one as None means "don't filter
        on it". So filter_tasks(pet_name="Rex") returns all of Rex's tasks,
        and filter_tasks(completed=False) returns every unfinished task.
        """
        results: list[Task] = []
        for pet in self.pets:
            if pet_name is not None and pet.name != pet_name:
                continue
            for task in pet.get_tasks():
                if completed is not None and task.completed != completed:
                    continue
                results.append(task)
        return results


@dataclass
class DailyPlan:
    """The scheduler's output: an ordered set of tasks plus reasoning."""

    scheduled_tasks: list[Task]
    total_time: int          # minutes
    reasoning: str
    deferred_tasks: list[Task] = field(default_factory=list)
    conflicts: list[tuple[Task, Task]] = field(default_factory=list)


class Scheduler:
    """Builds a daily plan from a set of tasks and available time."""

    def generate_plan(self, tasks: list[Task], available_time: int) -> DailyPlan:
        """Fit tasks into available_time (minutes) and return a DailyPlan.

        Uses a simple greedy strategy: order tasks by priority, then add
        them one at a time while they fit. Tasks that don't fit are deferred.
        """
        ordered = self.prioritize_tasks(tasks)

        scheduled: list[Task] = []
        deferred: list[Task] = []
        used = 0

        for task in ordered:
            if used + task.duration <= available_time:
                scheduled.append(task)
                used += task.duration
            else:
                deferred.append(task)

        conflicts = self.find_conflicts(scheduled)

        reasoning = (
            f"Scheduled {len(scheduled)} of {len(tasks)} task(s) in priority "
            f"order, using {used} of {available_time} available minutes."
        )
        if deferred:
            reasoning += f" Deferred {len(deferred)} task(s) that did not fit."
        if conflicts:
            reasoning += f" Warning: {len(conflicts)} time conflict(s) detected."

        return DailyPlan(
            scheduled_tasks=scheduled,
            total_time=used,
            reasoning=reasoning,
            deferred_tasks=deferred,
            conflicts=conflicts,
        )

    def prioritize_tasks(self, tasks: list[Task]) -> list[Task]:
        """Return tasks ordered highest priority first (stable sort)."""
        return sorted(
            tasks,
            key=lambda task: _PRIORITY_RANK[task.priority],
            reverse=True,
        )

    @staticmethod
    def _to_minutes(hhmm: str) -> int:
        """Convert an 'HH:MM' string to minutes since midnight."""
        hours, minutes = hhmm.split(":")
        return int(hours) * 60 + int(minutes)

    def find_conflicts(self, tasks: list[Task]) -> list[tuple[Task, Task]]:
        """Return pairs of tasks whose same-day time windows overlap.

        Each task occupies [time, time + duration) on the same day. Tasks
        are sorted by start time, then swept once: for each task we only
        compare against later tasks until one starts at or after this task
        ends (the sort guarantees nothing beyond that can overlap). Works
        across pets, since it just looks at time windows. Returns an empty
        list when there are no conflicts -- it never raises.
        """
        ordered = sorted(tasks, key=lambda task: self._to_minutes(task.time))

        conflicts: list[tuple[Task, Task]] = []
        for i, task in enumerate(ordered):
            end_i = self._to_minutes(task.time) + task.duration
            for other in ordered[i + 1:]:
                if self._to_minutes(other.time) >= end_i:
                    break  # sorted by start: no later task can overlap this one
                conflicts.append((task, other))
        return conflicts

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        """Return tasks ordered by start time (earliest first).

        Each task's time is a zero-padded 24-hour "HH:MM" string. Because
        that format is fixed-width and zero-padded, comparing the strings
        directly already gives chronological order ("08:30" < "09:00" <
        "14:15"), so a lambda that returns task.time is all the key needs.
        """
        return sorted(tasks, key=lambda task: task.time)
