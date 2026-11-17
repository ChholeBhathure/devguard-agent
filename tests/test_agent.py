from unittest.mock import MagicMock, patch
import pytest
from devguard.agent import DevGuardAgent
from devguard.schemas.finding import SecurityReport


@patch("devguard.agent.genai.Client")
def test_agent_initialization(mock_genai_client, monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "fake_test_key")
    agent = DevGuardAgent()
    assert agent.model_name == "gemini-2.5-flash"
    assert agent.api_key == "fake_test_key"
    mock_genai_client.assert_called_once()


@patch("devguard.agent.genai.Client")
def test_analyze_code_returns_structured_report(mock_genai_client, monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "fake_test_key")

    expected_report = SecurityReport(
        project_name="Test Project",
        summary="Test security audit",
        findings=[],
        recommendations=["Use secure coding practices."]
    )
    mock_response = MagicMock()
    mock_response.parsed = expected_report

    # Configure mock client return value
    mock_instance = mock_genai_client.return_value
    mock_instance.models.generate_content.return_value = mock_response

    agent = DevGuardAgent()
    result = agent.analyze_code("print('Hello, World!')")

    assert isinstance(result, SecurityReport)
    assert result.project_name == "Test Project"
    assert result.findings == []

    mock_instance.models.generate_content.assert_called_once()

@patch("devguard.agent.genai.Client")
def test_analyze_code_raises_error_for_missing_response(mock_genai_client, monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "fake_test_key")

    # Mock the Gemini response object
    mock_response = MagicMock()
    mock_response.parsed = None
    
    # Configure mock client return value
    mock_instance = mock_genai_client.return_value
    mock_instance.models.generate_content.return_value = mock_response

    agent = DevGuardAgent()

    with pytest.raises(ValueError, match="valid structured report"):
        agent.analyze_code("print('Hello, World!')")

def test_analyze_code_rejects_empty_input(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "fake_test_key")

    with patch("devguard.agent.genai.Client"):
        agent = DevGuardAgent()
        with pytest.raises(ValueError, match="cannot be empty"):
            agent.analyze_code("   ")  # Input with only whitespace

def test_analyze_code_rejects_non_string_input(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "fake_test_key")

    with patch("devguard.agent.genai.Client"):
        agent = DevGuardAgent()
        with pytest.raises(TypeError, match="must be a string"):
            agent.analyze_code(None)  # Non-string input
@patch("devguard.agent.genai.Client")
def test_analyze_repository_mocked(mock_genai_client, monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "fake_test_key")
    
    # Mock the Gemini response object
    mock_response = MagicMock()
    mock_response.parsed = {
        "project_name": "Test Project",
        "findings": [{
            "title": "SQL Injection",
            "severity": "high",
            "category": "Injection",
            "file_path": "main.py",
            "line_number": 5, # This is line 5 of the chunk
            "description": "Bad SQL",
            "evidence": "query = 'SELECT * FROM users'",
            "recommendation": "Use parameterized queries",
            "confidence": 0.9
        }],
        "summary": "Found issues.",
        "recommendations": ["Fix SQL"]
    }
    
    mock_instance = mock_genai_client.return_value
    mock_instance.models.generate_content.return_value = mock_response
    
    agent = DevGuardAgent()
    
    # Fake files passed by the retriever
    fake_files = [{
        "file_path": "main.py",
        "source_code": "line 1\nline 2\nline 3\nline 4\nline 5\nline 6\nline 7\nline 8\nline 9\nline 10"
    }]
    
    report = agent.analyze_repository(fake_files)
    
    assert report.project_name == "Scanned Project"
    assert len(report.findings) == 1
    assert report.findings[0].title == "SQL Injection"
    # Since the chunk starts at line 1, line 5 stays line 5. 
    # But if the chunk started at line 10, it would be 5 + 10 - 1 = 14.