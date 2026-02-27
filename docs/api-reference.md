# API Reference — aumai-nyayasetu

> **Legal Disclaimer:** This tool does not provide legal advice. All information is for
> general awareness only. Consult a qualified legal professional before taking any
> legal action.

Package: `aumai_nyayasetu` | Version: 0.1.0 | Python: 3.11+

---

## Module: `aumai_nyayasetu.models`

All models use Pydantic v2. Validation is enforced at construction time.

---

### `RightsCategory`

Enum of legal rights categories.

```python
class RightsCategory(str, Enum):
    FUNDAMENTAL = "fundamental"
    LABOR = "labor"
    CONSUMER = "consumer"
    PROPERTY = "property"
    FAMILY = "family"
    CRIMINAL_DEFENSE = "criminal_defense"
    WOMEN = "women"
    CHILDREN = "children"
    SC_ST = "sc_st"
    DISABILITY = "disability"
```

Inherits from `str` — values can be used directly as strings. Used as the `--category`
option in the CLI.

---

### `LegalRight`

A specific legal right with its law reference and claim procedure.

```python
class LegalRight(BaseModel):
    code: str
    name: str
    category: RightsCategory
    description: str
    relevant_law: str
    how_to_claim: str
    documents_needed: list[str] = []
```

**Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `code` | `str` | Yes | Internal code, e.g. `"FR-01"`, `"LR-01"`, `"WR-01"` |
| `name` | `str` | Yes | Short name of the right |
| `category` | `RightsCategory` | Yes | Category enum value |
| `description` | `str` | Yes | Plain-English description of the right |
| `relevant_law` | `str` | Yes | Act, section, or article reference |
| `how_to_claim` | `str` | Yes | Step-by-step claim instruction |
| `documents_needed` | `list[str]` | No | Documents required to exercise the right |

**Built-in rights by code:**

| Code | Name | Category |
|------|------|----------|
| `FR-01` | Right to Equality | `fundamental` |
| `FR-02` | Right to Freedom | `fundamental` |
| `FR-03` | Right against Exploitation | `fundamental` |
| `FR-04` | Right to Life and Liberty | `fundamental` |
| `FR-05` | Right to Education | `fundamental` |
| `LR-01` | Minimum Wage | `labor` |
| `LR-02` | Protection against Harassment at Work | `labor` |
| `CR-01` | Consumer Protection | `consumer` |
| `WR-01` | Protection from Domestic Violence | `women` |
| `WR-02` | Right against Dowry | `women` |
| `ST-01` | Protection against Caste Atrocities | `sc_st` |
| `CH-01` | Child Protection | `children` |
| `DR-01` | Disability Rights | `disability` |
| `PR-01` | Property Rights | `property` |

---

### `LegalAidCenter`

A District Legal Services Authority (DLSA) legal aid centre.

```python
class LegalAidCenter(BaseModel):
    center_id: str
    name: str
    district: str
    state: str
    address: str = ""
    phone: str = ""
    services: list[str] = []
    free_service: bool = True
```

**Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `center_id` | `str` | Yes | Internal identifier, e.g. `"DLSA-DEL"` |
| `name` | `str` | Yes | Centre name |
| `district` | `str` | Yes | District |
| `state` | `str` | Yes | State |
| `address` | `str` | No | Physical address |
| `phone` | `str` | No | Contact phone number |
| `services` | `list[str]` | No | Services offered |
| `free_service` | `bool` | No | Whether services are free (always `True` for DLSAs) |

---

### `EligibilityCheck`

Result of a free legal aid eligibility check.

```python
class EligibilityCheck(BaseModel):
    eligible: bool
    reason: str
    income_threshold: float
    criteria_met: list[str] = []
    criteria_not_met: list[str] = []
```

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `eligible` | `bool` | Whether the applicant qualifies for free legal aid |
| `reason` | `str` | Human-readable explanation |
| `income_threshold` | `float` | Applicable income threshold in INR |
| `criteria_met` | `list[str]` | List of criteria the applicant satisfies |
| `criteria_not_met` | `list[str]` | List of criteria the applicant does not satisfy |

When `income_threshold` is `0`, the applicant is income-exempt (special category).

---

### `LegalProcedure`

Step-by-step legal procedure with documents, timeline, and cost.

```python
class LegalProcedure(BaseModel):
    name: str
    description: str
    steps: list[str]
    documents: list[str]
    timeline: str
    cost: str
```

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `name` | `str` | Procedure name |
| `description` | `str` | Brief description |
| `steps` | `list[str]` | Ordered list of steps to follow |
| `documents` | `list[str]` | Documents to bring |
| `timeline` | `str` | Expected time frame |
| `cost` | `str` | Fee information |

**Built-in procedures:**

| Key | Name |
|-----|------|
| `"fir"` | Filing an FIR |
| `"bail"` | Bail Application |
| `"consumer"` | Consumer Complaint |
| `"rti"` | RTI Application |
| `"domestic_violence"` | Domestic Violence Complaint |

