from __future__ import annotations

from decimal import Decimal

import pytest

from emp_management import Employee
from employee_service import (
    EmployeeInput,
    build_employee,
    parse_salary,
    persist_employee,
)


class CountingStore:
    def __init__(self) -> None:
        self.calls = 0

    def save_employee(self, employee: Employee) -> int:
        _ = employee
        self.calls += 1
        return 11


def test_parse_salary_returns_decimal() -> None:
    assert parse_salary("30000.50") == Decimal("30000.50")


def test_parse_salary_invalid_raises() -> None:
    with pytest.raises(ValueError, match="salary must be a valid number"):
        parse_salary("bad-value")


def test_build_employee_from_input() -> None:
    employee = build_employee(
        EmployeeInput(
            name="one",
            empid="1abc234",
            emptype="Senior",
            salary="30000",
            available_leaves=12,
            leaves_taken=2,
            extra_hours=10,
            worked_days=30,
        )
    )

    assert employee.empname == "one"
    assert employee.empid == "1abc234"
    assert employee.salary == Decimal("30000.00")


def test_persist_employee_skips_when_disabled() -> None:
    store = CountingStore()
    employee = build_employee(
        EmployeeInput(
            name="one",
            empid="1abc234",
            emptype="Senior",
            salary="30000",
            available_leaves=12,
            leaves_taken=2,
            extra_hours=10,
            worked_days=30,
        )
    )

    record_id = persist_employee(employee, store, enable_storage=False)
    assert record_id is None
    assert store.calls == 0
