# TodoMaster

A beautiful, robust command-line todo list application with rich terminal UI, persistent storage, priorities, due dates, and strong test coverage.

## Features

- 📝 **Task Management**: Add, edit, complete, and delete tasks
- 🎯 **Priorities**: High, medium, and low priority levels with color coding
- 📅 **Due Dates**: Natural language date parsing (e.g., "tomorrow", "+3d", "next friday")
- 🏷️ **Tags**: Organize tasks with tags and categories
- 🎨 **Rich UI**: Beautiful tables, colored priorities, and readable panels
- 💾 **Persistent Storage**: SQLite database for reliable data storage
- 🔍 **Search**: Find tasks by description or tags
- 📊 **Statistics**: Track task completion and productivity
- 🧪 **Well Tested**: Comprehensive test suite with high coverage

## Installation

### Using UV (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd todomaster

# Install with UV
uv install

# Or install in development mode
uv install --dev
```

### Using pip

```bash
# Clone the repository
git clone <repository-url>
cd todomaster

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .

# Or install with development dependencies
pip install -e ".[dev]"
```

## Usage

TodoMaster provides a simple `todo` command with various subcommands:

### Basic Task Management

```bash
# Add a new task
todo add "Buy milk" --priority high --due tomorrow --tag shopping

# List all pending tasks
todo list

# List all tasks (including completed)
todo list --all

# Show overdue tasks
todo list --overdue

# Mark a task as completed
todo done 1

# Edit a task
todo edit 1 --description "Buy organic milk" --due +3d

# Delete a task
todo delete 1

# Clear all completed tasks
todo clear
```

### Viewing Tasks

```bash
# Show detailed information about a task
todo show 1

# Show tasks due today and overdue tasks
todo today

# Show tasks for the next 7 days
todo upcoming

# Search tasks
todo search "milk"
todo search "work"

# Show task statistics
todo stats
```

### Filtering and Organization

```bash
# Filter by priority
todo list --priority high

# Filter by tag
todo list --tag shopping

# Show only pending tasks
todo list --pending

# Multiple filters work together
todo list --priority high --tag work --pending
```

## Priority Levels

- **High** 🔴: Urgent and important tasks
- **Medium** 🟡: Standard priority tasks (default)
- **Low** 🟢: Nice-to-have tasks

## Date Formats

TodoMaster supports natural language date parsing:

- **Relative dates**: `today`, `tomorrow`, `yesterday`
- **Relative offsets**: `+3d` (3 days), `+1w` (1 week)
- **ISO dates**: `2026-12-25`
- **Common formats**: `12/25/2026`, `25-12-2026`

## Tags

Organize tasks with tags using comma or space separation:

```bash
todo add "Finish report" --tag "work,urgent"
todo add "Buy groceries" --tag "shopping personal"
todo add "Learn Python" --tag "learning coding"
```

## Terminal UI Examples

### Task List View
```
┌─────────────────────────────────────────────────────────────┐
│ TodoMaster • 8 pending • 3 overdue                          │
├────┬───────────────┬────────────────────────────┬───────────┤
│ ID │ Priority      │ Description                │ Due       │
├────┼───────────────┼────────────────────────────┼───────────┤
│ 3  │ HIGH • 🔴     │ Finish Ralph Wiggum prompt │ Today     │
│ 1  │ medium • 🟡   │ Buy milk & eggs            │ Tomorrow  │
│ 7  │ low • 🟢      │ Read linting docs          │ In 5 days │
└────┴───────────────┴────────────────────────────┴───────────┘
```

### Task Detail View
```
┌─────────────────────────────────────────────────────────────┐
│ Finish Ralph Wiggum prompt                                  │
│ Priority: HIGH • 🔴     Created: 2026-01-11  │
├─────────────────────────────────────────────────────────────┤
│ Description:                                                │
│ Create perfect Ralph-style todo prompt for Grok testing     │
│                                                             │
│ Due: Today (overdue by 4h)                                  │
│ Tags: ai, testing, fun                                      │
└─────────────────────────────────────────────────────────────┘
```

Use `todo show <id>` to view task details. Use separate commands to interact with tasks:
- `todo done <id>` - Mark as completed
- `todo edit <id>` - Edit the task
- `todo delete <id>` - Delete the task

## Configuration

TodoMaster stores data in:
- **Database**: `~/.local/share/todomaster/tasks.db`
- **Configuration**: `~/.config/todomaster/config.yaml` (optional)

The database is created automatically on first run.

## Development

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src/todomaster --cov-report=term-missing

# Run specific test file
uv run pytest tests/test_tasks.py
```

### Code Quality

```bash
# Run linting
uv run ruff check src/todomaster

# Format code
uv run black src/todomaster tests

# Run both
uv run ruff check src/todomaster && uv run black src/todomaster tests
```

### Project Structure

```
todomaster/
├── src/todomaster/
│   ├── __init__.py      # Package initialization
│   ├── cli.py           # Main CLI interface (Typer)
│   ├── tasks.py         # Core task model and business logic
│   ├── storage.py       # SQLite persistence layer
│   ├── ui.py            # Rich UI components
│   └── utils.py         # Date parsing and utilities
├── tests/
│   ├── test_tasks.py    # Task model tests
│   ├── test_storage.py  # Storage layer tests
│   ├── test_cli.py      # CLI interface tests
│   └── test_utils.py    # Utility function tests
├── pyproject.toml       # Project configuration and dependencies
└── README.md           # This file
```

## Commands Reference

| Command | Description | Example |
|---------|-------------|---------|
| `add` | Add a new task | `todo add "Buy milk" --priority high` |
| `list` | List tasks with filters | `todo list --all --priority high` |
| `done` | Mark task as completed | `todo done 1` |
| `edit` | Edit existing task | `todo edit 1 --description "New text"` |
| `delete` | Delete a task | `todo delete 1` |
| `clear` | Remove completed tasks | `todo clear` |
| `show` | Show task details | `todo show 1` |
| `today` | Show today's tasks | `todo today` |
| `upcoming` | Show next 7 days | `todo upcoming` |
| `search` | Search tasks | `todo search "milk"` |
| `stats` | Show statistics | `todo stats` |

## Requirements

- Python 3.10+
- SQLite (included with Python)
- Dependencies defined in `pyproject.toml`:
  - `typer`: CLI framework
  - `rich`: Terminal UI
  - `pendulum`: Date handling

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run tests and linting
6. Submit a pull request

## Support

For issues, questions, or feature requests, please open an issue on the GitHub repository.