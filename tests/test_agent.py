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

    assert mock_instance.chat.completions.create.call_count == 1


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

@patch("devguard.agent.OpenAI")
def test_analyze_repository_continues_after_chunk_failure(
    mock_openai, monkeypatch
):
    monkeypatch.setenv("OPENROUTER_API_KEY", "fake_test_key")

    chunks = [
        {
            "file_path": "main.py",
            "start_line": 1,
            "end_line": 10,
            "source_code": "chunk 1"
        },
        {
            "file_path": "main.py",
            "start_line": 11,
            "end_line": 20,
            "source_code": "chunk 2"
        },
        {
            "file_path": "main.py",
            "start_line": 21,
            "end_line": 30,
            "source_code": "chunk 3"
        }
    ]

    with patch(
        "devguard.chunker.chunk_source_code",
        return_value=chunks
    ):
        agent = DevGuardAgent()

        first_report = SecurityReport(
            project_name="Test",
            findings=[
                {
                    "title": "SQL Injection",
                    "severity": "high",
                    "category": "Injection",
                    "file_path": None,
                    "line_number": 2,
                    "description": "Unsafe SQL query.",
                    "evidence": "query = user_input",
                    "recommendation": "Use parameterized queries.",
                    "confidence": 0.9
                }
            ],
            summary="Finding detected.",
            recommendations=[]
        )

        third_report = SecurityReport(
            project_name="Test",
            findings=[
                {
                    "title": "Hardcoded Secret",
                    "severity": "high",
                    "category": "Secrets",
                    "file_path": None,
                    "line_number": 3,
                    "description": "Hardcoded password.",
                    "evidence": "password = 'secret'",
                    "recommendation": "Use environment variables.",
                    "confidence": 0.95
                }
            ],
            summary="Finding detected.",
            recommendations=[]
        )

        agent.analyze_code = MagicMock(
            side_effect=[
                first_report,
                RuntimeError("API temporarily unavailable"),
                third_report
            ]
        )

        report = agent.analyze_repository([
            {
                "file_path": "main.py",
                "source_code": "dummy source code"
            }
        ])

    assert len(report.findings) == 2
    assert report.findings[0].title == "SQL Injection"
    assert report.findings[1].title == "Hardcoded Secret"

    assert len(report.failed_chunks) == 1
    assert report.failed_chunks[0].file_path == "main.py"
    assert report.failed_chunks[0].start_line == 11
    assert report.failed_chunks[0].end_line == 20

    assert "partially completed" in report.summary.lower()
    assert agent.analyze_code.call_count == 3


@patch("devguard.agent.OpenAI")
def test_analyze_repository_returns_report_when_all_chunks_fail(
    mock_openai, monkeypatch
):
    monkeypatch.setenv("OPENROUTER_API_KEY", "fake_test_key")

    chunks = [
        {
            "file_path": "auth.py",
            "start_line": 1,
            "end_line": 10,
            "source_code": "chunk 1"
        },
        {
            "file_path": "auth.py",
            "start_line": 11,
            "end_line": 20,
            "source_code": "chunk 2"
        }
    ]

    with patch(
        "devguard.chunker.chunk_source_code",
        return_value=chunks
    ):
        agent = DevGuardAgent()

        agent.analyze_code = MagicMock(
            side_effect=RuntimeError("API request failed")
        )

        report = agent.analyze_repository([
            {
                "file_path": "auth.py",
                "source_code": "dummy source code"
            }
        ])

    assert report.findings == []
    assert len(report.failed_chunks) == 2

    assert "analysis failed for every chunk" in report.summary.lower()
    assert report.failed_chunks[0].error == "API request failed"
    assert report.failed_chunks[1].start_line == 11


@patch("devguard.agent.OpenAI")
def test_analyze_repository_records_failed_chunk_error(
    mock_openai, monkeypatch
):
    monkeypatch.setenv("OPENROUTER_API_KEY", "fake_test_key")

    chunks = [
        {
            "file_path": "payment.py",
            "start_line": 40,
            "end_line": 60,
            "source_code": "chunk code"
        }
    ]

    with patch(
        "devguard.chunker.chunk_source_code",
        return_value=chunks
    ):
        agent = DevGuardAgent()

        agent.analyze_code = MagicMock(
            side_effect=ValueError("Invalid model response")
        )

        report = agent.analyze_repository([
            {
                "file_path": "payment.py",
                "source_code": "dummy source code"
            }
        ])

    failed_chunk = report.failed_chunks[0]

    assert failed_chunk.file_path == "payment.py"
    assert failed_chunk.start_line == 40
    assert failed_chunk.end_line == 60
    assert failed_chunk.error == "Invalid model response"

