"""Core domain model for employee leave and payroll logic."""

from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import ClassVar


@dataclass(slots=True)
class Employee:
    """Represents one employee for leave eligibility and payroll calculation."""

    empname: str
    empid: str
    emptype: str
    available_leaves: int
    worked_days: int
    extra_hrs_worked: int
    leaves_taken: int
    salary: Decimal

    VALID_TYPES: ClassVar[tuple[str, ...]] = ("Senior", "Junior", "Temporary")
    EXTRA_PAY_RATE: ClassVar[dict[str, Decimal]] = {
        "Senior": Decimal("300"),
        "Junior": Decimal("200"),
        "Temporary": Decimal("100"),
    }
    LEAVE_DEDUCTION_RATE: ClassVar[dict[str, Decimal]] = {
        "Senior": Decimal("200"),
        "Junior": Decimal("100"),
        "Temporary": Decimal("50"),
    }
    EMP_ID_PATTERN: ClassVar[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9]{4,20}$")
    MAX_WORKED_DAYS: ClassVar[int] = 31
    MAX_EXTRA_HOURS: ClassVar[int] = 300
    MAX_LEAVES_TAKEN: ClassVar[int] = 31
    MAX_AVAILABLE_LEAVES: ClassVar[int] = 365
    MAX_SALARY: ClassVar[Decimal] = Decimal("10000000.00")

    def __post_init__(self) -> None:
        self.empname = self.empname.strip()
        self.empid = self.empid.strip()
        self.emptype = self.emptype.strip()
        self.salary = self._to_decimal(self.salary, "salary")

        self._validate_name()
        self._validate_employee_type()
        self._validate_employee_id()
        self._validate_int_field(
            value=self.available_leaves,
            field_name="available_leaves",
            minimum=0,
            maximum=self.MAX_AVAILABLE_LEAVES,
        )
        self._validate_int_field(
            value=self.leaves_taken,
            field_name="leaves_taken",
            minimum=0,
            maximum=self.MAX_LEAVES_TAKEN,
        )
        self._validate_int_field(
            value=self.worked_days,
            field_name="worked_days",
            minimum=0,
            maximum=self.MAX_WORKED_DAYS,
        )
        self._validate_int_field(
            value=self.extra_hrs_worked,
            field_name="extra_hrs_worked",
            minimum=0,
            maximum=self.MAX_EXTRA_HOURS,
        )
        if self.salary < Decimal("0"):
            raise ValueError("salary must be non-negative")
        if self.salary > self.MAX_SALARY:
            raise ValueError(f"salary must be <= {self.MAX_SALARY}")

    @staticmethod
    def _to_decimal(value: object, field_name: str) -> Decimal:
        try:
            decimal_value = Decimal(str(value))
        except (InvalidOperation, ValueError) as exc:
            raise ValueError(f"{field_name} must be a valid number") from exc
        return decimal_value.quantize(Decimal("0.01"))

    @staticmethod
    def _validate_int_field(
        value: int,
        field_name: str,
        minimum: int,
        maximum: int,
    ) -> None:
        if not isinstance(value, int):
            raise ValueError(f"{field_name} must be an integer")
        if value < minimum:
            raise ValueError(f"{field_name} must be >= {minimum}")
        if value > maximum:
            raise ValueError(f"{field_name} must be <= {maximum}")

    def _validate_name(self) -> None:
        if not self.empname:
            raise ValueError("empname must not be empty")

    def _validate_employee_id(self) -> None:
        if not self.EMP_ID_PATTERN.fullmatch(self.empid):
            raise ValueError(
                "empid must be 4-20 characters and contain only letters and numbers"
            )

    def _validate_employee_type(self) -> None:
        if self.emptype not in self.VALID_TYPES:
            raise ValueError(
                f"Invalid employee type: '{self.emptype}'. "
                f"Valid types are: {self.VALID_TYPES}"
            )

    def getWorkingHours(self) -> int:
        """Return total worked days for the pay period."""
        return self.worked_days

    def isEligible(self) -> bool:
        """Return True when requested leaves are within available balance."""
        return self.leaves_taken <= self.available_leaves

    def getTotalPay(self) -> Decimal:
        """Return total salary after leave deduction and extra-hour addition."""
        leave_deduction = (
            Decimal(self.leaves_taken) * self.LEAVE_DEDUCTION_RATE[self.emptype]
        )
        extra_pay = self.ExtraPay()
        return self.salary - leave_deduction + extra_pay

    def ExtraPay(self) -> Decimal:
        """Return extra pay based on employee type and extra worked hours."""
        rate = self.EXTRA_PAY_RATE[self.emptype]
        return Decimal(self.extra_hrs_worked) * rate
