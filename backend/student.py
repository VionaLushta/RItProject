"""Simple student data model for CampusMate AI."""

from __future__ import annotations


class Student:
    """Store basic student counters in one small object."""

    def __init__(
        self,
        name: str = "Student",
        questions_asked: int = 0,
        quizzes_completed: int = 0,
        correct_answers: int = 0,
        incorrect_answers: int = 0,
    ) -> None:
        self.name = name
        self.questions_asked = questions_asked
        self.quizzes_completed = quizzes_completed
        self.correct_answers = correct_answers
        self.incorrect_answers = incorrect_answers

    def add_question(self) -> None:
        self.questions_asked += 1

    def add_quiz(self) -> None:
        self.quizzes_completed += 1

    def add_correct_answer(self) -> None:
        self.correct_answers += 1

    def add_incorrect_answer(self) -> None:
        self.incorrect_answers += 1

    def to_dict(self) -> dict[str, int | str]:
        return {
            "name": self.name,
            "questions_asked": self.questions_asked,
            "quizzes_completed": self.quizzes_completed,
            "correct_answers": self.correct_answers,
            "incorrect_answers": self.incorrect_answers,
        }

