"""CLI entrypoint for employee management."""

from __future__ import annotations

import argparse
import logging
import sys
from collections.abc import Sequence
from decimal import Decimal, InvalidOperation

from emp_management import Employee

EXIT_SUCCESS = 0
EXIT_VALIDATION_ERROR = 1
EXIT_UNEXPECTED_ERROR = 99


class MaxLevelFilter(logging.Filter):
    """Allow log records only up to a max level."""

    def __init__(self, max_level: int) -> None:
        super().__init__()
        self.max_level = max_level

    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno <= self.max_level


def configure_logging() -> logging.Logger:
    logger = logging.getLogger("employee_cli")

    logger.setLevel(logging.INFO)
    logger.propagate = False
    logger.handlers.clear()

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.INFO)
    stdout_handler.addFilter(MaxLevelFilter(logging.WARNING))
    stdout_handler.setFormatter(logging.Formatter("%(message)s"))

    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(logging.ERROR)
    stderr_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))

    logger.addHandler(stdout_handler)
    logger.addHandler(stderr_handler)
    return logger


LOGGER = configure_logging()


def get_currency_prefix() -> str:
    symbol = "₹"
    encoding = sys.stdout.encoding or "utf-8"

    try:
        symbol.encode(encoding)
    except UnicodeEncodeError:
        return "Rs."

    return symbol


def format_money(value: Decimal) -> str:
    normalized = value.quantize(Decimal("0.01"))
    as_text = format(normalized, "f")
    return as_text.rstrip("0").rstrip(".")


def parse_salary(value: str) -> Decimal:
    try:
        return Decimal(value)
    except (InvalidOperation, ValueError) as exc:
        raise ValueError("salary must be a valid number") from exc


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Employee Management CLI")
    parser.add_argument("--name", required=True)
    parser.add_argument("--id", required=True)
    parser.add_argument(
        "--type",
        required=True,
        choices=["Senior", "Junior", "Temporary"],
    )
    parser.add_argument("--salary", required=True)
    parser.add_argument("--available_leaves", type=int, required=True)
    parser.add_argument("--leaves_taken", type=int, required=True)
    parser.add_argument("--extra_hours", type=int, required=True)
    parser.add_argument("--worked_days", type=int, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    logger = configure_logging()
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        salary = parse_salary(args.salary)
        employee = Employee(
            empname=args.name,
            empid=args.id,
            emptype=args.type,
            salary=salary,
            available_leaves=args.available_leaves,
            leaves_taken=args.leaves_taken,
            extra_hrs_worked=args.extra_hours,
            worked_days=args.worked_days,
        )
    except ValueError as exc:
        logger.error(str(exc))
        return EXIT_VALIDATION_ERROR
    except Exception as exc:  # pragma: no cover
        logger.error("Unexpected error: %s", str(exc))
        return EXIT_UNEXPECTED_ERROR

    currency = get_currency_prefix()
    logger.info("")
    logger.info("===== Employee Summary =====")
    logger.info("Name: %s", employee.empname)
    logger.info("Working Days: %s", employee.getWorkingHours())
    logger.info("Eligible for Leave: %s", employee.isEligible())
    logger.info("Extra Pay: %s%s", currency, format_money(employee.ExtraPay()))
    logger.info("Total Salary: %s%s", currency, format_money(employee.getTotalPay()))
    logger.info("=============================")
    logger.info("")
    return EXIT_SUCCESS


if __name__ == "__main__":
    raise SystemExit(main())
