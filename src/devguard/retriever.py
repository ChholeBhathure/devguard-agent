import os
from pathlib import Path
from typing import Any
from devguard.parser import parse_python_file
from devguard.config import load_config

class LocalRetriever:
    """Scans local directories and gathers structural AST metadata from Python files."""

    def __init__(self, root_dir: str = ".", config: dict[str, Any] | None = None):
        self.root_dir = Path(root_dir).resolve()
        if not self.root_dir.is_dir():
            raise ValueError(f"Invalid project directory: {self.root_dir}")
        self.config = (config if config is not None else load_config(self.root_dir))
        ignore_dirs = self.config.get("ignore_dirs", [])

        if not isinstance(ignore_dirs, list):
            raise ValueError("ignore_dirs must be a list")
        
        self.ignore_dirs = set(ignore_dirs)
        max_file_size_kb=self.config.get("max_file_size_kb",500)
        self.max_file_size_bytes = int(max_file_size_kb) * 1024

        #Stores errors encountered during scanning.
        self.scan_errors: list[dict[str, str]] = []
            
    def scan_directory(self) -> list[dict[str, Any]]:
        """Scan  project and return metadata from valid .py files."""
        indexed_files: list[dict[str,Any]]=[]
        self.scan_errors.clear()

        for current_dir, dirs, files in os.walk(self.root_dir,onerror=self._handle_walk_error):
            #Skip ignored directories
            dirs[:] = [directory for directory in dirs if directory not in self.ignore_dirs]

            for filename in files:
                if not filename.lower().endswith(".py"):
                    continue
                path = Path(current_dir) / filename
                try:
                    file_size = path.stat().st_size
                    if file_size > self.max_file_size_bytes:
                        self.scan_errors.append({
                            "file": str(path),
                            "error": "File exceeds maximum allowed size.",
                        })
                        continue
                    #Extracts structural metadata from the Python file using AST.
                    parsed_data=parse_python_file(path)
                    if parsed_data:
                        parsed_data["file_path"] = str(
                            path.relative_to(self.root_dir)
                        )
                        indexed_files.append(parsed_data)
                    
                except (SyntaxError,UnicodeError,OSError,ValueError) as error:
                        self.scan_errors.append({
                            "file": str(path),
                            "error": str(error)
                        })
                        continue
        return indexed_files
    def _handle_walk_error(self, error: OSError) -> None:
        self.scan_errors.append({
            "file": str(error.filename or self.root_dir),
            "error": str(error),
        })