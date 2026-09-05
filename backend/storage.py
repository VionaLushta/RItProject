"""Small JSON storage helpers for CampusMate AI."""

from __future__ import annotations

import json
import warnings
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from backend.student import Student

ROOT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_HISTORY_PATH = ROOT_DIR / "backend" / "data" / "history.json"
DEFAULT_DATA = {
    "questions": [],
    "quizzes": [],
    "statistics": {},
}


def _copy_default_data() -> dict[str, Any]:
    return {
        "questions": [],
        "quizzes": [],
        "statistics": {},
    }


def _resolve_path(file_path: str | Path | None) -> Path:
    if file_path is None:
        return DEFAULT_HISTORY_PATH
    return Path(file_path)


def _normalize_data(data: Any) -> dict[str, Any]:
    if not isinstance(data, dict):
        return _copy_default_data()

    normalized = _copy_default_data()

    questions = data.get("questions", [])
    quizzes = data.get("quizzes", [])
    statistics = data.get("statistics", {})

    if isinstance(questions, list):
        normalized["questions"] = questions
    if isinstance(quizzes, list):
        normalized["quizzes"] = quizzes
    if "interactions" in data and isinstance(data["interactions"], list):
        normalized["interactions"] = data["interactions"]
    if isinstance(statistics, dict):
        normalized["statistics"] = statistics

    return normalized


def load_data(file_path: str | Path | None = None) -> dict[str, Any]:
    """Load stored JSON data and return safe empty data when needed."""
    path = _resolve_path(file_path)

    if not path.exists():
        return _copy_default_data()

    try:
        raw_text = path.read_text(encoding="utf-8").strip()
    except OSError as exc:
        warnings.warn(f"Could not read history file '{path}': {exc}", RuntimeWarning)
        return _copy_default_data()

    if not raw_text:
        warnings.warn(f"History file '{path}' is empty. Using safe default data.", RuntimeWarning)
        return _copy_default_data()

    try:
        loaded = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        warnings.warn(
            f"History file '{path}' contains invalid JSON. Using safe default data: {exc}",
            RuntimeWarning,
        )
        return _copy_default_data()

    return _normalize_data(loaded)


def save_data(data: dict[str, Any], file_path: str | Path | None = None) -> None:
    """Save data to disk in a readable JSON format."""
    path = _resolve_path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    normalized = _normalize_data(data)
    temp_path = path.with_suffix(path.suffix + ".tmp")

    with temp_path.open("w", encoding="utf-8") as file:
        json.dump(normalized, file, indent=2, ensure_ascii=False)
        file.write("\n")

    temp_path.replace(path)


def add_question_record(
    question: str,
    answer: str,
    file_path: str | Path | None = None,
) -> dict[str, Any]:
    """Store one question and answer pair."""
    data = load_data(file_path)
    data["questions"].append({"question": question, "answer": answer})
    save_data(data, file_path)
    return data


def add_ai_interaction(
    interaction_type: str,
    title: str,
    user_input: str,
    output: str,
    file_path: str | Path | None = None,
) -> dict[str, Any]:
    """Persist one AI interaction with an exact UTC date and time."""
    data = load_data(file_path)
    data.setdefault("interactions", [])
    data["interactions"].append(
        {
            "type": interaction_type,
            "title": title.strip(),
            "input": user_input.strip(),
            "output": output.strip(),
            "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        }
    )
    save_data(data, file_path)
    return data


def get_question_history(file_path: str | Path | None = None) -> list[dict[str, Any]]:
    """Return the saved question history."""
    data = load_data(file_path)
    return data["questions"]


def add_quiz_record(quiz_record: dict[str, Any], file_path: str | Path | None = None) -> dict[str, Any]:
    """Store one quiz record."""
    data = load_data(file_path)
    data["quizzes"].append(quiz_record)
    save_data(data, file_path)
    return data


def delete_history_record(section: str, index: int, file_path: str | Path | None = None) -> dict[str, Any]:
    """Delete one history record from a known history section."""
    if section not in {"interactions", "questions", "quizzes"}:
        raise ValueError("History section must be interactions, questions, or quizzes.")

    data = load_data(file_path)
    records = data.setdefault(section, [])

    if not isinstance(records, list) or index < 0 or index >= len(records):
        raise ValueError("History item was not found.")

    deleted = records.pop(index)
    save_data(data, file_path)
    return {"deleted": deleted, "history": data}


def save_student_statistics(student: Student | dict[str, Any], file_path: str | Path | None = None) -> dict[str, Any]:
    """Save one student's counters under the statistics section."""
    data = load_data(file_path)

    if isinstance(student, Student):
        student_data = student.to_dict()
    else:
        student_data = dict(student)

    student_name = str(student_data.get("name", "Student"))
    data["statistics"][student_name] = student_data
    save_data(data, file_path)
    return data
