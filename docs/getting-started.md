# Getting Started with aumai-nyayasetu

> **Legal Disclaimer:** This tool does not provide legal advice. All information is for
> general awareness only. Consult a qualified legal professional before taking any
> legal action.

---

## Prerequisites

- Python 3.11 or higher (`python --version` to check)
- pip 23+ (`pip --version` to check)

No database, no API key, no network connection required after installation.

---

## Installation

**From PyPI (recommended):**

```bash
pip install aumai-nyayasetu
```

**Development install (from source):**

```bash
git clone https://github.com/aumai/aumai-nyayasetu
cd aumai-nyayasetu
pip install -e ".[dev]"
```

**Verify the installation:**

```bash
nyayasetu --version
nyayasetu rights --category fundamental
```

You should see a list of fundamental rights with codes, descriptions, and claim procedures.

---

## Step-by-Step Tutorial

This tutorial covers the four core workflows: browsing rights, checking eligibility,
finding a legal aid centre, and getting a document checklist.

### Step 1: Browse legal rights

**List all rights in a category:**

```bash
nyayasetu rights --category labor
```

**Search by keyword:**

```bash
nyayasetu rights --search "minimum wage"
nyayasetu rights --search "domestic violence"
nyayasetu rights --search "child"
```

**Get all rights as JSON for integration:**

```bash
nyayasetu rights --json-output > all_rights.json
```

**Python equivalent:**

```python
from aumai_nyayasetu.core import RightsDatabase
from aumai_nyayasetu.models import RightsCategory

db = RightsDatabase()

# By category
labor_rights = db.by_category(RightsCategory.LABOR)
for right in labor_rights:
    print(f"[{right.code}] {right.name}")
    print(f"  Law: {right.relevant_law}")
    print(f"  How to claim: {right.how_to_claim}")

# By keyword search
results = db.search("wage")
print(f"Found {len(results)} rights matching 'wage'")

# By code
right = db.get_by_code("FR-04")
print(right.name)  # Right to Life and Liberty
```

### Step 2: Check eligibility for free legal aid

Free legal aid in India is a right, not a charity. The National Legal Services Authority
(NALSA) mandates free aid for persons below income thresholds and for special categories.

**CLI:**

```bash
# General applicant — annual income Rs 2,50,000
nyayasetu eligible --income 250000

# SC/ST applicant — higher income threshold applies
nyayasetu eligible --income 450000 --sc-st

# Women are exempt from income criteria
nyayasetu eligible --income 999999 --category women

# Check a borderline case
nyayasetu eligible --income 300000
```

**Python:**

```python
from aumai_nyayasetu.core import EligibilityChecker

checker = EligibilityChecker()

# Standard check
result = checker.check(annual_income=200000)
print(f"Eligible: {result.eligible}")      # True
print(f"Reason: {result.reason}")

# SC/ST elevated threshold
result = checker.check(annual_income=450000, is_sc_st=True)
print(f"Eligible: {result.eligible}")      # True (< Rs 5,00,000)

# Income-exempt category
result = checker.check(annual_income=9999999, category="women")
print(f"Eligible: {result.eligible}")      # True (income waived)
print(f"Criteria met: {result.criteria_met}")
```

### Step 3: Find a legal aid centre

```bash
# By state
nyayasetu centers --state Delhi
nyayasetu centers --state Maharashtra

# By district
nyayasetu centers --district Mumbai

# All centres (national helplines also printed)
nyayasetu centers
```

Output includes centre name, address, phone number, services offered, and whether the
service is free. National helplines are always printed: NALSA 15100, Women Helpline 181,
Childline 1098.

**Python:**

```python
from aumai_nyayasetu.core import LegalAidDirectory

directory = LegalAidDirectory()

centres = directory.find_by_state("Karnataka")
for centre in centres:
    print(f"{centre.name}: {centre.phone}")
    print(f"  Services: {', '.join(centre.services)}")
    print(f"  Free: {centre.free_service}")

# All centres
all_centres = directory.all_centres()
print(f"Total centres in directory: {len(all_centres)}")
```

### Step 4: Get a document checklist for a legal procedure

Before visiting a lawyer, a police station, or a court, knowing which documents to bring
can mean the difference between action and being turned away.

```bash
nyayasetu documents --procedure fir
nyayasetu documents --procedure bail
nyayasetu documents --procedure consumer
nyayasetu documents --procedure rti
nyayasetu documents --procedure domestic_violence
```

Output for `fir`:

```
=======================================================
  Filing an FIR
=======================================================

Report a cognizable offence to police.

Steps:
  Go to nearest police station
  Narrate the incident
  Officer writes FIR
  Read and sign
  Get free copy
  If refused: complain to SP/DCP or approach Magistrate u/s 156(3) CrPC

Documents needed:
  - Identity proof
  - Evidence if available
  - Witness details

Timeline: Must be registered immediately
Cost: Free
```

**Python:**

```python
from aumai_nyayasetu.core import DocumentHelper

helper = DocumentHelper()

proc = helper.get_procedure("rti")
print(f"Name: {proc.name}")
print(f"Timeline: {proc.timeline}")
print(f"Cost: {proc.cost}")
print("Steps:")
for step in proc.steps:
    print(f"  - {step}")
```

### Step 5: Describe a legal issue and get matched guidance

```bash
nyayasetu help --query "my employer has not paid my salary for two months"
nyayasetu help --query "I want to file a complaint against a defective phone"
nyayasetu help --query "police are refusing to register my FIR"
```

