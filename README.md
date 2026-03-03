# Employee Management System

A small CLI application that models employee leave eligibility and payroll rules with production-grade basics:

- strict input validation
- Decimal-based money calculations
- structured CLI logging and exit codes
- automated tests, linting, typing, and CI

## Requirements

- Python 3.10

## Installation

```bash
python -m pip install --upgrade pip
pip install -e .
```

For development tools:

```bash
pip install -e .[dev]
```

## CLI Usage

After installation, run the console script:

```bash
employee-cli --name one --id 1abc234 --type Senior --salary 30000 --available_leaves 12 --leaves_taken 2 --extra_hours 10 --worked_days 30
```

You can also run directly:

```bash
python src/app.py --name one --id 1abc234 --type Senior --salary 30000 --available_leaves 12 --leaves_taken 2 --extra_hours 10 --worked_days 30
```

## Validation Rules

- `empid` must be 4-20 alphanumeric characters
- `type` must be one of `Senior`, `Junior`, `Temporary`
- numeric fields must be non-negative integers
- sensible caps are enforced:
  - `worked_days <= 31`
  - `leaves_taken <= 31`
  - `available_leaves <= 365`
  - `extra_hours <= 300`
  - `salary <= 10000000.00`

## Business Rules

- Extra pay per hour:
  - Senior: `300`
  - Junior: `200`
  - Temporary: `100`
- Leave deduction per day:
  - Senior: `200`
  - Junior: `100`
  - Temporary: `50`
- Total pay:
  - `salary - (leaves_taken * deduction_rate) + extra_pay`

## Development Commands

```bash
ruff check .
black --check .
mypy src
pytest -q
```

## CI

GitHub Actions runs lint, format check, type check, and tests on every push and pull request.
