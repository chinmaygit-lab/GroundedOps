"""Local-only JSON API and readable browser UI. No third-party front-end libraries."""
from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from .engine import GroundedEngine
from .providers import ProviderError

WEB = Path(__file__).with_name("web.html")
SCRIPT = Path(__file__).with_name("app.js")


def build_handler(engine: GroundedEngine, eval_cases: list | None = None):
    class Handler(BaseHTTPRequestHandler):
        def _send(self, status: int, content: bytes, mime: str):
            self.send_response(status)
            self.send_header("Content-Type", mime)
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Security-Policy", "default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self'; connect-src 'self'; base-uri 'none'; frame-ancestors 'none'")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)

        def _json(self, status, value):
            self._send(status, json.dumps(value).encode("utf-8"), "application/json; charset=utf-8")

        def do_GET(self):
            if self.path == "/":
                self._send(200, WEB.read_bytes(), "text/html; charset=utf-8")
            elif self.path == "/app.js":
                self._send(200, SCRIPT.read_bytes(), "text/javascript; charset=utf-8")
            elif self.path == "/api/status":
                self._json(200, {"name": "GroundedOps", "provider": engine.provider,
                                 "passages": len(engine.retriever.passages),
                                 "documents": sorted(set(x.source for x in engine.retriever.passages))})
            else:
                self._json(404, {"error": "Not found"})

        def do_POST(self):
            if self.path not in ("/api/ask", "/api/evaluate"):
                self._json(404, {"error": "Not found"})
                return
            origin = self.headers.get("Origin")
            if origin and origin not in (f"http://localhost:{self.server.server_port}", f"http://127.0.0.1:{self.server.server_port}"):
                self._json(403, {"error": "Origin not permitted"})
                return
            try:
                size = int(self.headers.get("Content-Length", "0"))
                if size < 0 or size > 10_000:
                    self._json(413, {"error": "Request too large"})
                    return
                payload = json.loads(self.rfile.read(size) or b"{}")
                if not isinstance(payload, dict):
                    raise ValueError("Expected a JSON object")
                if self.path == "/api/ask":
                    if not isinstance(payload.get("question"), str):
                        raise ValueError("Question must be text")
                    self._json(200, engine.ask(payload["question"]))
                else:
                    self._json(200, engine.evaluate(eval_cases or []))
            except (ValueError, TypeError, json.JSONDecodeError) as exc:
                self._json(400, {"error": str(exc)})
            except ProviderError as exc:
                self._json(502, {"error": str(exc)})

    return Handler


def serve(engine: GroundedEngine, port: int, eval_cases: list | None = None):
    if not 1024 <= port <= 65535:
        raise ValueError("Use a port between 1024 and 65535")
    httpd = ThreadingHTTPServer(("127.0.0.1", port), build_handler(engine, eval_cases))
    print(f"GroundedOps on http://127.0.0.1:{port} | provider={engine.provider} | Ctrl+C to stop")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
