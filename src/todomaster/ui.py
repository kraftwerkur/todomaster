"""Rich UI components for TodoMaster."""

from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from .tasks import Priority, Task


class TodoUI:
    """Rich UI components for displaying tasks."""

    def __init__(self):
        """Initialize UI with console."""
        self.console = Console()

    def get_priority_color(self, priority: Priority) -> str:
        """Get color for priority level."""
        colors = {
            Priority.HIGH: "red",
            Priority.MEDIUM: "yellow",
            Priority.LOW: "green",
        }
        return colors.get(priority, "white")

    def get_priority_icon(self, priority: Priority) -> str:
        """Get icon for priority level."""
        icons = {
            Priority.HIGH: "🔴",
            Priority.MEDIUM: "🟡",
            Priority.LOW: "🟢",
        }
        return icons.get(priority, "⚪")

    def format_date(self, date: datetime | None) -> str:
        """Format date for display."""
        if date is None:
            return "No due date"

        now = datetime.now()  # noqa: DTZ005
        diff = date - now

        if date.date() == now.date():
            return "Today"
        elif diff.days == -1:
            return "Yesterday (overdue)"
        elif diff.days < 0:
            return f"Overdue by {abs(diff.days)}d"
        elif diff.days == 1:
            return "Tomorrow"
        elif diff.days < 7:
            return f"In {diff.days} days"
        else:
            return date.strftime("%Y-%m-%d")

    def render_task_table(self, tasks: list[Task], title: str = "Tasks") -> None:
        """Render tasks in a beautiful table."""
        if not tasks:
            self.console.print(Panel("No tasks found.", title=title))
            return

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("ID", style="cyan", width=4)
        table.add_column("Priority", style="bold", width=12)
        table.add_column("Description", style="white", width=40)
        table.add_column("Due", style="blue", width=12)
        table.add_column("Tags", style="green", width=15)

        for task in tasks:
            priority_text = Text()
            priority_text.append(f"{task.priority.value.upper()} ", style="bold")
            priority_text.append(self.get_priority_icon(task.priority))
            priority_text.stylize(self.get_priority_color(task.priority))

            due_text = self.format_date(task.due_date)
            if task.is_overdue:
                due_style = "red"
            elif task.is_due_today:
                due_style = "yellow"
            else:
                due_style = "blue"

            tags_text = ", ".join(task.tags) if task.tags else ""

            table.add_row(
                str(task.id),
                priority_text,
                task.description,
                Text(due_text, style=due_style),
                tags_text,
            )

        stats = self._get_task_stats(tasks)
        subtitle = f"{stats['pending']} pending • {stats['overdue']} overdue"

        self.console.print(Panel(table, title=f"{title} • {subtitle}"))

    def render_task_detail(self, task: Task) -> None:
        """Render detailed view of a single task."""
        priority_text = Text()
        priority_text.append(f"{task.priority.value.upper()} ", style="bold")
        priority_text.append(self.get_priority_icon(task.priority))
        priority_text.stylize(self.get_priority_color(task.priority))

        content = []
        content.append(f"Priority: {priority_text}")
        content.append(
            f"Created: {task.created_at.strftime('%Y-%m-%d %H:%M') if task.created_at else 'Unknown'}"
        )

        if task.due_date:
            due_text = self.format_date(task.due_date)
            if task.is_overdue:
                due_text = f"{due_text} ⚠️"
            content.append(f"Due: {due_text}")

        if task.tags:
            content.append(f"Tags: {', '.join(task.tags)}")

        content.append("")
        content.append("Description:")
        content.append(task.description)

        if task.completed and task.completed_at:
            content.append("")
            content.append(f"Completed: {task.completed_at.strftime('%Y-%m-%d %H:%M')}")

        panel_content = "\n".join(content)
        self.console.print(Panel(panel_content, title=task.description, expand=False))

    def render_stats(self, stats: dict) -> None:
        """Render task statistics."""
        stats_table = Table(show_header=False, box=None)
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Count", style="bold")

        stats_table.add_row("Total Tasks", str(stats["total"]))
        stats_table.add_row("Pending", str(stats["pending"]))
        stats_table.add_row("Completed", str(stats["completed"]))
        stats_table.add_row("Overdue", Text(str(stats["overdue"]), style="red"))

        self.console.print(Panel(stats_table, title="📊 Statistics"))

    def render_success(self, message: str) -> None:
        """Render success message."""
        self.console.print(f"✅ {message}", style="green bold")

    def render_error(self, message: str) -> None:
        """Render error message."""
        self.console.print(f"❌ {message}", style="red bold")

    def render_warning(self, message: str) -> None:
        """Render warning message."""
        self.console.print(f"⚠️  {message}", style="yellow bold")

    def render_info(self, message: str) -> None:
        """Render info message."""
        self.console.print(f"ℹ️  {message}", style="blue bold")

    def _get_task_stats(self, tasks: list[Task]) -> dict:
        """Get statistics for a list of tasks."""
        pending = sum(1 for task in tasks if not task.completed)
        overdue = sum(1 for task in tasks if task.is_overdue)
        return {
            "pending": pending,
            "overdue": overdue,
        }

    def render_help(self) -> None:
        """Render help information."""
        help_table = Table(show_header=True, header_style="bold magenta")
        help_table.add_column("Command", style="cyan")
        help_table.add_column("Description", style="white")
        help_table.add_column("Example", style="green")

        commands = [
            ("add", "Add a new task", 'todo add "Buy milk" --priority high'),
            ("list", "List all tasks", "todo list"),
            ("done", "Mark task as completed", "todo done 1"),
            ("edit", "Edit a task", 'todo edit 1 "New description"'),
            ("delete", "Delete a task", "todo delete 1"),
            ("clear", "Remove completed tasks", "todo clear"),
            ("show", "Show task details", "todo show 1"),
            ("today", "Show tasks due today", "todo today"),
            ("upcoming", "Show upcoming tasks", "todo upcoming"),
            ("search", "Search tasks", 'todo search "milk"'),
        ]

        for cmd, desc, example in commands:
            help_table.add_row(cmd, desc, example)

        self.console.print(Panel(help_table, title="📖 TodoMaster Help"))
