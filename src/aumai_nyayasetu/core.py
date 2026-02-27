"""Core logic for aumai-nyayasetu."""

from __future__ import annotations

from aumai_nyayasetu.models import (
    EligibilityCheck, LegalAidCenter, LegalProcedure, LegalRight, QueryResult, RightsCategory,
)

DISCLAIMER = (
    "This tool does NOT provide legal advice. All information is for general awareness only. "
    "Consult a qualified legal professional before taking any legal action."
)

_RIGHTS: list[LegalRight] = [
    LegalRight(code="FR-01", name="Right to Equality", category=RightsCategory.FUNDAMENTAL,
               description="No discrimination on grounds of religion, race, caste, sex, or place of birth.",
               relevant_law="Articles 14-18, Constitution of India",
               how_to_claim="File writ petition under Article 32 (SC) or Article 226 (HC)",
               documents_needed=["Identity proof", "Evidence of discrimination"]),
    LegalRight(code="FR-02", name="Right to Freedom", category=RightsCategory.FUNDAMENTAL,
               description="Freedom of speech, assembly, association, movement, residence, and profession.",
               relevant_law="Article 19, Constitution of India",
               how_to_claim="Challenge restriction through writ petition in High Court or Supreme Court",
               documents_needed=["Evidence of restriction"]),
    LegalRight(code="FR-03", name="Right against Exploitation", category=RightsCategory.FUNDAMENTAL,
               description="Prohibition of human trafficking, forced labor, and child labor in hazardous work.",
               relevant_law="Articles 23-24, Constitution of India",
               how_to_claim="File complaint at police station or contact NHRC",
               documents_needed=["Evidence of exploitation", "Identity proof"]),
    LegalRight(code="FR-04", name="Right to Life and Liberty", category=RightsCategory.FUNDAMENTAL,
               description="No deprivation of life or liberty except by law. Includes dignity, privacy, clean environment.",
               relevant_law="Article 21, Constitution of India",
               how_to_claim="File habeas corpus if detained, or writ petition for other violations",
               documents_needed=["Evidence of violation"]),
    LegalRight(code="FR-05", name="Right to Education", category=RightsCategory.FUNDAMENTAL,
               description="Free and compulsory education for children aged 6-14. 25% EWS reservation in private schools.",
               relevant_law="Article 21A, RTE Act 2009",
               how_to_claim="Apply to nearest government school. Complain to DEO if denied.",
               documents_needed=["Birth certificate", "Address proof", "Income certificate for EWS"]),
    LegalRight(code="LR-01", name="Minimum Wage", category=RightsCategory.LABOR,
               description="Every worker entitled to minimum wages as notified by state/central government.",
               relevant_law="Code on Wages 2019",
               how_to_claim="File complaint with Labour Commissioner or Labour Court",
               documents_needed=["Employment proof", "Salary slips"]),
    LegalRight(code="LR-02", name="Protection against Harassment at Work", category=RightsCategory.LABOR,
               description="Workplace with 10+ employees must have Internal Complaints Committee. Protection for all women.",
               relevant_law="POSH Act 2013",
               how_to_claim="File complaint with ICC within 3 months. If no ICC, file with District Officer.",
               documents_needed=["Written complaint with details", "Evidence/witness names"]),
    LegalRight(code="CR-01", name="Consumer Protection", category=RightsCategory.CONSUMER,
               description="Protection against hazardous goods, unfair trade, and deficient services. Product liability.",
               relevant_law="Consumer Protection Act 2019",
               how_to_claim="File on consumerhelpline.gov.in or at District Consumer Forum",
               documents_needed=["Purchase receipt", "Evidence of defect"]),
    LegalRight(code="WR-01", name="Protection from Domestic Violence", category=RightsCategory.WOMEN,
               description="Right to reside in shared household. Protection orders, monetary relief, custody.",
               relevant_law="DV Act 2005",
               how_to_claim="File with Protection Officer or Magistrate Court. Call Women Helpline 181.",
               documents_needed=["Identity proof", "Medical reports", "Marriage certificate"]),
    LegalRight(code="WR-02", name="Right against Dowry", category=RightsCategory.WOMEN,
               description="Giving or taking dowry is illegal. Dowry death punishable with 7 years to life.",
               relevant_law="Dowry Prohibition Act 1961, BNS Section 80/85",
               how_to_claim="File FIR at police station or call Women's Helpline 181.",
               documents_needed=["Evidence of dowry demand", "Witness statements"]),
    LegalRight(code="ST-01", name="Protection against Caste Atrocities", category=RightsCategory.SC_ST,
               description="Special protections for SC/ST against caste discrimination, violence, and social boycott.",
               relevant_law="SC/ST (Prevention of Atrocities) Act 1989",
               how_to_claim="File FIR (police cannot refuse). Approach DM if police refuse.",
               documents_needed=["Caste certificate", "Evidence of atrocity"]),
    LegalRight(code="CH-01", name="Child Protection", category=RightsCategory.CHILDREN,
               description="Protection against all abuse, exploitation, neglect. Special courts for sexual offences.",
               relevant_law="POCSO Act 2012, JJ Act 2015",
               how_to_claim="Call Childline 1098. File at police station.",
               documents_needed=["Child's identity", "Medical reports if applicable"]),
    LegalRight(code="DR-01", name="Disability Rights", category=RightsCategory.DISABILITY,
               description="4% reservation in govt jobs. Accessible buildings, transport, ICT. Equal education.",
               relevant_law="RPwD Act 2016",
               how_to_claim="Get disability certificate from district hospital. Approach Chief Commissioner for violations.",
               documents_needed=["Disability certificate", "Medical documents"]),
    LegalRight(code="PR-01", name="Property Rights", category=RightsCategory.PROPERTY,
               description="No deprivation of property except by law. Equal inheritance for women.",
               relevant_law="Article 300A, Hindu Succession Act 1956 (amended 2005)",
               how_to_claim="File civil suit. For inheritance, approach civil court.",
               documents_needed=["Property documents", "Family tree"]),
]

