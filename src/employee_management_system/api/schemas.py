"""Pydantic schemas for FastAPI requests and responses."""

from __future__ import annotations

from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field


class EmployeePayload(BaseModel):
    name: str = Field(..., min_length=1)
    empid: str = Field(..., min_length=4, max_length=20)
    emptype: Literal["Senior", "Junior", "Temporary"]
    salary: str
    available_leaves: int = Field(..., ge=0)
    leaves_taken: int = Field(..., ge=0)
    extra_hours: int = Field(..., ge=0)
    worked_days: int = Field(..., ge=0)


class EmployeeResponse(BaseModel):
    empname: str
    empid: str
    emptype: str
    working_days: int
    eligible_for_leave: bool
    extra_pay: Decimal
    total_salary: Decimal
    record_id: int | None = None


class HealthResponse(BaseModel):
    status: str
