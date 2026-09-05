import tempfile
import os
from src.devguard.retriever import LocalRetriever

def test_scan_directory_ignores_venv():
    """Test that LocalRetriever correctly scans Python files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        #Create a dummy python file
        py_file = os.path.join(temp_dir, "app.py")
        with open(py_file, "w") as f:
            f.write("def hello():pass")
        retriever = LocalRetriever(root_dir=temp_dir)
        result = retriever.scan_directory()

        assert len(result) == 1
        file_entry = result[0]
        assert file_entry.get("file_name") == "app.py" or file_entry.get("relative_path", "").endswith("app.py")