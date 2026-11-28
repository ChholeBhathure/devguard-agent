import sys
from pathlib import Path
import os
import time
import streamlit as st
from devguard.agent import DevGuardAgent
from devguard.retriever import LocalRetriever
from devguard.report_generator import generate_pdf_report

st.set_page_config(page_title="DevGuard AI", page_icon="🛡️", layout="wide")



if "finding_reviews" not in st.session_state:
    st.session_state.finding_reviews = {}

if "snippet_report" not in st.session_state:
    st.session_state.snippet_report = None

if "repository_report" not in st.session_state:
    st.session_state.repository_report = None

if "repository_scan_errors" not in st.session_state:
    st.session_state.repository_scan_errors = []

if "security_report" not in st.session_state:
    st.session_state.security_report = None

# Add the repository root directory to Python's module search path
src_path = Path(__file__).parent / "src"
sys.path.append(str(src_path.resolve()))



st.title("🛡️ DevGuard — AI Code Auditor")
st.write("Analyze individual code snippets or scan entire local Python repositories for vulnerabilities.")

# API key configuration
with st.sidebar:
    st.header("Configuration")

    openrouter_key = ""

    try:
        openrouter_key = st.secrets.get("OPENROUTER_API_KEY", "")
    except Exception:
        pass

    if not openrouter_key:
        openrouter_key = os.getenv("OPENROUTER_API_KEY", "")

    if openrouter_key:
        st.success("OpenRouter API key configured.")
    else:
        st.warning("OpenRouter API key not configured.")

        openrouter_key = st.text_input(
            "Enter OpenRouter API Key:",
            type="password",
            key="openrouter_api_key_input"
        )

def get_finding_id(finding):
    """Generate a stable identifier for a security finding."""

    return (
        f"{finding.file_path or 'unknown'}|"
        f"{finding.line_number or 'unknown'}|"
        f"{finding.title.casefold()}|"
        f"{finding.category.casefold()}"
    )
def render_findings(report, report_key):
    """Render the complete Pydantic SecurityReport in Streamlit."""

    st.subheader("Analysis Summary")
    st.info(report.summary)

    findings_count = len(report.findings)

    severity_counts = {
        "Critical": 0,
        "High": 0,
        "Medium": 0,
        "Low": 0,
        "Info": 0
    }

    for finding in report.findings:
        severity_counts[finding.severity.capitalize()] += 1

    st.subheader("Security Overview")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Findings", findings_count)
    col2.metric("Failed Chunks", len(report.failed_chunks))
    col3.metric("Warnings", len(report.warnings))

    st.subheader("Severity Breakdown")

    severity_cols = st.columns(5)

    for col, (severity, count) in zip(
        severity_cols,
        severity_counts.items()
    ):
        col.metric(severity, count)

    st.subheader("Security Findings")

    if not report.findings:
        st.success("No vulnerabilities were reported.")
    else:
        review_counts = {
            "Needs review": 0,
            "Confirmed": 0,
            "False positive": 0
        }

        for index, finding in enumerate(report.findings):

            with st.expander(
                f"[{finding.severity.upper()}] {finding.title}"
            ):
                col1, col2 = st.columns(2)

                with col1:
                    st.write(
                        f"**File:** {finding.file_path or 'N/A'}"
                    )
                    st.write(
                        f"**Line:** {finding.line_number or 'Unavailable'}"
                    )

                with col2:
                    st.write(f"**Category:** {finding.category}")
                    st.write(
                        f"**Confidence:** {finding.confidence * 100:.0f}%"
                    )

                st.write("**Description**")
                st.write(finding.description)

                st.write("**Evidence**")
                st.code(finding.evidence, language="python")

                st.write("**Recommendation**")
                st.info(finding.recommendation)

                st.divider()
                st.write("**Developer Verification**")

                # Each finding gets its own widget key.
                widget_key = f"review_{report_key}_{index}"

                if widget_key not in st.session_state:
                    st.session_state[widget_key] = (
                        st.session_state.finding_reviews.get(
                            widget_key,
                            "Needs review"
                        )
                    )

                review_status = st.selectbox(
                    "Review Status",
                    [
                        "Needs review",
                        "Confirmed",
                        "False positive"
                    ],
                    key=widget_key
                )

                st.session_state.finding_reviews[widget_key] = (
                    review_status
                )

                review_counts[review_status] += 1

        # Display the overview AFTER all findings are processed.
        st.subheader("Developer Verification Overview")

        review_cols = st.columns(3)

        review_cols[0].metric(
            "Needs Review",
            review_counts["Needs review"]
        )

        review_cols[1].metric(
            "Confirmed",
            review_counts["Confirmed"]
        )

        review_cols[2].metric(
            "False Positives",
            review_counts["False positive"]
        )

    st.subheader("Failed Chunks")

    if not report.failed_chunks:
        st.success("All chunks were analyzed successfully.")
    else:
        for failed in report.failed_chunks:
            with st.expander(
                f"{failed.file_path} "
                f"(Lines {failed.start_line}-{failed.end_line})"
            ):
                st.error(failed.error)

    st.subheader("Analysis Warnings")

    if not report.warnings:
        st.success("No analysis warnings.")
    else:
        for warning in report.warnings:
            st.warning(warning)

    st.subheader("General Recommendations")

    for recommendation in report.recommendations:
        st.markdown(f"- {recommendation}")

