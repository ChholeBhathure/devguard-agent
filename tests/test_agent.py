from unittest.mock import MagicMock, patch
import pytest
from devguard.agent import DevGuardAgent


@patch("devguard.agent.genai.Client")
def test_agent_initialization(mock_genai_client, monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "fake_test_key")
    agent = DevGuardAgent()
    assert agent.model_name == "gemini-2.5-flash"
    assert agent.api_key == "fake_test_key"


@patch("devguard.agent.genai.Client")
def test_analyze_repository_mocked(mock_genai_client, monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "fake_test_key")

    # Mock the Gemini response object
    mock_response = MagicMock()
    mock_response.text = "No critical vulnerabilities found."
    
    # Configure mock client return value
    mock_instance = mock_genai_client.return_value
    mock_instance.models.generate_content.return_value = mock_response

    agent = DevGuardAgent()
    sample_files = [{"filename": "main.py", "ast": "Module(...)"}]
    
    result = agent.analyze_repository(sample_files)

    assert "No critical vulnerabilities found." in result
    assert mock_instance.models.generate_content.called