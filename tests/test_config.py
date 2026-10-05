"""Tests for the configuration priority logic."""

import argparse
import json
import tempfile
import unittest
from pathlib import Path

from config import DEFAULT_CONFIG, build_config


def make_args(**values) -> argparse.Namespace:
    """Build a Namespace like the CLI parser does (None = not given)."""
    args = {"config": None, "vfs": None, "prompt": None, "script": None}
    args.update(values)
    return argparse.Namespace(**args)


class BuildConfigTest(unittest.TestCase):
    """defaults < JSON file < command line."""

    def write_json(self, data: dict) -> str:
        """Store a JSON config in a temporary directory."""
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        path = Path(folder.name) / "config.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        return str(path)

    def test_defaults(self):
        """Without any input the defaults are used."""
        config = build_config(make_args())
        self.assertEqual(config["prompt"], DEFAULT_CONFIG["prompt"])

    def test_json_overrides_defaults(self):
        """JSON values replace the defaults."""
        path = self.write_json({"prompt": "json> "})
        config = build_config(make_args(config=path))
        self.assertEqual(config["prompt"], "json> ")

    def test_cli_overrides_json(self):
        """Command-line values have the highest priority."""
        path = self.write_json({"prompt": "json> ", "vfs_path": "a.json"})
        config = build_config(make_args(config=path, prompt="cli> "))
        self.assertEqual(config["prompt"], "cli> ")
        self.assertEqual(config["vfs_path"], "a.json")

    def test_empty_cli_value_still_wins(self):
        """An empty string on the CLI disables a script from the file."""
        path = self.write_json({"startup_script": "s.txt"})
        config = build_config(make_args(config=path, script=""))
        self.assertEqual(config["startup_script"], "")

    def test_unknown_key_is_rejected(self):
        """Typos in the JSON file are reported."""
        path = self.write_json({"promt": "x"})
        with self.assertRaises(ValueError):
            build_config(make_args(config=path))

    def test_wrong_type_is_rejected(self):
        """Values must be strings."""
        path = self.write_json({"prompt": 5})
        with self.assertRaises(ValueError):
            build_config(make_args(config=path))


if __name__ == "__main__":
    unittest.main()
