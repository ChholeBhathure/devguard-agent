import os
from typing import List, Dict, Any
from dotenv import load_dotenv
from google import genai
from google.genai import types
from devguard.chunker import chunk_ast_payloads

# Load secrets from the .env file into system environment variables.
load_dotenv()


class DevGuardAgent:
    def __init__(self, api_key: str = None, token_limit: int = 8000, model_name: str = "gemini-3.6-flash"):
        self.token_limit = token_limit
        self.model_name = model_name
        
        # Use provided api_key or fall back to environment variable
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not set in the environment variables.")

        # Initialize the official Gemini client with the API key
        self.client = genai.Client(api_key=self.api_key)

        # System instructions: Frame strictly around educational code quality and refactoring
        self.system_instructions = (
            """You are DevGuard, an AI assistant for educational Python code review and refactoring.
               Your goal is to review code snippets, explain best practices for data safety, and show refactored examples using parameterized inputs or modern coding standards.
               # System instructions: Frame strictly around educational code quality and refactoring
        self.system_instructions = (
            """You are DevGuard, an AI assistant for educational Python code review and refactoring.
Your goal is to review code snippets, explain best practices for data safety, and show refactored examples using parameterized inputs or modern coding standards.
Always respond with helpful recommendations and corrected code examples."""
        )Always respond with helpful recommendations and corrected code examples."""
        )

    def analyze_repository(self, indexed_files: List[Dict[str, Any]]) -> str:
        """
        Chunks AST payloads within token budgets and analyzes each chunk.
        """
        chunks = chunk_ast_payloads(indexed_files, max_tokens=self.token_limit)
        results = []

        config = types.GenerateContentConfig(
            system_instruction=self.system_instructions,
            temperature=0.2,
        )

        for idx, chunk in enumerate(chunks, 1):
            prompt = (
            f"Review the following Python code AST batch ({idx}/{len(chunks)}):\n{chunk}\n\n"
            "Please provide an educational code review, explaining best practices "
            "and showing refactored code examples to improve data safety."
            )
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config,
            )
            results.append(response.text)

        return "\n\n".join(results)

    def review_codebase(self, project_index: List[Dict[str, Any]]) -> str:
        """
        Formats the AST metadata and calls Gemini to perform a code review.
        """
        prompt = f"Here is the AST structure of the project I want you to review:\n\n{project_index}\n\nPlease provide a concise code review summary, highlighting potential issues, security risks, or improvements."

        config = types.GenerateContentConfig(
            system_instruction=self.system_instructions,
            temperature=0.2,
        )

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=config,
        )
        return response.text
    
