import sys
from pathlib import Path

# Add the repository root directory to Python's module search path
src_path = Path(__file__).parent / "src"
sys.path.append(str(src_path.resolve()))

import os
import time
import streamlit as st
from devguard.agent import DevGuardAgent

st.set_page_config(page_title="DevGuard AI - Universal Security Auditor", page_icon="🛡️")

st.title("🛡️ DevGuard — Universal AI Code Auditor & Debugger")
st.write("Upload or paste code in any programming or scripting language to run a live security and bug scan.")

# Retrieve API key from user input or environment variable
gemini_key = st.text_input("Enter Gemini API Key:", type="password")
if not gemini_key:
    gemini_key = os.getenv("GEMINI_API_KEY")

# Universal Language Selector
language = st.selectbox(
    "Select Programming / Scripting Language:",
    [
        "Auto-detect",
        "Python",
        "JavaScript / Node.js",
        "React / JSX / TSX",
        "HTML / CSS",
        "SQL",
        "C / C++",
        "Java",
        "Go",
        "Rust",
        "Bash / Shell",
        "PHP"
    ]
)

code_input = st.text_area(
    "Source Code:",
    height=250,
    value="""expApp.listen(4001, () => {
    console.log("Server running on port 4001")
    })"""
)

if st.button("Run Security Audit"):
    if not gemini_key:
        st.error("Please provide a valid Gemini API Key.")
    elif not code_input.strip():
        st.warning("Please enter code to analyze.")
    else:
        with st.spinner("Analyzing code and running Gemini security audit..."):
            max_retries = 3
            report = None

            for attempt in range(max_retries):
                try:
                    agent = DevGuardAgent(api_key=gemini_key)
                    report = agent.analyze_code(code_input, language=language)
                    break
                except Exception as e:
                    error_msg = str(e)
                    is_503 = "503" in error_msg or "UNAVAILABLE" in error_msg or "high demand" in error_msg
                    if is_503 and attempt < max_retries - 1:
                        time.sleep(3)
                        continue
                    else:
                        st.error(f"Audit failed: {e}")
                        break

            if report:
                st.markdown(report)