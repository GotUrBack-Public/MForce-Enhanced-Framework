import importlib.util
import io
import json
import socket
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path

FILE = Path(__file__).resolve().parents[1] / "src/offensive/tcp_scan.py"
spec = importlib.util.spec_from_file_location("tcp_scan", FILE)
scanner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scanner)


class TcpScanTests(unittest.TestCase):
    def test_ports(self):
        self.assertEqual(scanner.parse_ports("443,80,81-82"), [80, 81, 82, 443])
        for invalid in ("", "0", "65536", "4-2", "1-129", "1,,2"):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                scanner.parse_ports(invalid)

    def test_localhost_allowed(self):
        self.assertIn("127.0.0.1", scanner.resolve_target("127.0.0.1", False))

    def test_public_requires_opt_in(self):
        with self.assertRaises(ValueError):
            scanner.resolve_target("8.8.8.8", False)

    def test_socket_probe(self):
        with socket.socket() as server:
            server.bind(("127.0.0.1", 0))
            server.listen()
            port = server.getsockname()[1]
            self.assertEqual(scanner.probe("127.0.0.1", port, 0.3)["state"], "OPEN")

    def test_json_result(self):
        with socket.socket() as server:
            server.bind(("127.0.0.1", 0))
            server.listen()
            port = server.getsockname()[1]
            output = io.StringIO()
            with redirect_stdout(output):
                scanner.main(["127.0.0.1", "--ports", str(port), "--authorized", "--json"])
            self.assertEqual(json.loads(output.getvalue())["results"][0]["state"], "OPEN")


if __name__ == "__main__":
    unittest.main()
