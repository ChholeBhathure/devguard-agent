import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
from devguard.schemas.finding import SecurityReport

load_dotenv()

class DevGuardAgent:
    def __init__(self, api_key: str = None, token_limit: int = 8000, model_name: str = "gemini-3.6-flash"):
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

    def analyze_repository(self, files: list[dict]) -> SecurityReport:
        from devguard.chunker import chunk_source_code
        
        all_findings = []
        project_name = "Scanned Project"
        
        # 1. Loop through every file the retriever found
        for file_entry in files:
            source_code = file_entry.get("source_code", "")
            file_path = file_entry.get("file_path", "unknown.py")
            
            if not source_code:
                continue
                
            # 2. Chunk the file's source code
            chunks = chunk_source_code(source_code, file_path)
            
            # 3. Analyze each chunk with Gemini
            for chunk in chunks:
                chunk_code = chunk["source_code"]
                start_line = chunk["start_line"]
                end_line = chunk["end_line"]
                
                # Create a prompt specific to this chunk
                prompt = f"File: {file_path}\nLines {start_line} to {end_line}\n\nCode:\n```python\n{chunk_code}\n```"
                
                # We reuse our existing Gemini call logic, but we need to handle the response
                # (We will refine this in the next step to handle errors and rate limits)
                try:
                    #Create a specialized prompt for the chunk
                    chunk_prompt=f"Audit this code from file'{file_path}'(lines{start_line}-{end_line}):\n\n{chunk_code}"
                    # Note: We are currently calling analyze_code for every chunk. 
                    # In a real app, we might want a dedicated method that doesn't repeat the project_name setup.
                    chunk_report = self.analyze_code(chunk_code, language="python")
                    
                    # Fix the line numbers to match the original file
                    for finding in chunk_report.findings:
                        finding.file_path=file_path
                        if finding.line_number:
                            # Adjust relative line number to absolute file line
                            finding.line_number = finding.line_number + start_line - 1
                        all_findings.append(finding)
                        
                except Exception as e:
                    print(f"Failed to analyze chunk in {file_path}: {e}")
                    continue

        # 4. Aggregate the findings into one final report
        final_report = SecurityReport(
            project_name=project_name,
            findings=all_findings,
            summary=f"Analyzed {len(files)} files and found {len(all_findings)} potential issues.",
            recommendations=["Review the findings and apply the suggested remediations."]
        )
        
        return final_report