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
MAIN = WEB / "html/main.html"


class SiteParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = []
        self.hrefs = []
        self.assets = []
        self.external_links = []

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
        if tag == "a" and (attrs.get("target") or "").lower() == "_blank":
            self.external_links.append({
                "href": attrs.get("href", ""),
                "rel": attrs.get("rel"),
            })


def public_html_files(root):
    """Include root redirects and the multi-page site under web/."""
    return sorted({*root.glob("*.html"),
                   *(root / "web").rglob("*.html")})


def unsafe_blank_links(markup):
    """Enforce the project's explicit noopener+noreferrer link policy."""
    parser = SiteParser()
    parser.feed(markup)
    return [link for link in parser.external_links
            if not {"noopener", "noreferrer"}.issubset(
                (link["rel"] or "").lower().split())]


class WebsiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.markup = MAIN.read_text(encoding="utf-8")
        cls.parser = SiteParser()
        cls.parser.feed(cls.markup)

    def test_target_blank_links_use_safe_rel_attributes(self):
        pages = public_html_files(ROOT)
        self.assertTrue(pages, "No public HTML pages found")
        for html_file in pages:
            with self.subTest(file=str(html_file.relative_to(ROOT))):
                self.assertEqual(
                    unsafe_blank_links(html_file.read_text(encoding="utf-8")), [],
                    f"{html_file}: target=_blank links require noopener noreferrer",
                )

    def test_unsafe_target_blank_detection_fixture(self):
        unsafe_samples = [
            '<a href="https://example.com" target="_blank">Unsafe link</a>',
            '<a href="https://example.com" target="_blank" rel="noopener">Missing noreferrer</a>',
            '<a href="https://example.com" target="_blank" rel="noreferrer">Missing noopener</a>',
            '<a href="https://example.com" target="_BLANK" rel="">Empty rel</a>',
        ]
        for html_snippet in unsafe_samples:
            with self.subTest(snippet=html_snippet):
                self.assertEqual(len(unsafe_blank_links(html_snippet)), 1)

    def test_safe_target_blank_links(self):
        for snippet in (
            '<a href="https://example.com" target="_blank" rel="noopener noreferrer">OK</a>',
            '<a target="_BLANK" rel="NOREFERRER nofollow NOOPENER">OK</a>',
            '<a href="https://example.com">Same tab</a>',
        ):
            with self.subTest(snippet=snippet):
                self.assertEqual(unsafe_blank_links(html_snippet), [])

    def test_public_html_discovery_includes_root_and_pages(self):
        import tempfile
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            expected = [root / name for name in
                        ("index.html", "web/html/main.html", "web/html/wiki.html")]
            for path in expected:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('<a target="_blank">Unsafe</a>', encoding="utf-8")
            self.assertEqual(set(public_html_files(root)), set(expected))

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
                self.assertTrue((MAIN.parent / path).resolve().is_file())

    def test_multipage_navigation_present(self):
        # The redesign is a multi-page site: Home, Wiki, Tutorials, Contributors.
        for page in ("wiki.html", "tutorial.html", "contributors.html"):
            with self.subTest(page=page):
                self.assertTrue((WEB / "html" / page).is_file())
                self.assertIn(page, self.markup)
        self.assertIn("site.css?v=1", self.markup)

    def test_site_never_performs_network_scans(self):
        script = (WEB / "js/site.js").read_text(encoding="utf-8")
        self.assertNotRegex(script, r"\bfetch\s*\(|XMLHttpRequest|WebSocket\s*\(")

    def test_reduced_motion_and_responsive_breakpoints(self):
        style = (WEB / "css/site.css").read_text(encoding="utf-8")
        self.assertIn("prefers-reduced-motion:reduce", style)
        self.assertIn("max-width:760px", style)

    def test_accessibility_features_present(self):
        self.assertIn('class="skip-link"', self.markup)
        self.assertIn('aria-label="Main navigation"', self.markup)
        css = (WEB / "css/site.css").read_text(encoding="utf-8")
        self.assertIn(":focus-visible", css)

    @unittest.skipUnless(shutil.which("node"), "Node.js unavailable")
    def test_javascript_interactions(self):
        subprocess.run(["node", str(ROOT / "tests/site_interactions.js")],
                       check=True, capture_output=True, text=True)

    @unittest.skipUnless(shutil.which("node"), "Node.js unavailable")
    def test_javascript_syntax(self):
        subprocess.run(["node", "--check", str(WEB / "js/site.js")],
                       check=True, capture_output=True, text=True)


if __name__ == "__main__":
    unittest.main()