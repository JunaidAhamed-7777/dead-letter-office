import http.client
import json
from pathlib import Path
import sys
import threading
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from server import make_server


class ServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = make_server(0)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def request(self, method, path, body=None, headers=None):
        connection = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=10)
        connection.request(method, path, body=body, headers=headers or {})
        response = connection.getresponse()
        result = response.status, dict(response.getheaders()), response.read()
        connection.close()
        return result

    def test_health_reports_actual_provider(self):
        status, headers, body = self.request("GET", "/api/health")
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body)["model"]["provider"], "CPUExecutionProvider")
        self.assertEqual(headers["Cache-Control"], "no-store")

    def test_answer_route(self):
        status, _, body = self.request("POST", "/api/ask", json.dumps({"question": "Where is the tin bird?"}), {"Content-Type": "application/json"})
        self.assertEqual(status, 200)
        self.assertIn("sources", json.loads(body))

    def test_rejects_cross_origin_and_rebinding(self):
        for headers in [{"Origin": "https://example.com"}, {"Host": "attacker.example"}]:
            self.assertEqual(self.request("GET", "/api/archive", headers=headers)[0], 403)

    def test_only_serves_whitelisted_files(self):
        for path in ["/../archive.py", "/data/letters.json", "/models/model.onnx", "/.git/config"]:
            self.assertEqual(self.request("GET", path)[0], 404)

    def test_invalid_json_and_payload(self):
        for body in ["{", "[]", '{"question": false}']:
            self.assertEqual(self.request("POST", "/api/ask", body, {"Content-Type": "application/json"})[0], 400)
        self.assertEqual(self.request("POST", "/api/ask", "x")[0], 415)
        self.assertEqual(self.request("POST", "/api/ask", "x" * 8193, {"Content-Type": "application/json"})[0], 413)


if __name__ == "__main__":
    unittest.main()