# Create two tabs
tab1, tab2 = st.tabs([
    "📝 Snippet Analysis",
    "📂 Repository Analysis"
])

# TAB 1
with tab1:
    language = st.selectbox(
        "Select Language:",
        ["Auto-detect", "Python", "JavaScript", "C++",
         "Java", "Go", "Rust", "SQL"]
    )

    code_input = st.text_area(
        "Paste Code Here:",
        height=250
    )
if st.button("Audit Snippet", type="primary"):
    if not openrouter_key:
        st.error("OpenRouter API key missing.")

    elif not code_input.strip():
        st.warning("Please enter code to analyze.")

    else:
        with st.spinner("DevGuard is auditing your code..."):
            try:
                agent = DevGuardAgent(api_key=openrouter_key)

                report = agent.analyze_code(
                    code_input,
                    language=language
                )

                # Save the report before rendering it.
                st.session_state.snippet_report = report

                # Reset previous verification decisions for a new scan.
                st.session_state.finding_reviews.clear()

                for key in list(st.session_state.keys()):
                    if key.startswith("review_"):
                        del st.session_state[key]

            except Exception as error:
                st.error(f"Audit failed: {error}")

# Render the saved report on every Streamlit rerun.
if st.session_state.snippet_report is not None:
    render_findings(
        st.session_state.snippet_report,
        "snippet"
    )
# TAB 2
with tab2:
    st.write("Scan a local folder containing Python files.")

    folder_path = st.text_input(
        "Enter absolute path to your project folder:"
    )

    if st.button("Scan Repository", type="primary"):

        if not openrouter_key:
            st.error("OpenRouter API key missing.")

        elif not folder_path.strip():
            st.warning("Please enter a project folder path.")

        elif not os.path.isdir(folder_path):
            st.error("Invalid folder path. Please provide a valid path.")

        else:
            try:
                with st.spinner("Scanning Python files..."):
                    retriever = LocalRetriever(root_dir=folder_path)
                    files = retriever.scan_directory()

                if not files:
                    st.warning("No Python files found in this directory.")

                else:
                    st.success(
                        f"Found {len(files)} Python files. "
                        "Starting security analysis..."
                    )

                    with st.spinner("DevGuard is analyzing your repository..."):
                        agent = DevGuardAgent(api_key=openrouter_key)

                        report = agent.analyze_repository(files)

                    st.session_state.repository_report = report
                    st.session_state.repository_scan_errors = (
                        retriever.scan_errors
                    )

                    st.session_state.finding_reviews.clear()

                    for key in list(st.session_state.keys()):
                        if key.startswith("review_"):
                            del st.session_state[key]

            except Exception as error:
                st.error(f"Repository scan failed: {error}")

    # Render the saved report on every Streamlit rerun.
    if st.session_state.repository_report is not None:
        render_findings(
            st.session_state.repository_report,
            "repository"
        )
        pdf_bytes = generate_pdf_report(
        st.session_state.repository_report
        )

        st.download_button(
            label="Download PDF Report",
            data=pdf_bytes,
            file_name="devguard_security_report.pdf",
            mime="application/pdf",
            key="download_repository_pdf"
        )
        # Download security report as JSON
        json_report = (
            st.session_state.repository_report.model_dump_json(
                indent=2
            )
        )

        st.download_button(
            label="Download JSON Report",
            data=json_report,
            file_name="devguard_security_report.json",
            mime="application/json",
            key="download_repository_json"
        )

        if st.session_state.repository_scan_errors:
            errors = st.session_state.repository_scan_errors

            st.warning(
                f"{len(errors)} files could not be scanned."
            )

            with st.expander("View scanning errors"):
                for error in errors:
                    st.write(error)