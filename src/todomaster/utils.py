"""Utility functions for TodoMaster."""

import re
from datetime import datetime, timedelta

try:
    import dateutil.parser
except ImportError:
    dateutil = None

from .tasks import Priority


def parse_date(date_str: str) -> datetime | None:
    """Parse natural language date strings."""
    if not date_str:
        return None

    date_str = date_str.strip().lower()

    # Handle relative dates
    if date_str == "today":
        return datetime.now()  # noqa: DTZ005
    elif date_str == "tomorrow":
        return datetime.now() + timedelta(days=1)  # noqa: DTZ005
    elif date_str == "yesterday":
        return datetime.now() - timedelta(days=1)  # noqa: DTZ005

    # Handle "+Nd" patterns (e.g., "+3d", "+1w")
    relative_match = re.match(r"^\+(\d+)([dw])$", date_str)
    if relative_match:
        num = int(relative_match.group(1))
        unit = relative_match.group(2)
        if unit == "d":
            return datetime.now() + timedelta(days=num)  # noqa: DTZ005
        elif unit == "w":
            return datetime.now() + timedelta(weeks=num)  # noqa: DTZ005

    # Handle "next X" patterns
    if date_str.startswith("next "):
        # For now, just skip this complex parsing
        pass

    # Try dateutil for natural language parsing if available
    try:
        from dateutil import parser

        parsed = parser.parse(date_str)
        return parsed
    except Exception:
        pass

    # Try pendulum for natural language parsing
    try:
        import dateutil.parser

        parsed = dateutil.parser.parse(date_str)
        return parsed
    except Exception:
        pass

    # Try ISO format
    try:
        return datetime.fromisoformat(date_str)
    except Exception:
        pass

    # Try common formats
    formats = [
        "%Y-%m-%d",
        "%m-%d-%Y",
        "%d-%m-%Y",
        "%Y/%m/%d",
        "%m/%d/%Y",
        "%d/%m/%Y",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)  # noqa: DTZ007
        except Exception:
            continue

    return None


def parse_priority(priority_str: str) -> Priority:
    """Parse priority string."""
    if not priority_str:
        return Priority.MEDIUM

    priority_str = priority_str.strip().lower()

    priority_map = {
        "high": Priority.HIGH,
        "h": Priority.HIGH,
        "medium": Priority.MEDIUM,
        "med": Priority.MEDIUM,
        "m": Priority.MEDIUM,
        "low": Priority.LOW,
        "l": Priority.LOW,
    }

    return priority_map.get(priority_str, Priority.MEDIUM)


def parse_tags(tags_str: str | None) -> list[str]:
    """Parse tags string into list."""
    if not tags_str:
        return []

    # Split by comma and space, clean up whitespace
    tags = []
    for tag in re.split(r"[,;\s]+", tags_str.strip()):
        tag = tag.strip()
        if tag:
            tags.append(tag)

    return list(set(tags))  # Remove duplicates


def validate_task_id(task_id_str: str) -> int | None:
    """Validate and parse task ID."""
    try:
        task_id = int(task_id_str)
        if task_id > 0:
            return task_id
    except ValueError:
        pass
    return None


def format_duration(start: datetime, end: datetime | None = None) -> str:
    """Format duration between two datetimes."""
    if end is None:
        end = datetime.now()  # noqa: DTZ005

    diff = end - start

    if diff.days > 0:
        return f"{diff.days}d"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours}h"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes}m"
    else:
        return f"{diff.seconds}s"


def truncate_text(text: str, max_length: int = 50) -> str:
    """Truncate text to specified length."""
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."


def sanitize_description(description: str) -> str:
    """Sanitize task description."""
    # Remove extra whitespace
    description = re.sub(r"\s+", " ", description.strip())
    # Remove potentially problematic characters
    description = re.sub(r'[<>"\']', "", description)
    return description


def get_default_due_date() -> datetime | None:
    """Get default due date (could be based on user preference)."""
    return None


def is_valid_date(date_str: str) -> bool:
    """Check if date string is valid."""
    return parse_date(date_str) is not None
