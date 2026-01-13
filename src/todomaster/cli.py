"""CLI interface for TodoMaster using Typer."""

from datetime import datetime, timedelta

import typer
from rich.console import Console

from .storage import Storage
from .tasks import Task
from .ui import TodoUI
from .utils import parse_date, parse_priority, parse_tags, validate_task_id

app = typer.Typer(
    help="TodoMaster - AI-Powered Terminal Todo List", invoke_without_command=True
)
ui = TodoUI()
console = Console()


def get_storage() -> Storage:
    """Get storage instance."""
    return Storage()


@app.command()
def add(
    description: str,
    priority: str | None = typer.Option(
        None, "--priority", "-p", help="Task priority (low, medium, high)"
    ),
    due: str | None = typer.Option(
        None, "--due", "-d", help="Due date (natural language supported)"
    ),
    tag: str | None = typer.Option(
        None, "--tag", "-t", help="Task tags (comma-separated)"
    ),
):
    """Add a new task."""
    try:
        task = Task(description=description)

        if priority:
            task.priority = parse_priority(priority)

        if due:
            task.due_date = parse_date(due)
            if task.due_date is None:
                ui.render_error(f"Invalid due date: {due}")
                return typer.Exit(1)

        if tag:
            task.tags = parse_tags(tag)

        storage = get_storage()
        created_task = storage.create_task(task)

        ui.render_success(f"Task created with ID: {created_task.id}")
        ui.render_task_detail(created_task)

    except Exception as e:
        ui.render_error(f"Failed to create task: {e}")
        return typer.Exit(1)


@app.command(name="list")
def list_command(
    show_all: bool = typer.Option(
        False, "--all", "-a", help="Show all tasks (including completed)"
    ),
    pending: bool = typer.Option(False, "--pending", help="Show only pending tasks"),
    overdue: bool = typer.Option(False, "--overdue", help="Show only overdue tasks"),
    priority: str | None = typer.Option(
        None, "--priority", "-p", help="Filter by priority"
    ),
    tag: str | None = typer.Option(None, "--tag", "-t", help="Filter by tag"),
):
    """List tasks with optional filtering."""
    try:
        storage = get_storage()

        if overdue:
            tasks = storage.get_overdue_tasks()
        elif pending:
            tasks = storage.get_pending_tasks()
        elif show_all:
            tasks = storage.get_all_tasks()
        else:
            tasks = storage.get_pending_tasks()

        # Apply additional filters
        if priority:
            target_priority = parse_priority(priority)
            tasks = [task for task in tasks if task.priority == target_priority]

        if tag:
            tasks = [task for task in tasks if tag in task.tags]

        title = "Tasks"
        if overdue:
            title = "Overdue Tasks"
        elif pending:
            title = "Pending Tasks"
        elif show_all:
            title = "All Tasks"

        ui.render_task_table(tasks, title)

    except Exception as e:
        ui.render_error(f"Failed to list tasks: {e}")
        return typer.Exit(1)


@app.command()
def done(task_id: str):
    """Mark a task as completed."""
    try:
        task_id_int = validate_task_id(task_id)
        if task_id_int is None:
            ui.render_error("Invalid task ID")
            return typer.Exit(1)

        storage = get_storage()
        task = storage.get_task(task_id_int)

        if task is None:
            ui.render_error(f"Task with ID {task_id_int} not found")
            return typer.Exit(1)

        if task.completed:
            ui.render_warning(f"Task {task_id_int} is already completed")
            return

        task.mark_completed()
        storage.update_task(task)

        ui.render_success(f"Task {task_id_int} marked as completed")

    except Exception as e:
        ui.render_error(f"Failed to complete task: {e}")
        return typer.Exit(1)


@app.command()
def edit(
    task_id: str,
    description: str | None = typer.Option(
        None, "--description", "-d", help="New description"
    ),
    priority: str | None = typer.Option(None, "--priority", "-p", help="New priority"),
    due: str | None = typer.Option(None, "--due", help="New due date"),
    tag: str | None = typer.Option(None, "--tag", "-t", help="Add tags"),
):
    """Edit an existing task."""
    try:
        task_id_int = validate_task_id(task_id)
        if task_id_int is None:
            ui.render_error("Invalid task ID")
            return typer.Exit(1)

        storage = get_storage()
        task = storage.get_task(task_id_int)

        if task is None:
            ui.render_error(f"Task with ID {task_id_int} not found")
            return typer.Exit(1)

        # Update fields
        if description:
            task.update_description(description)

        if priority:
            task.update_priority(parse_priority(priority))

        if due:
            new_date = parse_date(due)
            if new_date is None:
                ui.render_error(f"Invalid due date: {due}")
                return typer.Exit(1)
            task.update_due_date(new_date)

        if tag:
            new_tags = parse_tags(tag)
            for new_tag in new_tags:
                task.add_tag(new_tag)

        storage.update_task(task)

        ui.render_success(f"Task {id} updated")
        ui.render_task_detail(task)

    except Exception as e:
        ui.render_error(f"Failed to edit task: {e}")
        return typer.Exit(1)


