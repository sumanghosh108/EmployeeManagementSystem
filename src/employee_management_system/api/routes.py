"""FastAPI routes for employee operations."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from employee_management_system.api.dependencies import get_employee_store
from employee_management_system.api.schemas import (
    EmployeePayload,
    EmployeeResponse,
    HealthResponse,
)
from employee_management_system.domain.employee import Employee
from employee_management_system.services.employee_service import (
    EmployeeInput,
    EmployeeStore,
    build_employee,
    persist_employee,
)
from employee_management_system.storage.postgres_store import DatabaseStoreError

router = APIRouter(prefix="/api/v1", tags=["employees"])


def _build_domain_employee(payload: EmployeePayload) -> Employee:
    try:
        return build_employee(
            EmployeeInput(
                name=payload.name,
                empid=payload.empid,
                emptype=payload.emptype,
                salary=payload.salary,
                available_leaves=payload.available_leaves,
                leaves_taken=payload.leaves_taken,
                extra_hours=payload.extra_hours,
                worked_days=payload.worked_days,
            )
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


def _build_response(
    employee: Employee,
    record_id: int | None,
) -> EmployeeResponse:
    return EmployeeResponse(
        empname=employee.empname,
        empid=employee.empid,
        emptype=employee.emptype,
        working_days=employee.getWorkingHours(),
        eligible_for_leave=employee.isEligible(),
        extra_pay=employee.ExtraPay(),
        total_salary=employee.getTotalPay(),
        record_id=record_id,
    )


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse(status="ok")


@router.post("/employees/preview", response_model=EmployeeResponse)
def preview_employee(payload: EmployeePayload) -> EmployeeResponse:
    employee = _build_domain_employee(payload)
    return _build_response(employee, record_id=None)


@router.post("/employees", response_model=EmployeeResponse)
def create_or_update_employee(
    payload: EmployeePayload,
    store: Annotated[EmployeeStore, Depends(get_employee_store)],
) -> EmployeeResponse:
    employee = _build_domain_employee(payload)
    try:
        record_id = persist_employee(
            employee,
            store,
            enable_storage=True,
        )
    except DatabaseStoreError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    return _build_response(employee, record_id=record_id)
