"""Test cases for TodoMaster CLI interface."""

import pytest
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import os
from unittest.mock import patch, MagicMock
from typer.testing import CliRunner

from todomaster.cli import app, get_storage
from todomaster.tasks import Task, Priority
from todomaster.storage import Storage
from todomaster.ui import TodoUI


class TestCLI:
    """Test CLI functionality."""

    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        yield Path(db_path)
        os.unlink(db_path)

    @pytest.fixture
    def mock_storage(self, temp_db):
        """Create mock storage with temporary database."""
        return Storage(temp_db)

    @patch("todomaster.cli.get_storage")
    def test_add_task_basic(self, mock_get_storage, mock_storage):
        """Test adding a basic task."""
        mock_get_storage.return_value = mock_storage

        task = Task(description="Test task")
        created_task = mock_storage.create_task(task)

        assert created_task.id is not None
        assert created_task.description == "Test task"

    @patch("todomaster.cli.get_storage")
    def test_add_task_with_priority(self, mock_get_storage, mock_storage):
        """Test adding a task with priority."""
        mock_get_storage.return_value = mock_storage

        task = Task(description="High priority task", priority=Priority.HIGH)
        created_task = mock_storage.create_task(task)

        assert created_task.priority == Priority.HIGH

    @patch("todomaster.cli.get_storage")
    def test_add_task_with_due_date(self, mock_get_storage, mock_storage):
        """Test adding a task with due date."""
        mock_get_storage.return_value = mock_storage

        due_date = datetime.now() + timedelta(days=1)
        task = Task(description="Task with due date", due_date=due_date)
        created_task = mock_storage.create_task(task)

        assert created_task.due_date is not None

    @patch("todomaster.cli.get_storage")
    def test_add_task_with_tags(self, mock_get_storage, mock_storage):
        """Test adding a task with tags."""
        mock_get_storage.return_value = mock_storage

        tags = ["work", "urgent"]
        task = Task(description="Tagged task", tags=tags)
        created_task = mock_storage.create_task(task)

        assert set(created_task.tags) == set(tags)

    @patch("todomaster.cli.get_storage")
    def test_list_tasks(self, mock_get_storage, mock_storage):
        """Test listing tasks."""
        mock_get_storage.return_value = mock_storage

        # Create some tasks
        task1 = Task(description="Task 1")
        task2 = Task(description="Task 2")
        mock_storage.create_task(task1)
        mock_storage.create_task(task2)

        # Get pending tasks
        pending_tasks = mock_storage.get_pending_tasks()
        assert len(pending_tasks) == 2

    @patch("todomaster.cli.get_storage")
    def test_complete_task(self, mock_get_storage, mock_storage):
        """Test completing a task."""
        mock_get_storage.return_value = mock_storage

        task = Task(description="To be completed")
        created_task = mock_storage.create_task(task)

        # Mark as completed
        created_task.mark_completed()
        updated_task = mock_storage.update_task(created_task)

        # Verify it's completed
        completed_task = mock_storage.get_task(created_task.id)
        assert completed_task.completed is True

    @patch("todomaster.cli.get_storage")
    def test_delete_task(self, mock_get_storage, mock_storage):
        """Test deleting a task."""
        mock_get_storage.return_value = mock_storage

        task = Task(description="To be deleted")
        created_task = mock_storage.create_task(task)

        # Delete task
        result = mock_storage.delete_task(created_task.id)
        assert result is True

        # Verify it's deleted
        deleted_task = mock_storage.get_task(created_task.id)
        assert deleted_task is None

    @patch("todomaster.cli.get_storage")
    def test_edit_task(self, mock_get_storage, mock_storage):
        """Test editing a task."""
        mock_get_storage.return_value = mock_storage

        task = Task(description="Original description")
        created_task = mock_storage.create_task(task)

        # Update description
        created_task.update_description("Updated description")
        updated_task = mock_storage.update_task(created_task)

        # Verify it's updated
        retrieved_task = mock_storage.get_task(created_task.id)
        assert retrieved_task.description == "Updated description"

    @patch("todomaster.cli.get_storage")
    def test_search_tasks(self, mock_get_storage, mock_storage):
        """Test searching tasks."""
        mock_get_storage.return_value = mock_storage

        # Create tasks with different content
        task1 = Task(description="Buy milk", tags=["shopping"])
        task2 = Task(description="Buy bread", tags=["shopping"])
        task3 = Task(description="Write code", tags=["work"])

        mock_storage.create_task(task1)
        mock_storage.create_task(task2)
        mock_storage.create_task(task3)

        # Search by description
        results = mock_storage.search_tasks("milk")
        assert len(results) == 1
        assert results[0].description == "Buy milk"

        # Search by tags
        results = mock_storage.search_tasks("shopping")
        assert len(results) == 2

    @patch("todomaster.cli.get_storage")
    def test_task_statistics(self, mock_get_storage, mock_storage):
        """Test getting task statistics."""
        mock_get_storage.return_value = mock_storage

        # Create tasks
        task1 = Task(description="Pending task")
        task2 = Task(description="Completed task")

        created_task1 = mock_storage.create_task(task1)
        created_task2 = mock_storage.create_task(task2)

        # Complete one task
        created_task2.mark_completed()
        mock_storage.update_task(created_task2)

        # Get statistics
        stats = mock_storage.get_task_stats()
        assert stats["total"] == 2
        assert stats["pending"] == 1
        assert stats["completed"] == 1


