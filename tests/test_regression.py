"""Behavioral regressions for the audit; uses isolated copies, never user config."""
import json
import os
from pathlib import Path
import pty
import re
import select
import shutil
import signal
import stat
import subprocess
import tempfile
import termios
import time
import unittest

SOURCE = Path(__file__).resolve().parents[1]


class Terminal:
    def __init__(self, root, script='xrm742.sh', args=()):
        self.master, self.slave = pty.openpty()
        self.original = termios.tcgetattr(self.slave)
        self.process = subprocess.Popen(
            ['bash', script, *args], cwd=root, env={**os.environ, 'TERM': 'xterm', 'TMPDIR': str(root / 'tmp')},
            stdin=self.slave, stdout=self.slave, stderr=self.slave, start_new_session=True)
        self.buffer = ''

    def expect(self, pattern, timeout=12):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            match = re.search(pattern, self.buffer)
            if match:
                self.buffer = self.buffer[match.end():]
                return match
            ready, _, _ = select.select([self.master], [], [], .1)
            if ready:
                self.buffer += os.read(self.master, 65536).decode(errors='replace')
            elif self.process.poll() is not None:
                break
        raise AssertionError(f'Missing {pattern!r}: {self.buffer[-2000:]}')

    def send(self, data):
        os.write(self.master, data.encode())

    def finish(self, expected=0):
        code = self.process.wait(timeout=8)
        assert code == expected, (code, expected)
        assert termios.tcgetattr(self.slave) == self.original, 'Terminal state was not restored'

    def close(self):
        if self.process.poll() is None:
            os.killpg(self.process.pid, signal.SIGKILL)
            self.process.wait()
        os.close(self.master)
        os.close(self.slave)


