# Employee Management System

A small CLI application that models employee leave eligibility and payroll rules with production-grade basics:

- strict input validation
- Decimal-based money calculations
- local PostgreSQL persistence for employee records
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

By default, each run stores employee data in PostgreSQL.

Run the console script:

```bash
employee-cli --name one --id 1abc234 --type Senior --salary 30000 --available_leaves 12 --leaves_taken 2 --extra_hours 10 --worked_days 30
```

You can also run directly:

```bash
python -m employee_management_system --name one --id 1abc234 --type Senior --salary 30000 --available_leaves 12 --leaves_taken 2 --extra_hours 10 --worked_days 30
```

Skip persistence when needed:

```bash
employee-cli --name one --id 1abc234 --type Senior --salary 30000 --available_leaves 12 --leaves_taken 2 --extra_hours 10 --worked_days 30 --no-store
```

## FastAPI Usage

Run API server:

```bash
employee-api
```

or

```bash
uvicorn employee_management_system.api.main:app --reload
```

API docs:

- `http://127.0.0.1:8000/docs`

Example preview request:

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/employees/preview" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "one",
    "empid": "1abc234",
    "emptype": "Senior",
    "salary": "30000",
    "available_leaves": 12,
    "leaves_taken": 2,
    "extra_hours": 10,
    "worked_days": 30
  }'
```

Example create/upsert request:

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/employees" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "one",
    "empid": "1abc234",
    "emptype": "Senior",
    "salary": "30000",
    "available_leaves": 12,
    "leaves_taken": 2,
    "extra_hours": 10,
    "worked_days": 30
  }'
```

## PostgreSQL Setup (Local)

1. Create a local database named `employee_management`.
2. Create a `.env` file in the project root:

```env
EMP_DB_HOST=localhost
EMP_DB_PORT=5432
EMP_DB_NAME=employee_management
EMP_DB_USER=postgres
EMP_DB_PASSWORD=postgres
EMP_DB_CONNECT_TIMEOUT=5
# EMP_DB_DSN=postgresql://postgres:postgres@localhost:5432/employee_management
```

You can copy from `.env.example`. `.env` is auto-loaded by the app.

3. Optional: set values directly in shell (overrides `.env`):

```cmd
set EMP_DB_HOST=localhost
set EMP_DB_PORT=5432
set EMP_DB_NAME=employee_management
set EMP_DB_USER=postgres
set EMP_DB_PASSWORD=postgres
set EMP_DB_CONNECT_TIMEOUT=5
```

On first successful write, table `employees` is created automatically.
`empid` is enforced as unique, and writes use upsert semantics (same `empid` updates existing row).

## Code Structure

- `src/employee_management_system/cli/app.py`: CLI argument parsing, logging, and summary output
- `src/employee_management_system/api/`: FastAPI app, routes, request/response schemas
- `src/employee_management_system/services/employee_service.py`: employee construction and persistence orchestration
- `src/employee_management_system/config/settings.py`: `.env` loading and database config parsing
- `src/employee_management_system/storage/postgres_store.py`: PostgreSQL table creation and insert/upsert logic
- `src/employee_management_system/domain/employee.py`: domain model and payroll/leave business rules

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

## Stored Columns

Each run inserts one row into `employees` with:

- input fields (`empid`, `empname`, `emptype`, `available_leaves`, `worked_days`, `extra_hrs_worked`, `leaves_taken`, `salary`)
- computed fields (`extra_pay`, `total_pay`, `is_eligible`)
- timestamp (`created_at`)

## Development Commands

```bash
ruff check .
black --check .
mypy src
pytest -q
```

## Current Flow

CLI (`cli/app.py`) -> service (`services/employee_service.py`) -> domain (`domain/employee.py`) -> storage (`storage/postgres_store.py`)
API (`api/routes.py`) -> service (`services/employee_service.py`) -> domain (`domain/employee.py`) -> storage (`storage/postgres_store.py`)

## CI

GitHub Actions runs lint, format check, type check, and tests on every push and pull request.
