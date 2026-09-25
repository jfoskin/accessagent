# app.py
from access_agent_scout.graph import compiled_graph
from access_agent_scout.state import AssessmentState
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

        for finding in findings_sorted:
            with st.expander(f"[{finding.severity.upper()}] {finding.description}"):
                if finding.is_best_practice:
                    st.write(
                        "**Best practice recommendation** (not a WCAG requirement)")
                else:
                    st.write(
                        f"**WCAG Criterion:** {finding.wcag_criterion} (Level {finding.level})")

                st.write(f"**Rule Id:** {finding.rule_id}")
                st.write(f"**Confidence:** {finding.confidence}")

                if finding.location.selector:
                    st.code(finding.location.selector, language="html")

                if finding.suggested_fix:
                    st.write(f"**Recommendations:** {finding.suggested_fix}")

elif scan_clicked and not url:
    st.error("Please enter a URL.")
