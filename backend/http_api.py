"""Minimal HTTP API for CampusMate AI."""

from __future__ import annotations

import json
from http import HTTPStatus
from pathlib import Path
from typing import Any

from backend.explanation_service import explain_topic
from backend.history_service import get_history
from backend.question_service import ask_question
from backend.quiz import generate_quiz, score_quiz
from backend.statistics_service import get_statistics
from backend.student import Student
from backend.storage import load_data
from backend.storage import add_ai_interaction
from backend.summarization_service import summarize_text

API_PREFIX = "/api"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8000


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        if isinstance(value, bool):
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def _student_from_storage(file_path: str | Path | None = None) -> Student:
    data = load_data(file_path)
    student_data = data.get("statistics", {}).get("Student", {})

    if not isinstance(student_data, dict):
        student_data = {}

    return Student(
        name=str(student_data.get("name", "Student")),
        questions_asked=_safe_int(student_data.get("questions_asked", 0)),
        quizzes_completed=_safe_int(student_data.get("quizzes_completed", 0)),
        correct_answers=_safe_int(student_data.get("correct_answers", 0)),
        incorrect_answers=_safe_int(student_data.get("incorrect_answers", 0)),
    )


def _normalize_path(path: str) -> str:
    if not path:
        return "/"
    if path != "/" and path.endswith("/"):
        return path.rstrip("/")
    return path


def _error(status: int, message: str) -> tuple[int, dict[str, Any]]:
    return status, {"error": message}


def dispatch_api_request(
    method: str,
    path: str,
    body: Any = None,
    file_path: str | Path | None = None,
) -> tuple[int, dict[str, Any]]:
    """Dispatch one API request and return a status/payload pair."""
    normalized_path = _normalize_path(path)
    method = method.upper()

    try:
        if method == "OPTIONS":
            return HTTPStatus.NO_CONTENT, {}

        if method == "GET" and normalized_path == f"{API_PREFIX}/health":
            return HTTPStatus.OK, {"status": "ok"}

        if method == "GET" and normalized_path == f"{API_PREFIX}/history":
            return HTTPStatus.OK, get_history(file_path)

        if method == "GET" and normalized_path == f"{API_PREFIX}/statistics":
            return HTTPStatus.OK, get_statistics(file_path)

        if method == "POST" and normalized_path == f"{API_PREFIX}/ask-ai":
            if not isinstance(body, dict):
                raise ValueError("Request body must be a JSON object.")
            answer = ask_question(body.get("question", ""), _student_from_storage(file_path), file_path)
            return HTTPStatus.OK, {"answer": answer}

        if method == "POST" and normalized_path == f"{API_PREFIX}/explain-topic":
            if not isinstance(body, dict):
                raise ValueError("Request body must be a JSON object.")
            explanation = explain_topic(body.get("topic", ""), body.get("difficulty", ""))
            add_ai_interaction("explain_topic", "Explain Topic", body.get("topic", ""), explanation, file_path)
            return HTTPStatus.OK, {"explanation": explanation}

        if method == "POST" and normalized_path == f"{API_PREFIX}/summarize":
            if not isinstance(body, dict):
                raise ValueError("Request body must be a JSON object.")
            summary = summarize_text(body.get("text", ""), body.get("style", ""))
            add_ai_interaction("summarize", "Summarize Text", body.get("text", ""), summary, file_path)
            return HTTPStatus.OK, {"summary": summary}

        if method == "POST" and normalized_path == f"{API_PREFIX}/generate-quiz":
            if not isinstance(body, dict):
                raise ValueError("Request body must be a JSON object.")
            question_count = body.get("question_count", body.get("questionCount"))
            quiz = generate_quiz(body.get("topic", ""), body.get("difficulty", ""), _safe_int(question_count))
            add_ai_interaction("quiz", "Generate Quiz", body.get("topic", ""), json.dumps(quiz, ensure_ascii=False), file_path)
            return HTTPStatus.OK, {"quiz": quiz}

        if method == "POST" and normalized_path == f"{API_PREFIX}/submit-quiz":
            if not isinstance(body, dict):
                raise ValueError("Request body must be a JSON object.")
            result = score_quiz(body.get("quiz"), body.get("answers"), _student_from_storage(file_path), file_path)
            return HTTPStatus.OK, {"result": result}

        if normalized_path.startswith(API_PREFIX):
            return _error(HTTPStatus.NOT_FOUND, "API route not found.")

        return _error(HTTPStatus.NOT_FOUND, "Route not found.")
    except ValueError as exc:
        return _error(HTTPStatus.BAD_REQUEST, str(exc))
    except RuntimeError as exc:
        return _error(HTTPStatus.BAD_GATEWAY, str(exc))
    except Exception:
        return _error(HTTPStatus.INTERNAL_SERVER_ERROR, "CampusMate couldn't complete this request. Please try again.")
