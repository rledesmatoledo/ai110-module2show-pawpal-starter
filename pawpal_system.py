"""PawPal+ system skeleton.

Generated from the UML class diagram. Data-holding classes use
dataclasses to keep the code clean; method bodies are left as stubs
(`raise NotImplementedError`) for implementation.
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


@dataclass
class Task:
    """A single pet-care task."""

    name: str
    duration: int          # minutes
    priority: Priority
    category: str
    recurs: Recurrence

    def is_recurring(self) -> bool:
        """Return True if this task repeats (daily or weekly)."""
        raise NotImplementedError


@dataclass
class Pet:
    """A pet owned by an Owner, with its own list of tasks."""

    name: str
    species: str
    breed: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        raise NotImplementedError

    def remove_task(self, task: Task) -> None:
        raise NotImplementedError

    def get_tasks(self) -> list[Task]:
        raise NotImplementedError


@dataclass
class Owner:
    """A pet owner with one or more pets."""

    name: str
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        raise NotImplementedError

    def remove_pet(self, pet: Pet) -> None:
        raise NotImplementedError

    def get_pets(self) -> list[Pet]:
        raise NotImplementedError


@dataclass
class DailyPlan:
    """The scheduler's output: an ordered set of tasks plus reasoning."""

    scheduled_tasks: list[Task]
    total_time: int          # minutes
    reasoning: str
    deferred_tasks: list[Task] = field(default_factory=list)


class Scheduler:
    """Builds a daily plan from a pet's tasks and available time."""

    def generate_plan(self, tasks: list[Task], available_time: int) -> DailyPlan:
        """Fit tasks into available_time (minutes) and return a DailyPlan."""
        raise NotImplementedError

    def prioritize_tasks(self, tasks: list[Task]) -> list[Task]:
        """Return tasks ordered by priority (and any other criteria)."""
        raise NotImplementedError
