"""
This file handles the text that will be passed to the llm.
"""

import json
from access_agent_scout.state import Finding

AGGREGATOR_SYSTEM_PROMPT = """You are an accessibility findings aggregator. 
Given a set of raw accessibility findings from an automated scanner, your job is to:

1. Identify and merge duplicate findings — the same underlying issue flagged 
more than once.
2. For each finding, "why_it_matters" and "suggested_fix" fields, tailored 
to the finding's rule_id and description.

IMPORTANT: Each finding may already include a wcag_criterion and level, 
extracted directly from the scanner's own rule metadata. These are 
authoritative — do NOT change, reinterpret, or invent a different WCAG 
criterion or level than what is provided.

If wcag_criterion is null/None for a finding, this means the underlying 
rule is a best-practice recommendation, not an actual WCAG requirement. 
In this case, do not invent a WCAG criterion — instead, clearly state in 
your explanation that this is a best-practice recommendation rather than 
a WCAG success criterion violation."""

AGGREGATOR_USER_PROMPT_TEMPLATE = """Here are {finding_count} raw findings from {source_count} scanners:

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
