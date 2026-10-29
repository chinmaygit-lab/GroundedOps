import http.client
import json
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path

from groundedops.engine import GroundedEngine
from groundedops.server import build_handler

ROOT = Path(__file__).resolve().parents[1]


class ServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        engine = GroundedEngine(ROOT / 'knowledge')
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), build_handler(engine))
        cls.port = cls.server.server_port
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def call(self, method, route, body=None, headers=None):
        conn = http.client.HTTPConnection('127.0.0.1', self.port, timeout=3)
        conn.request(method, route, body=json.dumps(body).encode() if body is not None else None, headers=headers or {})
        response = conn.getresponse()
        data = response.read()
        status = response.status
        conn.close()
        return status, json.loads(data) if route not in ('/', '/app.js') and data else data

    def test_status(self):
        status, body = self.call('GET', '/api/status')
        self.assertEqual(status, 200)
        self.assertIn('integrations.md', body['documents'])

    def test_ask(self):
        status, body = self.call('POST', '/api/ask', {'question': 'Who approves task completion?'})
        self.assertEqual(status, 200)
        self.assertTrue(body['sources'])

    def test_bad_question(self):
        status, body = self.call('POST', '/api/ask', {'question': ''})
        self.assertEqual(status, 400)

    def test_cross_origin_blocked(self):
        status, body = self.call('POST', '/api/ask', {'question': 'test'}, {'Origin': 'https://evil.example'})
        self.assertEqual(status, 403)

    def test_html(self):
        status, content = self.call('GET', '/')
        self.assertEqual(status, 200)
        self.assertIn(b'GroundedOps', content)
        self.assertIn(b'<script src="/app.js" defer></script>', content)
        self.assertNotIn(b'<script>\n', content)

    def test_external_javascript(self):
        status, content = self.call('GET', '/app.js')
        self.assertEqual(status, 200)
        self.assertIn(b"init();", content)
        self.assertIn(b"/api/status", content)

    def test_script_allowed_by_csp(self):
        conn = http.client.HTTPConnection('127.0.0.1', self.port, timeout=3)
        conn.request('GET', '/')
        response = conn.getresponse()
        policy = response.getheader('Content-Security-Policy')
        response.read()
        conn.close()
        self.assertIn("script-src 'self'", policy)
        self.assertIn("script-src 'self';", policy)
        self.assertNotIn("script-src 'self' 'unsafe-inline'", policy)



if __name__ == '__main__':
    unittest.main()
