"""Task model and data structures for TodoMaster."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class Priority(Enum):
    """Task priority levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class Task:
    """A task with description, priority, due date, and tags."""

    description: str
    priority: Priority = Priority.MEDIUM
    due_date: datetime | None = None
    completed: bool = False
    tags: list[str] = field(default_factory=list)
    id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    completed_at: datetime | None = None

    def __post_init__(self):
        """Initialize timestamps when task is created."""
        if self.created_at is None:
            self.created_at = datetime.now()  # noqa: DTZ005
            self.updated_at = datetime.now()  # noqa: DTZ005

    @property
    def is_overdue(self) -> bool:
        """Check if task is overdue."""
        if self.due_date is None or self.completed:
            return False
        return datetime.now() > self.due_date  # noqa: DTZ005

    @property
    def is_due_today(self) -> bool:
        """Check if task is due today."""
        if self.due_date is None:
            return False
        today = datetime.now().date()  # noqa: DTZ005
        return self.due_date.date() == today

    def mark_completed(self):
        """Mark task as completed."""
        self.completed = True
        self.completed_at = datetime.now()  # noqa: DTZ005
        self.updated_at = datetime.now()  # noqa: DTZ005

    def update_description(self, description: str):
        """Update task description."""
        self.description = description
        self.updated_at = datetime.now()  # noqa: DTZ005

    def update_priority(self, priority: Priority):
        """Update task priority."""
        self.priority = priority
        self.updated_at = datetime.now()  # noqa: DTZ005

    def update_due_date(self, due_date: datetime | None):
        """Update task due date."""
        self.due_date = due_date
        self.updated_at = datetime.now()  # noqa: DTZ005

    def add_tag(self, tag: str):
        """Add a tag to the task."""
        if tag not in self.tags:
            self.tags.append(tag)
            self.updated_at = datetime.now()  # noqa: DTZ005

    def remove_tag(self, tag: str):
        """Remove a tag from the task."""
        if tag in self.tags:
            self.tags.remove(tag)
            self.updated_at = datetime.now()  # noqa: DTZ005