@patch("devguard.agent.OpenAI")
def test_analyze_repository_removes_duplicate_findings(
    mock_openai, monkeypatch
):
    monkeypatch.setenv("OPENROUTER_API_KEY", "fake_test_key")

    chunks = [
        {
            "file_path": "auth.py",
            "start_line": 1,
            "end_line": 10,
            "source_code": "\n".join(["line"]*10)
        },
        {
            "file_path": "auth.py",
            "start_line": 6,
            "end_line": 15,
            "source_code": "\n".join(["line"]*10)
        }
    ]

    duplicate_finding = {
        "title": "SQL Injection",
        "severity": "high",
        "category": "Injection",
        "file_path": None,
        "line_number": 8,
        "description": "Unsafe SQL query.",
        "evidence": "query = user_input",
        "recommendation": "Use parameterized queries.",
        "confidence": 0.9
    }

    first_report = SecurityReport(
        project_name="Test",
        findings=[duplicate_finding],
        summary="First chunk.",
        recommendations=[]
    )
    second_chunk_duplicate = {
        **duplicate_finding,
        "line_number":3
    }
    second_report = SecurityReport(
        project_name="Test",
        findings=[second_chunk_duplicate],
        summary="Second chunk.",
        recommendations=[]
    )

    with patch(
        "devguard.chunker.chunk_source_code",
        return_value=chunks
    ):
        agent = DevGuardAgent()
        agent.analyze_code = MagicMock(
            side_effect=[first_report, second_report]
        )

        report = agent.analyze_repository([
            {
                "file_path": "auth.py",
                "source_code": "dummy source code"
            }
        ])

    assert len(report.findings) == 1
    assert report.findings[0].title == "SQL Injection"
    assert report.findings[0].file_path == "auth.py"
    assert report.findings[0].line_number == 8


@patch("devguard.agent.OpenAI")
def test_analyze_repository_preserves_distinct_findings(
    mock_openai, monkeypatch
):
    monkeypatch.setenv("OPENROUTER_API_KEY", "fake_test_key")

    chunks = [
        {
            "file_path": "auth.py",
            "start_line": 1,
            "end_line": 10,
            "source_code": "chunk 1"
        },
        {
            "file_path": "auth.py",
            "start_line": 6,
            "end_line": 15,
            "source_code": "chunk 2"
        }
    ]

    first_finding = {
        "title": "SQL Injection",
        "severity": "high",
        "category": "Injection",
        "file_path": None,
        "line_number": 8,
        "description": "Unsafe SQL query.",
        "evidence": "query = user_input",
        "recommendation": "Use parameterized queries.",
        "confidence": 0.9
    }

    second_finding = {
        "title": "Hardcoded Secret",
        "severity": "high",
        "category": "Secrets",
        "file_path": None,
        "line_number": 3,
        "description": "Hardcoded password.",
        "evidence": "password = 'secret'",
        "recommendation": "Use environment variables.",
        "confidence": 0.95
    }

    first_report = SecurityReport(
        project_name="Test",
        findings=[first_finding],
        summary="First chunk.",
        recommendations=[]
    )
    second_report = SecurityReport(
        project_name="Test",
        findings=[second_finding],
        summary="Second chunk.",
        recommendations=[]
    )

    with patch(
        "devguard.chunker.chunk_source_code",
        return_value=chunks
    ):
        agent = DevGuardAgent()
        agent.analyze_code = MagicMock(
            side_effect=[first_report, second_report]
        )

        report = agent.analyze_repository([
            {
                "file_path": "auth.py",
                "source_code": "dummy source code"
            }
        ])

    assert len(report.findings) == 2

    titles = {finding.title for finding in report.findings}

    assert titles == {"SQL Injection", "Hardcoded Secret"}

