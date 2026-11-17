from typing import Literal
from pydantic import BaseModel, Field

class SecurityFinding(BaseModel):
    title: str
    severity: Literal["critical", "high", "medium", "low", "info"]
    category: str
    file_path: str | None = None
    line_number: int | None = None
    description: str
    evidence: str
    recommendation: str
    confidence: float = Field(ge=0.0, le=1.0)

class SecurityReport(BaseModel):
    project_name: str
    findings: list[SecurityFinding]
    summary: str
    recommendations: list[str]