@app.command()
def delete(task_id: str):
    """Delete a task."""
    try:
        task_id_int = validate_task_id(task_id)
        if task_id_int is None:
            ui.render_error("Invalid task ID")
            return typer.Exit(1)

        storage = get_storage()
        task = storage.get_task(task_id_int)

        if task is None:
            ui.render_error(f"Task with ID {task_id_int} not found")
            return typer.Exit(1)

        if typer.confirm(f"Delete task '{task.description}'?"):
            if storage.delete_task(task_id_int):
                ui.render_success(f"Task {task_id_int} deleted")
            else:
                ui.render_error(f"Failed to delete task {task_id_int}")

    except Exception as e:
        ui.render_error(f"Failed to delete task: {e}")
        return typer.Exit(1)


@app.command()
def clear():
    """Remove all completed tasks."""
    try:
        storage = get_storage()
        completed_count = storage.clear_completed()

        if completed_count > 0:
            ui.render_success(f"Cleared {completed_count} completed task(s)")
        else:
            ui.render_info("No completed tasks to clear")

    except Exception as e:
        ui.render_error(f"Failed to clear tasks: {e}")
        return typer.Exit(1)


@app.command()
def show(task_id: str):
    """Show detailed information about a task."""
    try:
        task_id_int = validate_task_id(task_id)
        if task_id_int is None:
            ui.render_error("Invalid task ID")
            return typer.Exit(1)

        storage = get_storage()
        task = storage.get_task(task_id_int)

        if task is None:
            ui.render_error(f"Task with ID {task_id_int} not found")
            return typer.Exit(1)

        ui.render_task_detail(task)

    except Exception as e:
        ui.render_error(f"Failed to show task: {e}")
        return typer.Exit(1)


@app.command()
def today():
    """Show tasks due today and overdue tasks."""
    try:
        storage = get_storage()
        today_tasks = storage.get_tasks_due_today()
        overdue_tasks = storage.get_overdue_tasks()

        if not today_tasks and not overdue_tasks:
            ui.render_info("No tasks due today")
            return

        if overdue_tasks:
            ui.render_task_table(overdue_tasks, "Overdue Tasks")

        if today_tasks:
            # Filter out already shown overdue tasks
            today_only = [task for task in today_tasks if not task.is_overdue]
            if today_only:
                ui.render_task_table(today_only, "Due Today")

    except Exception as e:
        ui.render_error(f"Failed to show today's tasks: {e}")
        return typer.Exit(1)


@app.command()
def upcoming():
    """Show tasks for the next 7 days."""
    try:
        storage = get_storage()
        all_pending = storage.get_pending_tasks()

        now = datetime.now()  # noqa: DTZ005
        week_ahead = now + timedelta(days=7)

        upcoming_tasks = [
            task
            for task in all_pending
            if task.due_date and now <= task.due_date <= week_ahead
        ]

        if not upcoming_tasks:
            ui.render_info("No upcoming tasks in the next 7 days")
            return

        ui.render_task_table(upcoming_tasks, "Upcoming Tasks (Next 7 Days)")

    except Exception as e:
        ui.render_error(f"Failed to show upcoming tasks: {e}")
        return typer.Exit(1)


@app.command()
def search(query: str):
    """Search tasks by description or tags."""
    try:
        storage = get_storage()
        results = storage.search_tasks(query)

        if not results:
            ui.render_info(f"No tasks found matching: {query}")
            return

        ui.render_task_table(results, f"Search Results: {query}")

    except Exception as e:
        ui.render_error(f"Failed to search tasks: {e}")
        return typer.Exit(1)


@app.command()
def stats():
    """Show task statistics."""
    try:
        storage = get_storage()
        stats = storage.get_task_stats()
        ui.render_stats(stats)

    except Exception as e:
        ui.render_error(f"Failed to get statistics: {e}")
        return typer.Exit(1)


@app.callback()
def main(
    version: bool = typer.Option(False, "--version", help="Show version and exit"),
):
    """TodoMaster - A beautiful, robust command-line todo list application."""
    if version:
        typer.echo("TodoMaster v0.1.0")
        raise typer.Exit(0)


if __name__ == "__main__":
    app()
