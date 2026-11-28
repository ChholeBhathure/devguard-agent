import pytest
from pathlib import Path
from devguard.retriever import LocalRetriever

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
def test_invalid_project_directory():
    with pytest.raises(ValueError, match="Invalid project directory"):
        LocalRetriever(root_dir="non_existent_dir")

def test_invalid_ignore_dirs_config(tmp_path):
    """ignore_dirs must be a list."""
    config = {
        "ignore_dirs": ".venv",
        "max_file_size_kb": 500
    }
    with pytest.raises(ValueError, match="ignore_dirs must be a list"):
        LocalRetriever(root_dir=str(tmp_path), config=config)

def test_ignored_directories_are_skipped(tmp_path):
    """Files inside ignored directories should not be scanned."""
    config = {
        "ignore_dirs": ["venv"],
        "max_file_size_kb": 500
    }
    ignored_dir = tmp_path / "venv"
    ignored_dir.mkdir()
    (ignored_dir / "ignored.py").write_text("print('ignored')")

    (tmp_path / "main.py").write_text("print('included')")

    retriever = LocalRetriever(tmp_path,config)
    files = retriever.scan_directory()

    assert len(files) == 1
    assert files[0]["file_name"] == "main.py"

def test_oversized_files_are_skipped(tmp_path):
    """Files exceeding max_file_size_kb should be skipped."""
    config = {
        "ignore_dirs": [],
        "max_file_size_kb": 1  # 1 KB limit
    }

    large_file = tmp_path / "large.py"
    large_file.write_text("#" + "x" * 2048)  # 2 KB file

    retriever = LocalRetriever(tmp_path, config)
    files = retriever.scan_directory()

    assert len(files) == 0
    assert len(retriever.scan_errors) == 1
    assert "maximum allowed size" in retriever.scan_errors[0]["error"]

def test_invalid_python_file_is_recorded(tmp_path):
    """Syntax errors should be recorded without stopping the scan."""
    config = {
        "ignore_dirs": [],
        "max_file_size_kb": 500
    }

    (tmp_path / "broken.py").write_text("def broken_function(:\n    pass")  # Invalid syntax
    (tmp_path / "valid.py").write_text("def valid_function():\n    return True")

    retriever = LocalRetriever(tmp_path, config)
    files = retriever.scan_directory()

    assert len(files) == 1
    assert files[0]["file_name"] == "valid.py"
    assert len(retriever.scan_errors) == 1
    assert "broken.py" in retriever.scan_errors[0]["file"]
def test_symlink_outside_project_is_skipped(tmp_path):
    """Files linked from outside the project must not be scanned."""
    project_dir = tmp_path / "project"
    project_dir.mkdir()

    external_file = tmp_path / "secret.py"
    external_file.write_text(
        "SECRET = 'outside project'",
        encoding="utf-8"
    )

    symlink_file = project_dir / "linked_secret.py"

    try:
        symlink_file.symlink_to(external_file)
    except (OSError, NotImplementedError):
        pytest.skip("Symlink creation is not supported on this system")

    retriever = LocalRetriever(
        root_dir=project_dir,
        config={"ignore_dirs": [], "max_file_size_kb": 500}
    )

    files = retriever.scan_directory()

    assert files == []
    assert len(retriever.scan_errors) == 1
    assert "outside the selected project directory" in (
        retriever.scan_errors[0]["error"]
    )
@pytest.mark.parametrize(
    "invalid_size",
    [0, -100, 1.5, "500", True, None]
)
def test_invalid_max_file_size_config(tmp_path, invalid_size):
    """Invalid max_file_size_kb values should be rejected."""
    config = {
        "ignore_dirs": [],
        "max_file_size_kb": invalid_size,
    }

    with pytest.raises(
        ValueError,
        match="max_file_size_kb must be a positive integer"
    ):
        LocalRetriever(root_dir=tmp_path, config=config)


def test_valid_max_file_size_config(tmp_path):
    """A positive integer file-size limit should be accepted."""
    config = {
        "ignore_dirs": [],
        "max_file_size_kb": 100,
    }

    retriever = LocalRetriever(root_dir=tmp_path, config=config)

    assert retriever.max_file_size_bytes == 100 * 1024