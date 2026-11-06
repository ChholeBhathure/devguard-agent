from unittest.mock import MagicMock, patch
import pytest
from devguard.agent import DevGuardAgent
from devguard.schemas.finding import SecurityReport


@patch("devguard.agent.genai.Client")
def test_agent_initialization(mock_genai_client, monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "fake_test_key")
    agent = DevGuardAgent()
    assert agent.model_name == "gemini-3.6-flash"
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