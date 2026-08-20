"""Focused tests for history and statistics backend helpers."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from backend.history_service import get_history, get_question_history, get_quiz_history
from backend.statistics_service import get_statistics
from backend.storage import add_question_record, add_quiz_record, load_data, save_data, save_student_statistics
from backend.student import Student


class HistoryStatisticsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.storage_path = Path(self.temp_dir.name) / "history.json"
        self.student = Student("Ava")

    def test_empty_question_history_returns_empty_list(self) -> None:
        self.assertEqual(get_question_history(self.storage_path), [])

    def test_saved_questions_can_be_retrieved(self) -> None:
        add_question_record("What is Python?", "A programming language.", self.storage_path)

        self.assertEqual(
            get_question_history(self.storage_path),
            [{"question": "What is Python?", "answer": "A programming language."}],
        )

    def test_multiple_questions_retain_order(self) -> None:
        add_question_record("Q1", "A1", self.storage_path)
        add_question_record("Q2", "A2", self.storage_path)

        history = get_question_history(self.storage_path)
        self.assertEqual([item["question"] for item in history], ["Q1", "Q2"])

    def test_empty_quiz_history_returns_empty_list(self) -> None:
        self.assertEqual(get_quiz_history(self.storage_path), [])

    def test_saved_completed_quizzes_can_be_retrieved(self) -> None:
        add_quiz_record(
            {
                "topic": "Python",
                "difficulty": "beginner",
                "total_questions": 2,
                "correct_answers": 2,
                "incorrect_answers": 0,
                "score_percentage": 100.0,
            },
            self.storage_path,
        )

        self.assertEqual(
            get_quiz_history(self.storage_path),
            [
                {
                    "topic": "Python",
                    "difficulty": "beginner",
                    "total_questions": 2,
                    "correct_answers": 2,
                    "incorrect_answers": 0,
                    "score_percentage": 100.0,
                }
            ],
        )

    def test_combined_history_contains_questions_and_quizzes(self) -> None:
        add_question_record("What is Python?", "A programming language.", self.storage_path)
        add_quiz_record(
            {
                "topic": "Python",
                "difficulty": "beginner",
                "total_questions": 1,
                "correct_answers": 1,
                "incorrect_answers": 0,
                "score_percentage": 100.0,
            },
            self.storage_path,
        )

        history = get_history(self.storage_path)
        self.assertEqual(len(history["questions"]), 1)
        self.assertEqual(len(history["quizzes"]), 1)

    def test_zero_history_statistics_return_zeros(self) -> None:
        self.assertEqual(
            get_statistics(self.storage_path),
            {
                "questions_asked": 0,
                "quizzes_completed": 0,
                "correct_answers": 0,
                "incorrect_answers": 0,
                "average_quiz_score": 0.0,
            },
        )

    def test_questions_asked_is_returned_correctly(self) -> None:
        self.student.add_question()
        self.student.add_question()
        save_student_statistics(self.student, self.storage_path)

        self.assertEqual(get_statistics(self.storage_path)["questions_asked"], 2)

    def test_quizzes_completed_is_returned_correctly(self) -> None:
        self.student.add_quiz()
        save_student_statistics(self.student, self.storage_path)

        self.assertEqual(get_statistics(self.storage_path)["quizzes_completed"], 1)

    def test_correct_answers_is_returned_correctly(self) -> None:
        self.student.add_correct_answer()
        self.student.add_correct_answer()
        save_student_statistics(self.student, self.storage_path)

        self.assertEqual(get_statistics(self.storage_path)["correct_answers"], 2)

    def test_incorrect_answers_is_returned_correctly(self) -> None:
        self.student.add_incorrect_answer()
        save_student_statistics(self.student, self.storage_path)

        self.assertEqual(get_statistics(self.storage_path)["incorrect_answers"], 1)

    def test_one_quiz_calculates_average_score_correctly(self) -> None:
        add_quiz_record(
            {
                "topic": "Python",
                "difficulty": "beginner",
                "total_questions": 1,
                "correct_answers": 1,
                "incorrect_answers": 0,
                "score_percentage": 80.0,
            },
            self.storage_path,
        )

        self.assertEqual(get_statistics(self.storage_path)["average_quiz_score"], 80.0)

    def test_multiple_quizzes_calculate_average_score_correctly(self) -> None:
        add_quiz_record(
            {
                "topic": "Python",
                "difficulty": "beginner",
                "total_questions": 1,
                "correct_answers": 1,
                "incorrect_answers": 0,
                "score_percentage": 80.0,
            },
            self.storage_path,
        )
        add_quiz_record(
            {
                "topic": "Python",
                "difficulty": "beginner",
                "total_questions": 1,
                "correct_answers": 1,
                "incorrect_answers": 0,
                "score_percentage": 60.0,
            },
            self.storage_path,
        )
        add_quiz_record(
            {
                "topic": "Python",
                "difficulty": "beginner",
                "total_questions": 1,
                "correct_answers": 1,
                "incorrect_answers": 0,
                "score_percentage": 100.0,
            },
            self.storage_path,
        )

        self.assertEqual(get_statistics(self.storage_path)["average_quiz_score"], 80.0)

    def test_average_score_is_zero_when_no_quizzes_exist(self) -> None:
        self.assertEqual(get_statistics(self.storage_path)["average_quiz_score"], 0.0)

    def test_missing_history_file_is_handled(self) -> None:
        missing_path = Path(self.temp_dir.name) / "missing.json"
        self.assertEqual(get_history(missing_path), {"questions": [], "quizzes": []})
        self.assertEqual(
            get_statistics(missing_path),
            {
                "questions_asked": 0,
                "quizzes_completed": 0,
                "correct_answers": 0,
                "incorrect_answers": 0,
                "average_quiz_score": 0.0,
            },
        )

    def test_empty_history_file_is_handled(self) -> None:
        self.storage_path.write_text("", encoding="utf-8")

        self.assertEqual(get_history(self.storage_path), {"questions": [], "quizzes": []})
        self.assertEqual(
            get_statistics(self.storage_path),
            {
                "questions_asked": 0,
                "quizzes_completed": 0,
                "correct_answers": 0,
                "incorrect_answers": 0,
                "average_quiz_score": 0.0,
            },
        )

    def test_invalid_json_is_handled_according_to_storage_policy(self) -> None:
        self.storage_path.write_text("{ not valid json", encoding="utf-8")

        self.assertEqual(get_history(self.storage_path), {"questions": [], "quizzes": []})
        self.assertEqual(
            get_statistics(self.storage_path),
            {
                "questions_asked": 0,
                "quizzes_completed": 0,
                "correct_answers": 0,
                "incorrect_answers": 0,
                "average_quiz_score": 0.0,
            },
        )

    def test_history_statistics_make_no_openai_calls(self) -> None:
        with patch("backend.ai_service.ask_ai") as mocked_ask_ai:
            get_history(self.storage_path)
            get_statistics(self.storage_path)

        mocked_ask_ai.assert_not_called()

    def test_existing_student_storage_behavior_remains_working(self) -> None:
        self.student.add_question()
        self.student.add_quiz()
        save_student_statistics(self.student, self.storage_path)

        data = load_data(self.storage_path)
        self.assertIn("Ava", data["statistics"])
        self.assertEqual(data["statistics"]["Ava"]["questions_asked"], 1)
        self.assertEqual(data["statistics"]["Ava"]["quizzes_completed"], 1)

    def test_existing_quiz_scoring_remains_working(self) -> None:
        add_quiz_record(
            {
                "topic": "Python",
                "difficulty": "beginner",
                "total_questions": 1,
                "correct_answers": 1,
                "incorrect_answers": 0,
                "score_percentage": 100.0,
            },
            self.storage_path,
        )

        self.assertEqual(len(get_quiz_history(self.storage_path)), 1)


if __name__ == "__main__":
    unittest.main()
