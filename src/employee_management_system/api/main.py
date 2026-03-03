"""FastAPI application entrypoint."""

from __future__ import annotations

import uvicorn
from fastapi import FastAPI

from employee_management_system.api.routes import router

app = FastAPI(
    title="Employee Management System API",
    version="1.0.0",
)
app.include_router(router)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "message": "Employee Management System API is running",
        "docs": "/docs",
        "health": "/api/v1/health",
    }


def run() -> None:
    uvicorn.run(
        "employee_management_system.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
    )
