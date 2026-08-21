"""CampusMate AI backend HTTP entry point."""

from __future__ import annotations

import argparse
import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from backend.http_api import DEFAULT_HOST, DEFAULT_PORT, dispatch_api_request
from backend.storage import DEFAULT_HISTORY_PATH


class CampusMateRequestHandler(BaseHTTPRequestHandler):
    storage_path: Path = DEFAULT_HISTORY_PATH

    def _send_json(self, status: int, payload: dict[str, Any]) -> None:
        response = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(response)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(response)

    def _parse_json_body(self) -> Any:
        content_length = int(self.headers.get("Content-Length", "0") or "0")
        if content_length <= 0:
            return None

        raw = self.rfile.read(content_length).decode("utf-8").strip()
        if not raw:
            return None

        return json.loads(raw)

    def do_OPTIONS(self) -> None:  # noqa: N802
        self.send_response(HTTPStatus.NO_CONTENT)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self) -> None:  # noqa: N802
        status, payload = dispatch_api_request("GET", self.path, file_path=self.storage_path)
        self._send_json(status, payload)

    def do_POST(self) -> None:  # noqa: N802
        try:
            body = self._parse_json_body()
        except json.JSONDecodeError:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": "Request body must be valid JSON."})
            return

        status, payload = dispatch_api_request("POST", self.path, body=body, file_path=self.storage_path)
        self._send_json(status, payload)

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
        return


def create_server(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> ThreadingHTTPServer:
    server = ThreadingHTTPServer((host, port), CampusMateRequestHandler)
    return server


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the CampusMate AI backend server.")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", default=DEFAULT_PORT, type=int)
    args = parser.parse_args()

    server = create_server(args.host, args.port)
    print(f"CampusMate AI backend running on http://{args.host}:{args.port}")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
