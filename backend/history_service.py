"""History retrieval helpers for CampusMate AI."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from backend.storage import load_data


def _records(data: dict[str, Any], key: str) -> list[dict[str, Any]]:
    """Return only valid record objects from the JSON history store."""
    records = data.get(key, [])
    if not isinstance(records, list):
        return []
    return [record for record in records if isinstance(record, dict)]


def get_question_history(file_path: str | Path | None = None) -> list[dict[str, Any]]:
    """Return persisted Ask AI question history."""
    data = load_data(file_path)
    return _records(data, "questions")


def get_quiz_history(file_path: str | Path | None = None) -> list[dict[str, Any]]:
    """Return persisted completed quiz history."""
    data = load_data(file_path)
    return _records(data, "quizzes")


def get_history(file_path: str | Path | None = None) -> dict[str, list[dict[str, Any]]]:
    """Return combined question and quiz history."""
    data = load_data(file_path)
    history = {
        "questions": _records(data, "questions"),
        "quizzes": _records(data, "quizzes"),
    }
    interactions = _records(data, "interactions")
    if interactions:
        history["interactions"] = interactions
    return history
