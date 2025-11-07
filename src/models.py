from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class SiteBundle(BaseModel):
    """
    A top-level container used by the orchestrator to collect
    and return results from all agents for a given address.
    """
    address: str
    score: float
    decision: str
    summary: str
    results: List[Dict] = Field(default_factory=list)


# ---------------------------
# Research Agent Models
# ---------------------------

class ResearchFinding(BaseModel):
    source: str
    title: str
    url: Optional[str] = None
    sentiment: Optional[str] = None


class ResearchResult(BaseModel):
    address: str
    favorable_policy: bool
    rationale: str
    findings: List[ResearchFinding] = Field(default_factory=list)


# ---------------------------
# Permitting Agent Models
# ---------------------------

class PermitChecklistItem(BaseModel):
    item: str
    required: bool = True
    provided: bool = False
    notes: Optional[str] = None


class PermitForm(BaseModel):
    jurisdiction: str
    project_type: str
    auto_filled_fields: Dict[str, str]
    checklist: List[PermitChecklistItem]


class PermittingResult(BaseModel):
    address: str
    jurisdiction: str
    # Make the form optional so returning `form=None` is valid
    form: Optional[PermitForm] = None
    readiness_score: int
    blockers: List[str] = Field(default_factory=list)


# ---------------------------
# Design Agent Models
# ---------------------------

class DesignResult(BaseModel):
    address: str
    capacity_kw: float
    annual_kwh: float
    bom: List[str]
    assumptions: Dict[str, Any]   # <-- allow floats/ints/strings



# ---------------------------
# Composite Agent Models
# ---------------------------

class AgentBundle(BaseModel):
    research: ResearchResult
    permitting: PermittingResult
    design: DesignResult


class FinalDecision(BaseModel):
    address: str
    score: int
    decision: str
    reasons: List[str]