_CENTERS: list[LegalAidCenter] = [
    LegalAidCenter(center_id="DLSA-DEL", name="Delhi DLSA", district="Central Delhi", state="Delhi",
                   address="Patiala House Courts", phone="011-23388888",
                   services=["Free legal aid", "Lok Adalat", "Mediation"]),
    LegalAidCenter(center_id="DLSA-MUM", name="Mumbai DLSA", district="Mumbai", state="Maharashtra",
                   address="City Civil Court, Mumbai", phone="022-22615835",
                   services=["Free legal aid", "Lok Adalat", "Victim compensation"]),
    LegalAidCenter(center_id="DLSA-BLR", name="Bangalore DLSA", district="Bangalore Urban", state="Karnataka",
                   address="City Civil Court Complex", phone="080-22212483",
                   services=["Free legal aid", "Mediation"]),
    LegalAidCenter(center_id="DLSA-CHN", name="Chennai DLSA", district="Chennai", state="Tamil Nadu",
                   address="High Court Campus", phone="044-25343668",
                   services=["Free legal aid", "Lok Adalat"]),
    LegalAidCenter(center_id="DLSA-KOL", name="Kolkata DLSA", district="Kolkata", state="West Bengal",
                   address="City Sessions Court", phone="033-22484002",
                   services=["Free legal aid", "Mediation"]),
    LegalAidCenter(center_id="DLSA-HYD", name="Hyderabad DLSA", district="Hyderabad", state="Telangana",
                   address="City Civil Court", phone="040-24512524",
                   services=["Free legal aid", "Lok Adalat"]),
    LegalAidCenter(center_id="DLSA-LKO", name="Lucknow DLSA", district="Lucknow", state="Uttar Pradesh",
                   address="District Court Complex", phone="0522-2616403",
                   services=["Free legal aid", "Legal awareness"]),
]

_PROCEDURES: dict[str, LegalProcedure] = {
    "fir": LegalProcedure(
        name="Filing an FIR", description="Report a cognizable offence to police.",
        steps=["Go to nearest police station", "Narrate the incident", "Officer writes FIR", "Read and sign", "Get free copy",
               "If refused: complain to SP/DCP or approach Magistrate u/s 156(3) CrPC"],
        documents=["Identity proof", "Evidence if available", "Witness details"],
        timeline="Must be registered immediately", cost="Free"),
    "bail": LegalProcedure(
        name="Bail Application", description="Apply for release from custody.",
        steps=["Bailable: apply at police station (must grant)", "Non-bailable: file in court",
               "Get lawyer or request free legal aid", "Court hears arguments", "Execute bail bond with surety"],
        documents=["FIR copy", "Identity proof", "Address proof", "Surety documents"],
        timeline="Bailable: immediate. Non-bailable: 1-7 days", cost="Court fee Rs 50-100. Free legal aid available."),
    "consumer": LegalProcedure(
        name="Consumer Complaint", description="File for defective goods or deficient services.",
        steps=["Try resolving with seller in writing first", "File on consumerhelpline.gov.in or call 1800-11-4000",
               "District Commission: up to Rs 1Cr", "State Commission: Rs 1-10Cr", "File within 2 years"],
        documents=["Purchase receipt", "Product details", "Written complaint to seller", "Evidence of defect"],
        timeline="3-5 months at district level", cost="Rs 200 for claims up to Rs 5L. No lawyer mandatory."),
    "rti": LegalProcedure(
        name="RTI Application", description="Get information from any public authority.",
        steps=["Write to PIO of concerned department", "State info needed clearly and specifically",
               "Pay Rs 10 fee", "PIO must reply in 30 days", "Appeal to senior officer if unsatisfied",
               "Second appeal to Information Commission within 90 days"],
        documents=["Written application with Rs 10 fee", "BPL card if applicable (fee exempt)"],
        timeline="Reply within 30 days. Life/liberty: 48 hours.", cost="Rs 10 + Rs 2/page for documents"),
    "domestic_violence": LegalProcedure(
        name="Domestic Violence Complaint", description="Get protection orders and relief under DV Act.",
        steps=["Call Women Helpline 181", "Contact district Protection Officer",
               "File with Protection Officer or Magistrate Court", "Court issues protection order",
               "Right to reside in shared household", "Claim maintenance, compensation, custody"],
        documents=["Identity proof", "Medical reports", "Evidence of violence", "Marriage certificate"],
        timeline="Protection order within days. Final order: 60 days.", cost="Free. No court fees for DV cases."),
}


