import pytest

from devguard.chunker import chunk_source_code


def test_chunk_source_code_basic():
    code = "line 1\nline 2\nline 3\nline 4\nline 5\n"

    chunks = chunk_source_code(
        code, "auth.py", max_tokens=2, overlap_lines=1
    )

    assert len(chunks) > 0
    assert chunks[0]["file_path"] == "auth.py"
    assert chunks[0]["start_line"] == 1


def test_chunk_source_code_empty():
    assert chunk_source_code("", "empty.py") == []


def test_chunk_source_code_invalid_token_limit():
    with pytest.raises(ValueError):
        chunk_source_code("some code", "file.py", max_tokens=0)


def test_chunk_source_code_negative_overlap():
    with pytest.raises(ValueError):
        chunk_source_code("some code", "file.py", overlap_lines=-1)


def test_chunk_source_code_preserves_line_numbers():
    source = "line1\nline2\nline3\nline4\n"

    chunks = chunk_source_code(
        source, "main.py", max_tokens=2, overlap_lines=0
    )

    assert chunks[0]["start_line"] == 1
    assert chunks[-1]["end_line"] == 4


def test_chunk_source_code_preserves_file_path():
    chunks = chunk_source_code("print('hello')\n", "main.py")

    assert chunks[0]["file_path"] == "main.py"


def test_chunk_source_code_preserves_overlap():
    source = "line 1\nline 2\nline 3\nline 4\n"

    chunks = chunk_source_code(
        source, "main.py", max_tokens=4, overlap_lines=2
    )

    
    # The second chunk should begin with the last two lines
    # of the first chunk.
    first_lines = chunks[0]["source_code"].splitlines()
    second_lines = chunks[1]["source_code"].splitlines()

    assert len(chunks) > 2
    

    assert second_lines[:2] == first_lines[-2:]


def test_chunk_source_code_handles_large_single_line():
    source = "x" * 1000

    chunks = chunk_source_code(
        source, "large.py", max_tokens=10, overlap_lines=0
    )

    assert len(chunks) > 1
    assert all(chunk["start_line"] == 1 for chunk in chunks)
    assert all(chunk["end_line"] == 1 for chunk in chunks)

    # All pieces together should preserve the original line.
    assert "".join(chunk["source_code"] for chunk in chunks) == source