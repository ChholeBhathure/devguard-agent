import pytest
from pydantic import ValidationError
from devguard.schemas.finding import SecurityFinding, SecurityReport

def test_security_finding_validation():
    finding = SecurityFinding(
        title="SQL Injection",
        severity="high",
        category= "Injection",
        description="User imput is directly added to SQL.",
        evidence="SQL query uses string concatenation.",
        recommendation="Use parameterized queries.",
        confidence=0.95

    )

    assert finding.severity == "high"
    assert finding.confidence == 0.95

def test_invalid_severity_is_rejected():
    with pytest.raises(ValidationError):
        SecurityFinding(
            title="Test",
            severity="urgent",
            category="Injection",
            description="Test description",
            evidence="Test evidence",
            recommendation="Test recommendation",
            confidence=0.9,
        )

def test_confidence_outside_range_is_rejected():
    with pytest.raises(ValidationError):
        SecurityFinding(
            title="Test",
            severity="low",
            category="Test",
            description="Test description",
            evidence="Test evidence",
            recommendation="Test recommendation",
            confidence=1.5,  # Invalid confidence
        )

def test_security_report_validation():
    report = SecurityReport(
        project_name="Demo Project",
        summary="One security issue found.",
        findings=[],
        recommendations=["Use secure coding practices."],
    )
    assert report.project_name == "Demo Project"
    assert len(report.findings) == 0