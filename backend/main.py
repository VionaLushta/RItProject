"""CampusMate AI backend HTTP entry point."""

from __future__ import annotations

import argparse
import json
import logging
import time
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from backend.http_api import DEFAULT_HOST, DEFAULT_PORT, _student_from_storage, dispatch_api_request
from backend.question_service import stream_question_answer
from backend.storage import DEFAULT_HISTORY_PATH

LOGGER = logging.getLogger("campusmate.backend")


class CampusMateRequestHandler(BaseHTTPRequestHandler):
    storage_path: Path = DEFAULT_HISTORY_PATH

    def _send_json(self, status: int, payload: dict[str, Any]) -> None:
        response = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(response)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,DELETE,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(response)

    def _send_stream_headers(self) -> None:
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "close")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,DELETE,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def _send_stream_event(self, event: str, data: dict[str, Any]) -> None:
        payload = json.dumps(data, ensure_ascii=False)
        message = f"event: {event}\ndata: {payload}\n\n".encode("utf-8")
        self.wfile.write(message)
        self.wfile.flush()

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
        self.send_header("Access-Control-Allow-Methods", "GET,POST,DELETE,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self) -> None:  # noqa: N802
        self._handle_json_request("GET")

    def do_DELETE(self) -> None:  # noqa: N802
        try:
            body = self._parse_json_body()
        except json.JSONDecodeError:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": "Request body must be valid JSON."})
            return

        status, payload = dispatch_api_request("DELETE", self.path, body=body, file_path=self.storage_path)
        self._send_json(status, payload)

    def do_POST(self) -> None:  # noqa: N802
        try:
            body = self._parse_json_body()
        except json.JSONDecodeError:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": "Request body must be valid JSON."})
            return

        if self.path.split("?", 1)[0].rstrip("/") == "/api/ask-ai/stream":
            if not isinstance(body, dict):
                self._send_json(HTTPStatus.BAD_REQUEST, {"error": "Request body must be a JSON object."})
                return

            student = _student_from_storage(self.storage_path)

            try:
                self._send_stream_headers()
                streamed_answer = []
                for chunk in stream_question_answer(body.get("question", ""), student, self.storage_path):
                    streamed_answer.append(chunk)
                    self._send_stream_event("delta", {"chunk": chunk})

                final_answer = "".join(streamed_answer).strip()
                self._send_stream_event("done", {"answer": final_answer})
                self.close_connection = True
            except ValueError as exc:
                self._send_stream_event("error", {"error": str(exc)})
                self.close_connection = True
            except RuntimeError as exc:
                self._send_stream_event("error", {"error": str(exc)})
                self.close_connection = True
            except BrokenPipeError:
                return
            except Exception:
                LOGGER.exception("Streaming request failed: POST %s", self.path)
                self._send_stream_event(
                    "error",
                    {"error": "CampusMate couldn't complete this request. Please try again."},
                )
                self.close_connection = True
            return

        status, payload = dispatch_api_request("POST", self.path, body=body, file_path=self.storage_path)
        self._send_json(status, payload)

    def _handle_json_request(self, method: str) -> None:
        started_at = time.perf_counter()
        status, payload = dispatch_api_request(method, self.path, file_path=self.storage_path)
        self._send_json(status, payload)
        elapsed_ms = (time.perf_counter() - started_at) * 1000
        LOGGER.info("%s %s -> %s (%.1f ms)", method, self.path, status, elapsed_ms)

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
        LOGGER.info("%s - %s", self.address_string(), format % args)


def create_server(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> ThreadingHTTPServer:
    server = ThreadingHTTPServer((host, port), CampusMateRequestHandler)
    return server


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        force=True,
    )
    parser = argparse.ArgumentParser(description="Run the CampusMate AI backend server.")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", default=DEFAULT_PORT, type=int)
    args = parser.parse_args()

    server = create_server(args.host, args.port)
    LOGGER.info("CampusMate AI backend running on http://%s:%s", args.host, args.port)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        LOGGER.info("CampusMate AI backend stopped")


if __name__ == "__main__":
    main()
