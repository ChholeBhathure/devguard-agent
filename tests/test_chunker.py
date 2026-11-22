import pytest
from devguard.chunker import chunk_source_code

def test_chunk_source_code_basic():
    code = "line 1\nline 2\nline 3\nline 4\nline 5\n"
    chunks = chunk_source_code(code, "auth.py", max_tokens=2, overlap_lines=1)
    
    assert len(chunks) > 0
    assert chunks[0]["file_path"] == "auth.py"
    assert chunks[0]["start_line"] == 1

def test_chunk_source_code_empty():
    chunks = chunk_source_code("", "empty.py")
    assert chunks == []

def test_chunk_source_code_invalid_tokens():
    with pytest.raises(ValueError):
        chunk_source_code("some code", "file.py", max_tokens=0)

def test_chunk_source_code_preserves_line_numbers():
    source = "line1\nline2\nline3\nline4\n"

    chunks = chunk_source_code(
        source,
        "main.py",
        max_tokens=2,
        overlap_lines=0
    )

    assert chunks[0]["start_line"] == 1
    assert chunks[-1]["end_line"] == 4


def test_chunk_source_code_preserves_file_path():
    source = "print('hello')\n"

    chunks = chunk_source_code(source, "main.py")

    assert chunks[0]["file_path"] == "main.py"


def test_chunk_source_code_returns_empty_for_empty_input():
    chunks = chunk_source_code("", "main.py")

    assert chunks == []


def test_chunk_source_code_rejects_invalid_token_limit():
    with pytest.raises(ValueError):
        chunk_source_code(
            "print('hello')",
            "main.py",
            max_tokens=0
        )


def test_chunk_source_code_rejects_negative_overlap():
    with pytest.raises(ValueError):
        chunk_source_code(
            "print('hello')",
            "main.py",
            overlap_lines=-1
        )