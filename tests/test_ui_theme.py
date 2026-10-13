"""Terminal rendering and keyboard shortcuts; no external Python dependencies."""
import os
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]


def bash(code, data='', **environment):
    return subprocess.run(
        ['bash', '-c', code], input=data, capture_output=True, text=True,
        cwd=ROOT, timeout=12,
        env={**os.environ, 'TERM': 'dumb', 'NO_COLOR': '', **environment},
    )


class TerminalUiRegression(unittest.TestCase):
    def test_narrow_renderer_and_colorless_output(self):
        result = bash('source src/core/runtime.sh; source src/ui/theme.lib; '
                      'MF_UI_COLUMNS=36 MF_UI_FORCE_COMPACT=1 mf_ui_header "MAIN MENU" "LINUX"; '
                      'mf_ui_section "WORKSPACES"; '
                      'mf_ui_row 1 "Network Information" "READY" 1; '
                      'mf_ui_footer "FULL HELP" "Q  Exit"')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('MAIN MENU', result.stdout)
        self.assertIn('Network Information', result.stdout)
        self.assertIn('Q  Exit', result.stdout)
        self.assertNotIn('\x1b', result.stdout)
        self.assertTrue(all(len(line) <= 36 for line in result.stdout.splitlines()), result.stdout)

    def test_long_content_is_clipped(self):
        result = bash('source src/core/runtime.sh; source src/ui/theme.lib; '
                      'MF_UI_COLUMNS=32 MF_UI_FORCE_COMPACT=1 mf_ui_header "FUNCTION PREVIEW" "VERY LONG TITLE"; '
                      'mf_ui_row 9 "This is an intentionally excessive module title" "some metadata" 1')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(all(len(line) <= 32 for line in result.stdout.splitlines()), result.stdout)

    def test_vi_navigation_numbers_and_help(self):
        for data, expected in [('j', 'DOWN'), ('k', 'UP'), ('?', 'HELP'), ('2', 'DIGIT_2'),
                               ('\x1b[H', 'HOME'), ('\x1b[F', 'END')]:
            with self.subTest(data=data):
                result = bash('source src/core/runtime.sh; mf_read_key; printf "%s" "$MF_KEY"', data)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout, expected)

    def test_linux_platform_label(self):
        result = bash('source src/core/runtime.sh; source src/ui/theme.lib; mf_ui_platform', PREFIX='')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(result.stdout, ('LINUX', 'UNIX'))


if __name__ == '__main__':
    unittest.main()
