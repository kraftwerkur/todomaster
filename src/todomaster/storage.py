"""SQLite storage layer for TodoMaster."""

import sqlite3
import threading
from datetime import datetime, timedelta
from pathlib import Path

from .tasks import Priority, Task


class Storage:
    """SQLite storage layer for persisting tasks."""

    def __init__(self, db_path: Path | None = None):
        """Initialize storage with optional database path."""
        if db_path is None:
            home = Path.home()
            db_dir = home / ".local" / "share" / "todomaster"
            db_dir.mkdir(parents=True, exist_ok=True)
            db_path = db_dir / "tasks.db"

        self.db_path = db_path
        self._lock = threading.Lock()
        self._init_db()

    def close(self):
        """Close any open database connections."""
        pass  # Context managers handle closing automatically

    def __del__(self):
        """Cleanup when Storage instance is destroyed."""
        try:
            self.close()
        except Exception:
            pass  # Ignore cleanup errors

    def _init_db(self):
        """Initialize the database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    description TEXT NOT NULL,
                    priority TEXT CHECK(priority IN ('low', 'medium', 'high')) DEFAULT 'medium',
                    due_date TEXT,
                    completed BOOLEAN DEFAULT FALSE,
                    tags TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    completed_at TEXT
                )
            """
            )
            conn.commit()

    def _task_from_row(self, row: tuple) -> Task:
        """Convert database row to Task object."""
        (
            id_,
            description,
            priority,
            due_date,
            completed,
            tags,
            created_at,
            updated_at,
            completed_at,
        ) = row

        task = Task(
            description=description,
            priority=Priority(priority),
            due_date=datetime.fromisoformat(due_date) if due_date else None,
            completed=bool(completed),
            tags=tags.split(",") if tags else [],
            id=id_,
            created_at=datetime.fromisoformat(created_at),
            updated_at=datetime.fromisoformat(updated_at),
            completed_at=datetime.fromisoformat(completed_at) if completed_at else None,
        )
        return task

    def _task_to_row(self, task: Task) -> tuple:
        """Convert Task object to database row."""
        return (
            task.description,
            task.priority.value,
            task.due_date.isoformat() if task.due_date else None,
            task.completed,
            ",".join(task.tags) if task.tags else None,
            task.created_at.isoformat() if task.created_at else None,
            task.updated_at.isoformat() if task.updated_at else None,
            task.completed_at.isoformat() if task.completed_at else None,
        )

    def create_task(self, task: Task) -> Task:
        """Create a new task in the database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                INSERT INTO tasks (description, priority, due_date, completed, tags, created_at, updated_at, completed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                self._task_to_row(task),
            )

            task.id = cursor.lastrowid
            conn.commit()
            return task

    def get_task(self, task_id: int) -> Task | None:
        """Get a task by ID."""
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT * FROM tasks WHERE id = ?", (task_id,)
            ).fetchone()
            if row:
                return self._task_from_row(row)
            return None

    def get_all_tasks(self) -> list[Task]:
        """Get all tasks."""
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT * FROM tasks ORDER BY created_at DESC"
            ).fetchall()
            return [self._task_from_row(row) for row in rows]

    def get_pending_tasks(self) -> list[Task]:
        """Get all pending (not completed) tasks."""
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT * FROM tasks WHERE completed = FALSE ORDER BY created_at DESC"
            ).fetchall()
            return [self._task_from_row(row) for row in rows]

    def get_completed_tasks(self) -> list[Task]:
        """Get all completed tasks."""
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT * FROM tasks WHERE completed = TRUE ORDER BY completed_at DESC"
            ).fetchall()
            return [self._task_from_row(row) for row in rows]

    def get_overdue_tasks(self) -> list[Task]:
        """Get all overdue tasks."""
        now = datetime.now().isoformat()  # noqa: DTZ005
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                """
                SELECT * FROM tasks
                WHERE completed = FALSE AND due_date IS NOT NULL AND due_date < ?
                ORDER BY due_date ASC
            """,
                (now,),
            ).fetchall()
            return [self._task_from_row(row) for row in rows]

    def get_tasks_due_today(self) -> list[Task]:
        """Get tasks due today."""
        today = datetime.now().date().isoformat()  # noqa: DTZ005
        tomorrow = (datetime.now().date() + timedelta(days=1)).isoformat()  # noqa: DTZ005

        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                """
                SELECT * FROM tasks
                WHERE completed = FALSE AND due_date >= ? AND due_date < ?
                ORDER BY due_date ASC
            """,
                (today, tomorrow),
            ).fetchall()
            return [self._task_from_row(row) for row in rows]

    def update_task(self, task: Task) -> Task:
        """Update an existing task."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                UPDATE tasks
                SET description = ?, priority = ?, due_date = ?, completed = ?, tags = ?, updated_at = ?, completed_at = ?
                WHERE id = ?
            """,
                (
                    task.description,
                    task.priority.value,
                    task.due_date.isoformat() if task.due_date else None,
                    task.completed,
                    ",".join(task.tags) if task.tags else None,
                    task.updated_at.isoformat() if task.updated_at else None,
                    task.completed_at.isoformat() if task.completed_at else None,
                    task.id,
                ),
            )
            conn.commit()
            return task

    def delete_task(self, task_id: int) -> bool:
        """Delete a task by ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            conn.commit()
            return cursor.rowcount > 0

    def clear_completed(self) -> int:
        """Delete all completed tasks."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("DELETE FROM tasks WHERE completed = TRUE")
            conn.commit()
            return cursor.rowcount

    def search_tasks(self, query: str) -> list[Task]:
        """Search tasks by description or tags."""
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                """
                SELECT * FROM tasks
                WHERE description LIKE ? OR tags LIKE ?
                ORDER BY created_at DESC
            """,
                (f"%{query}%", f"%{query}%"),
            ).fetchall()
            return [self._task_from_row(row) for row in rows]

    def get_task_stats(self) -> dict:
        """Get task statistics."""
        with sqlite3.connect(self.db_path) as conn:
            total = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
            pending = conn.execute(
                "SELECT COUNT(*) FROM tasks WHERE completed = FALSE"
            ).fetchone()[0]
            completed = conn.execute(
                "SELECT COUNT(*) FROM tasks WHERE completed = TRUE"
            ).fetchone()[0]
            overdue = conn.execute(
                """
                SELECT COUNT(*) FROM tasks
                WHERE completed = FALSE AND due_date IS NOT NULL AND due_date < datetime('now')
            """
            ).fetchone()[0]

            return {
                "total": total,
                "pending": pending,
                "completed": completed,
                "overdue": overdue,
            }
