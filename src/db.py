"""PostgreSQL persistence for employee records."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import psycopg
from psycopg import Connection

from emp_management import Employee
from settings import ConfigurationError, DatabaseConfig

CREATE_EMPLOYEES_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS employees (
    id BIGSERIAL PRIMARY KEY,
    empid VARCHAR(20) NOT NULL,
    empname VARCHAR(255) NOT NULL,
    emptype VARCHAR(20) NOT NULL,
    available_leaves INTEGER NOT NULL,
    worked_days INTEGER NOT NULL,
    extra_hrs_worked INTEGER NOT NULL,
    leaves_taken INTEGER NOT NULL,
    salary NUMERIC(12, 2) NOT NULL,
    extra_pay NUMERIC(12, 2) NOT NULL,
    total_pay NUMERIC(12, 2) NOT NULL,
    is_eligible BOOLEAN NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
"""

CHECK_DUPLICATE_EMPIDS_SQL = """
SELECT empid
FROM employees
GROUP BY empid
HAVING COUNT(*) > 1
LIMIT 1;
"""

ENSURE_EMPLOYEE_EMPID_UNIQUE_INDEX_SQL = """
CREATE UNIQUE INDEX IF NOT EXISTS employees_empid_unique_idx
ON employees (empid);
"""

UPSERT_EMPLOYEE_SQL = """
INSERT INTO employees (
    empid,
    empname,
    emptype,
    available_leaves,
    worked_days,
    extra_hrs_worked,
    leaves_taken,
    salary,
    extra_pay,
    total_pay,
    is_eligible
) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (empid) DO UPDATE
SET
    empname = EXCLUDED.empname,
    emptype = EXCLUDED.emptype,
    available_leaves = EXCLUDED.available_leaves,
    worked_days = EXCLUDED.worked_days,
    extra_hrs_worked = EXCLUDED.extra_hrs_worked,
    leaves_taken = EXCLUDED.leaves_taken,
    salary = EXCLUDED.salary,
    extra_pay = EXCLUDED.extra_pay,
    total_pay = EXCLUDED.total_pay,
    is_eligible = EXCLUDED.is_eligible,
    created_at = NOW()
RETURNING id;
"""


class DatabaseStoreError(RuntimeError):
    """Raised when PostgreSQL storage operations fail."""


class PostgresEmployeeStore:
    """Stores employee records in a local PostgreSQL database."""

    def __init__(self, config: DatabaseConfig | None = None) -> None:
        try:
            self.config = config or DatabaseConfig.from_env()
        except ConfigurationError as exc:
            raise DatabaseStoreError(str(exc)) from exc

    def _connect(self) -> Connection[Any]:
        try:
            if self.config.dsn:
                return psycopg.connect(
                    self.config.dsn,
                    connect_timeout=self.config.connect_timeout,
                )

            return psycopg.connect(
                host=self.config.host,
                port=self.config.port,
                dbname=self.config.dbname,
                user=self.config.user,
                password=self.config.password,
                connect_timeout=self.config.connect_timeout,
            )
        except psycopg.Error as exc:
            raise DatabaseStoreError(
                "Unable to connect to PostgreSQL. "
                "Check .env or EMP_DB_* variables and local DB status."
            ) from exc

    def save_employee(self, employee: Employee) -> int:
        extra_pay = employee.ExtraPay().quantize(Decimal("0.01"))
        total_pay = employee.getTotalPay().quantize(Decimal("0.01"))

        try:
            with self._connect() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(CREATE_EMPLOYEES_TABLE_SQL)
                    cursor.execute(CHECK_DUPLICATE_EMPIDS_SQL)
                    duplicate_empid = cursor.fetchone()
                    if duplicate_empid:
                        raise DatabaseStoreError(
                            "Cannot enforce unique empid because duplicates "
                            "already exist "
                            f"(example: {duplicate_empid[0]}). Remove duplicates first."
                        )

                    cursor.execute(ENSURE_EMPLOYEE_EMPID_UNIQUE_INDEX_SQL)
                    cursor.execute(
                        UPSERT_EMPLOYEE_SQL,
                        (
                            employee.empid,
                            employee.empname,
                            employee.emptype,
                            employee.available_leaves,
                            employee.worked_days,
                            employee.extra_hrs_worked,
                            employee.leaves_taken,
                            employee.salary,
                            extra_pay,
                            total_pay,
                            employee.isEligible(),
                        ),
                    )
                    record = cursor.fetchone()
        except psycopg.Error as exc:
            raise DatabaseStoreError(
                "Unable to store employee data in PostgreSQL."
            ) from exc

        if not record:
            raise DatabaseStoreError("Failed to fetch inserted employee record id.")

        return int(record[0])
