import sys
from pathlib import Path

# Add the repository root directory to Python's module search path
src_path = Path(__file__).parent / "src"
sys.path.append(str(Path(__file__).parent.resolve()))

import streamlit as st
import os
from devguard.agent import analyze_code  # Uses your existing Gemini agent logic

st.set_page_config(page_title="DevGuard AI - Online Security Auditor", page_icon="🛡️")

st.title("🛡️ DevGuard — AI Security Auditor")
st.write("Upload or paste Python code below to run a live security and vulnerability scan.")

# Retrieve API key from environment variable or user input
gemini_key = os.getenv("GEMINI_API_KEY")
if not gemini_key:
    gemini_key = st.text_input("Enter Gemini API Key:", type="password")

code_input = st.text_area("Python Source Code:", height=250, value="""def login(user, pwd):\n    query = f"SELECT * FROM users WHERE user='{user}' AND pass='{pwd}'"\n    return query""")

if st.button("Run Security Audit"):
    if not gemini_key:
        st.error("Please provide a valid Gemini API Key.")
    elif not code_input.strip():
        st.warning("Please enter code to analyze.")
    else:
        with st.spinner("Analyzing codebase AST and running Gemini security audit..."):
            try:
                # Call agent analysis logic directly
                report = analyze_code(code_input, api_key=gemini_key)
                st.markdown("### 📋 Audit Results")
                st.markdown(report)
            except Exception as e:
                st.error(f"Audit failed: {str(e)}")