**Python:**

```python
from aumai_nyayasetu.core import RightsAdvisor

advisor = RightsAdvisor()
result = advisor.advise("employer not paying salary for two months")

print(f"Relevant rights: {len(result.rights)}")
for right in result.rights:
    print(f"  [{right.code}] {right.name}")

print(f"Relevant procedures: {len(result.procedures)}")
for proc in result.procedures:
    print(f"  {proc.name} — {proc.description[:60]}...")

# Disclaimer is always present
print(result.disclaimer)
```

---

## 5 Common Patterns

### Pattern 1: Build a rights-awareness chatbot backend

```python
from aumai_nyayasetu.core import RightsAdvisor
from aumai_nyayasetu.models import QueryResult

advisor = RightsAdvisor()

def handle_user_query(query: str) -> QueryResult:
    result = advisor.advise(query)
    return result

# Integrate result.rights and result.procedures into your response
# Always surface result.disclaimer to the user
response = handle_user_query("I was fired without notice or payment")
```

### Pattern 2: Batch eligibility screening

```python
from aumai_nyayasetu.core import EligibilityChecker

checker = EligibilityChecker()

applicants = [
    {"name": "Ramesh", "income": 180000, "is_sc_st": False},
    {"name": "Sunita", "income": 420000, "is_sc_st": True},
    {"name": "Kavitha", "income": 800000, "is_sc_st": False, "category": "women"},
]

for applicant in applicants:
    category = applicant.get("category")
    result = checker.check(
        annual_income=applicant["income"],
        is_sc_st=applicant.get("is_sc_st", False),
        category=category,
    )
    status = "ELIGIBLE" if result.eligible else "NOT ELIGIBLE"
    print(f"{applicant['name']}: {status} — {result.reason}")
```

### Pattern 3: Export rights database to JSON for a mobile app

```python
import json
from aumai_nyayasetu.core import RightsDatabase

db = RightsDatabase()
all_rights = [r.model_dump() for r in db.all_rights()]

with open("rights_database.json", "w", encoding="utf-8") as f:
    json.dump(all_rights, f, ensure_ascii=False, indent=2)

print(f"Exported {len(all_rights)} rights to rights_database.json")
```

### Pattern 4: Generate a per-category procedure guide

```python
from aumai_nyayasetu.core import DocumentHelper

helper = DocumentHelper()

with open("procedure_guide.txt", "w", encoding="utf-8") as f:
    for proc in helper.all_procedures():
        f.write(f"\n{'='*60}\n")
        f.write(f"{proc.name}\n")
        f.write(f"{'='*60}\n")
        f.write(f"{proc.description}\n\n")
        f.write("Steps:\n")
        for step in proc.steps:
            f.write(f"  {step}\n")
        f.write(f"\nTimeline: {proc.timeline}\n")
        f.write(f"Cost: {proc.cost}\n")
```

### Pattern 5: Validate all rights for a specific law

```python
from aumai_nyayasetu.core import RightsDatabase

db = RightsDatabase()
constitution_rights = db.search("Constitution of India")
print(f"Rights grounded in the Constitution: {len(constitution_rights)}")
for r in constitution_rights:
    print(f"  [{r.code}] {r.relevant_law}")
```

---

## Troubleshooting FAQ

**Q: `nyayasetu: command not found` after pip install.**

A: The pip scripts directory may not be on your PATH. Try:

```bash
python -m aumai_nyayasetu.cli --help
```

On Linux/Mac, add `~/.local/bin` to PATH. On Windows, check the Python Scripts directory.

---

**Q: `--category` gives an error about invalid choice.**

A: The `--category` option only accepts the exact enum values. Run:

```bash
nyayasetu rights --help
```

The valid choices are listed: `fundamental`, `labor`, `consumer`, `property`, `family`,
`criminal_defense`, `women`, `children`, `sc_st`, `disability`.

---

**Q: `nyayasetu help --query "..."` returns no matches.**

A: The matching is keyword-based on the query string against right descriptions and law
names. Try broader or different keywords. For example: `wage` instead of `salary`,
`domestic` instead of `household`, `fir` instead of `police complaint`.

---

**Q: `documents --procedure` returns "Unknown procedure".**

A: Valid procedure keys are: `fir`, `bail`, `consumer`, `rti`, `domestic_violence`.
The key must match exactly (underscores, not spaces). The `DocumentHelper.get_procedure`
method also accepts partial name matching, so `helper.get_procedure("FIR")` works in
the Python API.

---

**Q: `EligibilityChecker.check` raises a ValueError.**

A: `annual_income` must be a non-negative number (>= 0). Passing a negative value raises
`ValueError: annual_income must be non-negative`.

---

**Q: Can nyayasetu access real government databases or verify current laws?**

A: No. All data is embedded in the package and reflects Indian law as encoded at the time
of the release. Laws change. Always verify current provisions with a qualified legal
professional or official government sources.

---

**Q: Is the disclaimer in `QueryResult` mandatory?**

A: Yes. The `QueryResult.disclaimer` field has a hardcoded default value and is always
included in API responses. The CLI always prints it. This is by design — the legal
disclaimer cannot be disabled or omitted.

---

## Next Steps

- [API Reference](api-reference.md) — complete documentation of every class, method, and model
- [Examples](../examples/quickstart.py) — working demo script
- [Contributing](../CONTRIBUTING.md) — how to contribute rights data or code
