import pytest
from pathlib import Path
from devguard.cli import save_report

def test_save_markdown_report(tmp_path):
    output_file = tmp_path / "audit_report.md"
    sample_content = "# Audit Report\n- No vulnerabilities found."

    save_report(sample_content, output_file)

    assert output_file.exists()
    assert output_file.read_text(encoding="utf-8") == sample_content

def test_save_html_report(tmp_path):
    output_file = tmp_path / "audit_report.html"
    sample_content = "Security Audit Passed"

    save_report(sample_content, output_file)

    assert output_file.exists()
    assert "<html>" in output_file.read_text(encoding="utf-8")
    assert "Security Audit Passed" in output_file.read_text(encoding="utf-8")