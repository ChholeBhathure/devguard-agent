import os
from pathlib import Path
from typing import List, Dict, Any
from devguard.parser import parse_python_file

class LocalRetriever:
    """Scans local directories and gathers structural AST metadata from Python files."""

    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir).resolve()
        self.ignore_dirs = {
            ".venv",
            "venv",
            "__pycache__",
            ".git",
            "build",
            "dist",
        }
    def scan_directory(self) -> List[Dict[str, Any]]:
        """Walks through the project directory and parses all valid .py files."""
        indexed_files = []

        '''for current_root, dirs, files in os.walk(self.root_dir):
            #Finds all .py files recursively, skipping ignored folders.
            indexed_files = []'''

        for path in self.root_dir.rglob("*.py"):
            #Check if any parent folder in the path is in ignore_dirs.
            try:
                rel_parts = path.relative_to(self.root_dir).parts
            except ValueError:
                continue

            if any(part in self.ignore_dirs for part in rel_parts[:-1]):
                continue
            try:
                parsed_data = parse_python_file(str(path))
                parsed_data["relative_path"] = str(path.relative_to(self.root_dir))
                indexed_files.append(parsed_data)
            except Exception:
                # Skip files with syntax errors smoothly
                continue
        return indexed_files