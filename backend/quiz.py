"""Reusable Generate Quiz backend flow for CampusMate AI."""

from __future__ import annotations

import json
from typing import Any

from backend.ai_service import ask_ai
from backend.prompts import QUIZ_DIFFICULTIES, build_quiz_prompt


def _normalize_difficulty(difficulty: str) -> str:
    if not isinstance(difficulty, str) or not difficulty.strip():
        raise ValueError(
            "Difficulty cannot be empty. Choose one of: beginner, intermediate, advanced."
        )

    normalized_difficulty = difficulty.strip().lower()
    if normalized_difficulty not in QUIZ_DIFFICULTIES:
        allowed = ", ".join(QUIZ_DIFFICULTIES)
        raise ValueError(f"Unsupported difficulty '{difficulty.strip()}'. Allowed difficulties: {allowed}.")

    return normalized_difficulty


def _validate_question_count(question_count: Any) -> int:
    if isinstance(question_count, bool) or not isinstance(question_count, int):
        raise ValueError("Question count must be an integer between 1 and 10.")
    if question_count < 1 or question_count > 10:
        raise ValueError("Question count must be between 1 and 10.")
    return question_count


def _validate_quiz_data(data: Any, question_count: int, topic: str, difficulty: str) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise ValueError("Quiz response must be a JSON object.")

    quiz_topic = data.get("topic")
    quiz_difficulty = data.get("difficulty")
    questions = data.get("questions")

    if quiz_topic != topic.strip():
        raise ValueError("Quiz response topic does not match the requested topic.")
    if quiz_difficulty != difficulty:
        raise ValueError("Quiz response difficulty does not match the requested difficulty.")
    if not isinstance(questions, list):
        raise ValueError("Quiz response must include a questions list.")
    if len(questions) != question_count:
        raise ValueError("Quiz response must contain the requested number of questions.")

    for index, question in enumerate(questions, start=1):
        if not isinstance(question, dict):
            raise ValueError(f"Question {index} must be an object.")

        question_text = question.get("question")
        options = question.get("options")
        correct_answer = question.get("correct_answer")

        if not isinstance(question_text, str) or not question_text.strip():
            raise ValueError(f"Question {index} must include non-empty question text.")
        if not isinstance(options, dict):
            raise ValueError(f"Question {index} must include options as an object.")
        if set(options.keys()) != {"A", "B", "C", "D"}:
            raise ValueError(f"Question {index} must include exactly A, B, C, and D options.")
        for key in ("A", "B", "C", "D"):
            option_text = options.get(key)
            if not isinstance(option_text, str) or not option_text.strip():
                raise ValueError(f"Question {index} option {key} must be non-empty text.")
        if correct_answer not in {"A", "B", "C", "D"}:
            raise ValueError(f"Question {index} must have a valid correct_answer of A, B, C, or D.")

    return data


def generate_quiz(topic: str, difficulty: str, question_count: int) -> dict[str, Any]:
    """Generate a structured multiple-choice quiz for the requested topic."""
    if not isinstance(topic, str) or not topic.strip():
        raise ValueError("Topic cannot be empty. Please enter a topic for the quiz.")

    normalized_difficulty = _normalize_difficulty(difficulty)
    validated_question_count = _validate_question_count(question_count)
    prompt = build_quiz_prompt(topic, normalized_difficulty, validated_question_count)
    response_text = ask_ai(prompt)

    if not response_text.strip():
        raise RuntimeError("CampusMate AI returned an empty quiz. Please try again.")

    try:
        parsed = json.loads(response_text)
    except json.JSONDecodeError as exc:
        raise RuntimeError("CampusMate AI returned malformed quiz JSON. Please try again.") from exc

    return _validate_quiz_data(parsed, validated_question_count, topic, normalized_difficulty)

def describe() -> str:
    return "Generate Quiz service"
