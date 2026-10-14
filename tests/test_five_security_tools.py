"""Functional offline tests for five new MForce security tools."""
import contextlib
import http.server
import importlib.util
import json
from pathlib import Path
import socket
import subprocess
import tempfile
import threading
import unittest

ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


http_audit = load("http_audit", "src/offensive/http_audit.py")
secret_audit = load("secrets_audit", "src/defensive/secrets_audit.py")


class Handler(http.server.BaseHTTPRequestHandler):
    calls = []

    def log_message(self, *args):
        pass

    def do_OPTIONS(self):
        self.__class__.calls.append(("OPTIONS", self.path))
        self.send_response(204)
        self.send_header("Allow", "GET, HEAD, OPTIONS")
        self.end_headers()

    def do_HEAD(self):
        self.__class__.calls.append(("HEAD", self.path))
        self.send_response(200 if self.path == "/.env" else 404)
        self.end_headers()

    def do_GET(self):
        self.__class__.calls.append(("GET", self.path))
        if self.path == "/redirect":
            self.send_response(302)
            self.send_header("Location", "/never")
        elif self.path == "/limited":
            self.send_response(429)
        else:
            self.send_response(200)
            origin = self.headers.get("Origin")
            if origin:
                self.send_header("Access-Control-Allow-Origin", origin)
                self.send_header("Access-Control-Allow-Credentials", "true")
            self.send_header("Set-Cookie", "session=PRIVATE_TEST_VALUE; HttpOnly; SameSite=Lax")
            self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"not a real vulnerability")


class HTTPAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=3)

    def setUp(self):
        Handler.calls.clear()

    def run_cli(self, mode, suffix="", *flags):
        return subprocess.run(
            ["python3", str(ROOT / "src/offensive/http_audit.py"),
             mode, self.url + suffix, "--authorized", "--json", *flags],
            capture_output=True, text=True, timeout=10,
        )

    def test_cors_two_bounded_get_requests(self):
        p = self.run_cli("cors")
        self.assertEqual(p.returncode, 0, p.stderr)
        report = json.loads(p.stdout)
        self.assertEqual(report["requests"], 2)
        self.assertEqual(len(Handler.calls), 2)
        self.assertTrue(all(x[0] == "GET" for x in Handler.calls))
        self.assertTrue(all(x["origin_reflected"] for x in report["results"]))

    def test_options_one_request(self):
        p = self.run_cli("methods")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(json.loads(p.stdout)["allow"], ["GET", "HEAD", "OPTIONS"])
        self.assertEqual(Handler.calls, [("OPTIONS", "/")])

    def test_cookie_values_are_not_disclosed(self):
        p = self.run_cli("cookies")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertNotIn("PRIVATE_TEST_VALUE", p.stdout)
        report = json.loads(p.stdout)
        self.assertTrue(report["cookies"][0]["httponly"])
        self.assertFalse(report["cookies"][0]["secure"])
        self.assertEqual(len(Handler.calls), 1)

    def test_path_checks_use_head_only(self):
        p = self.run_cli("paths")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(len(Handler.calls), 5)
        self.assertTrue(all(method == "HEAD" for method, _ in Handler.calls))
        self.assertTrue(json.loads(p.stdout)["results"][0]["review"])

    def test_no_auth_no_network(self):
        p = subprocess.run(
            ["python3", str(ROOT / "src/offensive/http_audit.py"),
             "cors", self.url], capture_output=True, text=True, timeout=5)
        self.assertNotEqual(p.returncode, 0)
        self.assertEqual(Handler.calls, [])

    def test_no_redirect_follow_and_stop_on_rate_limit(self):
        p = self.run_cli("cookies", "/redirect")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(Handler.calls, [("GET", "/redirect")])
        Handler.calls.clear()
        p = self.run_cli("cors", "/limited")
        self.assertNotEqual(p.returncode, 0)
        self.assertEqual(len(Handler.calls), 1)

    def test_rejects_credentials_fragments_and_bad_timeout(self):
        for url in ("http://user:pass@127.0.0.1/", "http://127.0.0.1/#frag"):
            with self.subTest(url=url):
                with self.assertRaises(ValueError):
                    http_audit.validate_target(url, False)
        p = self.run_cli("methods", "", "--timeout", "100")
        self.assertNotEqual(p.returncode, 0)
        self.assertEqual(Handler.calls, [])

    def test_module_wrappers_are_registered_and_help_works(self):
        for module in ("cor404", "met405", "coo406", "pth407"):
            with self.subTest(module=module):
                p = subprocess.run(
                    ["bash", str(ROOT / "src/functions" / (module + ".sh")), "--help"],
                    capture_output=True, text=True, timeout=8)
                # Bash wrapper expects mode + --help, no network request.
                self.assertEqual(p.returncode, 0, p.stderr)
                self.assertIn("--authorized", p.stdout)


class SecretScannerTests(unittest.TestCase):
    def test_offline_scan_reports_only_location_and_rule(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "src").mkdir()
            (root / "src" / "config.py").write_text(
                'password = "NOT_REAL_SECRET_123456"\n'
                'safe = 1\n', encoding="utf-8")
            (root / ".git").mkdir()
            (root / ".git" / "ignored.py").write_text(
                'password = "OTHER_SECRET_VALUE"\n')
            report = secret_audit.scan(root)
            self.assertEqual(report["checked_files"], 1)
            self.assertEqual(len(report["findings"]), 1)
            self.assertEqual(report["findings"][0]["file"], "src/config.py")
            self.assertNotIn("NOT_REAL_SECRET", json.dumps(report))

    def test_rejects_symlink_and_limits_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "file.py").write_text("hello\n")
            (root / "alias.py").symlink_to(root / "file.py")
            with self.assertRaises(ValueError):
                secret_audit.scan(root / "alias.py")
            self.assertEqual(secret_audit.scan(root)["checked_files"], 1)

    def test_cli_exit_status_and_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            file = Path(tmp) / "config.txt"
            file.write_text("-----BEGIN PRIVATE KEY-----\n", encoding="utf-8")
            p = subprocess.run(
                ["bash", str(ROOT / "src/functions/sec601.sh"), str(file), "--json"],
                capture_output=True, text=True, timeout=8)
            self.assertEqual(p.returncode, 1, p.stderr)
            self.assertEqual(json.loads(p.stdout)["findings"][0]["rule"],
                             "private_key_marker")


if __name__ == "__main__":
    unittest.main()
