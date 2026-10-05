"""Configuration loading: defaults < JSON file < command line."""

import argparse
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG = {
    "vfs_path": str(REPO_ROOT / "vfs_examples" / "minimal.json"),
    "prompt": "{vfs}:{cwd}$ ",
    "startup_script": "",
}
CLI_TO_CONFIG = {
    "vfs": "vfs_path",
    "prompt": "prompt",
    "script": "startup_script",
}


def load_json_config(path: str | None) -> dict:
    """Read a JSON configuration file and check its keys."""
    if not path:
        return {}
    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, dict):
        raise ValueError("Configuration root must be a JSON object.")
    unknown = sorted(set(data) - set(DEFAULT_CONFIG))
    if unknown:
        raise ValueError(f"Unknown configuration keys: {', '.join(unknown)}")
    return data


def build_config(args: argparse.Namespace) -> dict:
    """Merge defaults, the JSON file and CLI values (CLI wins)."""
    config = dict(DEFAULT_CONFIG)
    config.update(load_json_config(args.config))
    for cli_key, config_key in CLI_TO_CONFIG.items():
        value = getattr(args, cli_key, None)
        if value is not None:
            config[config_key] = value
    config["config_path"] = args.config
    return validate_config(config)


def validate_config(config: dict) -> dict:
    """Check that every parameter has a valid value."""
    for key in DEFAULT_CONFIG:
        if not isinstance(config[key], str):
            raise ValueError(f"{key} must be a string.")
    if not config["vfs_path"]:
        raise ValueError("vfs_path must be a non-empty string.")
    return config
