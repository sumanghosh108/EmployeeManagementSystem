from __future__ import annotations

from app import EXIT_SUCCESS, EXIT_VALIDATION_ERROR, main


def test_cli_success(capsys) -> None:
    exit_code = main(
        [
            "--name",
            "one",
            "--id",
            "1abc234",
            "--type",
            "Senior",
            "--salary",
            "30000",
            "--available_leaves",
            "12",
            "--leaves_taken",
            "2",
            "--extra_hours",
            "10",
            "--worked_days",
            "30",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == EXIT_SUCCESS
    assert "Employee Summary" in captured.out
    assert "Total Salary:" in captured.out
    assert captured.err == ""


def test_cli_validation_error(capsys) -> None:
    exit_code = main(
        [
            "--name",
            "one",
            "--id",
            "bad-id",
            "--type",
            "Senior",
            "--salary",
            "30000",
            "--available_leaves",
            "12",
            "--leaves_taken",
            "2",
            "--extra_hours",
            "10",
            "--worked_days",
            "30",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == EXIT_VALIDATION_ERROR
    assert "ERROR:" in captured.err
