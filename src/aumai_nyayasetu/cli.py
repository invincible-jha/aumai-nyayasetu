"""CLI entry point for aumai-nyayasetu."""

from __future__ import annotations

import json

import click

from aumai_nyayasetu.core import (
    DISCLAIMER as _DISCLAIMER_TEXT,
    DocumentHelper,
    EligibilityChecker,
    LegalAidDirectory,
    RightsAdvisor,
    RightsDatabase,
)
from aumai_nyayasetu.models import RightsCategory

_DISCLAIMER = f"\nDISCLAIMER: {_DISCLAIMER_TEXT}\n"


@click.group()
@click.version_option()
def cli() -> None:
    """AumAI NyayaSetu - Legal aid and rights awareness for India."""


@cli.command()
@click.option("--category", type=click.Choice([c.value for c in RightsCategory]), help="Filter by category")
@click.option("--search", "query", default=None, help="Search by keyword")
@click.option("--json-output", is_flag=True, help="Output as JSON")
def rights(category: str | None, query: str | None, json_output: bool) -> None:
    """Search and list legal rights."""
    db = RightsDatabase()

    if query:
        results = db.search(query)
    elif category:
        results = db.by_category(RightsCategory(category))
    else:
        results = db.all_rights()

    if json_output:
        click.echo(json.dumps([r.model_dump() for r in results], indent=2, ensure_ascii=False))
        return

    for right in results:
        click.echo(f"\n[{right.code}] {right.name}")
        click.echo(f"  Category: {right.category.value}")
        click.echo(f"  Law: {right.relevant_law}")
        click.echo(f"  {right.description}")
        click.echo(f"  How to claim: {right.how_to_claim}")
        if right.documents_needed:
            click.echo(f"  Documents: {', '.join(right.documents_needed)}")

    click.echo(f"\nFound {len(results)} right(s).")
    click.echo(_DISCLAIMER)


@cli.command()
@click.option("--income", required=True, type=float, help="Annual income in INR")
@click.option("--category", default=None, help="Special category (women/children/sc_st/disability)")
@click.option("--sc-st", is_flag=True, help="Applicant is SC/ST")
def eligible(income: float, category: str | None, sc_st: bool) -> None:
    """Check eligibility for free legal aid."""
    checker = EligibilityChecker()
    result = checker.check(annual_income=income, category=category, is_sc_st=sc_st)

    if result.eligible:
        click.echo(f"\n  ELIGIBLE for free legal aid")
    else:
        click.echo(f"\n  NOT ELIGIBLE for free legal aid")

    click.echo(f"  Reason: {result.reason}")
    if result.criteria_met:
        for c in result.criteria_met:
            click.echo(f"    [OK] {c}")
    if result.criteria_not_met:
        for c in result.criteria_not_met:
            click.echo(f"    [X]  {c}")

    click.echo(f"\n  Income threshold: Rs {result.income_threshold:,.0f}/year")
    click.echo(_DISCLAIMER)


@cli.command()
@click.option("--state", default=None, help="Filter by state")
@click.option("--district", default=None, help="Filter by district")
def centers(state: str | None, district: str | None) -> None:
    """Find legal aid centers near you."""
    directory = LegalAidDirectory()

    if district:
        results = directory.find_by_district(district)
    elif state:
        results = directory.find_by_state(state)
    else:
        results = directory.all_centers()

    for center in results:
        click.echo(f"\n  {center.name}")
        click.echo(f"  District: {center.district}, {center.state}")
        if center.address:
            click.echo(f"  Address: {center.address}")
        if center.phone:
            click.echo(f"  Phone: {center.phone}")
        if center.services:
            click.echo(f"  Services: {', '.join(center.services)}")
        click.echo(f"  Free service: {'Yes' if center.free_service else 'No'}")

    click.echo(f"\nFound {len(results)} center(s).")
    click.echo("\nHelplines: NALSA 15100 | Women 181 | Childline 1098")
    click.echo(_DISCLAIMER)


@cli.command()
@click.option("--procedure", required=True, help="Procedure name (fir/bail/consumer/rti/domestic_violence)")
def documents(procedure: str) -> None:
    """Get document checklist for a legal procedure."""
    helper = DocumentHelper()
    proc = helper.get_procedure(procedure)

    if proc is None:
        click.echo(f"Unknown procedure: {procedure}")
        click.echo("Available: " + ", ".join(p.name for p in helper.all_procedures()))
        return

    click.echo(f"\n{'='*55}")
    click.echo(f"  {proc.name}")
    click.echo(f"{'='*55}")
    click.echo(f"\n{proc.description}\n")

    click.echo("Steps:")
    for step in proc.steps:
        click.echo(f"  {step}")

    click.echo("\nDocuments needed:")
    for doc in proc.documents:
        click.echo(f"  - {doc}")

    click.echo(f"\nTimeline: {proc.timeline}")
    click.echo(f"Cost: {proc.cost}")
    click.echo(_DISCLAIMER)


@cli.command(name="help")
@click.option("--query", required=True, help="Describe your legal issue")
def help_cmd(query: str) -> None:
    """Get matched rights and procedures for your legal issue."""
    advisor = RightsAdvisor()
    result = advisor.advise(query)

    if result.rights:
        click.echo(f"\nRelevant Rights ({len(result.rights)}):")
        for r in result.rights:
            click.echo(f"  [{r.code}] {r.name} - {r.relevant_law}")

    if result.procedures:
        click.echo(f"\nRelevant Procedures ({len(result.procedures)}):")
        for p in result.procedures:
            click.echo(f"  - {p.name}: {p.description[:80]}...")

    if not result.rights and not result.procedures:
        click.echo("\nNo specific matches found. Try different keywords or browse by category with 'rights --category'")

    click.echo(_DISCLAIMER)


main = cli

if __name__ == "__main__":
    cli()
