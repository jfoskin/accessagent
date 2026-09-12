from langgraph.graph import StateGraph, START, END

from access_agent_scout.state import AssessmentState
from access_agent_scout.nodes.dom_scan import dom_scan_node


graph = StateGraph(AssessmentState)

graph.add_node("dom_scan", dom_scan_node)

graph.add_edge(START, "dom_scan_node")
graph.add_edge("dom_scan_node", END)


compiled_graph = graph.compile()
