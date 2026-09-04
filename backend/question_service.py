"""Reusable Ask AI question flow for CampusMate AI."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

from backend.ai_service import ask_ai, stream_ai
from backend.prompts import build_question_answer_prompt
from backend.storage import add_ai_interaction, add_question_record, save_student_statistics
from backend.student import Student


def ask_question(
    question: str,
    student: Student,
    file_path: str | Path | None = None,
) -> str:
    """Answer a student question, persist it, and update statistics."""
    if not isinstance(question, str) or not question.strip():
        raise ValueError("Question cannot be empty. Please type a study question.")

    prompt = build_question_answer_prompt(question)
    answer = ask_ai(prompt)

    if not answer.strip():
        raise RuntimeError("CampusMate AI returned an empty answer. Please try again.")

    add_question_record(question.strip(), answer, file_path)
    add_ai_interaction("ask_ai", "Ask AI", question, answer, file_path)
    student.add_question()
    save_student_statistics(student, file_path)

    return answer


def stream_question_answer(
    question: str,
    student: Student,
    file_path: str | Path | None = None,
) -> Iterator[str]:
    """Stream a question answer, then persist the completed result once."""
    if not isinstance(question, str) or not question.strip():
        raise ValueError("Question cannot be empty. Please type a study question.")

    prompt = build_question_answer_prompt(question)
    answer_parts: list[str] = []

    for chunk in stream_ai(prompt):
        if not chunk:
            continue
        answer_parts.append(chunk)
        yield chunk

    answer = "".join(answer_parts).strip()
    if not answer:
        raise RuntimeError("CampusMate AI returned an empty answer. Please try again.")

    add_question_record(question.strip(), answer, file_path)
    add_ai_interaction("ask_ai", "Ask AI", question, answer, file_path)
    student.add_question()
    save_student_statistics(student, file_path)
