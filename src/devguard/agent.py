import os
from typing import Dict, Any, List
from dotenv import load_dotenv
from google import genai
from google.genai import types

#Load secrets from the .env files into system environment variables.
load_dotenv()

class DevGuardAgent:
    """ The AI agent responsible for sending project content to Gemini and retrieving code reviews."""

    def __init__(self, model_name: str = "gemini-3.6-flash"):
        #Fetch the key safely from environment variables.
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY is not set in the environment variables.")

        #Initialize the official Gemini client with the API key.
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name

        #System instructions: Tells Gemini who it is and how to behave.
        self.system_instructions = (
            "You are DevGuard, an expert senior code reviewer and security auditor."
            "Analyze the provided Python AST project structure and code context."
            "Identify potential bugs,security vulnerabilities, missing docstrings,"
            "and performance bottlenecks. Provide clear, actionable bullet points."
        )

    def review_codebase(self, project_index: List[Dict[str, Any]]) -> str:
        """Formats the AST metadata and calls Gemini to perform a code review. """

        # Builds the prompt dynamically using our retriever's output.
        prompt = ("Here is the AST structure of the project I want you to review:\n\n")
        prompt += f"{project_index}\n\n"
        prompt += "Please provide a concise code review summary, highlighting potential issues, security vulnerabilities, and suggestions for improvement."

        #Configure system instructions and parameters
        config = types.GenerateContentConfig(
            system_instruction=self.system_instructions,
            temperature=0.2,  #Low temperature makes answers precise and non-creative
        )
        response = self.client.models.generate_content(model=self.model_name, contents=prompt, config=config)
        return response.text