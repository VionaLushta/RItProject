"""Focused tests for the Ask Question backend flow."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from backend.question_service import ask_question
from backend.storage import get_question_history, load_data
from backend.student import Student


class AskQuestionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.storage_path = Path(self.temp_dir.name) / "history.json"
        self.student = Student("Ava")

    def test_valid_question_returns_an_answer(self) -> None:
        with patch("backend.question_service.ask_ai", return_value="Python is a programming language.") as mocked_ask_ai:
            answer = ask_question("What is Python?", self.student, self.storage_path)

        self.assertEqual(answer, "Python is a programming language.")
        mocked_ask_ai.assert_called_once()
        self.assertIn("CampusMate AI, a helpful study assistant.", mocked_ask_ai.call_args.args[0])

    def test_question_and_answer_are_saved_to_history(self) -> None:
        with patch("backend.question_service.ask_ai", return_value="It is a programming language."):
            ask_question("What is Python?", self.student, self.storage_path)

        history = get_question_history(self.storage_path)
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["question"], "What is Python?")
        self.assertEqual(history[0]["answer"], "It is a programming language.")

    def test_questions_asked_increases_by_one(self) -> None:
        with patch("backend.question_service.ask_ai", return_value="It is a programming language."):
            ask_question("What is Python?", self.student, self.storage_path)

        self.assertEqual(self.student.questions_asked, 1)
        stored = load_data(self.storage_path)
        self.assertEqual(stored["statistics"]["Ava"]["questions_asked"], 1)

    def test_empty_question_is_rejected(self) -> None:
        with patch("backend.question_service.ask_ai") as mocked_ask_ai:
            with self.assertRaisesRegex(ValueError, "Question cannot be empty"):
                ask_question("", self.student, self.storage_path)

        mocked_ask_ai.assert_not_called()

    def test_whitespace_only_question_is_rejected(self) -> None:
        with patch("backend.question_service.ask_ai") as mocked_ask_ai:
            with self.assertRaisesRegex(ValueError, "Question cannot be empty"):
                ask_question("   ", self.student, self.storage_path)

        mocked_ask_ai.assert_not_called()

    def test_failed_ai_request_does_not_save_history(self) -> None:
        with patch("backend.question_service.ask_ai", side_effect=RuntimeError("OpenAI request failed.")):
            with self.assertRaisesRegex(RuntimeError, "OpenAI request failed"):
                ask_question("What is Python?", self.student, self.storage_path)

        self.assertEqual(get_question_history(self.storage_path), [])

    def test_failed_ai_request_does_not_increase_statistics(self) -> None:
        with patch("backend.question_service.ask_ai", side_effect=RuntimeError("OpenAI request failed.")):
            with self.assertRaisesRegex(RuntimeError, "OpenAI request failed"):
                ask_question("What is Python?", self.student, self.storage_path)

        self.assertEqual(self.student.questions_asked, 0)
        stored = load_data(self.storage_path)
        self.assertEqual(stored["statistics"], {})


if __name__ == "__main__":
    unittest.main()
