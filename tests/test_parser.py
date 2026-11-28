import tempfile
from pathlib import Path
from textwrap import dedent

from devguard.parser import parse_python_file


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
        file_path.write_text(sample_code, encoding="utf-8")

        result = parse_python_file(file_path)

    functions = result["functions"]

    assert len(functions) == 2
    assert functions[0]["scope"] == "method"
    assert functions[0]["qualified_name"] == "UserService.authenticate"

    assert functions[1]["scope"] == "nested"
    assert (
        functions[1]["qualified_name"]
        == "UserService.authenticate.validate_password"
    )


def test_parse_simple_python_file():
    sample_code = dedent("""\
        import os
        from pathlib import Path

        class SampleClass:
            def sample_method(self):
                pass

        def sample_function():
            return True
    """)

    with tempfile.TemporaryDirectory() as temp_dir:
        file_path = Path(temp_dir) / "sample.py"
        file_path.write_text(sample_code, encoding="utf-8")

        result = parse_python_file(file_path)

    assert result is not None
    assert len(result["classes"]) == 1
    assert result["classes"][0]["name"] == "SampleClass"
    assert len(result["functions"]) == 2

    assert len(result["imports"]) == 2
    assert result["imports"][0]["name"] == "import os"
    assert result["imports"][0]["lineno"] == 1
    assert result["imports"][1]["name"] == "from pathlib import Path"
    assert result["imports"][1]["lineno"] == 2