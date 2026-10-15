"""Regression checks for the independent, course-free Academy overview."""
import json
from html.parser import HTMLParser
from pathlib import Path
import re
import shutil
import subprocess
import unittest
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
ACADEMY = ROOT / "academy"
HTML = ACADEMY / "index.html"
MAIN = ROOT / "web/html/main.html"


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []
        self.links = []
        self.assets = []
        self.areas = []
        self.filters = []
        self.courses = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.append(a["id"])
        if "href" in a:
            self.links.append(a["href"])
        if tag == "script" and "src" in a:
            self.assets.append(a["src"])
        if tag == "link" and a.get("rel") == "stylesheet":
            self.assets.append(a["href"])
        if "data-area" in a:
            self.areas.append(a["data-area"])
        if "data-area-filter" in a:
            self.filters.append(a["data-area-filter"])
        if "data-course" in a:
            self.courses.append(a["data-course"])


class AcademyPortalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = HTML.read_text(encoding="utf-8")
        cls.page = Page()
        cls.page.feed(cls.html)

    def test_standalone_page_has_own_assets_and_no_legacy_css(self):
        self.assertTrue(HTML.is_file())
        self.assertEqual(len(self.page.ids), len(set(self.page.ids)))
        self.assertIn("./assets/css/academy.css?v=1", self.page.assets)
        self.assertIn("./assets/js/academy.js?v=1", self.page.assets)
        self.assertNotIn("global.css", self.html)
        self.assertNotIn("learn.js", self.html)
        self.assertNotIn("glass.css", self.html)
        for asset in self.page.assets:
            path = urlsplit(asset).path
            with self.subTest(asset=asset):
                self.assertTrue((ACADEMY / path).resolve().is_file())

    def test_links_and_sections_are_valid(self):
        for href in self.page.links:
            if href.startswith("#") and len(href) > 1:
                with self.subTest(href=href):
                    self.assertIn(href[1:], self.page.ids)
            elif href.startswith(".") and not href.startswith("//"):
                with self.subTest(href=href):
                    path = urlsplit(href).path
                    self.assertTrue((ACADEMY / path).resolve().exists())
        self.assertIn("de", re.findall(r'<html lang="([^"]+)"', self.html))

    def test_no_courses_or_false_enrollment(self):
        self.assertEqual(json.loads((ACADEMY / "data/courses.json").read_text()), [])
        self.assertEqual(self.page.courses, [])
        self.assertEqual(set(self.page.areas),
                         {"foundation", "osint", "security", "reporting"})
        self.assertEqual(set(self.page.filters),
                         {"all", "foundation", "osint", "security", "reporting"})
        self.assertIn("Noch keine Kurse verfügbar", self.html)
        self.assertIn("0 KURSE", self.html)
        self.assertNotIn("Jetzt einschreiben", self.html)

    def test_homepage_only_links_to_separate_academy(self):
        homepage = MAIN.read_text(encoding="utf-8")
        self.assertIn('href="../../academy/"', homepage)
        self.assertNotIn('id="schulung"', homepage)
        self.assertNotIn('class="academy-roadmap"', homepage)
        self.assertIn("enterprise.css?v=1", homepage)
        self.assertTrue((ROOT / "web/css/enterprise.css").is_file())

    def test_accessibility_and_responsive_support(self):
        self.assertIn('class="skip-link"', self.html)
        self.assertIn('aria-live="polite"', self.html)
        self.assertIn('aria-expanded="false"', self.html)
        self.assertIn('aria-controls="academy-sidebar"', self.html)
        css = (ACADEMY / "assets/css/academy.css").read_text()
        self.assertIn("prefers-reduced-motion:reduce", css)
        self.assertIn("max-width:990px", css)
        self.assertIn("max-width:640px", css)
        script = (ACADEMY / "assets/js/academy.js").read_text()
        self.assertNotRegex(script, r"\bfetch\s*\(|XMLHttpRequest|WebSocket\s*\(")

    @unittest.skipUnless(shutil.which("node"), "Node.js unavailable")
    def test_academy_javascript(self):
        subprocess.run(["node", "--check", str(ACADEMY / "assets/js/academy.js")],
                       check=True, capture_output=True, text=True)
        subprocess.run(["node", str(ROOT / "tests/academy_interactions.js")],
                       check=True, capture_output=True, text=True)


if __name__ == "__main__":
    unittest.main()
