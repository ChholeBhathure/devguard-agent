import sys
from pathlib import Path

# Add the repository root directory to Python's module search path
src_path = Path(__file__).parent / "src"
sys.path.append(str(src_path.resolve()))

import os
import time
import streamlit as st
from devguard.agent import DevGuardAgent
from devguard.retriever import LocalRetriever

st.set_page_config(page_title="DevGuard AI", page_icon="🛡️", layout="wide")

st.title("🛡️ DevGuard — AI Code Auditor")
st.write("Analyze individual code snippets or scan entire local Python repositories for vulnerabilities.")

# Sidebar for API Key
with st.sidebar:
    st.header("Configuration")
    gemini_key = st.text_input("Enter OpenRouter API Key:", type="password")
    if not gemini_key:
        gemini_key = os.getenv("OPENROUTER_API_KEY")
    
    if not gemini_key:
        st.warning("⚠️ Please provide a valid Gemini API Key to proceed.")

# Create two tabs for the UI
tab1, tab2 = st.tabs(["📝 Snippet Analysis", "📂 Repository Analysis"])

def render_findings(report):
    """Helper function to render the Pydantic SecurityReport in Streamlit."""
    st.subheader("Analysis Summary")
    st.info(report.summary)
    
    if not report.findings:
        st.success("🎉 No vulnerabilities found!")
        return

    st.write(f"**Total Findings:** {len(report.findings)}")
    
    for finding in report.findings:
        # Color code based on severity
        color = "red" if finding.severity in ["critical", "high"] else "orange" if finding.severity == "medium" else "blue"
        
        with st.expander(f"[{finding.severity.upper()}] {finding.title}"):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**File:** `{finding.file_path or 'N/A'}`")
                st.markdown(f"**Line:** `{finding.line_number or 'N/A'}`")
            with col2:
                st.markdown(f"**Category:** `{finding.category}`")
                st.markdown(f"**Confidence:** `{finding.confidence * 100:.0f}%`")
            
            st.write(f"**Description:** {finding.description}")
            st.code(finding.evidence, language="python")
            st.success(f"**Recommendation:** {finding.recommendation}")

# --- TAB 1: SNIPPET ANALYSIS ---
with tab1:
    language = st.selectbox(
        "Select Language:",
        ["Auto-detect", "Python", "JavaScript", "C++", "Java", "Go", "Rust", "SQL"]
    )
    
    code_input = st.text_area("Paste Code Here:", height=250)
    
    if st.button("Audit Snippet", type="primary"):
        if not gemini_key:
            st.error("API Key missing.")
        elif not code_input.strip():
            st.warning("Please enter code to analyze.")
        else:
            with st.spinner("Gemini is auditing the snippet..."):
                max_retries = 3
                report = None
                for attempt in range(max_retries):
                    try:
                        agent = DevGuardAgent(api_key=gemini_key)
                        report = agent.analyze_code(code_input, language=language)
                        break
                    except Exception as e:
                        if "503" in str(e) and attempt < max_retries - 1:
                            time.sleep(3)
                            continue
                        st.error(f"Audit failed: {e}")
                        break
                
                if report:
                    render_findings(report)

# --- TAB 2: REPOSITORY ANALYSIS ---
with tab2:
    st.write("Scan a local folder containing Python files.")
    folder_path = st.text_input("Enter absolute path to your project folder (e.g., C:\\Projects\\MyApp):")
    
    if st.button("Scan Repository", type="primary"):
        if not gemini_key:
            st.error("API Key missing.")
        elif not os.path.isdir(folder_path):
            st.error("Invalid folder path. Please provide a valid absolute path.")
        else:
            with st.spinner("Scanning directory and chunking files..."):
                try:
                    retriever = LocalRetriever(root_dir=folder_path)
                    files = retriever.scan_directory()
                    
                    if not files:
                        st.warning("No Python files found in the directory.")
                    else:
                        st.write(f"Found {len(files)} Python files. Starting AI analysis...")
                        
                        agent = DevGuardAgent(api_key=gemini_key)
                        report = agent.analyze_repository(files)
                        render_findings(report)
                        
                except Exception as e:
                    st.error(f"Repository scan failed: {e}")