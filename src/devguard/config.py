import json
from pathlib import Path
from typing import Dict, Any, Union

DEFAULT_CONFIG: Dict[str, Any] = {
    "ignore_dirs":[".venv", "venv", "__pycache__", ".git", "build", "dist"],
    "severity_threshold": "low",
    "max_file_size_kb": 500,
}

def load_config(target_dir: Union[str, Path] = ".") -> Dict[str, Any]:
    target_path = Path(target_dir).resolve()
    """
    
    Searches for a .devguardrc.json in the target dictionary or user root.
    Falls back to DEFAULT_CONFIG if none is found.
    """

    config_file = target_dir / ".devguardrc.json"

    if config_file.is_file():
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                user_config = json.load(f)
                # Merge user settings onto defaults
                merged_config = DEFAULT_CONFIG.copy()

                # merge lists for ignore_dirs instead of completely overwriting
                if "ignore_dirs" in user_config:
                    merged_config["ignore_dirs"] = list(
                        set(DEFAULT_CONFIG["ignore_dirs"] + user_config["ignore_dirs"])
                    )
                # Update remaining scalar keys
                for key, value in user_config.items():
                    if key != "ignore_dirs":
                        merged_config[key] = value

                return merged_config
        except (json.JSONDecodeError, OSError):
            pass

    return DEFAULT_CONFIG.copy()
