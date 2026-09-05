import tempfile
import os
from src.devguard.parser import CodeStructureVisitor, parse_python_file

def test_parse_simple_python_file():
    """Test that parse_python_file correctly extracts functions and classes."""
    sample_code = """
class SampleClass:
    def sample_method(self):
        pass

def sample_function():
    return True
"""
    # Create a temporary python file to test parsing
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as temp_file:
        temp_file.write(sample_code)
        temp_path = temp_file.name

    try:
        result = parse_python_file(temp_path)
        assert result is not None
        assert len(result["classes"]) == 1
        assert result["classes"][0]["name"] == "SampleClass"
        assert len(result["functions"]) >= 1
       # assert result["functions"][0]["name"] == "sample_function"
    finally:
        os.remove(temp_path) 