import pytest
from pydantic import ValidationError
from devguard.schemas.finding import SecurityFinding, SecurityReport,  FailedChunk

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

def test_security_report_defaults_to_no_failed_chunks():
    report = SecurityReport(
        project_name="Demo",
        findings=[],
        summary="Analysis completed",
        recommendations=[]
    )

    assert report.failed_chunks == []


def test_failed_chunk_validation():
    report = SecurityReport(
        project_name="Demo",
        findings=[],
        summary="Partial analysis",
        recommendations=[],
        failed_chunks=[
            FailedChunk(
                file_path="auth.py",
                start_line=50,
                end_line=100,
                error="API request failed"
            )
        ]
    )

    assert len(report.failed_chunks) == 1
    assert report.failed_chunks[0].file_path == "auth.py"
    assert report.failed_chunks[0].start_line == 50

def test_security_report_defaults_to_no_warnings():
    report = SecurityReport(
        project_name="Demo",
        findings=[],
        summary="Analysis completed",
        recommendations=[]
    )

    assert report.warnings == []


def test_security_report_accepts_warnings():
    report = SecurityReport(
        project_name="Demo",
        findings=[],
        summary="Analysis completed with warnings",
        recommendations=[],
        warnings=["Invalid line number in auth.py"]
    )

    assert len(report.warnings) == 1
    assert report.warnings[0] == "Invalid line number in auth.py"    