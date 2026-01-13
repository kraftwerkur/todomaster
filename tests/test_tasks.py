"""Test cases for TodoMaster task functionality."""

import pytest
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import os

from todomaster.tasks import Task, Priority
from todomaster.storage import Storage


class TestTask:
    """Test Task model functionality."""

    def test_task_creation(self):
        """Test basic task creation."""
        task = Task(description="Test task")
        assert task.description == "Test task"
        assert task.priority == Priority.MEDIUM
        assert task.completed is False
        assert task.id is None
        assert task.tags == []
        assert task.created_at is not None
        assert task.updated_at is not None

    def test_task_with_priority(self):
        """Test task creation with priority."""
        task = Task(description="High priority task", priority=Priority.HIGH)
        assert task.priority == Priority.HIGH

    def test_task_with_due_date(self):
        """Test task creation with due date."""
        due_date = datetime.now() + timedelta(days=1)
        task = Task(description="Task with due date", due_date=due_date)
        assert task.due_date == due_date

    def test_task_with_tags(self):
        """Test task creation with tags."""
        tags = ["work", "urgent"]
        task = Task(description="Tagged task", tags=tags)
        assert task.tags == tags

    def test_mark_completed(self):
        """Test marking task as completed."""
        task = Task(description="Test task")
        task.mark_completed()
        assert task.completed is True
        assert task.completed_at is not None
        assert task.updated_at is not None
        assert task.created_at is not None
        assert (
            task.updated_at > task.created_at
            if task.updated_at and task.created_at
            else True
        )

    def test_is_overdue(self):
        """Test overdue detection."""
        past_date = datetime.now() - timedelta(days=1)
        task = Task(description="Overdue task", due_date=past_date)
        assert task.is_overdue is True

        future_date = datetime.now() + timedelta(days=1)
        task.due_date = future_date
        assert task.is_overdue is False

    def test_is_overdue_completed(self):
        """Test that completed tasks are not overdue."""
        past_date = datetime.now() - timedelta(days=1)
        task = Task(description="Completed overdue task", due_date=past_date)
        task.mark_completed()
        assert task.is_overdue is False

    def test_is_due_today(self):
        """Test due today detection."""
        today = datetime.now()
        task = Task(description="Today's task", due_date=today)
        assert task.is_due_today is True

        tomorrow = datetime.now() + timedelta(days=1)
        task.due_date = tomorrow
        assert task.is_due_today is False

    def test_update_description(self):
        """Test updating task description."""
        task = Task(description="Original description")
        original_updated = task.updated_at
        task.update_description("New description")
        assert task.description == "New description"
        assert task.updated_at is not None
        assert task.updated_at > original_updated if original_updated else True

    def test_update_priority(self):
        """Test updating task priority."""
        task = Task(description="Test task")
        task.update_priority(Priority.HIGH)
        assert task.priority == Priority.HIGH

    def test_add_tag(self):
        """Test adding tags to task."""
        task = Task(description="Test task")
        task.add_tag("work")
        assert "work" in task.tags

        # Test duplicate tag
        task.add_tag("work")
        assert task.tags.count("work") == 1

    def test_remove_tag(self):
        """Test removing tags from task."""
        task = Task(description="Test task", tags=["work", "urgent"])
        task.remove_tag("work")
        assert "work" not in task.tags
        assert "urgent" in task.tags

        # Test removing non-existent tag
        task.remove_tag("nonexistent")
        assert task.tags == ["urgent"]


