"""PawPal+ system.

Core implementation of the four main classes (Task, Pet, Owner, Scheduler)
plus the DailyPlan result object and the Priority/Recurrence enums.
"""

from __future__ import annotations

from dataclasses import dataclass, field
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
    completed: bool = False

    def is_recurring(self) -> bool:
        """Return True if this task repeats (daily or weekly)."""
        return self.recurs != Recurrence.NONE

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True


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


@dataclass
class DailyPlan:
    """The scheduler's output: an ordered set of tasks plus reasoning."""

    scheduled_tasks: list[Task]
    total_time: int          # minutes
    reasoning: str
    deferred_tasks: list[Task] = field(default_factory=list)


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

        reasoning = (
            f"Scheduled {len(scheduled)} of {len(tasks)} task(s) in priority "
            f"order, using {used} of {available_time} available minutes."
        )
        if deferred:
            reasoning += f" Deferred {len(deferred)} task(s) that did not fit."

        return DailyPlan(
            scheduled_tasks=scheduled,
            total_time=used,
            reasoning=reasoning,
            deferred_tasks=deferred,
        )

    def prioritize_tasks(self, tasks: list[Task]) -> list[Task]:
        """Return tasks ordered highest priority first (stable sort)."""
        return sorted(
            tasks,
            key=lambda task: _PRIORITY_RANK[task.priority],
            reverse=True,
        )