class RightsDatabase:
    def __init__(self) -> None:
        self._rights = list(_RIGHTS)

    def by_category(self, category: RightsCategory) -> list[LegalRight]:
        return [r for r in self._rights if r.category == category]

    def search(self, query: str) -> list[LegalRight]:
        q = query.lower()
        return [r for r in self._rights if q in r.name.lower() or q in r.description.lower() or q in r.relevant_law.lower()]

    def get_by_code(self, code: str) -> LegalRight | None:
        return next((r for r in self._rights if r.code == code), None)

    def all_rights(self) -> list[LegalRight]:
        return list(self._rights)


class EligibilityChecker:
    GENERAL_THRESHOLD: float = 300000.0
    SC_ST_THRESHOLD: float = 500000.0
    EXEMPT: set[str] = {"women", "children", "sc_st", "disability", "custody", "trafficking_victim"}

    def check(self, annual_income: float, category: str | None = None, is_sc_st: bool = False) -> EligibilityCheck:
        if annual_income < 0:
            raise ValueError(f"annual_income must be non-negative, got {annual_income}")
        if category and category.lower() in self.EXEMPT:
            return EligibilityCheck(eligible=True, reason=f"Eligible as {category} (income waived)", income_threshold=0,
                                    criteria_met=[f"Category '{category}' exempt from income criteria"])
        threshold = self.SC_ST_THRESHOLD if is_sc_st else self.GENERAL_THRESHOLD
        if annual_income <= threshold:
            return EligibilityCheck(eligible=True, reason=f"Income within Rs {threshold:,.0f} limit", income_threshold=threshold,
                                    criteria_met=[f"Income Rs {annual_income:,.0f} <= Rs {threshold:,.0f}"])
        return EligibilityCheck(eligible=False, reason=f"Income exceeds Rs {threshold:,.0f}", income_threshold=threshold,
                                criteria_not_met=[f"Income Rs {annual_income:,.0f} > Rs {threshold:,.0f}"])


class LegalAidDirectory:
    def __init__(self) -> None:
        self._centers = list(_CENTERS)

    def find_by_state(self, state: str) -> list[LegalAidCenter]:
        return [c for c in self._centers if state.lower() in c.state.lower()]

    def find_by_district(self, district: str) -> list[LegalAidCenter]:
        return [c for c in self._centers if district.lower() in c.district.lower()]

    def all_centers(self) -> list[LegalAidCenter]:
        return list(self._centers)


class RightsAdvisor:
    def __init__(self) -> None:
        self._db = RightsDatabase()

    def advise(self, query: str) -> QueryResult:
        rights = self._db.search(query)
        procedures: list[LegalProcedure] = []
        q = query.lower()
        for key, keywords in [("fir", ["fir", "police", "crime", "theft"]), ("bail", ["bail", "arrest", "custody"]),
                              ("consumer", ["consumer", "product", "refund"]), ("rti", ["rti", "information", "transparency"]),
                              ("domestic_violence", ["domestic", "violence", "abuse"])]:
            if any(k in q for k in keywords) and key in _PROCEDURES:
                procedures.append(_PROCEDURES[key])
        return QueryResult(rights=rights, procedures=procedures, disclaimer=DISCLAIMER)


__all__ = [
    "RightsDatabase",
    "EligibilityChecker",
    "LegalAidDirectory",
    "RightsAdvisor",
    "DocumentHelper",
]


class DocumentHelper:
    def get_procedure(self, name: str) -> LegalProcedure | None:
        key = name.lower().replace(" ", "_")
        if key in _PROCEDURES:
            return _PROCEDURES[key]
        return next((v for k, v in _PROCEDURES.items() if name.lower() in v.name.lower()), None)

    def all_procedures(self) -> list[LegalProcedure]:
        return list(_PROCEDURES.values())
