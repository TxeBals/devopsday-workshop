"""Due dates."""
from datetime import date, timedelta


def due_date(issue_date: date, days: int = 30) -> date:
    """Due date: issue date + `days` calendar days. If it falls on a Saturday or Sunday,
    it moves to the following Monday."""
    result = issue_date + timedelta(days=days)
    if result.weekday() == 5:
        result += timedelta(days=2)
    return result
