from __future__ import annotations

from decimal import Decimal

import pytest

from employee_management_system.domain.employee import Employee


def build_employee(**overrides: object) -> Employee:
    data: dict[str, object] = {
        "empname": "one",
        "empid": "1abc234",
        "emptype": "Senior",
        "available_leaves": 12,
        "worked_days": 30,
        "extra_hrs_worked": 10,
        "leaves_taken": 2,
        "salary": "30000",
    }
    data.update(overrides)
    return Employee(**data)


def test_get_working_hours() -> None:
    employee = build_employee(worked_days=21)
    assert employee.getWorkingHours() == 21


@pytest.mark.parametrize(
    ("leaves_taken", "expected"),
    [
        (2, True),
        (12, True),
        (13, False),
    ],
)
def test_is_eligible(leaves_taken: int, expected: bool) -> None:
    employee = build_employee(leaves_taken=leaves_taken)
    assert employee.isEligible() is expected


@pytest.mark.parametrize(
    ("emptype", "extra_hrs_worked", "expected"),
    [
        ("Senior", 4, Decimal("1200")),
        ("Junior", 4, Decimal("800")),
        ("Temporary", 4, Decimal("400")),
    ],
)
def test_extra_pay_by_employee_type(
    emptype: str,
    extra_hrs_worked: int,
    expected: Decimal,
) -> None:
    employee = build_employee(emptype=emptype, extra_hrs_worked=extra_hrs_worked)
    assert employee.ExtraPay() == expected


def test_total_pay_uses_decimal_math() -> None:
    employee = build_employee()
    assert employee.getTotalPay() == Decimal("32600.00")


@pytest.mark.parametrize(
    ("field", "value", "error_message"),
    [
        ("salary", "-1", "salary must be non-negative"),
        ("available_leaves", -1, "available_leaves must be >= 0"),
        ("leaves_taken", -1, "leaves_taken must be >= 0"),
        ("worked_days", -1, "worked_days must be >= 0"),
        ("extra_hrs_worked", -1, "extra_hrs_worked must be >= 0"),
    ],
)
def test_negative_values_rejected(
    field: str,
    value: object,
    error_message: str,
) -> None:
    with pytest.raises(ValueError, match=error_message):
        build_employee(**{field: value})


def test_invalid_employee_type_rejected() -> None:
    with pytest.raises(ValueError, match="Invalid employee type"):
        build_employee(emptype="Intern")


def test_invalid_employee_id_rejected() -> None:
    with pytest.raises(ValueError, match="empid must be 4-20 characters"):
        build_employee(empid="bad-id")
