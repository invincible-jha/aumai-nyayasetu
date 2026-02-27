"""Tests for the aumai-nyayasetu CLI.

LEGAL DISCLAIMER: This test suite is for software testing purposes only.
Consult a qualified legal professional before taking any legal action.
"""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from aumai_nyayasetu.cli import main


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


def test_cli_version(runner: CliRunner) -> None:
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.output


def test_cli_help(runner: CliRunner) -> None:
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "NyayaSetu" in result.output or "legal" in result.output.lower()


def test_rights_command_no_args_lists_all(runner: CliRunner) -> None:
    result = runner.invoke(main, ["rights"])
    assert result.exit_code == 0
    assert "Found" in result.output


def test_rights_command_category_fundamental(runner: CliRunner) -> None:
    result = runner.invoke(main, ["rights", "--category", "fundamental"])
    assert result.exit_code == 0
    assert "fundamental" in result.output.lower() or "Equality" in result.output

def test_rights_command_category_women(runner: CliRunner) -> None:
    result = runner.invoke(main, ["rights", "--category", "women"])
    assert result.exit_code == 0


def test_rights_command_search_keyword(runner: CliRunner) -> None:
    result = runner.invoke(main, ["rights", "--search", "equality"])
    assert result.exit_code == 0
    assert "Equality" in result.output or "Found" in result.output


def test_rights_command_json_output(runner: CliRunner) -> None:
    result = runner.invoke(main, ["rights", "--json-output"])
    assert result.exit_code == 0
    assert result.output.strip().startswith("[")


def test_rights_command_shows_disclaimer(runner: CliRunner) -> None:
    result = runner.invoke(main, ["rights"])
    assert "legal advice" in result.output.lower() or "DISCLAIMER" in result.output


def test_eligible_command_low_income_eligible(runner: CliRunner) -> None:
    result = runner.invoke(main, ["eligible", "--income", "100000"])
    assert result.exit_code == 0
    assert "ELIGIBLE" in result.output


def test_eligible_command_high_income_not_eligible(runner: CliRunner) -> None:
    result = runner.invoke(main, ["eligible", "--income", "5000000"])
    assert result.exit_code == 0
    assert "NOT ELIGIBLE" in result.output


def test_eligible_command_women_category_exempt(runner: CliRunner) -> None:
    result = runner.invoke(main, ["eligible", "--income", "9999999", "--category", "women"])
    assert result.exit_code == 0
    assert "ELIGIBLE" in result.output


def test_eligible_command_sc_st_flag(runner: CliRunner) -> None:
    result = runner.invoke(main, ["eligible", "--income", "400000", "--sc-st"])
    assert result.exit_code == 0
    assert "ELIGIBLE" in result.output


def test_eligible_command_shows_disclaimer(runner: CliRunner) -> None:
    result = runner.invoke(main, ["eligible", "--income", "100000"])
    assert "legal advice" in result.output.lower() or "DISCLAIMER" in result.output


def test_centers_command_no_args(runner: CliRunner) -> None:
    result = runner.invoke(main, ["centers"])
    assert result.exit_code == 0
    assert "Found" in result.output


def test_centers_command_filter_by_state(runner: CliRunner) -> None:
    result = runner.invoke(main, ["centers", "--state", "Delhi"])
    assert result.exit_code == 0
    assert "Delhi" in result.output


def test_centers_command_filter_by_district(runner: CliRunner) -> None:
    result = runner.invoke(main, ["centers", "--district", "Mumbai"])
    assert result.exit_code == 0
    assert "Mumbai" in result.output


def test_centers_command_shows_helplines(runner: CliRunner) -> None:
    result = runner.invoke(main, ["centers"])
    assert "NALSA" in result.output or "15100" in result.output


def test_centers_command_nonexistent_state(runner: CliRunner) -> None:
    result = runner.invoke(main, ["centers", "--state", "NonExistentState99"])
    assert result.exit_code == 0
    assert "0" in result.output or "Found 0" in result.output


def test_documents_command_fir(runner: CliRunner) -> None:
    result = runner.invoke(main, ["documents", "--procedure", "fir"])
    assert result.exit_code == 0
    assert "FIR" in result.output


def test_documents_command_bail(runner: CliRunner) -> None:
    result = runner.invoke(main, ["documents", "--procedure", "bail"])
    assert result.exit_code == 0
    assert "Bail" in result.output or "bail" in result.output.lower()


def test_documents_command_consumer(runner: CliRunner) -> None:
    result = runner.invoke(main, ["documents", "--procedure", "consumer"])
    assert result.exit_code == 0
    assert "Consumer" in result.output


def test_documents_command_rti(runner: CliRunner) -> None:
    result = runner.invoke(main, ["documents", "--procedure", "rti"])
    assert result.exit_code == 0
    assert "RTI" in result.output or "Information" in result.output


def test_documents_command_domestic_violence(runner: CliRunner) -> None:
    result = runner.invoke(main, ["documents", "--procedure", "domestic_violence"])
    assert result.exit_code == 0


def test_documents_command_unknown_procedure(runner: CliRunner) -> None:
    result = runner.invoke(main, ["documents", "--procedure", "nonexistentprocedure"])
    assert result.exit_code == 0
    assert "Unknown" in result.output or "Available" in result.output


def test_help_command_fir_query(runner: CliRunner) -> None:
    result = runner.invoke(main, ["help", "--query", "how to file an FIR at police"])
    assert result.exit_code == 0


def test_help_command_bail_query(runner: CliRunner) -> None:
    result = runner.invoke(main, ["help", "--query", "someone is under arrest custody"])
    assert result.exit_code == 0


def test_help_command_shows_disclaimer(runner: CliRunner) -> None:
    result = runner.invoke(main, ["help", "--query", "domestic violence abuse"])
    assert "DISCLAIMER" in result.output or "legal advice" in result.output.lower()


def test_help_command_unmatched_query(runner: CliRunner) -> None:
    result = runner.invoke(main, ["help", "--query", "xyzunknownissuexyz999"])
    assert result.exit_code == 0
    assert "No specific matches" in result.output or "DISCLAIMER" in result.output