class AuditRegression(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=SOURCE.parent)
        self.root = Path(self.temp.name) / 'repo'
        shutil.copytree(SOURCE, self.root, ignore=shutil.ignore_patterns('.git', '__pycache__', 'logo.png', 'tmp*'))
        (self.root / 'tmp').mkdir()
        self.terminals = []

    def tearDown(self):
        for terminal in self.terminals:
            terminal.close()
        self.temp.cleanup()

    def terminal(self, script='xrm742.sh', args=()):
        terminal = Terminal(self.root, script, args)
        self.terminals.append(terminal)
        return terminal

    def config(self, **values):
        path = self.root / 'src/auth/ath.json'
        data = json.loads(path.read_text())
        data.update(values)
        path.write_text(json.dumps(data))

    def run_bash(self, code, input=''):
        process = subprocess.Popen(['bash', '-c', code], cwd=self.root, stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                                   start_new_session=True,
                                   env={**os.environ, 'TERM': 'xterm', 'TMPDIR': str(self.root / 'tmp')})
        try:
            stdout, stderr = process.communicate(input, timeout=10)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            stdout, stderr = process.communicate()
            self.fail(f'Timed out: {code}: {stderr[-1000:]} {stdout[-1000:]}')
        return subprocess.CompletedProcess(code, process.returncode, stdout, stderr)

    def test_syntax_json_and_modes(self):
        for path in self.root.rglob('*'):
            if path.suffix in ('.sh', '.lib'):
                result = subprocess.run(['bash', '-n', str(path)], capture_output=True)
                self.assertEqual(result.returncode, 0, str(path))
            if path.suffix == '.sh':
                self.assertTrue(path.stat().st_mode & stat.S_IXUSR, str(path))
            if path.suffix == '.json':
                json.loads(path.read_text())

    def test_registry_and_metadata(self):
        categories = json.loads((self.root / 'src/data/cats.json').read_text())['categories']
        functions = json.loads((self.root / 'src/data/funcs.json').read_text())['functions']
        for item in functions:
            self.assertIn(item['category'], [c['id'] for c in categories])
            if item['enabled']:
                self.assertTrue((self.root / 'src/functions' / item['entry']).is_file())
                lib = item.get('library', item['id'])
                meta = json.loads((self.root / f'src/lib/{lib}/{lib}.json').read_text())
                self.assertEqual(item['entry'], meta['entry'])
        for kind, file in [('auth', 'src/auth/ath.json'), ('categories', 'src/data/cats.json'),
                           ('functions', 'src/data/funcs.json'), ('colors', 'src/colors/clrs.json')]:
            self.assertEqual(self.run_bash(f'source src/core/runtime.sh; mf_require_json {file} {kind}').returncode, 0)

    def test_invalid_auth_fails_closed(self):
        path = self.root / 'src/auth/ath.json'
        for content in ['{broken', '', '{} {}', '{"enabled":"yes"}', '{"max_attempts":0}',
                        '{"max_attempts":"3"}', '{"delay_on_failure":-1}', '{"code_length":65}',
                        '{"case_sensitive":null}']:
            path.write_text(content)
            result = self.run_bash('bash src/auth/lgn.sh')
            self.assertNotEqual(result.returncode, 0, content)
            self.assertNotIn('SESSION READY', result.stdout)
            self.assertEqual(list((self.root / 'tmp').iterdir()), [])

    def test_disabled_verification_and_eof(self):
        self.config(enabled=False)
        result = self.run_bash('bash xrm742.sh')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn('STARTUP VERIFICATION', result.stdout)
        self.assertIn('MAIN MENU', result.stdout)
        self.assertEqual(list((self.root / 'tmp').iterdir()), [])

    def test_key_handling(self):
        for data, expected in [('', 'EOF'), ('\n', 'ENTER'), ('q', 'BACK'), ('\x1b[A', 'UP'), ('\x1b', 'IGNORE')]:
            result = self.run_bash('source src/core/runtime.sh; mf_read_key; printf \'%s\\n\' "$MF_KEY"', data)
            self.assertEqual(result.stdout.strip(), expected)

    def test_startup_navigation_and_modules(self):
        term = self.terminal()
        term.expect('STARTUP VERIFICATION')
        code = term.expect(r'([A-Z2-9]{3}-[A-Z2-9]{3})').group(1)
        term.send(code.lower() + '\n')
        term.expect('MAIN MENU')
        # Network: category -> function list -> preview -> module -> return.
        term.send('\n'); term.expect('CATEGORY INFO')
        term.send('\n'); term.expect('FUNCTION SELECT')
        term.send('\n'); term.expect('FUNCTION PREVIEW')
        term.send('\n'); term.expect('NETWORK INFORMATION')
        term.expect('Press ENTER to return')
        term.send('\n'); term.expect('FUNCTION SELECT')
        term.send('q'); term.expect('MAIN MENU')
        # System module retains its original navigation and output.
        term.send('\x1b[B\n'); term.expect('CATEGORY INFO')
        term.send('\n'); term.expect('FUNCTION SELECT')
        term.send('\n'); term.expect('FUNCTION PREVIEW')
        term.send('\n'); term.expect('SYSTEM INFORMATION')
        term.expect('Press ENTER to return')
        term.send('\n'); term.expect('FUNCTION SELECT')
        term.send('q'); term.expect('MAIN MENU')
        # Category Info resolves the last highlighted category (Settings).
        term.send('\x1b[B' * 6 + '\n'); term.expect('CATEGORY INFO')
        term.expect('Settings')
        term.send('q'); term.expect('MAIN MENU')
        term.send('\x1b[A\n'); term.expect('ABOUT')
        term.expect('v0.01.2')
        term.send('\n'); term.expect('MAIN MENU')
        term.send('q'); term.finish()
        self.assertEqual(list((self.root / 'tmp').iterdir()), [])

    def test_configurable_code_and_case(self):
        self.config(code_length=9, case_sensitive=True, delay_on_failure=0)
        term = self.terminal('src/auth/lgn.sh')
        code = term.expect(r'([A-Z2-9]{3}-[A-Z2-9]{6})').group(1)
        term.send('wrong\n')
        term.expect('Invalid verification code')
        code = term.expect(r'([A-Z2-9]{3}-[A-Z2-9]{6})').group(1)
        term.send(code + '\n')
        term.expect('MAIN MENU'); term.send('q'); term.finish()
        # Deterministically exercise lowercase against an uppercase code.
        script = (self.root / 'src/auth/lgn.sh').read_text()
        definitions = script[:script.rfind('\nmain')]
        path = self.root / 'src/auth/probe.sh'
        path.write_text(definitions + '\ngenerate_code() { echo ABC-DEF; }\nmain\n')
        self.config(max_attempts=1)
        result = self.run_bash('bash src/auth/probe.sh', 'abc-def\n')
        self.assertEqual(result.returncode, 1)
        self.assertNotIn('SESSION READY', result.stdout)

    def test_session_isolation_and_signal_cleanup(self):
        self.config(enabled=False)
        first = self.terminal('src/auth/lgn.sh'); first.expect('MAIN MENU')
        second = self.terminal('src/auth/lgn.sh'); second.expect('MAIN MENU')
        dirs = list((self.root / 'tmp').iterdir())
        self.assertEqual(len(dirs), 2)
        for directory in dirs:
            self.assertEqual(stat.S_IMODE(directory.stat().st_mode), 0o700)
            self.assertEqual(stat.S_IMODE((directory / 'session.json').stat().st_mode), 0o600)
        first.process.send_signal(signal.SIGTERM); first.finish(143)
        self.assertEqual(len(list((self.root / 'tmp').iterdir())), 1)
        second.send('q'); second.finish()
        self.assertEqual(list((self.root / 'tmp').iterdir()), [])

    def test_module_help_and_disabled_config(self):
        for wrapper, lib in [('lar386.sh', 'frc386'), ('vkn193.sh', 'sys193')]:
            result = self.run_bash(f'bash src/functions/{wrapper} --help')
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('Usage:', result.stdout)
            path = self.root / f'src/lib/{lib}/{lib}.conf'
            path.write_text(path.read_text().replace('enabled=true', 'enabled=false'))
            result = self.run_bash(f'bash src/functions/{wrapper}')
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('Module disabled', result.stderr)

    def test_bad_data_and_unknown_entries(self):
        result = self.run_bash('bash src/ui/fp.sh net Network bogus ../../xrm742.sh Bogus')
        self.assertNotEqual(result.returncode, 0)
        for file, script in [('src/data/cats.json', 'src/ui/cs.sh'),
                             ('src/data/funcs.json', 'src/ui/fs.sh net Network'),
                             ('src/colors/clrs.json', 'src/ui/ap.sh')]:
            path = self.root / file; original = path.read_text()
            path.write_text('{}')
            result = self.run_bash('bash ' + script)
            self.assertNotEqual(result.returncode, 0, file)
            path.write_text(original)


if __name__ == '__main__':
    unittest.main(verbosity=2)
