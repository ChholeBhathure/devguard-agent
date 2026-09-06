from pathlib import Path
from typing import List, Dict, Any
from devguard.parser import parse_python_file
from devguard.config import load_config

class LocalRetriever:
    """Scans local directories and gathers structural AST metadata from Python files."""

    def __init__(self, root_dir: str = ".", config: Dict[str, Any] = None):
        self.root_dir = Path(root_dir).resolve()
        self.config = config or load_config(self.root_dir)
        self.ignore_dirs = set(self.config.get("ignore_dirs", []))
            
    def scan_directory(self) -> List[Dict[str, Any]]:
        """Walks through the project directory and parses all valid .py files."""
        indexed_files = []

        for path in self.root_dir.rglob("*.py"):
            #Check if any parent folder in the path is in ignore_dirs.
            try:
                rel_parts = path.relative_to(self.root_dir).parts
            except ValueError:
                continue

            if any(part in self.ignore_dirs for part in rel_parts[:-1]):
                continue
            parsed_data = parse_python_file(path)
            if parsed_data:
                indexed_files.append(parsed_data)
        return indexed_files