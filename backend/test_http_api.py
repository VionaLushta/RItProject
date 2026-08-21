"""Tests for the minimal CampusMate HTTP API layer."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from backend.http_api import dispatch_api_request
from backend.storage import add_question_record, add_quiz_record, save_student_statistics
from backend.student import Student


class HttpApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.storage_path = Path(self.temp_dir.name) / "history.json"

    def test_health_endpoint_returns_ok(self) -> None:
        status, payload = dispatch_api_request("GET", "/api/health", file_path=self.storage_path)

        self.assertEqual(int(status), 200)
        self.assertEqual(payload, {"status": "ok"})

    def test_ask_ai_endpoint_delegates_to_question_service(self) -> None:
        student = Student("Student", questions_asked=3, quizzes_completed=1, correct_answers=4, incorrect_answers=2)
        save_student_statistics(student, self.storage_path)

        with patch("backend.http_api.ask_question", return_value="Answer") as mocked_ask_question:
            status, payload = dispatch_api_request(
                "POST",
                "/api/ask-ai",
                {"question": "What is TCP?"},
                self.storage_path,
            )

        self.assertEqual(int(status), 200)
        self.assertEqual(payload, {"answer": "Answer"})
        mocked_ask_question.assert_called_once()
        self.assertEqual(mocked_ask_question.call_args.args[0], "What is TCP?")
        self.assertEqual(mocked_ask_question.call_args.args[2], self.storage_path)
        self.assertEqual(mocked_ask_question.call_args.args[1].questions_asked, 3)

    def test_generate_quiz_endpoint_wraps_quiz_payload(self) -> None:
        quiz = {
            "topic": "Python",
            "difficulty": "beginner",
            "questions": [
                {
                    "question": "What is Python?",
                    "options": {"A": "Snake", "B": "Language", "C": "Car", "D": "Planet"},
                    "correct_answer": "B",
                }
            ],
        }

        with patch("backend.http_api.generate_quiz", return_value=quiz) as mocked_generate_quiz:
            status, payload = dispatch_api_request(
                "POST",
                "/api/generate-quiz",
                {"topic": "Python", "difficulty": "beginner", "question_count": 1},
                self.storage_path,
            )

        self.assertEqual(int(status), 200)
        self.assertEqual(payload, {"quiz": quiz})
        mocked_generate_quiz.assert_called_once_with("Python", "beginner", 1)

    def test_submit_quiz_endpoint_delegates_to_scoring_service(self) -> None:
        student = Student("Student", questions_asked=1, quizzes_completed=2, correct_answers=5, incorrect_answers=1)
        save_student_statistics(student, self.storage_path)
        quiz = {
            "topic": "Python",
            "difficulty": "beginner",
            "questions": [
                {
                    "question": "What is Python?",
                    "options": {"A": "Snake", "B": "Language", "C": "Car", "D": "Planet"},
                    "correct_answer": "B",
                }
            ],
        }
        result = {
            "total_questions": 1,
            "correct_answers": 1,
            "incorrect_answers": 0,
            "score_percentage": 100.0,
            "feedback": [],
        }

        with patch("backend.http_api.score_quiz", return_value=result) as mocked_score_quiz:
            status, payload = dispatch_api_request(
                "POST",
                "/api/submit-quiz",
                {"quiz": quiz, "answers": ["B"]},
                self.storage_path,
            )

        self.assertEqual(int(status), 200)
        self.assertEqual(payload, {"result": result})
        mocked_score_quiz.assert_called_once()
        self.assertEqual(mocked_score_quiz.call_args.args[0], quiz)
        self.assertEqual(mocked_score_quiz.call_args.args[1], ["B"])
        self.assertEqual(mocked_score_quiz.call_args.args[2].quizzes_completed, 2)

    def test_history_and_statistics_endpoints_return_real_data(self) -> None:
        add_question_record("What is Python?", "A language.", self.storage_path)
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

        status_history, history_payload = dispatch_api_request("GET", "/api/history", file_path=self.storage_path)
        status_stats, stats_payload = dispatch_api_request("GET", "/api/statistics", file_path=self.storage_path)

        self.assertEqual(int(status_history), 200)
        self.assertEqual(len(history_payload["questions"]), 1)
        self.assertEqual(len(history_payload["quizzes"]), 1)
        self.assertEqual(int(status_stats), 200)
        self.assertEqual(stats_payload["questions_asked"], 0)

    def test_invalid_json_body_is_rejected(self) -> None:
        status, payload = dispatch_api_request("POST", "/api/ask-ai", None, self.storage_path)

        self.assertEqual(int(status), 400)
        self.assertIn("Request body must be a JSON object", payload["error"])


if __name__ == "__main__":
    unittest.main()
