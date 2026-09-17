from access_agent_scout.state import AggregatedFindings
from access_agent_scout.llm import get_llm

llm = get_llm().with_structured_output(AggregatedFindings)

test_prompt = """ Given the accessibilty findings, mapp it to a WCAG 2.2 criterion:

Rule: image-alt
Description: Image must have alternative text
Severity: critical
Raw tags: ["wcag2a", "wcag111", "cat.text-alternatives"]

Return one finding in the AggregatedFindings format."""

try:
    result = llm.invoke(test_prompt)
    print("SUCCESS")
    print(result)
except Exception as e:
    print("FAILED")
    print(type(e).__name__, ":", e)
