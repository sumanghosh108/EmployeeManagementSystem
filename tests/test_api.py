from __future__ import annotations

from fastapi.testclient import TestClient

from employee_management_system.api.dependencies import get_employee_store
from employee_management_system.api.main import app
from employee_management_system.domain.employee import Employee
from employee_management_system.storage.postgres_store import DatabaseStoreError


class FakeStore:
    def save_employee(self, employee: Employee) -> int:
        _ = employee
        return 21


class FailingStore:
    def save_employee(self, employee: Employee) -> int:
        _ = employee
        raise DatabaseStoreError("Database is unavailable")


def base_payload() -> dict[str, object]:
    return {
        "name": "one",
        "empid": "1abc234",
        "emptype": "Senior",
        "salary": "30000",
        "available_leaves": 12,
        "leaves_taken": 2,
        "extra_hours": 10,
        "worked_days": 30,
    }


def test_health_endpoint() -> None:
    client = TestClient(app)
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_root_endpoint() -> None:
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["docs"] == "/docs"


def test_preview_endpoint() -> None:
    client = TestClient(app)
    response = client.post("/api/v1/employees/preview", json=base_payload())
    payload = response.json()

    assert response.status_code == 200
    assert payload["empname"] == "one"
    assert payload["empid"] == "1abc234"
    assert payload["record_id"] is None


def test_create_or_update_endpoint_success() -> None:
    app.dependency_overrides[get_employee_store] = lambda: FakeStore()
    try:
        client = TestClient(app)
        response = client.post("/api/v1/employees", json=base_payload())
    finally:
        app.dependency_overrides.clear()

    payload = response.json()
    assert response.status_code == 200
    assert payload["record_id"] == 21


def test_create_or_update_endpoint_validation_error() -> None:
    app.dependency_overrides[get_employee_store] = lambda: FakeStore()
    try:
        client = TestClient(app)
        payload = base_payload()
        payload["empid"] = "bad-id"
        response = client.post("/api/v1/employees", json=payload)
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 400
    assert "empid must be 4-20 characters" in response.json()["detail"]


def test_create_or_update_endpoint_db_error() -> None:
    app.dependency_overrides[get_employee_store] = lambda: FailingStore()
    try:
        client = TestClient(app)
        response = client.post("/api/v1/employees", json=base_payload())
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 503
    assert response.json()["detail"] == "Database is unavailable"
