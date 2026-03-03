"""Service layer for employee creation and persistence flow."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Protocol

from emp_management import Employee


class EmployeeStore(Protocol):
    """Contract for employee persistence backends."""

    def save_employee(self, employee: Employee) -> int: ...


@dataclass(frozen=True)
class EmployeeInput:
    """Input payload used by the service layer."""

    name: str
    empid: str
    emptype: str
    salary: str
    available_leaves: int
    leaves_taken: int
    extra_hours: int
    worked_days: int


def parse_salary(value: str) -> Decimal:
    try:
        return Decimal(value)
    except (InvalidOperation, ValueError) as exc:
        raise ValueError("salary must be a valid number") from exc


def build_employee(employee_input: EmployeeInput) -> Employee:
    return Employee(
        empname=employee_input.name,
        empid=employee_input.empid,
        emptype=employee_input.emptype,
        salary=parse_salary(employee_input.salary),
        available_leaves=employee_input.available_leaves,
        leaves_taken=employee_input.leaves_taken,
        extra_hrs_worked=employee_input.extra_hours,
        worked_days=employee_input.worked_days,
    )


def persist_employee(
    employee: Employee,
    store: EmployeeStore,
    enable_storage: bool = True,
) -> int | None:
    if not enable_storage:
        return None
    return store.save_employee(employee)
