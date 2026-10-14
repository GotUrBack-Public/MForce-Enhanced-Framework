"""Regression checks for MForce governance, documentation and privacy links."""
import json
import re
import unittest
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
DOCS = [
    "CONTRIBUTING.md",
    "CODE_OF_CONDUCT.md",
    "CHANGELOG.md",
    "SUPPORT.md",
    "SECURITY.md",
    "GUIDLINES&&TERMSOFUSE.md",
    "social/ai_usage.txt",
    "social/contributors.md",
    "social/how_to_contribute.md",
    "docs/MAINTAINERS.md",
    "DSGVO/README.md",
    "DSGVO/DATENFLUESSE.md",
    "DSGVO/CHECKLISTE.md",
    "DSGVO/LOESCHUNG_UND_AUFBEWAHRUNG.md",
    "DSGVO/DATENSCHUTZHINWEISE_VORLAGE.md",
    "DSGVO/VERZEICHNIS_VORLAGE.md",
    "DSGVO/INCIDENT_RESPONSE.md",
    ".github/PULL_REQUEST_TEMPLATE.md",
    ".github/ISSUE_TEMPLATE/bug_report.md",
    ".github/ISSUE_TEMPLATE/feature_request.md",
    ".github/ISSUE_TEMPLATE/custom.md",
]


class DocumentationTests(unittest.TestCase):
    def test_required_docs_are_substantial(self):
        for path in DOCS:
            with self.subTest(path=path):
                file = ROOT / path
                self.assertTrue(file.is_file(), f"Missing documentation: {path}")
                self.assertGreater(len(file.read_text(encoding="utf-8").strip()), 280, path)

    def test_internal_markdown_links_resolve(self):
        # Check only relative links, not remote destinations or generated anchors.
        for name in ["README.md", *[p for p in DOCS if p.endswith(".md")]]:
            file = ROOT / name
            content = file.read_text(encoding="utf-8")
            for href in re.findall(r"(?<!!)\[[^\]]+\]\(([^)]+)\)", content):
                href = href.strip().split("#", 1)[0]
                if not href or href.startswith(("http://", "https://", "mailto:", "/")):
                    continue
                target = (file.parent / unquote(href)).resolve()
                with self.subTest(file=name, href=href):
                    self.assertTrue(target.is_relative_to(ROOT.resolve()))
                    self.assertTrue(target.exists(), f"{name}: broken link {href}")

    def test_module_count_and_offensive_registry(self):
        # The README is maintained independently; never assert on its wording.
        registry = json.loads((ROOT / "src/data/funcs.json").read_text(encoding="utf-8"))
        enabled = [x for x in registry["functions"] if x["enabled"]]
        self.assertEqual(len(enabled), 16)
        self.assertEqual(len({item["id"] for item in enabled}), len(enabled))
        names = {item["name"] for item in enabled}
        for module in ("TCP Port Scanner", "XSS Payload Lab", "HTTP Reflection Inspector"):
            self.assertIn(module, names)
        self.assertTrue((ROOT / "README.md").is_file())

    def test_dsgvo_templates_do_not_claim_certification(self):
        hub = (ROOT / "DSGVO/README.md").read_text(encoding="utf-8")
        template = (ROOT / "DSGVO/DATENSCHUTZHINWEISE_VORLAGE.md").read_text(encoding="utf-8")
        self.assertIn("Keine", hub)
        self.assertIn("NICHT UNVERÄNDERT VERÖFFENTLICHEN", template)
        self.assertIn("[eintragen]", template)
        flows = (ROOT / "DSGVO/DATENFLUESSE.md").read_text(encoding="utf-8")
        for term in ("rdap.org", "GitHub Pages", "Shell-History", "HTTP Reflection Inspector"):
            self.assertIn(term, flows)

    def test_github_templates_and_dependabot_config(self):
        dependabot = (ROOT / ".github/dependabot.yml").read_text(encoding="utf-8")
        self.assertIn("version: 2", dependabot)
        self.assertIn('package-ecosystem: "github-actions"', dependabot)
        for name in ("bug_report.md", "feature_request.md", "custom.md"):
            content = (ROOT / ".github/ISSUE_TEMPLATE" / name).read_text(encoding="utf-8")
            self.assertTrue(content.startswith("---\n"))
            self.assertIn("about:", content)
        self.assertTrue((ROOT / ".github/ISSUE_TEMPLATE/config.yml").exists())

    def test_bounty_reward_limit_is_consistent(self):
        scope = (ROOT / "Bug_Bounty/13.10.2026-10:00C/scope.txt").read_text(encoding="utf-8")
        self.assertIn("€70", scope)
        self.assertNotIn("€100", scope)
        self.assertIn("No automatic payout", scope)


if __name__ == "__main__":
    unittest.main()
