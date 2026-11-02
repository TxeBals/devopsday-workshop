# AGENTS.md — invoices project

- Python 3.11+, no external dependencies except pytest.
- Tests: `python -m pytest -q`. Always run them after changing code.
- Amounts in euros with 2 decimals and half-up rounding (use `decimal`, never `round()` on floats).
- Don't change the existing tests to make them pass: fix the code.