---

### `QueryResult`

Combined result of a rights-and-procedures advisory query.

```python
class QueryResult(BaseModel):
    rights: list[LegalRight] = []
    procedures: list[LegalProcedure] = []
    nearest_centers: list[LegalAidCenter] = []
    disclaimer: str = "This tool does NOT provide legal advice..."
```

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `rights` | `list[LegalRight]` | Matched rights for the query |
| `procedures` | `list[LegalProcedure]` | Matched procedures for the query |
| `nearest_centers` | `list[LegalAidCenter]` | Relevant aid centres (populated if provided) |
| `disclaimer` | `str` | Legal disclaimer — always present, cannot be empty |

The `disclaimer` field has a hardcoded default. It is populated by all code paths
and is always surfaced in CLI output.

---

## Module: `aumai_nyayasetu.core`

---

### `DISCLAIMER`

```python
DISCLAIMER: str = (
    "This tool does NOT provide legal advice. All information is for general awareness only. "
    "Consult a qualified legal professional before taking any legal action."
)
```

Module-level constant. Used as the `disclaimer` in `QueryResult` and printed by all
CLI commands.

---

### `RightsDatabase`

In-memory database of `LegalRight` objects.

```python
class RightsDatabase:
    def __init__(self) -> None: ...
```

Initialises with 14 built-in `LegalRight` objects.

**Methods:**

#### `by_category`

```python
def by_category(self, category: RightsCategory) -> list[LegalRight]
```

Return all rights in the given category.

| Parameter | Type | Description |
|-----------|------|-------------|
| `category` | `RightsCategory` | Category to filter by |

Returns: `list[LegalRight]` (may be empty).

---

#### `search`

```python
def search(self, query: str) -> list[LegalRight]
```

Search rights by keyword. Matches if the lowercased `query` is a substring of any of:
`right.name.lower()`, `right.description.lower()`, or `right.relevant_law.lower()`.

| Parameter | Type | Description |
|-----------|------|-------------|
| `query` | `str` | Keyword or phrase to search |

Returns: `list[LegalRight]`

---

#### `get_by_code`

```python
def get_by_code(self, code: str) -> LegalRight | None
```

Return a single right by its exact code.

| Parameter | Type | Description |
|-----------|------|-------------|
| `code` | `str` | Exact code, e.g. `"FR-04"` |

Returns: `LegalRight` or `None` if not found.

---

#### `all_rights`

```python
def all_rights(self) -> list[LegalRight]
```

Return all 14 built-in rights.

Returns: `list[LegalRight]` (copy).

---

### `EligibilityChecker`

Checks eligibility for free legal aid under NALSA criteria.

```python
class EligibilityChecker:
    GENERAL_THRESHOLD: float = 300000.0
    SC_ST_THRESHOLD: float = 500000.0
    EXEMPT: set[str] = {"women", "children", "sc_st", "disability",
                        "custody", "trafficking_victim"}
```

**Class attributes:**

| Attribute | Value | Description |
|-----------|-------|-------------|
| `GENERAL_THRESHOLD` | `300000.0` | Annual income limit for general category (Rs 3,00,000) |
| `SC_ST_THRESHOLD` | `500000.0` | Annual income limit for SC/ST (Rs 5,00,000) |
| `EXEMPT` | `set` | Categories exempt from income criteria |

**Methods:**

#### `check`

```python
def check(
    self,
    annual_income: float,
    category: str | None = None,
    is_sc_st: bool = False,
) -> EligibilityCheck
```

Check eligibility for free legal aid.

| Parameter | Type | Description |
|-----------|------|-------------|
| `annual_income` | `float` | Annual income in INR (must be >= 0) |
| `category` | `str | None` | Special category string. If in `EXEMPT`, income is waived. |
| `is_sc_st` | `bool` | If `True`, uses `SC_ST_THRESHOLD` instead of `GENERAL_THRESHOLD` |

Returns: `EligibilityCheck`

**Raises:** `ValueError` if `annual_income < 0`.

**Logic:**
1. If `category.lower()` is in `EXEMPT` → eligible, income waived.
2. Select threshold: `SC_ST_THRESHOLD` if `is_sc_st`, else `GENERAL_THRESHOLD`.
3. If `annual_income <= threshold` → eligible.
4. Otherwise → not eligible.

---

### `LegalAidDirectory`

Directory of DLSA legal aid centres.

```python
class LegalAidDirectory:
    def __init__(self) -> None: ...
```

Initialises with 7 built-in `LegalAidCenter` records.

**Methods:**

#### `find_by_state`

```python
def find_by_state(self, state: str) -> list[LegalAidCenter]
```

Find centres in a state. Case-insensitive partial match.

| Parameter | Type | Description |
|-----------|------|-------------|
| `state` | `str` | State name or partial name |

