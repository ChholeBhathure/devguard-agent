import os
from google import genai
from google.genai import types
from devguard.schemas.finding import SecurityReport

from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

class DevGuardAgent:
    def __init__(self, api_key: str = None, token_limit: int = 8000, model_name: str = "gemini-3.6-flash"):
        self.token_limit = token_limit
        self.model_name = model_name

        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not set in the environment variables.")

        self.client = genai.Client(api_key=self.api_key)

        self.system_instruction = """
        You are DevGuard, an expert AI Security Auditor, Code Reviewer, and Debugger capable of analyzing code across any programming or scripting language (Python, JavaScript, TypeScript, React/JSX, HTML, CSS, SQL, C/C++, Java, Go, Rust, Bash, PHP, etc.).

        When provided with a code snippet and its programming language:
        1. Identify syntax errors, logic bugs, runtime performance bottlenecks, and security vulnerabilities (e.g., Injection, XSS, Memory Leaks, Unsafe State Management).
        2. Provide clear, step-by-step explanations of what went wrong.
        3. Deliver fully refactored, production-ready code with secure best practices applied.
        """

    def analyze_code(self, code_snippet: str, language: str = "Auto-detect") -> SecurityReport:
        if not isinstance(code_snippet, str):
            raise TypeError("code_snippet must be a string.")

        if not code_snippet.strip():
            raise ValueError("code_snippet cannot be empty.")
        prompt = f"""
        Programming/Scripting Language: {language}

        Code Snippet:
        ```{language.lower()}
        {code_snippet}
        ```

        Perform a security audit of the supplied code.

        Instructions:
        1.Identify genuine security vulnerabilities.
        2.Explain each vulnerability clearly.
        3.Include relevant code evidence.
        4.Suggest a secure remediation.
        5.Assign severity: critical, high, medium, low, or info.
        6.Give a confidence score between 0.0 and 1.0 for each finding.
        7.Do not invent vulnerabilities,evidence, or line numbers.
        8.If no vulnerabilities are found, return an empty findings list.
        9.Return a structured security report.
        """
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=self.system_instruction,
                temperature=0.2,
                response_mime_type="application/json",
                response_schema=SecurityReport,
            )
        )

        if response.parsed is None:
            raise ValueError("Gemini did not return a valid structured report.")
        return SecurityReport.model_validate(response.parsed)
    
