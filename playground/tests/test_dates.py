from datetime import date

from invoices.dates import due_date


def test_due_date_weekday():
    assert due_date(date(2026, 3, 2), 30) == date(2026, 4, 1)  # Wednesday


def test_due_date_saturday_moves_to_monday():
    assert due_date(date(2026, 3, 5), 30) == date(2026, 4, 6)  # 4 Apr is a Saturday -> Monday 6


def test_due_date_sunday_moves_to_monday():
    assert due_date(date(2026, 3, 6), 30) == date(2026, 4, 6)  # 5 Apr is a Sunday -> Monday 6