Returns: `list[LegalAidCenter]`

---

#### `find_by_district`

```python
def find_by_district(self, district: str) -> list[LegalAidCenter]
```

Find centres in a district. Case-insensitive partial match.

| Parameter | Type | Description |
|-----------|------|-------------|
| `district` | `str` | District name or partial name |

Returns: `list[LegalAidCenter]`

---

#### `all_centers`

```python
def all_centers(self) -> list[LegalAidCenter]
```

Return all 7 built-in centres.

Returns: `list[LegalAidCenter]` (copy).

---

### `RightsAdvisor`

Matches a user's described legal issue to relevant rights and procedures.

```python
class RightsAdvisor:
    def __init__(self) -> None: ...
```

**Methods:**

#### `advise`

```python
def advise(self, query: str) -> QueryResult
```

Get matched rights and procedures for a described legal issue.

| Parameter | Type | Description |
|-----------|------|-------------|
| `query` | `str` | Natural-language description of the issue |

Returns: `QueryResult` with `disclaimer` always set.

**Matching logic:**

Rights: calls `RightsDatabase.search(query)`.

Procedures — keyword trigger map:

| Procedure key | Trigger keywords |
|---------------|-----------------|
| `"fir"` | `"fir"`, `"police"`, `"crime"`, `"theft"` |
| `"bail"` | `"bail"`, `"arrest"`, `"custody"` |
| `"consumer"` | `"consumer"`, `"product"`, `"refund"` |
| `"rti"` | `"rti"`, `"information"`, `"transparency"` |
| `"domestic_violence"` | `"domestic"`, `"violence"`, `"abuse"` |

---

### `DocumentHelper`

Retrieves `LegalProcedure` objects by name or key.

```python
class DocumentHelper:
```

No constructor parameters.

**Methods:**

#### `get_procedure`

```python
def get_procedure(self, name: str) -> LegalProcedure | None
```

Get a procedure by key or partial name match.

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | `str` | Procedure key (e.g. `"fir"`) or partial name (e.g. `"Consumer"`) |

Returns: `LegalProcedure` or `None`.

**Resolution order:**
1. Normalise: `name.lower().replace(" ", "_")`
2. Exact key match in `_PROCEDURES`
3. Partial name match: first `LegalProcedure` whose `name.lower()` contains `name.lower()`

---

#### `all_procedures`

```python
def all_procedures(self) -> list[LegalProcedure]
```

Return all five built-in procedures.

Returns: `list[LegalProcedure]`

---

## Module: `aumai_nyayasetu.cli`

CLI entry point. Access via the `nyayasetu` shell command (also aliased as `main`).

```python
@click.group()
def cli() -> None: ...

main = cli
```

### Commands

| Command | Description |
|---------|-------------|
| `rights` | Search and list legal rights |
| `eligible` | Check eligibility for free legal aid |
| `centers` | Find legal aid centres |
| `documents` | Get document checklist for a legal procedure |
| `help` | Get matched rights and procedures for a described issue |

### `_DISCLAIMER`

```python
_DISCLAIMER: str = f"\nDISCLAIMER: {_DISCLAIMER_TEXT}\n"
```

Printed at the end of every CLI command's output. Cannot be suppressed.

---

## Public API Surface (`__all__`)

### `aumai_nyayasetu.models`

```python
__all__ = [
    "RightsCategory",
    "LegalRight",
    "LegalAidCenter",
    "EligibilityCheck",
    "LegalProcedure",
    "QueryResult",
]
```

### `aumai_nyayasetu.core`

```python
__all__ = [
    "RightsDatabase",
    "EligibilityChecker",
    "LegalAidDirectory",
    "RightsAdvisor",
    "DocumentHelper",
]
```

---

## Exceptions

| Situation | Exception |
|-----------|-----------|
| `annual_income < 0` in `EligibilityChecker.check` | `ValueError` |
| Invalid `RightsCategory` string | `ValueError` (enum construction) |
| Invalid Pydantic field | `pydantic.ValidationError` |

---

## Built-in DLSA Centres

| Centre ID | Name | State | Phone |
|-----------|------|-------|-------|
| `DLSA-DEL` | Delhi DLSA | Delhi | 011-23388888 |
| `DLSA-MUM` | Mumbai DLSA | Maharashtra | 022-22615835 |
| `DLSA-BLR` | Bangalore DLSA | Karnataka | 080-22212483 |
| `DLSA-CHN` | Chennai DLSA | Tamil Nadu | 044-25343668 |
| `DLSA-KOL` | Kolkata DLSA | West Bengal | 033-22484002 |
| `DLSA-HYD` | Hyderabad DLSA | Telangana | 040-24512524 |
| `DLSA-LKO` | Lucknow DLSA | Uttar Pradesh | 0522-2616403 |

National helplines: NALSA 15100 | Women Helpline 181 | Childline 1098
