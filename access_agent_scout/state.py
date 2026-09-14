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
    raw_tags: list[str] = Field(default_factory=list)


# The object that gets passed from node to node as it flows through the LangGraph pipeline
class AssessmentState(BaseModel):
    input_type: Literal['url', 'repo']
    input_value: str
    findings: list[Finding] = Field(default_factory=list)
    aggregated_findings: list[AggregatedFinding] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)


class AggregatedFinding(Finding):
    """A finding after the aggregator has processed it. The WCAG mapping and severity are now required, not optional, as this is the aggregators job"""
    wcag_criterion: str
    level: Literal["A", "AA", "AAA"]


class AggregatedFindings(BaseModel):
    """Container so the aggregator can retturn a full deduped list in one structures-output call."""
    findings: list[AggregatedFinding] = Field(default_factory=list)
