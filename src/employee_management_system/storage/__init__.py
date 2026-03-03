"""Storage adapters."""

from employee_management_system.storage.postgres_store import (
    CHECK_DUPLICATE_EMPIDS_SQL,
    ENSURE_EMPLOYEE_EMPID_UNIQUE_INDEX_SQL,
    UPSERT_EMPLOYEE_SQL,
    DatabaseStoreError,
    PostgresEmployeeStore,
)

__all__ = [
    "CHECK_DUPLICATE_EMPIDS_SQL",
    "ENSURE_EMPLOYEE_EMPID_UNIQUE_INDEX_SQL",
    "UPSERT_EMPLOYEE_SQL",
    "DatabaseStoreError",
    "PostgresEmployeeStore",
]
