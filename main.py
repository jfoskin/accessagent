# app.py
from access_agent_scout.graph import compiled_graph
from access_agent_scout.state import AssessmentState
from access_agent_scout.nodes.explain import explain_finding
from access_agent_scout.wcag_reference import get_name, get_reference_url, is_obsolete_in_2_2
import streamlit as st
from dotenv import load_dotenv
load_dotenv()


def _normalize_url(url: str) -> str:
    """Adds https:// to the front of a URL if no scheme is present."""
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url


st.set_page_config(page_title="Access Agent", page_icon="♿")
st.title("Access Agent")
st.write("Enter a URL to scan it for accessibility issues against WCAG 2.2.")

with st.form("scan_form"):
    url = st.text_input("Enter website url", placeholder="https://example.com")
    scan_clicked = st.form_submit_button("Scan")

if scan_clicked and url:
    url = _normalize_url(url)
    st.caption(f"Scanning: {url}")

    with st.spinner("Scanning page for accessibility issues"):
        try:
            state = AssessmentState(input_type="url", input_value=url)
            result = compiled_graph.invoke(state)
        except Exception as e:
            st.error(f"Something went wrong while scanning this page: {e}")
            st.stop()

    # store the scan result so it survives future reruns (e.g. explain button clicks)
    st.session_state["scan_result"] = result

elif scan_clicked and not url:
    st.error("Please enter a URL.")

# render results from session_state — runs on EVERY rerun, not just the scan click
if "scan_result" in st.session_state:
    result = st.session_state["scan_result"]
    findings = result.get("aggregated_findings", [])
    errors = result.get("errors", [])

    if errors:
        for error in errors:
            st.warning(f"⚠️ {error}")

    if not findings:
        st.success("✅ No accessibility issues found.")
    else:
        st.subheader(f"Found {len(findings)} issue(s)")

        severity_order = {"critical": 0,
                          "serious": 1, "moderate": 2, "minor": 3}
        findings_sorted = sorted(
            findings, key=lambda f: severity_order.get(f.severity, 99))

        if "open_finding_key" not in st.session_state:
            st.session_state["open_finding_key"] = None

        for finding in findings_sorted:
            stable_key = f"{finding.rule_id}_{finding.location.selector}_{finding.location.line}"
            expander_key = f"expander_{stable_key}"
            explain_key = f"explain_btn_{stable_key}"
            result_key = f"explain_result_{stable_key}"

            if expander_key not in st.session_state:
                st.session_state[expander_key] = False

            with st.expander(
                f"[{finding.severity.upper()}] {finding.description}",
                expanded=st.session_state[expander_key],
                key=expander_key,
            ):
                if finding.is_best_practice:
                    st.write(
                        "**Best practice recommendation** (not a WCAG requirement)")
                else:
                    criterion_name = get_name(finding.wcag_criterion)
                    reference_url = get_reference_url(finding.wcag_criterion)
                    if criterion_name:
                        st.write(
                            f"**WCAG Criterion:** {finding.wcag_criterion} — {criterion_name} (Level {finding.level})")
                    else:
                        st.write(
                            f"**WCAG Criterion:** {finding.wcag_criterion} (Level {finding.level})")
                    if reference_url:
                        st.caption(
                            f"[Read the full success criterion]({reference_url})")

                    if is_obsolete_in_2_2(finding.wcag_criterion):
                        st.caption("⚠️ Note: this criterion was removed/made obsolete in WCAG 2.2. "
                                   "The underlying issue axe-core flagged is still valid — "
                                   "modern browsers/assistive tech handle it directly — "
                                   "but this specific criterion number no longer applies under 2.2.")

                st.write(f"**Rule Id:** {finding.rule_id}")
                st.write(f"**Confidence:** {finding.confidence}")

                if finding.location.selector:
                    st.write("**Affected element (CSS selector):**")
                    st.code(finding.location.selector, language="css")

                if st.button("Explain this issue", key=explain_key):
                    st.session_state["open_finding_key"] = stable_key
                    with st.spinner("Generating explanation..."):
                        explanation = explain_finding(finding)
                    st.session_state[result_key] = explanation

                if result_key in st.session_state:
                    explanation = st.session_state[result_key]
                    st.write(
                        f"**Why this matters:** {explanation.why_it_matters}")
                    st.code(explanation.suggested_fix, language="html")
