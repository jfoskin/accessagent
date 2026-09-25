# from pathlib import Path

# from access_agent_scout.state import AssessmentState
# from access_agent_scout.nodes.dom_scan import dom_scan_node
# from access_agent_scout.prompts import build_aggregator_prompt

# test_page = (Path(__file__).parent / ".." / "tests" /
#              "fixtures" / "test_page.html").resolve().as_uri()

# state = AssessmentState(input_type="url", input_value=test_page)
# result = dom_scan_node(state)

# findings = result["findings"]
# print(f"Got {len(findings)} real findings from dom_scan_node")

# prompt = build_aggregator_prompt(findings)
# print(prompt)


from access_agent_scout.wcag_reference import parse_wcag_from_tags

# color-contrast — should resolve correctly
print(parse_wcag_from_tags(["cat.color", "wcag2aa", "wcag143"]))
# expect: ('1.4.3', 'AA')

# landmark-one-main — best-practice only, no real WCAG mapping
print(parse_wcag_from_tags(["cat.semantics", "best-practice"]))
# expect: (None, None)
