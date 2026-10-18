"""Unit tests for automated source, file and directory badge counts."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from importlib.util import module_from_spec, spec_from_file_location

ROOT = Path(__file__).resolve().parents[1]
SPEC = spec_from_file_location("repository_stats", ROOT / "scripts/repository_stats.py")
stats = module_from_spec(SPEC)
SPEC.loader.exec_module(stats)


class RepositoryStatsTests(unittest.TestCase):
    def test_counts_are_based_on_tracked_files_only(self):
        with tempfile.TemporaryDirectory() as temp:
            repo = Path(temp)
            subprocess.run(["git", "init", "-q", str(repo)], check=True)
            (repo / "src").mkdir()
            (repo / "src" / "app.py").write_text("print('a')\n\n# comment\n", encoding="utf-8")
            (repo / "src" / "style.css").write_text("a{}\n", encoding="utf-8")
            (repo / "README.md").write_text("text\n", encoding="utf-8")
            (repo / "untracked.js").write_text("doSomething();\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(repo), "add", "src", "README.md"], check=True)
            self.assertEqual(stats.calculate(repo), {
                "code_lines": 3, "files": 3, "directories": 1
            })

    def test_nested_directories_are_counted_once(self):
        with tempfile.TemporaryDirectory() as temp:
            repo = Path(temp)
            subprocess.run(["git", "init", "-q", str(repo)], check=True)
            (repo / "a" / "b").mkdir(parents=True)
            (repo / "a" / "b" / "x.sh").write_text("echo ok\n", encoding="utf-8")
            (repo / "a" / "b" / "y.py").write_text("\npass\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(repo), "add", "a"], check=True)
            self.assertEqual(stats.calculate(repo), {
                "code_lines": 2, "files": 2, "directories": 2
            })

    def test_shields_endpoint_payloads(self):
        payloads = stats.render_badges({
            "code_lines": 4638, "files": 186, "directories": 52
        })
        self.assertEqual(set(payloads), {
            "code-lines.json", "files.json", "directories.json"
        })
        for name, raw in payloads.items():
            data = json.loads(raw)
            self.assertEqual(data["schemaVersion"], 1)
            self.assertTrue(data["message"])
            self.assertTrue(data["label"])
            self.assertTrue(data["color"])
        self.assertEqual(json.loads(payloads["code-lines.json"])["message"], "4,638")

    def test_shields_endpoint_json_format_in_output_directory(self):
        """Validate output files and schema written to a temporary output directory."""
        with tempfile.TemporaryDirectory() as out_temp:
            out_dir = Path(out_temp)
            payloads = stats.render_badges({
                "code_lines": 1250, "files": 42, "directories": 7
            })
            for name, content in payloads.items():
                (out_dir / name).write_text(content, encoding="utf-8")

            expected_badges = {
                "code-lines.json": ("Code lines", "1,250", "blue"),
                "files.json": ("Files", "42", "brightgreen"),
                "directories.json": ("Directories", "7", "orange"),
            }

            for filename, (expected_label, expected_message, expected_color) in expected_badges.items():
                target_file = out_dir / filename
                self.assertTrue(target_file.is_file(), f"Missing badge file: {filename}")
                content = target_file.read_text(encoding="utf-8")
                self.assertTrue(content.endswith("\n"))

                data = json.loads(content)
                self.assertEqual(
                    set(data.keys()),
                    {"schemaVersion", "label", "message", "color"},
                    f"Unexpected keys in {filename}: {data.keys()}",
                )
                self.assertIs(type(data["schemaVersion"]), int)
                self.assertEqual(data["schemaVersion"], 1)
                self.assertIs(type(data["label"]), str)
                self.assertEqual(data["label"], expected_label)
                self.assertIs(type(data["message"]), str)
                self.assertEqual(data["message"], expected_message)
                self.assertIs(type(data["color"]), str)
                self.assertEqual(data["color"], expected_color)

    def test_cli_main_generates_valid_statistics_files(self):
        """Verify repository_stats.py CLI invocation outputs valid JSON files offline."""
        with tempfile.TemporaryDirectory() as repo_temp, tempfile.TemporaryDirectory() as out_temp:
            repo = Path(repo_temp)
            out_dir = Path(out_temp)
            subprocess.run(["git", "init", "-q", str(repo)], check=True)
            (repo / "test.py").write_text("print('test')\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(repo), "add", "test.py"], check=True)

            cmd = [
                sys.executable,
                str(ROOT / "scripts/repository_stats.py"),
                "--repo", str(repo),
                "--output-dir", str(out_dir),
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            self.assertEqual(result.returncode, 0)

            summary = json.loads(result.stdout.strip())
            self.assertEqual(summary, {"code_lines": 1, "directories": 0, "files": 1})

            for filename in ("code-lines.json", "files.json", "directories.json"):
                badge_file = out_dir / filename
                self.assertTrue(badge_file.is_file())
                badge_data = json.loads(badge_file.read_text(encoding="utf-8"))
                self.assertEqual(badge_data["schemaVersion"], 1)
                self.assertIsInstance(badge_data["label"], str)
                self.assertIsInstance(badge_data["message"], str)
                self.assertIsInstance(badge_data["color"], str)


if __name__ == "__main__":
    unittest.main()
