"""Quickstart examples for aumai-nyayasetu.

This script demonstrates the five core workflows:
  1. Browsing and searching legal rights
  2. Checking eligibility for free legal aid
  3. Finding legal aid centres
  4. Getting document checklists for legal procedures
  5. Getting advice for a described legal issue

Run directly to verify your installation:

    python examples/quickstart.py

Legal Disclaimer: This tool does NOT provide legal advice. All information is
for general awareness only. Consult a qualified legal professional before taking
any legal action.
"""

from __future__ import annotations

from aumai_nyayasetu.core import (
    DISCLAIMER,
    DocumentHelper,
    EligibilityChecker,
    LegalAidDirectory,
    RightsAdvisor,
    RightsDatabase,
)
from aumai_nyayasetu.models import RightsCategory


def demo_rights_database() -> None:
    """Demonstrate RightsDatabase search and category browsing.

    The database contains 14 built-in LegalRight objects across 10 categories.
    Rights can be retrieved by category enum, keyword search, or exact code.
    """
    print("\n" + "=" * 60)
    print("DEMO 1: Rights Database")
    print("=" * 60)

    db = RightsDatabase()

    # Count all rights
    all_rights = db.all_rights()
    print(f"\nTotal rights in database: {len(all_rights)}")

    # List rights by category
    print("\nFundamental Rights:")
    for right in db.by_category(RightsCategory.FUNDAMENTAL):
        print(f"  [{right.code}] {right.name}")
        print(f"    Law: {right.relevant_law}")

    # Keyword search
    print("\nKeyword search: 'wage'")
    wage_rights = db.search("wage")
    for right in wage_rights:
        print(f"  [{right.code}] {right.name} — {right.relevant_law}")

    # Keyword search: women's rights
    print("\nKeyword search: 'domestic'")
    domestic_rights = db.search("domestic")
    for right in domestic_rights:
        print(f"  [{right.code}] {right.name}")
        print(f"    How to claim: {right.how_to_claim}")
        if right.documents_needed:
            print(f"    Documents: {', '.join(right.documents_needed)}")

    # Exact code lookup
    print("\nLookup by code: FR-04")
    fr04 = db.get_by_code("FR-04")
    if fr04:
        print(f"  Name: {fr04.name}")
        print(f"  Description: {fr04.description}")

    # Non-existent code
    missing = db.get_by_code("XX-99")
    print(f"\nLookup non-existent code XX-99: {missing}")  # None


def demo_eligibility_checker() -> None:
    """Demonstrate EligibilityChecker across different income and category scenarios.

    Free legal aid thresholds in India:
    - General: Rs 3,00,000/year
    - SC/ST: Rs 5,00,000/year
    - Women, children, persons with disabilities, custody cases: income exempt
    """
    print("\n" + "=" * 60)
    print("DEMO 2: Eligibility for Free Legal Aid")
    print("=" * 60)

    checker = EligibilityChecker()

    scenarios = [
        # (description, income, category, is_sc_st)
        ("General applicant — Rs 2.5L", 250000, None, False),
        ("General applicant — Rs 3.5L (above threshold)", 350000, None, False),
        ("SC/ST applicant — Rs 4.5L", 450000, None, True),
        ("SC/ST applicant — Rs 5.5L (above SC/ST threshold)", 550000, None, True),
        ("Woman (any income) — Rs 10L", 1000000, "women", False),
        ("Child (any income) — Rs 0", 0, "children", False),
        ("Person with disability — Rs 8L", 800000, "disability", False),
    ]

    for description, income, category, is_sc_st in scenarios:
        result = checker.check(
            annual_income=income,
            category=category,
            is_sc_st=is_sc_st,
        )
        status = "ELIGIBLE" if result.eligible else "NOT ELIGIBLE"
        print(f"\n  {description}")
        print(f"    {status} — {result.reason}")
        if result.criteria_met:
            for c in result.criteria_met:
                print(f"    [OK] {c}")
        if result.criteria_not_met:
            for c in result.criteria_not_met:
                print(f"    [X]  {c}")

    # Demonstrate ValueError for negative income
    print("\n  Negative income raises ValueError:")
    try:
        checker.check(annual_income=-1)
    except ValueError as exc:
        print(f"    ValueError: {exc}")


