from langgraph.graph import StateGraph, START, END

from access_agent_scout.state import AssessmentState
from access_agent_scout.nodes.dom_scan import dom_scan_node


def planner_node(state: AssessmentState) -> dict:

    return {}


def aggregator_node(state: AssessmentState) -> dict:
    return {"aggregated_findings": state.findings}


def report_node(state: AssessmentState) -> dict:
    "real report formating coming later"
    return {}


graph = StateGraph(AssessmentState)

graph.add_node("planner", planner_node)
graph.add_node("dom_scan", dom_scan_node)
graph.add_node("aggregator", aggregator_node)
graph.add_node("report", report_node)

graph.add_edge(START, "planner")
graph.add_edge("planner", "dom_scan")
graph.add_edge("dom_scan", "aggregator")
graph.add_edge("aggregator", "report")
graph.add_edge("report", END)


compiled_graph = graph.compile()