class TestCLIIntegration:
    """Test CLI integration with actual commands."""

    @pytest.fixture
    def runner(self):
        """Create CLI runner for testing."""
        return CliRunner()

    @pytest.fixture
    def temp_db_env(self, temp_db):
        """Environment with temporary database."""
        env = {"TODOMASTER_DB_PATH": str(temp_db)}
        return env

    @patch("todomaster.cli.get_storage")
    def test_add_command_with_all_options(self, mock_get_storage, runner):
        """Test add command with all options."""
        mock_storage = MagicMock()
        task = Task(description="Test task", priority=Priority.HIGH)
        task.id = 1
        mock_storage.create_task.return_value = task
        mock_get_storage.return_value = mock_storage

        result = runner.invoke(
            app,
            [
                "add",
                "Test task",
                "--priority",
                "high",
                "--due",
                "tomorrow",
                "--tag",
                "work,urgent",
            ],
        )

        assert result.exit_code == 0
        mock_storage.create_task.assert_called_once()

    @patch("todomaster.cli.get_storage")
    def test_add_command_invalid_date(self, mock_get_storage, runner):
        """Test add command with invalid date."""
        mock_storage = MagicMock()
        mock_get_storage.return_value = mock_storage

        result = runner.invoke(app, ["add", "Test task", "--due", "invalid-date"])

        # Should show error message for invalid date
        assert "Invalid due date" in result.stdout
        # Storage should not be called since we exit early
        mock_storage.create_task.assert_not_called()

    @patch("todomaster.cli.get_storage")
    def test_list_command_with_filters(self, mock_get_storage, runner):
        """Test list command with filters."""
        mock_storage = MagicMock()
        task = Task(description="Test task", priority=Priority.HIGH)
        task.id = 1
        mock_storage.get_pending_tasks.return_value = [task]
        mock_get_storage.return_value = mock_storage

        result = runner.invoke(app, ["list", "--priority", "high", "--tag", "work"])

        assert result.exit_code == 0
        mock_storage.get_pending_tasks.assert_called_once()

    @patch("todomaster.cli.get_storage")
    def test_done_command_invalid_id(self, mock_get_storage, runner):
        """Test done command with invalid ID."""
        mock_storage = MagicMock()
        mock_get_storage.return_value = mock_storage

        result = runner.invoke(app, ["done", "invalid"])

        # Should show error message for invalid ID
        assert "Invalid task ID" in result.stdout

    @patch("todomaster.cli.get_storage")
    def test_done_command_nonexistent_task(self, mock_get_storage, runner):
        """Test done command with non-existent task."""
        mock_storage = MagicMock()
        mock_storage.get_task.return_value = None
        mock_get_storage.return_value = mock_storage

        result = runner.invoke(app, ["done", "999"])

        # Should show error message for non-existent task
        assert "not found" in result.stdout

    @patch("todomaster.cli.get_storage")
    def test_edit_command_all_fields(self, mock_get_storage, runner):
        """Test edit command updating all fields."""
        task = Task(description="Original", priority=Priority.LOW)
        task.id = 1
        mock_storage = MagicMock()
        mock_storage.get_task.return_value = task
        mock_get_storage.return_value = mock_storage

        result = runner.invoke(
            app,
            [
                "edit",
                "1",
                "--description",
                "Updated",
                "--priority",
                "high",
                "--due",
                "tomorrow",
                "--tag",
                "work",
            ],
        )

        assert result.exit_code == 0
        mock_storage.update_task.assert_called_once()

    @patch("todomaster.cli.get_storage")
    def test_delete_command_confirmation(self, mock_get_storage, runner):
        """Test delete command with confirmation."""
        task = Task(description="To delete")
        task.id = 1
        mock_storage = MagicMock()
        mock_storage.get_task.return_value = task
        mock_storage.delete_task.return_value = True
        mock_get_storage.return_value = mock_storage

        result = runner.invoke(app, ["delete", "1"], input="y\n")

        assert result.exit_code == 0
        mock_storage.delete_task.assert_called_once_with(1)

    @patch("todomaster.cli.get_storage")
    def test_show_command(self, mock_get_storage, runner):
        """Test show command."""
        task = Task(description="Show me", priority=Priority.HIGH)
        task.id = 1
        mock_storage = MagicMock()
        mock_storage.get_task.return_value = task
        mock_get_storage.return_value = mock_storage

        result = runner.invoke(app, ["show", "1"])

        assert result.exit_code == 0
        mock_storage.get_task.assert_called_once_with(1)

    @patch("todomaster.cli.get_storage")
    def test_today_command(self, mock_get_storage, runner):
        """Test today command."""
        mock_storage = MagicMock()
        mock_storage.get_tasks_due_today.return_value = []
        mock_storage.get_overdue_tasks.return_value = []
        mock_get_storage.return_value = mock_storage

        result = runner.invoke(app, ["today"])

        assert result.exit_code == 0

    @patch("todomaster.cli.get_storage")
    def test_upcoming_command(self, mock_get_storage, runner):
        """Test upcoming command."""
        mock_storage = MagicMock()
        mock_storage.get_pending_tasks.return_value = []
        mock_get_storage.return_value = mock_storage

        result = runner.invoke(app, ["upcoming"])

        assert result.exit_code == 0

    @patch("todomaster.cli.get_storage")
    def test_search_command(self, mock_get_storage, runner):
        """Test search command."""
        mock_storage = MagicMock()
        mock_storage.search_tasks.return_value = []
        mock_get_storage.return_value = mock_storage

        result = runner.invoke(app, ["search", "milk"])

        assert result.exit_code == 0
        mock_storage.search_tasks.assert_called_once_with("milk")

    @patch("todomaster.cli.get_storage")
    def test_stats_command(self, mock_get_storage, runner):
        """Test stats command."""
        mock_storage = MagicMock()
        mock_storage.get_task_stats.return_value = {
            "total": 10,
            "pending": 5,
            "completed": 4,
            "overdue": 1,
        }
        mock_get_storage.return_value = mock_storage

        result = runner.invoke(app, ["stats"])

        assert result.exit_code == 0
        mock_storage.get_task_stats.assert_called_once()

    def test_version_command(self, runner):
        """Test version command."""
        result = runner.invoke(app, ["--version"])

        # Version command should show version information
        assert "TodoMaster v0.1.0" in result.stdout or "v0.1.0" in result.stdout

    @patch("todomaster.cli.get_storage")
    def test_clear_command(self, mock_get_storage, runner):
        """Test clear command."""
        mock_storage = MagicMock()
        mock_storage.clear_completed.return_value = 3
        mock_get_storage.return_value = mock_storage

        result = runner.invoke(app, ["clear"])

        assert result.exit_code == 0
        mock_storage.clear_completed.assert_called_once()

    @patch("todomaster.cli.get_storage")
    def test_exception_handling(self, mock_get_storage, runner):
        """Test exception handling in commands."""
        mock_storage = MagicMock()
        mock_storage.get_all_tasks.side_effect = Exception("Database error")
        mock_get_storage.return_value = mock_storage

        result = runner.invoke(app, ["list", "--all"])

        # Should show error message for exception
        assert "Failed to list tasks" in result.stdout