def demo_legal_aid_directory() -> None:
    """Demonstrate LegalAidDirectory search by state and district.

    The built-in directory contains 7 DLSA centres across major Indian cities.
    National helplines are always available regardless of location.
    """
    print("\n" + "=" * 60)
    print("DEMO 3: Legal Aid Directory")
    print("=" * 60)

    directory = LegalAidDirectory()

    # All centres
    all_centres = directory.all_centers()
    print(f"\nTotal DLSA centres in directory: {len(all_centres)}")

    # Filter by state
    print("\nCentres in Maharashtra:")
    mah_centres = directory.find_by_state("Maharashtra")
    for centre in mah_centres:
        print(f"  {centre.name} ({centre.district})")
        print(f"  Phone: {centre.phone}")
        print(f"  Services: {', '.join(centre.services)}")
        print(f"  Free service: {centre.free_service}")

    # Filter by district
    print("\nCentres in Bangalore:")
    blr_centres = directory.find_by_district("Bangalore")
    for centre in blr_centres:
        print(f"  {centre.name} — {centre.address}")

    # National helplines (always available)
    print("\nNational Helplines:")
    print("  NALSA (legal aid):  15100")
    print("  Women Helpline:     181")
    print("  Childline:          1098")


def demo_document_helper() -> None:
    """Demonstrate DocumentHelper for retrieving step-by-step legal procedures.

    Knowing which documents to bring and what steps to follow before visiting
    a police station, court, or consumer forum can prevent delays and refusals.
    """
    print("\n" + "=" * 60)
    print("DEMO 4: Document Checklists and Procedures")
    print("=" * 60)

    helper = DocumentHelper()

    # List all available procedures
    all_procs = helper.all_procedures()
    print(f"\nAvailable procedures: {len(all_procs)}")
    for proc in all_procs:
        print(f"  - {proc.name} | Timeline: {proc.timeline} | Cost: {proc.cost}")

    # Full detail for FIR
    print("\nDetailed procedure: Filing an FIR")
    fir = helper.get_procedure("fir")
    if fir:
        print(f"  {fir.description}\n")
        print("  Steps:")
        for i, step in enumerate(fir.steps, 1):
            print(f"    {i}. {step}")
        print("\n  Documents needed:")
        for doc in fir.documents:
            print(f"    - {doc}")

    # Partial name lookup — "Consumer"
    print("\nPartial name lookup: 'Consumer'")
    consumer = helper.get_procedure("Consumer")
    if consumer:
        print(f"  Found: {consumer.name}")
        print(f"  Timeline: {consumer.timeline}")
        print(f"  Cost: {consumer.cost}")

    # Non-existent procedure
    unknown = helper.get_procedure("random_procedure")
    print(f"\nNon-existent procedure result: {unknown}")  # None


def demo_rights_advisor() -> None:
    """Demonstrate RightsAdvisor for keyword-based legal issue matching.

    RightsAdvisor combines RightsDatabase search and procedure keyword
    matching to give a one-stop response to a described legal situation.
    The disclaimer is always included in the result and cannot be suppressed.
    """
    print("\n" + "=" * 60)
    print("DEMO 5: Rights Advisor")
    print("=" * 60)

    advisor = RightsAdvisor()

    queries = [
        "my employer is not paying minimum wages for three months",
        "husband threatening domestic violence, need protection",
        "police are refusing to register my FIR",
        "I was discriminated against based on my caste",
    ]

    for query in queries:
        print(f"\nQuery: \"{query}\"")
        result = advisor.advise(query)

        if result.rights:
            print(f"  Relevant rights ({len(result.rights)}):")
            for right in result.rights:
                print(f"    [{right.code}] {right.name} — {right.relevant_law}")

        if result.procedures:
            print(f"  Relevant procedures ({len(result.procedures)}):")
            for proc in result.procedures:
                print(f"    - {proc.name}: {proc.description[:70]}...")

        if not result.rights and not result.procedures:
            print("  No direct matches found.")

    # Disclaimer is always present on every QueryResult
    result = advisor.advise("test")
    print(f"\n{result.disclaimer}")


def main() -> None:
    """Run all quickstart demonstrations."""
    print("aumai-nyayasetu Quickstart")
    print(f"\nDISCLAIMER: {DISCLAIMER}")

    demo_rights_database()
    demo_eligibility_checker()
    demo_legal_aid_directory()
    demo_document_helper()
    demo_rights_advisor()

    print("\n" + "=" * 60)
    print("All demos complete.")
    print("See docs/api-reference.md for full API documentation.")
    print("=" * 60)


if __name__ == "__main__":
    main()
