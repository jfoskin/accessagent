'''
This file is the single source of what data looks like as it moves through the graph.
'''

from typing import Literal, Optional
from pydantic import BaseModel, Field


class Location(BaseModel):
    selector: Optional[str] = None
    url: Optional[str] = None
    file: Optional[str] = None
    line: Optional[int] = None


class Finding(BaseModel):
    rule_id: str
    wcag_criteroin: Optional[str] = None
    level: Literal["A", "AA", "AAA"] = None
    severity: Literal["critical",  "serious",  "moderate",  "minor"]
    location: Location
    description: str
    confidence: Literal["high",  "needs_review"] = "needs_review"
    suggested_fix: Optional[str] = None
    source_agent: str


# The object that gets passed from node to node as it flows through the LangGraph pipeline
class AssessmentState(BaseModel):
    input_type: Literal['url', 'repo']
    input_value: str
    findings: list[Finding] = Field(default_factory=list)
    aggregated_findings: list[Finding] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
