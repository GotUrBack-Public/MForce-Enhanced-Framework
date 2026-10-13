"""Offline unit tests for XSS lab and real HTTP reflection inspector."""
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SECURITY = ROOT / "src/offensive"


def load(name):
    spec = importlib.util.spec_from_file_location(name, SECURITY / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


xss = load("xss_lab")
reflection = load("reflection")


class XSSLabTests(unittest.TestCase):
    def test_library_contains_100_real_lab_examples(self):
        items = xss.library()
        self.assertEqual(len(items), 100)
        self.assertTrue(any("<script>alert(1)</script>" == x.payload for x in items))
        self.assertTrue(any("innerHTML" in x.context for x in items))
        self.assertEqual(len(set((x.category, x.context, x.payload) for x in items)), 100)

    def test_offline_json_output_and_category_filter(self):
        result = subprocess.run([sys.executable, str(SECURITY / "xss_lab.py"),
                                 "--category", "html", "--format", "json"],
                                check=True, capture_output=True, text=True)
        data = json.loads(result.stdout)
        self.assertGreater(data["count"], 10)
        self.assertTrue(all(item["category"] == "html" for item in data["payloads"]))

    def test_local_filter_does_not_access_network(self):
        with patch("socket.create_connection", side_effect=AssertionError("network access")):
            self.assertEqual(len([p for p in xss.library() if p.category == "url"]), 8)


class ReflectionTests(unittest.TestCase):
    def test_marker_classification(self):
        marker = "MFORCE123ABC"
        self.assertIn("html_text", reflection.classify(f"<p>{marker}</p>", marker, "text/html"))
        self.assertIn("attribute:data-q", reflection.classify(
            f'<div data-q="{marker}"></div>', marker, "text/html"))
        self.assertIn("script_block", reflection.classify(
            f"<script>let q='{marker}'</script>", marker, "text/html"))
        self.assertEqual(reflection.classify("<p>not present</p>", marker, "text/html"), [])

    def test_authorization_required(self):
        with self.assertRaises(SystemExit):
            reflection.main(["http://127.0.0.1/?q=hello"])

    def test_no_redirects(self):
        handler = reflection.NoRedirect()
        self.assertIsNone(handler.redirect_request(None, None, 302, "Moved", {}, "http://elsewhere"))

    def test_real_marker_request_and_report(self):
        seen = []
        def fake_fetch(url, timeout):
            seen.append(url)
            marker = dict(__import__("urllib.parse", fromlist=["parse_qsl"]).parse_qsl(
                __import__("urllib.parse", fromlist=["urlsplit"]).urlsplit(url).query))["q"]
            return 200, "text/html", f"<p>{marker}</p>"
        with patch.object(reflection, "fetch", side_effect=fake_fetch):
            self.assertEqual(reflection.main(["http://127.0.0.1/?q=old", "--authorized"]), 0)
        self.assertEqual(len(seen), 1)
        self.assertNotIn("old", seen[0])
        self.assertIn("MFORCE", seen[0])

    def test_public_hosts_need_explicit_opt_in(self):
        with patch.object(reflection.socket, "getaddrinfo",
                          return_value=[(2, 1, 6, "", ("8.8.8.8", 443))]):
            with self.assertRaisesRegex(ValueError, "allow-public"):
                reflection.validate_url("https://example.org/?q=x", False)


if __name__ == "__main__":
    unittest.main()
