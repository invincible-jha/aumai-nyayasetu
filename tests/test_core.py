"""Comprehensive tests for aumai-nyayasetu core and models.

LEGAL DISCLAIMER: This test suite is for software testing purposes only.
The legal information used does not constitute legal advice.
Consult a qualified legal professional for any legal matters.
"""

from __future__ import annotations

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from pydantic import ValidationError

from aumai_nyayasetu.core import (
    DocumentHelper,
    EligibilityChecker,
    LegalAidDirectory,
    RightsAdvisor,
    RightsDatabase,
)
from aumai_nyayasetu.models import (
    EligibilityCheck,
    LegalAidCenter,
    LegalProcedure,
    LegalRight,
    QueryResult,
    RightsCategory,
)

_DISCLAIMER = (
    "This tool does NOT provide legal advice. All information is for general awareness only. "
    "Consult a qualified legal professional before taking any legal action."
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def rights_db() -> RightsDatabase:
    return RightsDatabase()


@pytest.fixture()
def eligibility_checker() -> EligibilityChecker:
    return EligibilityChecker()


@pytest.fixture()
def directory() -> LegalAidDirectory:
    return LegalAidDirectory()


@pytest.fixture()
def advisor() -> RightsAdvisor:
    return RightsAdvisor()


@pytest.fixture()
def doc_helper() -> DocumentHelper:
    return DocumentHelper()


# ---------------------------------------------------------------------------
# RightsCategory enum tests
# ---------------------------------------------------------------------------


class TestRightsCategory:
    def test_all_expected_categories_exist(self) -> None:
        categories = [c.value for c in RightsCategory]
        assert "fundamental" in categories
        assert "labor" in categories
        assert "consumer" in categories
        assert "women" in categories
        assert "sc_st" in categories
        assert "children" in categories
        assert "disability" in categories

    def test_enum_str_value(self) -> None:
        assert RightsCategory.FUNDAMENTAL == "fundamental"
        assert RightsCategory.LABOR == "labor"


# ---------------------------------------------------------------------------
# LegalRight model tests
# ---------------------------------------------------------------------------


class TestLegalRight:
    def test_basic_creation(self) -> None:
        right = LegalRight(
            code="TEST-01",
            name="Test Right",
            category=RightsCategory.FUNDAMENTAL,
            description="A test right.",
            relevant_law="Article 21",
            how_to_claim="File a petition",
        )
        assert right.code == "TEST-01"
        assert right.category == RightsCategory.FUNDAMENTAL

    def test_documents_needed_defaults_empty(self) -> None:
        right = LegalRight(
            code="TEST-02",
            name="Right",
            category=RightsCategory.CONSUMER,
            description="Consumer right.",
            relevant_law="Consumer Protection Act 2019",
            how_to_claim="File complaint",
        )
        assert right.documents_needed == []


# ---------------------------------------------------------------------------
# LegalAidCenter model tests
# ---------------------------------------------------------------------------


class TestLegalAidCenter:
    def test_basic_creation(self) -> None:
        center = LegalAidCenter(
            center_id="DLSA-TEST",
            name="Test DLSA",
            district="Test District",
            state="Test State",
        )
        assert center.center_id == "DLSA-TEST"
        assert center.free_service is True  # default

    def test_free_service_default_true(self) -> None:
        center = LegalAidCenter(
            center_id="C-001",
            name="Center",
            district="District",
            state="State",
        )
        assert center.free_service is True


# ---------------------------------------------------------------------------
# EligibilityCheck model tests
# ---------------------------------------------------------------------------


class TestEligibilityCheck:
    def test_eligible_check(self) -> None:
        check = EligibilityCheck(
            eligible=True,
            reason="Income within limit",
            income_threshold=300000.0,
            criteria_met=["Income Rs 100,000 <= Rs 300,000"],
        )
        assert check.eligible is True

    def test_not_eligible_check(self) -> None:
        check = EligibilityCheck(
            eligible=False,
            reason="Income exceeds limit",
            income_threshold=300000.0,
            criteria_not_met=["Income Rs 500,000 > Rs 300,000"],
        )
        assert check.eligible is False

    def test_criteria_default_empty(self) -> None:
        check = EligibilityCheck(
            eligible=True,
            reason="Test",
            income_threshold=0.0,
        )
        assert check.criteria_met == []
        assert check.criteria_not_met == []


# ---------------------------------------------------------------------------
# RightsDatabase tests
# ---------------------------------------------------------------------------


class TestRightsDatabase:
    def test_all_rights_returns_list(self, rights_db: RightsDatabase) -> None:
        rights = rights_db.all_rights()
        assert isinstance(rights, list)
        assert len(rights) >= 10

    def test_by_category_fundamental(self, rights_db: RightsDatabase) -> None:
        rights = rights_db.by_category(RightsCategory.FUNDAMENTAL)
        assert len(rights) >= 4
        for r in rights:
            assert r.category == RightsCategory.FUNDAMENTAL

    def test_by_category_women(self, rights_db: RightsDatabase) -> None:
        rights = rights_db.by_category(RightsCategory.WOMEN)
        assert len(rights) >= 1
        for r in rights:
            assert r.category == RightsCategory.WOMEN

    def test_by_category_sc_st(self, rights_db: RightsDatabase) -> None:
        rights = rights_db.by_category(RightsCategory.SC_ST)
        assert len(rights) >= 1

    def test_by_category_disability(self, rights_db: RightsDatabase) -> None:
        rights = rights_db.by_category(RightsCategory.DISABILITY)
        assert len(rights) >= 1

    def test_by_category_empty_for_unknown(self, rights_db: RightsDatabase) -> None:
        rights = rights_db.by_category(RightsCategory.FAMILY)
        # FAMILY may not have entries in the current dataset
        assert isinstance(rights, list)

    def test_search_equality(self, rights_db: RightsDatabase) -> None:
        rights = rights_db.search("equality")
        assert len(rights) >= 1
        # "Right to Equality" should appear
        names = [r.name for r in rights]
        assert any("Equality" in name for name in names)

    def test_search_case_insensitive(self, rights_db: RightsDatabase) -> None:
        lower = rights_db.search("equality")
        upper = rights_db.search("EQUALITY")
        assert len(lower) == len(upper)

    def test_search_wage(self, rights_db: RightsDatabase) -> None:
        rights = rights_db.search("wage")
        assert len(rights) >= 1

    def test_search_no_results(self, rights_db: RightsDatabase) -> None:
        rights = rights_db.search("xyznonexistentterm12345")
        assert rights == []

    def test_get_by_code_fr_01(self, rights_db: RightsDatabase) -> None:
        right = rights_db.get_by_code("FR-01")
        assert right is not None
        assert right.name == "Right to Equality"

    def test_get_by_code_lr_01(self, rights_db: RightsDatabase) -> None:
        right = rights_db.get_by_code("LR-01")
        assert right is not None
        assert "Wage" in right.name or "wage" in right.name.lower()

    def test_get_by_code_nonexistent_returns_none(self, rights_db: RightsDatabase) -> None:
        assert rights_db.get_by_code("ZZ-99") is None

    def test_all_rights_returns_new_list(self, rights_db: RightsDatabase) -> None:
        list1 = rights_db.all_rights()
        list2 = rights_db.all_rights()
        assert list1 is not list2

    def test_fr_04_right_to_life_present(self, rights_db: RightsDatabase) -> None:
        right = rights_db.get_by_code("FR-04")
        assert right is not None
        assert "Life" in right.name or "life" in right.name.lower()

    def test_fr_05_right_to_education_present(self, rights_db: RightsDatabase) -> None:
        right = rights_db.get_by_code("FR-05")
        assert right is not None
        assert "Education" in right.name

    def test_all_rights_have_how_to_claim(self, rights_db: RightsDatabase) -> None:
        for right in rights_db.all_rights():
            assert len(right.how_to_claim) > 0


# ---------------------------------------------------------------------------
# EligibilityChecker tests
# ---------------------------------------------------------------------------


class TestEligibilityChecker:
    def test_low_income_eligible_general(self, eligibility_checker: EligibilityChecker) -> None:
        result = eligibility_checker.check(annual_income=100000.0)
        assert result.eligible is True

    def test_income_at_threshold_eligible(self, eligibility_checker: EligibilityChecker) -> None:
        result = eligibility_checker.check(annual_income=300000.0)
        assert result.eligible is True

    def test_income_above_threshold_not_eligible(
        self, eligibility_checker: EligibilityChecker
    ) -> None:
        result = eligibility_checker.check(annual_income=400000.0)
        assert result.eligible is False

    def test_sc_st_higher_threshold(self, eligibility_checker: EligibilityChecker) -> None:
        result = eligibility_checker.check(annual_income=400000.0, is_sc_st=True)
        assert result.eligible is True
        assert result.income_threshold == EligibilityChecker.SC_ST_THRESHOLD

    def test_sc_st_above_500k_not_eligible(
        self, eligibility_checker: EligibilityChecker
    ) -> None:
        result = eligibility_checker.check(annual_income=600000.0, is_sc_st=True)
        assert result.eligible is False

    def test_women_category_exempt(self, eligibility_checker: EligibilityChecker) -> None:
        result = eligibility_checker.check(annual_income=1000000.0, category="women")
        assert result.eligible is True

    def test_children_category_exempt(self, eligibility_checker: EligibilityChecker) -> None:
        result = eligibility_checker.check(annual_income=2000000.0, category="children")
        assert result.eligible is True

    def test_sc_st_category_exempt(self, eligibility_checker: EligibilityChecker) -> None:
        result = eligibility_checker.check(annual_income=5000000.0, category="sc_st")
        assert result.eligible is True

    def test_disability_category_exempt(self, eligibility_checker: EligibilityChecker) -> None:
        result = eligibility_checker.check(annual_income=999999.0, category="disability")
        assert result.eligible is True

    def test_custody_category_exempt(self, eligibility_checker: EligibilityChecker) -> None:
        result = eligibility_checker.check(annual_income=999999.0, category="custody")
        assert result.eligible is True

    def test_category_case_insensitive(self, eligibility_checker: EligibilityChecker) -> None:
        result = eligibility_checker.check(annual_income=999999.0, category="WOMEN")
        assert result.eligible is True

    def test_result_has_reason(self, eligibility_checker: EligibilityChecker) -> None:
        result = eligibility_checker.check(annual_income=100000.0)
        assert len(result.reason) > 0

    def test_result_has_income_threshold(self, eligibility_checker: EligibilityChecker) -> None:
        result = eligibility_checker.check(annual_income=100000.0)
        assert result.income_threshold == EligibilityChecker.GENERAL_THRESHOLD

    def test_zero_income_eligible(self, eligibility_checker: EligibilityChecker) -> None:
        result = eligibility_checker.check(annual_income=0.0)
        assert result.eligible is True


# ---------------------------------------------------------------------------
# LegalAidDirectory tests
# ---------------------------------------------------------------------------


class TestLegalAidDirectory:
    def test_all_centers_returns_list(self, directory: LegalAidDirectory) -> None:
        centers = directory.all_centers()
        assert isinstance(centers, list)
        assert len(centers) >= 5

    def test_find_by_state_delhi(self, directory: LegalAidDirectory) -> None:
        centers = directory.find_by_state("Delhi")
        assert len(centers) >= 1
        for c in centers:
            assert "Delhi" in c.state or "delhi" in c.state.lower()

    def test_find_by_state_case_insensitive(self, directory: LegalAidDirectory) -> None:
        lower = directory.find_by_state("maharashtra")
        upper = directory.find_by_state("Maharashtra")
        assert len(lower) == len(upper)

    def test_find_by_state_nonexistent_returns_empty(
        self, directory: LegalAidDirectory
    ) -> None:
        centers = directory.find_by_state("NonExistentStateName99")
        assert centers == []

    def test_find_by_district_mumbai(self, directory: LegalAidDirectory) -> None:
        centers = directory.find_by_district("Mumbai")
        assert len(centers) >= 1

    def test_find_by_district_nonexistent_returns_empty(
        self, directory: LegalAidDirectory
    ) -> None:
        centers = directory.find_by_district("NonExistentDistrict99")
        assert centers == []

    def test_all_centers_returns_new_list(self, directory: LegalAidDirectory) -> None:
        list1 = directory.all_centers()
        list2 = directory.all_centers()
        assert list1 is not list2

    def test_centers_have_phone(self, directory: LegalAidDirectory) -> None:
        for center in directory.all_centers():
            # Phone may be empty string, but field must exist
            assert hasattr(center, "phone")

    def test_centers_have_services(self, directory: LegalAidDirectory) -> None:
        # At least some centers must have services listed
        has_services = any(len(c.services) > 0 for c in directory.all_centers())
        assert has_services

    def test_find_kolkata(self, directory: LegalAidDirectory) -> None:
        centers = directory.find_by_state("West Bengal")
        assert len(centers) >= 1


# ---------------------------------------------------------------------------
# RightsAdvisor tests
# ---------------------------------------------------------------------------


class TestRightsAdvisor:
    def test_advise_returns_query_result(self, advisor: RightsAdvisor) -> None:
        result = advisor.advise("domestic violence")
        assert isinstance(result, QueryResult)

    def test_advise_disclaimer_present(self, advisor: RightsAdvisor) -> None:
        result = advisor.advise("theft and police")
        assert result.disclaimer == _DISCLAIMER

    def test_advise_fir_procedure_matched(self, advisor: RightsAdvisor) -> None:
        result = advisor.advise("how to file an FIR at the police station")
        assert len(result.procedures) >= 1
        procedure_names = [p.name for p in result.procedures]
        assert any("FIR" in name for name in procedure_names)

    def test_advise_bail_procedure_matched(self, advisor: RightsAdvisor) -> None:
        result = advisor.advise("my relative is under arrest and in custody, how to get bail")
        assert len(result.procedures) >= 1

    def test_advise_consumer_procedure_matched(self, advisor: RightsAdvisor) -> None:
        result = advisor.advise("I bought a defective product and need a consumer refund")
        procedure_names = [p.name for p in result.procedures]
        assert any("Consumer" in name for name in procedure_names)

    def test_advise_rti_procedure_matched(self, advisor: RightsAdvisor) -> None:
        result = advisor.advise("I need information about transparency and RTI")
        procedure_names = [p.name for p in result.procedures]
        assert any("RTI" in name for name in procedure_names)

    def test_advise_domestic_violence_procedure_matched(
        self, advisor: RightsAdvisor
    ) -> None:
        result = advisor.advise("I am a victim of domestic violence and abuse")
        procedure_names = [p.name for p in result.procedures]
        assert any("Violence" in name or "Domestic" in name for name in procedure_names)

    def test_advise_rights_matched_for_equality(self, advisor: RightsAdvisor) -> None:
        result = advisor.advise("equality")
        # Should find Right to Equality
        right_names = [r.name for r in result.rights]
        assert any("Equality" in name for name in right_names)

    def test_advise_unmatched_query_returns_empty_rights_and_procedures(
        self, advisor: RightsAdvisor
    ) -> None:
        result = advisor.advise("xyzunknownissuethatdoesnotmatch999")
        assert isinstance(result.rights, list)
        assert isinstance(result.procedures, list)


# ---------------------------------------------------------------------------
# DocumentHelper tests
# ---------------------------------------------------------------------------


class TestDocumentHelper:
    def test_get_procedure_fir(self, doc_helper: DocumentHelper) -> None:
        proc = doc_helper.get_procedure("fir")
        assert proc is not None
        assert proc.name == "Filing an FIR"

    def test_get_procedure_bail(self, doc_helper: DocumentHelper) -> None:
        proc = doc_helper.get_procedure("bail")
        assert proc is not None
        assert "Bail" in proc.name

    def test_get_procedure_consumer(self, doc_helper: DocumentHelper) -> None:
        proc = doc_helper.get_procedure("consumer")
        assert proc is not None
        assert "Consumer" in proc.name

    def test_get_procedure_rti(self, doc_helper: DocumentHelper) -> None:
        proc = doc_helper.get_procedure("rti")
        assert proc is not None
        assert "RTI" in proc.name

    def test_get_procedure_domestic_violence(self, doc_helper: DocumentHelper) -> None:
        proc = doc_helper.get_procedure("domestic_violence")
        assert proc is not None
        assert "Violence" in proc.name or "Domestic" in proc.name

    def test_get_procedure_by_partial_name(self, doc_helper: DocumentHelper) -> None:
        proc = doc_helper.get_procedure("Filing an FIR")
        assert proc is not None

    def test_get_procedure_nonexistent_returns_none(self, doc_helper: DocumentHelper) -> None:
        proc = doc_helper.get_procedure("nonexistentprocedure99")
        assert proc is None

    def test_all_procedures_returns_list(self, doc_helper: DocumentHelper) -> None:
        procs = doc_helper.all_procedures()
        assert isinstance(procs, list)
        assert len(procs) >= 4

    def test_each_procedure_has_steps(self, doc_helper: DocumentHelper) -> None:
        for proc in doc_helper.all_procedures():
            assert len(proc.steps) > 0

    def test_each_procedure_has_documents(self, doc_helper: DocumentHelper) -> None:
        for proc in doc_helper.all_procedures():
            assert len(proc.documents) > 0

    def test_each_procedure_has_cost(self, doc_helper: DocumentHelper) -> None:
        for proc in doc_helper.all_procedures():
            assert len(proc.cost) > 0

    def test_fir_procedure_is_free(self, doc_helper: DocumentHelper) -> None:
        proc = doc_helper.get_procedure("fir")
        assert proc is not None
        assert "Free" in proc.cost or "free" in proc.cost.lower()

    def test_fir_steps_mention_police_station(self, doc_helper: DocumentHelper) -> None:
        proc = doc_helper.get_procedure("fir")
        assert proc is not None
        steps_text = " ".join(proc.steps).lower()
        assert "police" in steps_text


# ---------------------------------------------------------------------------
# Integration tests
# ---------------------------------------------------------------------------


class TestIntegration:
    def test_rights_db_all_categories_populated(
        self, rights_db: RightsDatabase
    ) -> None:
        all_rights = rights_db.all_rights()
        categories_present = {r.category for r in all_rights}
        # At least 6 different categories should be in the DB
        assert len(categories_present) >= 6

    def test_eligibility_exempt_categories_cover_all_defined(
        self, eligibility_checker: EligibilityChecker
    ) -> None:
        for cat in EligibilityChecker.EXEMPT:
            result = eligibility_checker.check(annual_income=10_000_000.0, category=cat)
            assert result.eligible is True, f"Category {cat!r} should be exempt"

    def test_document_helper_and_rights_db_both_return_results(
        self, rights_db: RightsDatabase, doc_helper: DocumentHelper
    ) -> None:
        rights = rights_db.by_category(RightsCategory.FUNDAMENTAL)
        fir = doc_helper.get_procedure("fir")
        assert len(rights) > 0
        assert fir is not None


# ---------------------------------------------------------------------------
# Hypothesis property-based tests
# ---------------------------------------------------------------------------


@given(income=st.floats(min_value=0.0, max_value=1_000_000.0, allow_nan=False))
@settings(max_examples=20)
def test_eligibility_checker_never_raises(income: float) -> None:
    checker = EligibilityChecker()
    result = checker.check(annual_income=income)
    assert isinstance(result, EligibilityCheck)
    assert isinstance(result.eligible, bool)


@given(query=st.text(min_size=3, max_size=100))
@settings(max_examples=15)
def test_rights_advisor_never_raises(query: str) -> None:
    advisor = RightsAdvisor()
    result = advisor.advise(query)
    assert isinstance(result, QueryResult)
    assert result.disclaimer == _DISCLAIMER


@given(
    income=st.floats(min_value=0.0, max_value=300000.0, allow_nan=False),
)
@settings(max_examples=15)
def test_income_within_general_threshold_always_eligible(income: float) -> None:
    checker = EligibilityChecker()
    result = checker.check(annual_income=income)
    assert result.eligible is True