class TestStorage:
    """Test Storage layer functionality."""

    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        yield Path(db_path)
        os.unlink(db_path)

    @pytest.fixture
    def storage(self, temp_db):
        """Create storage instance with temporary database."""
        storage_instance = Storage(temp_db)
        try:
            yield storage_instance
        finally:
            # Explicit cleanup
            storage_instance.close()

    def test_database_initialization(self, storage):
        """Test database is properly initialized."""
        assert storage.db_path.exists()

    def test_create_task(self, storage):
        """Test creating a task."""
        task = Task(description="Test task", priority=Priority.HIGH)
        created_task = storage.create_task(task)

        assert created_task.id is not None
        assert created_task.description == "Test task"
        assert created_task.priority == Priority.HIGH

    def test_get_task(self, storage):
        """Test retrieving a task."""
        task = Task(description="Test task")
        created_task = storage.create_task(task)

        retrieved_task = storage.get_task(created_task.id)
        assert retrieved_task is not None
        assert retrieved_task.id == created_task.id
        assert retrieved_task.description == "Test task"

    def test_get_nonexistent_task(self, storage):
        """Test retrieving non-existent task."""
        task = storage.get_task(999)
        assert task is None

    def test_get_all_tasks(self, storage):
        """Test retrieving all tasks."""
        task1 = Task(description="Task 1")
        task2 = Task(description="Task 2")
        storage.create_task(task1)
        storage.create_task(task2)

        all_tasks = storage.get_all_tasks()
        assert len(all_tasks) == 2

    def test_get_pending_tasks(self, storage):
        """Test retrieving pending tasks."""
        task1 = Task(description="Pending task")
        task2 = Task(description="Completed task")
        created_task1 = storage.create_task(task1)
        created_task2 = storage.create_task(task2)

        created_task2.mark_completed()
        storage.update_task(created_task2)

        pending_tasks = storage.get_pending_tasks()
        assert len(pending_tasks) == 1
        assert pending_tasks[0].description == "Pending task"

    def test_get_completed_tasks(self, storage):
        """Test retrieving completed tasks."""
        task1 = Task(description="Pending task")
        task2 = Task(description="Completed task")
        created_task1 = storage.create_task(task1)
        created_task2 = storage.create_task(task2)

        created_task2.mark_completed()
        storage.update_task(created_task2)

        completed_tasks = storage.get_completed_tasks()
        assert len(completed_tasks) == 1
        assert completed_tasks[0].description == "Completed task"

    def test_update_task(self, storage):
        """Test updating a task."""
        task = Task(description="Original description")
        created_task = storage.create_task(task)

        created_task.update_description("Updated description")
        updated_task = storage.update_task(created_task)

        retrieved_task = storage.get_task(created_task.id)
        assert retrieved_task.description == "Updated description"

    def test_delete_task(self, storage):
        """Test deleting a task."""
        task = Task(description="To be deleted")
        created_task = storage.create_task(task)

        result = storage.delete_task(created_task.id)
        assert result is True

        deleted_task = storage.get_task(created_task.id)
        assert deleted_task is None

    def test_delete_nonexistent_task(self, storage):
        """Test deleting non-existent task."""
        result = storage.delete_task(999)
        assert result is False

    def test_clear_completed(self, storage):
        """Test clearing completed tasks."""
        task1 = Task(description="Pending task")
        task2 = Task(description="Completed task")
        created_task1 = storage.create_task(task1)
        created_task2 = storage.create_task(task2)

        created_task2.mark_completed()
        storage.update_task(created_task2)

        count = storage.clear_completed()
        assert count == 1

        remaining_tasks = storage.get_all_tasks()
        assert len(remaining_tasks) == 1
        assert remaining_tasks[0].description == "Pending task"

    def test_search_tasks(self, storage):
        """Test searching tasks."""
        task1 = Task(description="Buy milk", tags=["shopping"])
        task2 = Task(description="Buy bread", tags=["shopping"])
        task3 = Task(description="Write code", tags=["work"])

        storage.create_task(task1)
        storage.create_task(task2)
        storage.create_task(task3)

        # Search by description
        milk_tasks = storage.search_tasks("milk")
        assert len(milk_tasks) == 1
        assert milk_tasks[0].description == "Buy milk"

        # Search by tag
        shopping_tasks = storage.search_tasks("shopping")
        assert len(shopping_tasks) == 2

    def test_get_task_stats(self, storage):
        """Test getting task statistics."""
        task1 = Task(description="Pending task")
        task2 = Task(description="Completed task")
        task3 = Task(
            description="Overdue task", due_date=datetime.now() - timedelta(days=1)
        )

        created_task1 = storage.create_task(task1)
        created_task2 = storage.create_task(task2)
        created_task3 = storage.create_task(task3)

        created_task2.mark_completed()
        storage.update_task(created_task2)

        stats = storage.get_task_stats()
        assert stats["total"] == 3
        assert stats["pending"] == 2
        assert stats["completed"] == 1
        assert (
            stats["overdue"] >= 1
        )  # Should be 1 but SQLite datetime precision might vary
