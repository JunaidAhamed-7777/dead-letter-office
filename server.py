#!/usr/bin/env python3
"""Private loopback-only demo. No request logging, external API calls, or uploads."""
from functools import partial
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import argparse
import json
import mimetypes
from pathlib import Path
from urllib.parse import urlsplit

from archive import Archive, ROOT


class Handler(BaseHTTPRequestHandler):
    server_version = "DeadLetterOffice/1.0"

    def log_message(self, *_):
        pass  # A question must not become a request log.

    def safe_request(self):
        port = self.server.server_port
        allowed = {f"127.0.0.1:{port}", f"localhost:{port}"}
        if self.headers.get("Host") not in allowed:
            self.send_json(403, {"error": "This archive only accepts localhost requests."})
            return False
        origin = self.headers.get("Origin")
        if origin and origin not in {f"http://{host}" for host in allowed}:
            self.send_json(403, {"error": "Cross-origin access is not permitted."})
            return False
        return True

    def send_response_headers(self, status, content_type, length):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(length))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; object-src 'none'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'")
        self.send_header("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        self.end_headers()

    def send_json(self, status, data):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response_headers(status, "application/json; charset=utf-8", len(body))
        self.wfile.write(body)

    def do_GET(self):
        if not self.safe_request():
            return
        path = urlsplit(self.path).path
        if path == "/api/health":
            self.send_json(200, {"status": "ready", "offline": True, "model": self.server.archive.metadata})
        elif path == "/api/archive":
            self.send_json(200, self.server.archive.catalogue())
        elif path in {"/", "/index.html", "/style.css", "/app.js"}:
            name = "index.html" if path == "/" else path[1:]
            file = ROOT / "web" / name
            if not file.is_file():
                self.send_json(503, {"error": "The reading room is not installed."})
                return
            body = file.read_bytes()
            self.send_response_headers(200, (mimetypes.guess_type(name)[0] or "application/octet-stream") + "; charset=utf-8", len(body))
            self.wfile.write(body)
        else:
            self.send_json(404, {"error": "This page is not in the archive. Return to /."})

    def do_POST(self):
        if not self.safe_request():
            return
        if urlsplit(self.path).path != "/api/ask":
            self.send_json(404, {"error": "Unknown archive action."})
            return
        if self.headers.get("Content-Type", "").split(";")[0] != "application/json":
            self.send_json(415, {"error": "Send the question as application/json."})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self.send_json(400, {"error": "Invalid request length."})
            return
        if length < 1 or length > 8192:
            self.send_json(413, {"error": "Request must be between 1 and 8192 bytes."})
            return
        try:
            data = json.loads(self.rfile.read(length).decode("utf-8"))
            if not isinstance(data, dict):
                raise ValueError("Send an object containing a question.")
            result = self.server.archive.ask(data.get("question"))
        except (ValueError, UnicodeDecodeError) as error:
            self.send_json(400, {"error": str(error)})
            return
        except Exception:
            self.send_json(500, {"error": "The local model could not finish this search. Try again or restart the server."})
            return
        self.send_json(200, result)


def make_server(port=8765, archive=None):
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    server.archive = archive or Archive()
    return server


def main():
    parser = argparse.ArgumentParser(description="Open the private Dead Letter Office on localhost.")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    print("Opening the archive and loading MiniLM on CPU…", flush=True)
    server = make_server(args.port)
    print(f"Dead Letter Office: http://127.0.0.1:{server.server_port} · network-free inference · Ctrl-C to close", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
