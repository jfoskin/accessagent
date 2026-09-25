'''
This file is the single source of what data looks like as it moves through the graph.
'''

from typing import Literal, Optional, Union
from pydantic import BaseModel, Field, ConfigDict


class Location(BaseModel):
    selector: Optional[str] = None
    url: Optional[str] = None
    file: Optional[str] = None
    line: Optional[int] = None


class Finding(BaseModel):
    model_config = ConfigDict(extra="forbid")  # restricts model
    rule_id: str
    wcag_criterion: Optional[str] = None
    level: Union[Literal["A", "AA", "AAA"], None] = None
    severity: Literal["critical",  "serious",  "moderate",  "minor"]
    location: Location
    description: str
    confidence: Literal["high",  "needs_review"] = "needs_review"
    suggested_fix: Optional[str] = None
    source_agent: str
    raw_tags: list[str] = Field(default_factory=list)


class AggregatedFinding(Finding):
    """A finding after the aggregator has processed it.  wcag_criterion/level stay Optional, inherited as-is from Finding —a genuinely best-practice-only rule (no real WCAG mapping) is a legitimate, correct outcome, not a failure to fix.
        """
    is_best_practice: bool = False  # True when axe-core provided no WCAG tag at all
    why_it_matters: str = ""  # generated plain-language explanation of real-world impact


class AggregatedFindings(BaseModel):
    """Container so the aggregator can retturn a full deduped list in one structures-output call."""
    findings: list[AggregatedFinding] = Field(default_factory=list)

# The object that gets passed from node to node as it flows through the LangGraph pipeline


class AssessmentState(BaseModel):
    input_type: Literal['url', 'repo']
    input_value: str
    findings: list[Finding] = Field(default_factory=list)
    aggregated_findings: list[AggregatedFinding] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
