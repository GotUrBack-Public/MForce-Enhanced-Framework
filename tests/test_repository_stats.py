"""Unit tests for automated source, file and directory badge counts."""
import json
import subprocess
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


if __name__ == "__main__":
    unittest.main()
