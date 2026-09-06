import tempfile
import os
from src.devguard.retriever import LocalRetriever

def test_scan_directory_ignores_venv(tmp_path):
    # Setup tests structure inside tmp_path
    venv_dir = tmp_path / ".venv"
    venv_dir.mkdir()
    (venv_dir / "ignored.py").write_text("def hidden(): pass")

    valid_file = tmp_path / "app.py"
    valid_file.write_text("def hello(): pass")

    # Pass explicit config to ensure clean test environment
    test_config = {"ignore_dirs": [".venv", "venv"]}
    retriever = LocalRetriever(root_dir=str(tmp_path), config=test_config)
    result = retriever.scan_directory()

    assert len(result) == 1