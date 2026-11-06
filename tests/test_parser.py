import tempfile
from pathlib import Path
import os
from devguard.parser import CodeStructureVisitor,parse_python_file

def test_nested_function_metadata():
    sample_code = """
class UserService:
    def authenticate(self):
        def validate_password():
            pass
        return validate_password()
"""
    
    
    with tempfile.TemporaryDirectory() as temp_dir:
        file_path = Path(temp_dir) / "sample.py"
        file_path.write_text(sample_code,encoding="utf-8")
        
        result = parse_python_file(file_path)
    functions = result["functions"]
    
    assert len(functions) == 2

    assert functions[0]["scope"] == "method"
    assert functions[0]["qualified_name"] == ("UserService.authenticate")

    assert functions[1]["scope"] == "nested"
    assert functions[1]["qualified_name"] == ("UserService.authenticate.validate_password")
    

    def test_parse_simple_python_file():
        """Test that parse_python_file correctly extracts functions and classes."""
        sample_code = """
    import os
    from pathlib import Path
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
            assert len(result["imports"])==2
            assert result["imports"][0]["name"]=="import os"
            assert result["imports"][0]["lineno"] == 2
            assert result["imports"][1]["name"]=="from pathlib import Path"
            assert result["imports"][1]["lineno"] == 3
        # assert result["functions"][0]["name"] == "sample_function"
        finally:
            os.remove(temp_path)