import json
from unittest.mock import MagicMock, patch

import pytest

from devguard.agent import DevGuardAgent
from devguard.schemas.finding import SecurityReport


def make_mock_response(report):
    """Create an OpenAI-compatible mock response."""
    response = MagicMock()
    response.choices[0].message.content = report.model_dump_json()
    return response


@patch("devguard.agent.OpenAI")
def test_agent_initialization(mock_openai, monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "fake_test_key")

    agent = DevGuardAgent()

    assert agent.api_key == "fake_test_key"
    assert agent.client == mock_openai.return_value

    mock_openai.assert_called_once_with(
        base_url="https://openrouter.ai/api/v1",
        api_key="fake_test_key"
    )


@patch("devguard.agent.OpenAI")
def test_analyze_code_returns_structured_report(mock_openai, monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "fake_test_key")

    expected_report = SecurityReport(
        project_name="Test Project",
        summary="Test security audit",
        findings=[],
        recommendations=["Use secure coding practices."]
    )

    mock_instance = mock_openai.return_value
    mock_instance.chat.completions.create.return_value = (
        make_mock_response(expected_report)
    )

    agent = DevGuardAgent()
    result = agent.analyze_code("print('Hello, World!')")

    assert isinstance(result, SecurityReport)
    assert result.project_name == "Test Project"
    assert result.findings == []

    mock_instance.chat.completions.create.assert_called_once()


@patch("devguard.agent.OpenAI")
def test_analyze_code_raises_error_for_missing_response(
    mock_openai, monkeypatch
):
    monkeypatch.setenv("OPENROUTER_API_KEY", "fake_test_key")

    mock_instance = mock_openai.return_value
    mock_response = MagicMock()
    mock_response.choices[0].message.content = None

    mock_instance.chat.completions.create.return_value = mock_response

    agent = DevGuardAgent()

    # Current fallback implementation retries each model
    # and raises an exception if every attempt fails.
    with pytest.raises(Exception, match="All model attempts failed"):
        agent.analyze_code("print('Hello, World!')")

    assert mock_instance.chat.completions.create.call_count == 3


@patch("devguard.agent.OpenAI")
def test_analyze_code_rejects_empty_input(mock_openai, monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "fake_test_key")

    agent = DevGuardAgent()

    with pytest.raises(ValueError):
        agent.analyze_code("   ")

    mock_openai.return_value.chat.completions.create.assert_not_called()


@patch("devguard.agent.OpenAI")
def test_analyze_code_rejects_non_string_input(mock_openai, monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "fake_test_key")

    agent = DevGuardAgent()

    with pytest.raises(TypeError):
        agent.analyze_code(None)

    mock_openai.return_value.chat.completions.create.assert_not_called()


@patch("devguard.agent.OpenAI")
def test_analyze_repository_mocked(mock_openai, monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "fake_test_key")

    expected_report = SecurityReport(
        project_name="Test Project",
        findings=[
            {
                "title": "SQL Injection",
                "severity": "high",
                "category": "Injection",
                "file_path": "main.py",
                "line_number": 5,
                "description": "Unsafe SQL query construction.",
                "evidence": "query = 'SELECT * FROM users'",
                "recommendation": "Use parameterized queries.",
                "confidence": 0.9
            }
        ],
        summary="Found issues.",
        recommendations=["Fix SQL injection."]
    )

    mock_instance = mock_openai.return_value
    mock_instance.chat.completions.create.return_value = (
        make_mock_response(expected_report)
    )

    agent = DevGuardAgent()

    fake_files = [
        {
            "file_path": "main.py",
            "source_code": (
                "line 1\n"
                "line 2\n"
                "line 3\n"
                "line 4\n"
                "line 5\n"
                "line 6\n"
                "line 7\n"
                "line 8\n"
                "line 9\n"
                "line 10"
            )
        }
    ]

    report = agent.analyze_repository(fake_files)

    assert report.project_name == "Scanned Project"
    assert len(report.findings) == 1

    finding = report.findings[0]

    assert finding.title == "SQL Injection"
    assert finding.file_path == "main.py"
    assert finding.line_number == 5

    mock_instance.chat.completions.create.assert_called_once()