"""Test cases for TodoMaster utility functions."""

import pytest
from datetime import datetime, timedelta

from todomaster.utils import (
    parse_date,
    parse_priority,
    parse_tags,
    validate_task_id,
    truncate_text,
    sanitize_description,
    is_valid_date,
)
from todomaster.tasks import Priority


class TestDateParsing:
    """Test date parsing functionality."""

    def test_parse_today(self):
        """Test parsing 'today'."""
        result = parse_date("today")
        assert result is not None
        assert result.date() == datetime.now().date()

    def test_parse_tomorrow(self):
        """Test parsing 'tomorrow'."""
        result = parse_date("tomorrow")
        assert result is not None
        assert result.date() == (datetime.now() + timedelta(days=1)).date()

    def test_parse_yesterday(self):
        """Test parsing 'yesterday'."""
        result = parse_date("yesterday")
        assert result is not None
        assert result.date() == (datetime.now() - timedelta(days=1)).date()

    def test_parse_relative_days(self):
        """Test parsing '+Nd' format."""
        result = parse_date("+3d")
        assert result is not None
        expected = datetime.now() + timedelta(days=3)
        assert abs((result - expected).total_seconds()) < 60  # Allow minute variance

    def test_parse_relative_weeks(self):
        """Test parsing '+Nw' format."""
        result = parse_date("+2w")
        assert result is not None
        expected = datetime.now() + timedelta(weeks=2)
        assert abs((result - expected).total_seconds()) < 60  # Allow minute variance

    def test_parse_iso_date(self):
        """Test parsing ISO date format."""
        result = parse_date("2026-12-25")
        assert result is not None
        assert result.year == 2026
        assert result.month == 12
        assert result.day == 25

    def test_parse_invalid_date(self):
        """Test parsing invalid date."""
        result = parse_date("not a date")
        assert result is None

    def test_parse_empty_date(self):
        """Test parsing empty date."""
        result = parse_date("")
        assert result is None
        # parse_date expects string, so we don't test with None


class TestPriorityParsing:
    """Test priority parsing functionality."""

    def test_parse_high_priority(self):
        """Test parsing high priority."""
        assert parse_priority("high") == Priority.HIGH
        assert parse_priority("h") == Priority.HIGH
        assert parse_priority("HIGH") == Priority.HIGH

    def test_parse_medium_priority(self):
        """Test parsing medium priority."""
        assert parse_priority("medium") == Priority.MEDIUM
        assert parse_priority("med") == Priority.MEDIUM
        assert parse_priority("m") == Priority.MEDIUM
        assert parse_priority("MEDIUM") == Priority.MEDIUM

    def test_parse_low_priority(self):
        """Test parsing low priority."""
        assert parse_priority("low") == Priority.LOW
        assert parse_priority("l") == Priority.LOW
        assert parse_priority("LOW") == Priority.LOW

    def test_parse_invalid_priority(self):
        """Test parsing invalid priority defaults to medium."""
        assert parse_priority("invalid") == Priority.MEDIUM
        assert parse_priority("") == Priority.MEDIUM
        # parse_priority expects string, so we don't test with None


class TestTagParsing:
    """Test tag parsing functionality."""

    def test_parse_single_tag(self):
        """Test parsing single tag."""
        result = parse_tags("work")
        assert result == ["work"]

    def test_parse_multiple_tags_comma(self):
        """Test parsing comma-separated tags."""
        result = parse_tags("work,urgent,project")
        assert set(result) == {"work", "urgent", "project"}

    def test_parse_multiple_tags_space(self):
        """Test parsing space-separated tags."""
        result = parse_tags("work urgent project")
        assert set(result) == {"work", "urgent", "project"}

    def test_parse_mixed_separators(self):
        """Test parsing mixed separators."""
        result = parse_tags("work, urgent project")
        assert set(result) == {"work", "urgent", "project"}

    def test_parse_empty_tags(self):
        """Test parsing empty tags."""
        assert parse_tags("") == []
        assert parse_tags(None) == []
        assert parse_tags("   ") == []

    def test_parse_duplicate_tags(self):
        """Test parsing duplicate tags are removed."""
        result = parse_tags("work, work, urgent, work")
        assert result == ["work", "urgent"] or result == ["urgent", "work"]
        assert len(result) == 2

    def test_parse_tags_with_whitespace(self):
        """Test parsing tags with extra whitespace."""
        result = parse_tags("  work ,  urgent  ")
        assert set(result) == {"work", "urgent"}


class TestTaskIdValidation:
    """Test task ID validation."""

    def test_validate_valid_id(self):
        """Test validating valid task IDs."""
        assert validate_task_id("1") == 1
        assert validate_task_id("42") == 42
        assert validate_task_id("999") == 999

    def test_validate_invalid_id(self):
        """Test validating invalid task IDs."""
        assert validate_task_id("0") is None
        assert validate_task_id("-1") is None
        assert validate_task_id("abc") is None
        assert validate_task_id("1.5") is None
        assert validate_task_id("") is None


class TestTextUtilities:
    """Test text utility functions."""

    def test_truncate_short_text(self):
        """Test truncating short text."""
        text = "Short text"
        result = truncate_text(text, 50)
        assert result == text

    def test_truncate_long_text(self):
        """Test truncating long text."""
        text = "This is a very long text that should be truncated"
        result = truncate_text(text, 20)
        assert result == "This is a very lo..."
        assert len(result) <= 20

    def test_truncate_exact_length(self):
        """Test truncating text of exact length."""
        text = "Exact length"
        result = truncate_text(text, 12)  # 12 characters to match actual text length
        assert result == text

    def test_sanitize_description(self):
        """Test sanitizing description."""
        result = sanitize_description(
            "  Multiple   spaces  and <script>alert('xss')</script>  "
        )
        assert result == "Multiple spaces and scriptalert(xss)/script"
        assert not result.startswith(" ")
        assert not result.endswith(" ")

    def test_sanitize_clean_text(self):
        """Test sanitizing already clean text."""
        text = "Clean description"
        result = sanitize_description(text)
        assert result == text


class TestDateValidation:
    """Test date validation."""

    def test_validate_valid_dates(self):
        """Test validating valid dates."""
        assert is_valid_date("today") is True
        assert is_valid_date("tomorrow") is True
        assert is_valid_date("2026-12-25") is True
        assert is_valid_date("+3d") is True

    def test_validate_invalid_dates(self):
        """Test validating invalid dates."""
        assert is_valid_date("not a date") is False
        assert is_valid_date("") is False
        # is_valid_date expects string, so we don't test with None