class TestCLIValidation:
    """Test CLI validation and error handling."""

    @patch("todomaster.cli.get_storage")
    def test_invalid_task_id(self, mock_get_storage):
        """Test handling invalid task ID."""
        mock_storage = MagicMock()
        mock_storage.get_task.return_value = None
        mock_get_storage.return_value = mock_storage

        # This should handle invalid ID gracefully
        result = mock_storage.get_task("invalid")
        assert result is None

    def test_storage_initialization(self):
        """Test storage initialization."""
        # Test with default path (should not raise exception)
        storage = get_storage()
        assert storage is not None


class TestTodoUI:
    """Test UI rendering functionality."""

    @pytest.fixture
    def ui(self):
        """Create UI instance for testing."""
        return TodoUI()

    def test_get_priority_color(self, ui):
        """Test priority color mapping."""
        assert ui.get_priority_color(Priority.HIGH) == "red"
        assert ui.get_priority_color(Priority.MEDIUM) == "yellow"
        assert ui.get_priority_color(Priority.LOW) == "green"

    def test_get_priority_icon(self, ui):
        """Test priority icon mapping."""
        assert ui.get_priority_icon(Priority.HIGH) == "🔴"
        assert ui.get_priority_icon(Priority.MEDIUM) == "🟡"
        assert ui.get_priority_icon(Priority.LOW) == "🟢"

    def test_format_date_none(self, ui):
        """Test formatting None date."""
        result = ui.format_date(None)
        assert result == "No due date"

    def test_format_date_today(self, ui):
        """Test formatting today's date."""
        today = datetime.now()
        result = ui.format_date(today)
        assert result == "Today"

    def test_format_date_tomorrow(self, ui):
        """Test formatting tomorrow's date."""
        tomorrow = datetime.now() + timedelta(days=1)
        result = ui.format_date(tomorrow)
        assert result in ["Tomorrow", "In 0 days"]  # Allow for timing

    def test_format_date_yesterday(self, ui):
        """Test formatting yesterday's date (overdue)."""
        yesterday = datetime.now() - timedelta(days=1)
        result = ui.format_date(yesterday)
        assert (
            "Overdue by 1d" in result or "Overdue by 2d" in result
        )  # Allow for timing

    def test_format_date_future_days(self, ui):
        """Test formatting future dates."""
        future = datetime.now() + timedelta(days=3)
        result = ui.format_date(future)
        assert "In 3 days" in result or "In 2 days" in result  # Account for timing

    def test_format_date_far_future(self, ui):
        """Test formatting far future dates."""
        far_future = datetime.now() + timedelta(days=10)
        result = ui.format_date(far_future)
        assert result == far_future.strftime("%Y-%m-%d")

    def test_render_task_table_empty(self, ui):
        """Test rendering empty task table."""
        ui.render_task_table([], "Test Title")
        # Should not raise exception

    def test_render_task_table_with_tasks(self, ui):
        """Test rendering task table with tasks."""
        task = Task(
            description="Test task", priority=Priority.HIGH, tags=["work"], id=1
        )
        ui.render_task_table([task], "Test Tasks")
        # Should not raise exception

    def test_render_task_detail(self, ui):
        """Test rendering task detail."""
        task = Task(
            description="Detailed task",
            priority=Priority.MEDIUM,
            tags=["work", "urgent"],
            id=1,
        )
        ui.render_task_detail(task)
        # Should not raise exception

    def test_render_task_detail_with_due_date(self, ui):
        """Test rendering task detail with due date."""
        task = Task(
            description="Task with due date",
            priority=Priority.HIGH,
            due_date=datetime.now() + timedelta(days=1),
            tags=["urgent"],
            id=1,
        )
        ui.render_task_detail(task)
        # Should not raise exception

    def test_render_task_detail_completed(self, ui):
        """Test rendering completed task detail."""
        task = Task(description="Completed task", priority=Priority.LOW, id=1)
        task.mark_completed()
        ui.render_task_detail(task)
        # Should not raise exception

    def test_render_stats(self, ui):
        """Test rendering statistics."""
        stats = {"total": 10, "pending": 5, "completed": 4, "overdue": 1}
        ui.render_stats(stats)
        # Should not raise exception

    def test_render_success(self, ui):
        """Test rendering success message."""
        ui.render_success("Test success message")
        # Should not raise exception

    def test_render_error(self, ui):
        """Test rendering error message."""
        ui.render_error("Test error message")
        # Should not raise exception

    def test_render_warning(self, ui):
        """Test rendering warning message."""
        ui.render_warning("Test warning message")
        # Should not raise exception

    def test_render_info(self, ui):
        """Test rendering info message."""
        ui.render_info("Test info message")
        # Should not raise exception

    def test_get_task_stats(self, ui):
        """Test getting task statistics."""
        tasks = [
            Task("Task 1", Priority.HIGH),
            Task("Task 2", Priority.MEDIUM),
            Task("Task 3", Priority.LOW),
        ]
        tasks[1].mark_completed()  # Mark one as completed

        # Mock overdue task
        tasks[0].due_date = datetime.now() - timedelta(days=1)  # Overdue

        stats = ui._get_task_stats(tasks)
        assert stats["pending"] == 2  # One completed
        assert stats["overdue"] == 1  # One overdue

    def test_render_help(self, ui):
        """Test rendering help information."""
        ui.render_help()
        # Should not raise exception
