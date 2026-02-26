"""Pydantic models for aumai-nyayasetu."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


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


class LegalRight(BaseModel):
    code: str
    name: str
    category: RightsCategory
    description: str
    relevant_law: str
    how_to_claim: str
    documents_needed: list[str] = Field(default_factory=list)


class LegalAidCenter(BaseModel):
    center_id: str
    name: str
    district: str
    state: str
    address: str = ""
    phone: str = ""
    services: list[str] = Field(default_factory=list)
    free_service: bool = True


class EligibilityCheck(BaseModel):
    eligible: bool
    reason: str
    income_threshold: float
    criteria_met: list[str] = Field(default_factory=list)
    criteria_not_met: list[str] = Field(default_factory=list)


class LegalProcedure(BaseModel):
    name: str
    description: str
    steps: list[str]
    documents: list[str]
    timeline: str
    cost: str


class QueryResult(BaseModel):
    rights: list[LegalRight] = Field(default_factory=list)
    procedures: list[LegalProcedure] = Field(default_factory=list)
    nearest_centers: list[LegalAidCenter] = Field(default_factory=list)
    disclaimer: str = "This tool does not provide legal advice. Consult a qualified legal professional."


__all__ = ["RightsCategory", "LegalRight", "LegalAidCenter", "EligibilityCheck", "LegalProcedure", "QueryResult"]
