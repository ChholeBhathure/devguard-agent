import json
from devguard.config import load_config, DEFAULT_CONFIG


def test_load_config_default(tmp_path):
    # Should fall back to default config if no .devguardrc.json exists
    config = load_config(tmp_path)
    assert config == DEFAULT_CONFIG


def test_load_config_custom(tmp_path):
    # Create custom .devguardrc.json
    config_file = tmp_path / ".devguardrc.json"
    custom_data = {
        "ignore_dirs": ["custom_dir"],
        "severity_threshold": "high"
    }
    config_file.write_text(json.dumps(custom_data))

    config = load_config(tmp_path)
    assert "custom_dir" in config["ignore_dirs"]
    assert config["severity_threshold"] == "high"
    # Verify defaults are preserved for unmentioned keys
    assert "max_file_size_kb" in config