"""MForce OSINT offline regression tests: no internet access or target scanning."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import re
import unittest
from unittest import mock

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('mf_osint',ROOT/'src/osint/inspect.py')
mf=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mf)

class OsintTests(unittest.TestCase):
    def capture(self, function, *args):
        buffer=io.StringIO()
        with contextlib.redirect_stdout(buffer): function(*args)
        return buffer.getvalue()

    def test_rate_statuses_are_evidence_not_guarantees(self):
        template={'url':'https://example.org','code':200,'headers':{},'body':b'', 'elapsed':.1}
        self.assertIn('UNKNOWN',self.capture(mf.rate,template))
        template['code']=429
        self.assertIn('OBSERVED',self.capture(mf.rate,template))
        template['code']=200
        template['headers']={'ratelimit-remaining':'2'}
        self.assertIn('ENFORCEMENT UNVERIFIED',self.capture(mf.rate,template))

    def test_dom_sinks_are_identified_as_heuristics(self):
        response={'url':'https://example.org','code':200,'headers':{},'body':b'', 'elapsed':.1}
        parsed=mf.HTML()
        parsed.feed('<script>node.innerHTML = location.hash;other.insertAdjacentHTML("beforeend",text);</script>')
        report=self.capture(mf.js_check,response,parsed)
        self.assertIn('innerHTML',report)
        self.assertIn('insertAdjacentHTML',report)
        self.assertIn('NOT proof of XSS',report)

    def test_html_public_metadata(self):
        page=mf.HTML()
        page.feed('<html><head><title>Public Page</title></head><body><form method="POST" action="/send?secret=test"></form><script src="/app.js"></script></body></html>')
        self.assertEqual(page.title,'Public Page')
        self.assertEqual(page.forms,[('POST','/send')])
        self.assertEqual(page.scripts,['/app.js'])

    def test_api_response_values_remain_hidden(self):
        resp={'url':'https://example.org','code':200,'headers':{'content-type':'application/json'},
              'body':b'{"access_token":"DO_NOT_PRINT_TOKEN","count":42}','elapsed':.1}
        report=self.capture(mf.api,resp)
        self.assertIn('access_token',report)
        self.assertNotIn('DO_NOT_PRINT_TOKEN',report)

    def test_reject_private_targets(self):
        for bad in ('file:///etc/passwd','http://localhost','https://user:secret@example.org','https://example.org/?api_key=secret'):
            with self.subTest(bad=bad),self.assertRaises(mf.Error): mf.url(bad)
        addr=[(2,1,6,'',('127.0.0.1',443))]
        with mock.patch.object(mf.socket,'getaddrinfo',return_value=addr):
            with self.assertRaises(mf.Error): mf.public('example.org',443)

    def test_no_additional_request_after_429(self):
        response={'url':'https://example.org','code':429,'headers':{},'body':b'', 'elapsed':.1}
        page=mf.HTML();page.scripts=['/app.js']
        with mock.patch.object(mf,'request') as fetch:
            self.capture(mf.js_check,response,page)
            fetch.assert_not_called()

    def test_external_js_bounded_to_three_requests(self):
        response={'url':'https://example.org','code':200,'headers':{},'body':b'', 'elapsed':.1}
        page=mf.HTML();page.scripts=['/src'+str(x)+'.js' for x in range(40)]
        script={'url':'https://example.org/app.js','code':200,'headers':{'content-type':'application/javascript'},'body':b'node.innerHTML = x;', 'elapsed':.1}
        with mock.patch.object(mf,'request',return_value=script) as fetch:
            report=self.capture(mf.js_check,response,page)
        self.assertEqual(fetch.call_count,3)
        self.assertIn('innerHTML',report)

    def test_registry_and_assets(self):
        registry=json.loads((ROOT/'src/data/funcs.json').read_text())['functions']
        ids={item['id'] for item in registry if item['enabled']}
        for id in ('dns211','ipa212','tls213','hdr214','web311','api312','rat313','jsn314','rob315','rdp316'):
            self.assertIn(id,ids)
            self.assertTrue((ROOT/'src/functions'/f'{id}.sh').exists())
            metadata=json.loads((ROOT/'src/lib'/id/f'{id}.json').read_text())
            self.assertEqual(metadata['entry'],id+'.sh')
            self.assertEqual(metadata['library'],id)
        html=(ROOT/'web/html/main.html').read_text()
        self.assertIn('responsible-use',html)
        self.assertIn('data-audit="dom"',html)
        self.assertRegex(html, r'global\.css\?v=\d+')
        self.assertRegex(html, r'main\.js\?v=\d+')
        self.assertIn('mf_ui_logo', (ROOT/'src/ui/theme.lib').read_text())

    def test_sanitized_output(self):
        self.assertNotIn('\x1b',mf.safe('hello\x1b[31m'))
        self.assertNotIn('\n',mf.safe('a\nb'))

if __name__=='__main__':unittest.main(verbosity=2)
