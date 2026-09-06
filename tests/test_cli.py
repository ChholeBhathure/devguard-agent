from pathlib import Path
from devguard.cli import save_report

def test_save_markdown_report(tmp_path):
    output_file = tmp_path / "report.md"
    save_report("Audit Summary", str(output_file))

    assert output_file.exists()
    assert output_file.read_text(encoding="utf-8") == "Audit Summary"

def test_save_html_report(tmp_path):
    output_file = tmp_path / "report.html"
    save_report("Audit Summary", str(output_file))
    assert output_file.exists()
    content = output_file.read_text(encoding="utf-8").lower()
    assert "<html" in content
    assert "</html>" in content