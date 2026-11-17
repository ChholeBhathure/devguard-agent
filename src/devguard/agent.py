import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
from devguard.schemas.finding import SecurityReport

load_dotenv()

class DevGuardAgent:
    def __init__(self, api_key: str = None, token_limit: int = 8000, model_name: str = "gemini-2.5-flash"):
        self.token_limit = token_limit
        self.model_name = model_name
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not set in the environment variables.")
        self.client = genai.Client(api_key=self.api_key)
        self.system_instruction = "You are DevGuard, an expert AI Security Auditor. Return a structured security report."

    def analyze_code(self, code_snippet: str, language: str = "Auto-detect") -> SecurityReport:
        if not isinstance(code_snippet, str):
            raise TypeError("code_snippet must be a string.")
        if not code_snippet.strip():
            raise ValueError("code_snippet cannot be empty.")

        prompt = f"Language: {language}\n\nCode:\n```{language.lower()}\n{code_snippet}\n```"

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