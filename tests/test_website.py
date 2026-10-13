"""Static website regression checks (no network or browser dependencies)."""
import re
import shutil
import subprocess
import unittest
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "web"
HTML = WEB / "html/main.html"


class SiteParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = []
        self.hrefs = []
        self.assets = []
        self.tutorials = []
        self.tracks = []
        self.module_tabs = []
        self.audit_tabs = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.append(attrs["id"])
        if "href" in attrs:
            self.hrefs.append(attrs["href"])
        if tag == "script" and "src" in attrs:
            self.assets.append(attrs["src"])
        if tag == "link" and attrs.get("rel") == "stylesheet":
            self.assets.append(attrs["href"])
        if "data-tutorial" in attrs:
            self.tutorials.append(attrs["data-tutorial"])
        if "data-track" in attrs:
            self.tracks.append(attrs["data-track"])
        if "data-module" in attrs:
            self.module_tabs.append(attrs["data-module"])
        if "data-audit" in attrs:
            self.audit_tabs.append(attrs["data-audit"])


class WebsiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.markup = HTML.read_text(encoding="utf-8")
        cls.parser = SiteParser()
        cls.parser.feed(cls.markup)

    def test_unique_ids_and_working_internal_links(self):
        ids = Counter(self.parser.ids)
        self.assertFalse([key for key, count in ids.items() if count != 1])
        for href in self.parser.hrefs:
            if href.startswith("#") and len(href) > 1:
                with self.subTest(href=href):
                    self.assertIn(href[1:], ids)

    def test_local_css_js_references_exist(self):
        for asset in self.parser.assets:
            with self.subTest(asset=asset):
                path = urlsplit(asset).path
                self.assertTrue((HTML.parent / path).resolve().is_file())

    def test_learning_experience_present(self):
        self.assertEqual(len(self.parser.tutorials), 5)
        self.assertEqual(len(set(self.parser.tutorials)), 5)
        self.assertEqual(len(self.parser.tracks), 4)
        self.assertEqual(len(set(self.parser.tracks)), 4)
        self.assertIn("#tutorials", self.parser.hrefs)
        self.assertIn("#schulung", self.parser.hrefs)
        self.assertIn("ROADMAP PREVIEW ONLY", self.markup)
        self.assertIn("not available yet", self.markup)

    def test_all_module_and_audit_tabs_registered(self):
        self.assertEqual(set(self.parser.module_tabs),
                         {"network", "system", "future", "scanner", "updater"})
        self.assertEqual(set(self.parser.audit_tabs), {"rate", "dom", "headers"})
        script = (WEB / "js/main.js").read_text(encoding="utf-8")
        self.assertIn("const auditTabs = $$('[data-audit]');", script)
        self.assertIn("scanner: {", script)
        self.assertIn("updater: {", script)

    def test_site_never_performs_network_scans(self):
        for name in ("global.js", "main.js", "learn.js"):
            script = (WEB / "js" / name).read_text(encoding="utf-8")
            with self.subTest(script=name):
                self.assertNotRegex(script, r"\bfetch\s*\(|XMLHttpRequest|WebSocket\s*\(")

    def test_reduced_motion_and_responsive_breakpoints(self):
        style = (WEB / "css/learn.css").read_text(encoding="utf-8")
        self.assertIn("prefers-reduced-motion:reduce", style)
        self.assertIn("max-width:460px", style)
        self.assertIn("max-width:1180px", style)

    @unittest.skipUnless(shutil.which("node"), "Node.js unavailable")
    def test_javascript_interactions(self):
        subprocess.run(["node", str(ROOT / "tests/site_interactions.js")],
                       check=True, capture_output=True, text=True)

    @unittest.skipUnless(shutil.which("node"), "Node.js unavailable")
    def test_javascript_syntax(self):
        for name in ("global.js", "main.js", "learn.js"):
            with self.subTest(name=name):
                subprocess.run(["node", "--check", str(WEB / "js" / name)],
                               check=True, capture_output=True, text=True)


if __name__ == "__main__":
    unittest.main()
