"""
This file handles the text that will be passed to the llm.
"""

import json
from access_agent_scout.state import Finding

AGGREGATOR_SYSTEM_PROMPT = """You are an accessibility findings aggregator. 
Given a set of raw accessibility findings from an automated scanner, identify 
and merge duplicate findings — the same underlying issue flagged more than once.

Each finding already includes a wcag_criterion and level extracted directly 
from the scanner's own rule metadata. These are authoritative — do not change 
or reinterpret them. If wcag_criterion is null, this is a best-practice 
recommendation, not a WCAG requirement."""


AGGREGATOR_USER_PROMPT_TEMPLATE = """Here are {finding_count} raw findings from {source_count} scanner(s):

{findings_json}

Review these findings, merge any duplicates and produce the final deduplicated list of WCAG mappings, severity and confidence for each distinct issue."""


def build_aggregator_prompt(findings: list[Finding]) -> str:
    """Builds the user-turn prompt text for the aggregator LLM  call."""

    findings_json = json.dumps(
        [f.model_dump() for f in findings], indent=2
    )

    source_agent = {f.source_agent for f in findings}

    return AGGREGATOR_USER_PROMPT_TEMPLATE.format(
        finding_count=len(findings),
        source_count=len(source_agent),
        findings_json=findings_json
    )
