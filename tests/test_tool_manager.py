"""Tests for the external tool catalog and safe argv-based process adapter."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ToolManagerTests(unittest.TestCase):
    def run_bash(self, code, env=None):
        return subprocess.run(
            ["bash", "-c", code], cwd=ROOT, text=True,
            capture_output=True, env={**os.environ, **(env or {})}, timeout=8,
        )

    def test_empty_catalog_loads(self):
        with tempfile.TemporaryDirectory() as temp:
            catalog = Path(temp) / "empty.json"
            catalog.write_text(json.dumps({"schema_version": 1, "tools": []}))
            result = self.run_bash(
                'source src/core/runtime.sh && source src/core/tool_manager.lib && '
                'mf_tools_load "' + str(catalog) + '" && printf "%s" "${#MF_TOOL_IDS[@]}"'
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, "0")

    def test_catalog_rejects_shell_syntax_in_command(self):
        with tempfile.TemporaryDirectory() as temp:
            catalog = Path(temp) / "catalog.json"
            catalog.write_text(json.dumps({"schema_version": 1, "tools": [{
                "id": "bad_tool", "name": "Bad", "command": "nmap;touch /tmp/pwned",
                "category": "test", "description": "invalid command", "enabled": True
            }]}))
            result = self.run_bash(
                'source src/core/runtime.sh && source src/core/tool_manager.lib && '
                f'mf_tools_validate "{catalog}"'
            )
            self.assertNotEqual(result.returncode, 0)

    def test_catalog_loads_package_mappings_for_all_supported_systems(self):
        result = self.run_bash(
            'source src/core/runtime.sh && source src/core/tool_manager.lib && '
            'mf_tools_load && printf "%s\\n" "${MF_TOOL_PACKAGES[0]}"'
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        packages = json.loads(result.stdout)
        for manager in ("termux", "apt", "dnf", "zypper", "pacman", "apk"):
            self.assertEqual(packages[manager], ["nmap"])

    def test_catalog_rejects_shell_syntax_in_package_names(self):
        with tempfile.TemporaryDirectory() as temp:
            catalog = Path(temp) / "catalog.json"
            catalog.write_text(json.dumps({"schema_version": 1, "tools": [{
                "id": "bad_tool", "name": "Bad", "command": "badtool",
                "category": "test", "description": "bad package", "enabled": True,
                "packages": {"apt": ["nmap;touch /tmp/pwned"]}
            }]}))
            result = self.run_bash(
                f'source src/core/runtime.sh && source src/core/tool_manager.lib && mf_tools_validate "{catalog}"'
            )
            self.assertNotEqual(result.returncode, 0)
    def test_registered_command_runs_without_shell_interpretation(self):
        with tempfile.TemporaryDirectory() as temp:
            bin_dir = Path(temp) / "bin"
            bin_dir.mkdir()
            marker = Path(temp) / "marker"
            executable = bin_dir / "mf-test-tool"
            executable.write_text('#!/bin/sh\nprintf "%s" "$1"\n')
            executable.chmod(0o755)
            catalog = Path(temp) / "catalog.json"
            catalog.write_text(json.dumps({"schema_version": 1, "tools": [{
                "id": "test_tool", "name": "Test", "command": "mf-test-tool",
                "category": "test", "description": "test adapter", "enabled": True
            }]}))
            result = self.run_bash(
                f'source src/core/runtime.sh && source src/core/tool_manager.lib && '
                f'mf_tools_load "{catalog}" && mf_tool_run test_tool "literal;touch {marker}"',
                {"PATH": f"{bin_dir}:{os.environ.get('PATH', '')}"},
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, f"literal;touch {marker}")
            self.assertFalse(marker.exists())

    def test_disabled_tool_does_not_run(self):
        with tempfile.TemporaryDirectory() as temp:
            catalog = Path(temp) / "catalog.json"
            catalog.write_text(json.dumps({"schema_version": 1, "tools": [{
                "id": "off_tool", "name": "Off", "command": "true",
                "category": "test", "description": "disabled", "enabled": False
            }]}))
            result = self.run_bash(
                f'source src/core/runtime.sh && source src/core/tool_manager.lib && '
                f'mf_tools_load "{catalog}" && mf_tool_run off_tool'
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("disabled", result.stderr)

    def test_unknown_tool_does_not_run(self):
        result = self.run_bash(
            'source src/core/runtime.sh && source src/core/tool_manager.lib && '
            'mf_tools_load && mf_tool_run not_registered'
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("not registered", result.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
