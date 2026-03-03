"""Dependencies used by FastAPI routes."""

from __future__ import annotations

from employee_management_system.services.employee_service import EmployeeStore
from employee_management_system.storage.postgres_store import PostgresEmployeeStore


def get_employee_store() -> EmployeeStore:
    return PostgresEmployeeStore()
