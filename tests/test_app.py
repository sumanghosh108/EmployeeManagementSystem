from __future__ import annotations

from employee_management_system.cli.app import (
    EXIT_DATABASE_ERROR,
    EXIT_SUCCESS,
    EXIT_VALIDATION_ERROR,
    main,
)
from employee_management_system.domain.employee import Employee
from employee_management_system.storage.postgres_store import DatabaseStoreError


class FakeStore:
    def __init__(self) -> None:
        self.saved = False
        self.last_employee: Employee | None = None

    def save_employee(self, employee: Employee) -> int:
        self.saved = True
        self.last_employee = employee
        return 7


class FailingStore:
    def save_employee(self, employee: Employee) -> int:
        _ = employee
        raise DatabaseStoreError("Database is unavailable")


def base_args() -> list[str]:
    return [
        "--name",
        "one",
        "--id",
        "1abc234",
        "--type",
        "Senior",
        "--salary",
        "30000",
        "--available_leaves",
        "12",
        "--leaves_taken",
        "2",
        "--extra_hours",
        "10",
        "--worked_days",
        "30",
    ]


def test_cli_success_no_store(capsys) -> None:
    exit_code = main([*base_args(), "--no-store"])

    captured = capsys.readouterr()
    assert exit_code == EXIT_SUCCESS
    assert "Employee Summary" in captured.out
    assert "Total Salary:" in captured.out
    assert "Stored Record ID" not in captured.out
    assert captured.err == ""


def test_cli_validation_error(capsys) -> None:
    args = base_args()
    args[3] = "bad-id"
    exit_code = main([*args, "--no-store"])

    captured = capsys.readouterr()
    assert exit_code == EXIT_VALIDATION_ERROR
    assert "ERROR:" in captured.err


def test_cli_stores_to_database_when_enabled(capsys) -> None:
    store = FakeStore()
    exit_code = main(base_args(), store=store)

    captured = capsys.readouterr()
    assert exit_code == EXIT_SUCCESS
    assert store.saved is True
    assert store.last_employee is not None
    assert "Stored Record ID: 7" in captured.out


def test_cli_database_error(capsys) -> None:
    exit_code = main(base_args(), store=FailingStore())

    captured = capsys.readouterr()
    assert exit_code == EXIT_DATABASE_ERROR
    assert "ERROR: Database is unavailable" in captured.err
