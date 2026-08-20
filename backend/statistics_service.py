"""Statistics helpers for CampusMate AI."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from backend.storage import load_data


def _safe_int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _sum_student_statistics(statistics: dict[str, Any]) -> dict[str, int]:
    totals = {
        "questions_asked": 0,
        "quizzes_completed": 0,
        "correct_answers": 0,
        "incorrect_answers": 0,
    }

    for student_data in statistics.values():
        if not isinstance(student_data, dict):
            continue
        totals["questions_asked"] += _safe_int(student_data.get("questions_asked", 0) or 0)
        totals["quizzes_completed"] += _safe_int(student_data.get("quizzes_completed", 0) or 0)
        totals["correct_answers"] += _safe_int(student_data.get("correct_answers", 0) or 0)
        totals["incorrect_answers"] += _safe_int(student_data.get("incorrect_answers", 0) or 0)

    return totals


def _calculate_average_quiz_score(quizzes: list[dict[str, Any]]) -> float:
    if not quizzes:
        return 0.0

    scores = []
    for quiz in quizzes:
        if not isinstance(quiz, dict):
            continue
        score = quiz.get("score_percentage", 0.0)
        try:
            scores.append(float(score))
        except (TypeError, ValueError):
            continue

    if not scores:
        return 0.0

    return round(sum(scores) / len(scores), 2)


def get_statistics(file_path: str | Path | None = None) -> dict[str, Any]:
    """Return aggregate CampusMate statistics from persisted JSON data."""
    data = load_data(file_path)
    totals = _sum_student_statistics(data["statistics"])
    average_quiz_score = _calculate_average_quiz_score(data["quizzes"])

    return {
        "questions_asked": totals["questions_asked"],
        "quizzes_completed": totals["quizzes_completed"],
        "correct_answers": totals["correct_answers"],
        "incorrect_answers": totals["incorrect_answers"],
        "average_quiz_score": average_quiz_score,
    }