@patch("devguard.agent.OpenAI")
def test_analyze_repository_converts_chunk_line_to_file_line(
    mock_openai, monkeypatch
):
    monkeypatch.setenv("OPENROUTER_API_KEY", "fake_test_key")

    chunks = [
        {
            "file_path": "auth.py",
            "start_line": 1,
            "end_line": 100,
            "source_code": "first chunk"
        },
        {
            "file_path": "auth.py",
            "start_line": 96,
            "end_line": 195,
            "source_code": "\n".join(["line"]*100)
        }
    ]

    second_chunk_report = SecurityReport(
        project_name="Test",
        findings=[
            {
                "title": "SQL Injection",
                "severity": "high",
                "category": "Injection",
                "file_path": None,
                "line_number": 25,
                "description": "Unsafe SQL query.",
                "evidence": "query = user_input",
                "recommendation": "Use parameterized queries.",
                "confidence": 0.9
            }
        ],
        summary="Finding detected.",
        recommendations=[]
    )

    with patch(
        "devguard.chunker.chunk_source_code",
        return_value=chunks
    ):
        agent = DevGuardAgent()

        agent.analyze_code = MagicMock(
            side_effect=[
                SecurityReport(
                    project_name="Test",
                    findings=[],
                    summary="No findings.",
                    recommendations=[]
                ),
                second_chunk_report
            ]
        )

        report = agent.analyze_repository([
            {
                "file_path": "auth.py",
                "source_code": "dummy source code"
            }
        ])

    assert len(report.findings) == 1
    assert report.findings[0].line_number == 120
    assert report.findings[0].file_path == "auth.py"

@pytest.mark.parametrize("invalid_line", [0, -5, 150])
@patch("devguard.agent.OpenAI")
def test_analyze_repository_preserves_finding_with_invalid_line_number(
    mock_openai, monkeypatch, invalid_line
):
    monkeypatch.setenv("OPENROUTER_API_KEY", "fake_test_key")

    chunks = [
        {
            "file_path": "auth.py",
            "start_line": 10,
            "end_line": 19,
            "source_code": "\n".join(["line"] * 10)
        }
    ]

    chunk_report = SecurityReport(
        project_name="Test",
        findings=[
            {
                "title": "SQL Injection",
                "severity": "high",
                "category": "Injection",
                "file_path": None,
                "line_number": invalid_line,
                "description": "Unsafe SQL query.",
                "evidence": "query = user_input",
                "recommendation": "Use parameterized queries.",
                "confidence": 0.9
            }
        ],
        summary="Finding detected.",
        recommendations=[]
    )

    with patch(
        "devguard.chunker.chunk_source_code",
        return_value=chunks
    ):
        agent = DevGuardAgent()
        agent.analyze_code = MagicMock(return_value=chunk_report)

        report = agent.analyze_repository([
            {
                "file_path": "auth.py",
                "source_code": "dummy source code"
            }
        ])

    assert len(report.findings) == 1
    assert report.findings[0].file_path == "auth.py"
    assert report.findings[0].line_number is None
    assert len(report.warnings) == 1
    assert "Invalid line number" in report.warnings[0]

@patch("devguard.agent.OpenAI")
def test_analyze_repository_accepts_valid_chunk_line_number(
    mock_openai, monkeypatch
):
    monkeypatch.setenv("OPENROUTER_API_KEY", "fake_test_key")

    chunks = [
        {
            "file_path": "auth.py",
            "start_line": 10,
            "end_line": 19,
            "source_code": "\n".join(["line"] * 10)
        }
    ]

    chunk_report = SecurityReport(
        project_name="Test",
        findings=[
            {
                "title": "SQL Injection",
                "severity": "high",
                "category": "Injection",
                "file_path": None,
                "line_number": 5,
                "description": "Unsafe SQL query.",
                "evidence": "query = user_input",
                "recommendation": "Use parameterized queries.",
                "confidence": 0.9
            }
        ],
        summary="Finding detected.",
        recommendations=[]
    )

    with patch(
        "devguard.chunker.chunk_source_code",
        return_value=chunks
    ):
        agent = DevGuardAgent()
        agent.analyze_code = MagicMock(return_value=chunk_report)

        report = agent.analyze_repository([
            {
                "file_path": "auth.py",
                "source_code": "dummy source code"
            }
        ])

    assert report.findings[0].line_number == 14
    assert report.warnings == []