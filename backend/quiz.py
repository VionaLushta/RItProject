"""Reusable Generate Quiz backend flow for CampusMate AI."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from backend.ai_service import ask_ai
from backend.prompts import QUIZ_DIFFICULTIES, build_quiz_prompt
from backend.storage import add_quiz_record, save_student_statistics
from backend.student import Student

VALID_ANSWER_CHOICES = {"A", "B", "C", "D"}


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


def _validate_quiz_question(question: Any, index: int) -> dict[str, Any]:
    if not isinstance(question, dict):
        raise ValueError(f"Question {index} must be an object.")

    question_text = question.get("question")
    options = question.get("options")
    correct_answer = question.get("correct_answer")

    if not isinstance(question_text, str) or not question_text.strip():
        raise ValueError(f"Question {index} must include non-empty question text.")
    if not isinstance(options, dict):
        raise ValueError(f"Question {index} must include options as an object.")
    if set(options.keys()) != VALID_ANSWER_CHOICES:
        raise ValueError(f"Question {index} must include exactly A, B, C, and D options.")
    for key in ("A", "B", "C", "D"):
        option_text = options.get(key)
        if not isinstance(option_text, str) or not option_text.strip():
            raise ValueError(f"Question {index} option {key} must be non-empty text.")
    if correct_answer not in VALID_ANSWER_CHOICES:
        raise ValueError(f"Question {index} must have a valid correct_answer of A, B, C, or D.")

    return {
        "question": question_text.strip(),
        "options": {key: options[key].strip() for key in ("A", "B", "C", "D")},
        "correct_answer": correct_answer,
    }


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
        questions[index - 1] = _validate_quiz_question(question, index)

    return {
        "topic": quiz_topic.strip(),
        "difficulty": quiz_difficulty,
        "questions": questions,
    }


def _validate_scored_quiz(quiz: Any) -> dict[str, Any]:
    if not isinstance(quiz, dict):
        raise ValueError("Quiz must be a JSON object.")

    topic = quiz.get("topic")
    difficulty = quiz.get("difficulty")
    questions = quiz.get("questions")

    if not isinstance(topic, str) or not topic.strip():
        raise ValueError("Quiz must include a non-empty topic.")
    if not isinstance(difficulty, str) or not difficulty.strip():
        raise ValueError("Quiz must include a non-empty difficulty.")

    normalized_difficulty = difficulty.strip().lower()
    if normalized_difficulty not in QUIZ_DIFFICULTIES:
        allowed = ", ".join(QUIZ_DIFFICULTIES)
        raise ValueError(f"Quiz difficulty must be one of: {allowed}.")
    if not isinstance(questions, list) or not questions:
        raise ValueError("Quiz must include a non-empty questions list.")

    normalized_questions = []
    for index, question in enumerate(questions, start=1):
        normalized_questions.append(_validate_quiz_question(question, index))

    return {
        "topic": topic.strip(),
        "difficulty": normalized_difficulty,
        "questions": normalized_questions,
    }


def _normalize_answer(answer: Any, index: int) -> str:
    if not isinstance(answer, str) or not answer.strip():
        raise ValueError(f"Answer {index} must be a non-empty answer choice.")

    normalized_answer = answer.strip().upper()
    if normalized_answer not in VALID_ANSWER_CHOICES:
        raise ValueError(f"Answer {index} must be one of A, B, C, or D.")

    return normalized_answer


def _validate_answers(answers: Any, question_count: int) -> list[str]:
    if isinstance(answers, (str, bytes)) or not isinstance(answers, (list, tuple)):
        raise ValueError("Answers must be a list of answer choices.")
    if len(answers) != question_count:
        raise ValueError("The number of answers must match the number of quiz questions.")

    return [_normalize_answer(answer, index) for index, answer in enumerate(answers, start=1)]


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


def score_quiz(
    quiz: Any,
    answers: Any,
    student: Student,
    file_path: str | Path | None = None,
) -> dict[str, Any]:
    """Score a completed quiz entirely in Python and persist the result."""
    if not isinstance(student, Student):
        raise ValueError("Student is required for quiz scoring.")

    validated_quiz = _validate_scored_quiz(quiz)
    normalized_answers = _validate_answers(answers, len(validated_quiz["questions"]))

    correct_count = 0
    feedback: list[dict[str, Any]] = []

    for index, (question, selected_answer) in enumerate(
        zip(validated_quiz["questions"], normalized_answers),
        start=1,
    ):
        is_correct = selected_answer == question["correct_answer"]
        if is_correct:
            correct_count += 1
        feedback.append(
            {
                "question_number": index,
                "selected_answer": selected_answer,
                "correct_answer": question["correct_answer"],
                "is_correct": is_correct,
            }
        )

    total_questions = len(validated_quiz["questions"])
    incorrect_count = total_questions - correct_count
    score_percentage = round((correct_count / total_questions) * 100, 1)

    result = {
        "total_questions": total_questions,
        "correct_answers": correct_count,
        "incorrect_answers": incorrect_count,
        "score_percentage": score_percentage,
        "feedback": feedback,
    }

    student.add_quiz()
    for _ in range(correct_count):
        student.add_correct_answer()
    for _ in range(incorrect_count):
        student.add_incorrect_answer()

    add_quiz_record(
        {
            "topic": validated_quiz["topic"],
            "difficulty": validated_quiz["difficulty"],
            "total_questions": total_questions,
            "correct_answers": correct_count,
            "incorrect_answers": incorrect_count,
            "score_percentage": score_percentage,
        },
        file_path,
    )
    save_student_statistics(student, file_path)

    return result


def describe() -> str:
    return "Generate Quiz service"
