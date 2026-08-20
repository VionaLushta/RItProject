"""History retrieval helpers for CampusMate AI."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from backend.storage import load_data


def get_question_history(file_path: str | Path | None = None) -> list[dict[str, Any]]:
    """Return persisted Ask AI question history."""
    data = load_data(file_path)
    return data["questions"]


def get_quiz_history(file_path: str | Path | None = None) -> list[dict[str, Any]]:
    """Return persisted completed quiz history."""
    data = load_data(file_path)
    return data["quizzes"]


def get_history(file_path: str | Path | None = None) -> dict[str, list[dict[str, Any]]]:
    """Return combined question and quiz history."""
    data = load_data(file_path)
    return {
        "questions": data["questions"],
        "quizzes": data["quizzes"],
    }
