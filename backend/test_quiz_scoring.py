"""Focused tests for the Take Quiz scoring backend flow."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from backend.quiz import score_quiz
from backend.storage import load_data
from backend.student import Student


class QuizScoringTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.storage_path = Path(self.temp_dir.name) / "history.json"
        self.student = Student("Ava")
        self.two_question_quiz = {
            "topic": "Python",
            "difficulty": "beginner",
            "questions": [
                {
                    "question": "Which keyword defines a function in Python?",
                    "options": {"A": "func", "B": "define", "C": "def", "D": "function"},
                    "correct_answer": "C",
                },
                {
                    "question": "Which symbol is used for comments in Python?",
                    "options": {"A": "#", "B": "//", "C": "<!--", "D": "*"},
                    "correct_answer": "A",
                },
            ],
        }

    def test_all_answers_correct_give_one_hundred_percent(self) -> None:
        result = score_quiz(self.two_question_quiz, ["C", "A"], self.student, self.storage_path)

        self.assertEqual(result["correct_answers"], 2)
        self.assertEqual(result["incorrect_answers"], 0)
        self.assertEqual(result["score_percentage"], 100.0)

    def test_all_answers_incorrect_give_zero_percent(self) -> None:
        result = score_quiz(self.two_question_quiz, ["B", "B"], self.student, self.storage_path)

        self.assertEqual(result["correct_answers"], 0)
        self.assertEqual(result["incorrect_answers"], 2)
        self.assertEqual(result["score_percentage"], 0.0)

    def test_mixed_answers_calculate_correct_percentage(self) -> None:
        result = score_quiz(self.two_question_quiz, ["C", "B"], self.student, self.storage_path)

        self.assertEqual(result["correct_answers"], 1)
        self.assertEqual(result["incorrect_answers"], 1)
        self.assertEqual(result["score_percentage"], 50.0)

    def test_one_question_quiz_works(self) -> None:
        quiz = {
            "topic": "Math",
            "difficulty": "intermediate",
            "questions": [
                {
                    "question": "What is 2 + 2?",
                    "options": {"A": "3", "B": "4", "C": "5", "D": "6"},
                    "correct_answer": "B",
                }
            ],
        }
        result = score_quiz(quiz, ["B"], self.student, self.storage_path)

        self.assertEqual(result["total_questions"], 1)
        self.assertEqual(result["correct_answers"], 1)
        self.assertEqual(result["incorrect_answers"], 0)
        self.assertEqual(result["score_percentage"], 100.0)

    def test_lowercase_answers_normalize_correctly(self) -> None:
        result = score_quiz(self.two_question_quiz, ["c", "a"], self.student, self.storage_path)

        self.assertEqual(result["correct_answers"], 2)
        self.assertEqual(result["score_percentage"], 100.0)
        self.assertEqual(result["feedback"][0]["selected_answer"], "C")
        self.assertEqual(result["feedback"][1]["selected_answer"], "A")

    def test_invalid_answer_e_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "one of A, B, C, or D"):
            score_quiz(self.two_question_quiz, ["E", "A"], self.student, self.storage_path)

        self.assertEqual(self.student.quizzes_completed, 0)

    def test_empty_answer_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "non-empty answer choice"):
            score_quiz(self.two_question_quiz, ["", "A"], self.student, self.storage_path)

    def test_too_few_answers_are_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "must match the number of quiz questions"):
            score_quiz(self.two_question_quiz, ["C"], self.student, self.storage_path)

    def test_too_many_answers_are_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "must match the number of quiz questions"):
            score_quiz(self.two_question_quiz, ["C", "A", "B"], self.student, self.storage_path)

    def test_missing_quiz_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "Quiz must be a JSON object"):
            score_quiz(None, ["C"], self.student, self.storage_path)

    def test_empty_quiz_question_list_is_rejected(self) -> None:
        quiz = {"topic": "Python", "difficulty": "beginner", "questions": []}

        with self.assertRaisesRegex(ValueError, "non-empty questions list"):
            score_quiz(quiz, [], self.student, self.storage_path)

    def test_malformed_quiz_is_rejected(self) -> None:
        quiz = {"topic": "Python", "difficulty": "beginner", "questions": "not a list"}

        with self.assertRaisesRegex(ValueError, "non-empty questions list"):
            score_quiz(quiz, ["C"], self.student, self.storage_path)

    def test_quizzes_completed_increments_exactly_once(self) -> None:
        score_quiz(self.two_question_quiz, ["C", "A"], self.student, self.storage_path)

        self.assertEqual(self.student.quizzes_completed, 1)

    def test_student_correct_answer_count_updates_correctly(self) -> None:
        score_quiz(self.two_question_quiz, ["C", "A"], self.student, self.storage_path)

        self.assertEqual(self.student.correct_answers, 2)

    def test_student_incorrect_answer_count_updates_correctly(self) -> None:
        score_quiz(self.two_question_quiz, ["B", "B"], self.student, self.storage_path)

        self.assertEqual(self.student.incorrect_answers, 2)

    def test_failed_validation_does_not_modify_student_statistics(self) -> None:
        with self.assertRaisesRegex(ValueError, "one of A, B, C, or D"):
            score_quiz(self.two_question_quiz, ["E", "A"], self.student, self.storage_path)

        self.assertEqual(self.student.quizzes_completed, 0)
        self.assertEqual(self.student.correct_answers, 0)
        self.assertEqual(self.student.incorrect_answers, 0)

    def test_successful_result_is_persisted(self) -> None:
        score_quiz(self.two_question_quiz, ["C", "A"], self.student, self.storage_path)

        data = load_data(self.storage_path)
        self.assertEqual(len(data["quizzes"]), 1)
        self.assertEqual(
            data["quizzes"][0],
            {
                "topic": "Python",
                "difficulty": "beginner",
                "total_questions": 2,
                "correct_answers": 2,
                "incorrect_answers": 0,
                "score_percentage": 100.0,
            },
        )
        self.assertIn("Ava", data["statistics"])

    def test_failed_submission_is_not_persisted(self) -> None:
        with self.assertRaisesRegex(ValueError, "one of A, B, C, or D"):
            score_quiz(self.two_question_quiz, ["E", "A"], self.student, self.storage_path)

        data = load_data(self.storage_path)
        self.assertEqual(data["quizzes"], [])
        self.assertEqual(data["statistics"], {})

    def test_score_result_has_expected_structure(self) -> None:
        result = score_quiz(self.two_question_quiz, ["C", "A"], self.student, self.storage_path)

        self.assertEqual(
            set(result.keys()),
            {"total_questions", "correct_answers", "incorrect_answers", "score_percentage", "feedback"},
        )
        self.assertIsInstance(result["feedback"], list)
        self.assertEqual(result["feedback"][0]["question_number"], 1)
        self.assertTrue(result["feedback"][0]["is_correct"])

    def test_scoring_makes_no_openai_request(self) -> None:
        with patch("backend.quiz.ask_ai") as mocked_ask_ai:
            score_quiz(self.two_question_quiz, ["C", "A"], self.student, self.storage_path)

        mocked_ask_ai.assert_not_called()


if __name__ == "__main__":
    unittest.main()
