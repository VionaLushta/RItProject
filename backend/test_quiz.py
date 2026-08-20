"""Focused tests for the Generate Quiz backend flow."""

from __future__ import annotations

import json
import unittest
from unittest.mock import patch

from backend.quiz import generate_quiz


class GenerateQuizTests(unittest.TestCase):
    def test_beginner_quiz_generation(self) -> None:
        payload = {
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
        with patch("backend.quiz.ask_ai", return_value=json.dumps(payload)) as mocked_ask_ai:
            result = generate_quiz("Python", "beginner", 1)

        self.assertEqual(result, payload)
        prompt = mocked_ask_ai.call_args.args[0]
        self.assertIn("Difficulty level: beginner", prompt)
        self.assertIn("definitions, basic concepts, and simple understanding", prompt)

    def test_intermediate_quiz_generation(self) -> None:
        payload = {
            "topic": "Python",
            "difficulty": "intermediate",
            "questions": [
                {
                    "question": "How do lists differ from tuples?",
                    "options": {"A": "No difference", "B": "Lists are mutable", "C": "Tuples are mutable", "D": "Both are strings"},
                    "correct_answer": "B",
                }
            ],
        }
        with patch("backend.quiz.ask_ai", return_value=json.dumps(payload)) as mocked_ask_ai:
            result = generate_quiz("Python", "Intermediate", 1)

        self.assertEqual(result, payload)
        prompt = mocked_ask_ai.call_args.args[0]
        self.assertIn("Difficulty level: intermediate", prompt)
        self.assertIn("application, relationships between concepts", prompt)

    def test_advanced_quiz_generation(self) -> None:
        payload = {
            "topic": "Python",
            "difficulty": "advanced",
            "questions": [
                {
                    "question": "Why might a generator be preferred over a list in some cases?",
                    "options": {"A": "It is always faster", "B": "It can reduce memory usage", "C": "It cannot be iterated", "D": "It only stores text"},
                    "correct_answer": "B",
                }
            ],
        }
        with patch("backend.quiz.ask_ai", return_value=json.dumps(payload)) as mocked_ask_ai:
            result = generate_quiz("Python", "advanced", 1)

        self.assertEqual(result, payload)
        prompt = mocked_ask_ai.call_args.args[0]
        self.assertIn("Difficulty level: advanced", prompt)
        self.assertIn("deeper mechanisms, technical details, reasoning", prompt)

    def test_topic_appears_in_prompt(self) -> None:
        payload = {
            "topic": "Biology",
            "difficulty": "beginner",
            "questions": [
                {
                    "question": "Question?",
                    "options": {"A": "One", "B": "Two", "C": "Three", "D": "Four"},
                    "correct_answer": "A",
                }
            ],
        }
        with patch("backend.quiz.ask_ai", return_value=json.dumps(payload)) as mocked_ask_ai:
            generate_quiz("Biology", "beginner", 1)

        prompt = mocked_ask_ai.call_args.args[0]
        self.assertIn("Topic: Biology", prompt)

    def test_question_count_appears_in_prompt(self) -> None:
        payload = {
            "topic": "Biology",
            "difficulty": "beginner",
            "questions": [
                {
                    "question": "Question 1?",
                    "options": {"A": "One", "B": "Two", "C": "Three", "D": "Four"},
                    "correct_answer": "A",
                },
                {
                    "question": "Question 2?",
                    "options": {"A": "One", "B": "Two", "C": "Three", "D": "Four"},
                    "correct_answer": "B",
                },
            ],
        }
        with patch("backend.quiz.ask_ai", return_value=json.dumps(payload)) as mocked_ask_ai:
            generate_quiz("Biology", "beginner", 2)

        prompt = mocked_ask_ai.call_args.args[0]
        self.assertIn("Number of questions: 2", prompt)

    def test_valid_json_ai_response_is_parsed_correctly(self) -> None:
        payload = {
            "topic": "Math",
            "difficulty": "beginner",
            "questions": [
                {
                    "question": "What is 2+2?",
                    "options": {"A": "3", "B": "4", "C": "5", "D": "6"},
                    "correct_answer": "B",
                }
            ],
        }
        with patch("backend.quiz.ask_ai", return_value=json.dumps(payload)):
            result = generate_quiz("Math", "beginner", 1)

        self.assertEqual(result, payload)

    def test_correct_number_of_questions_is_required(self) -> None:
        payload = {
            "topic": "Math",
            "difficulty": "beginner",
            "questions": [],
        }
        with patch("backend.quiz.ask_ai", return_value=json.dumps(payload)):
            with self.assertRaisesRegex(ValueError, "requested number of questions"):
                generate_quiz("Math", "beginner", 1)

    def test_each_question_requires_exactly_four_options(self) -> None:
        payload = {
            "topic": "Math",
            "difficulty": "beginner",
            "questions": [
                {
                    "question": "What is 2+2?",
                    "options": {"A": "3", "B": "4", "C": "5"},
                    "correct_answer": "B",
                }
            ],
        }
        with patch("backend.quiz.ask_ai", return_value=json.dumps(payload)):
            with self.assertRaisesRegex(ValueError, "exactly A, B, C, and D"):
                generate_quiz("Math", "beginner", 1)

    def test_invalid_correct_answer_values_are_rejected(self) -> None:
        payload = {
            "topic": "Math",
            "difficulty": "beginner",
            "questions": [
                {
                    "question": "What is 2+2?",
                    "options": {"A": "3", "B": "4", "C": "5", "D": "6"},
                    "correct_answer": "E",
                }
            ],
        }
        with patch("backend.quiz.ask_ai", return_value=json.dumps(payload)):
            with self.assertRaisesRegex(ValueError, "valid correct_answer"):
                generate_quiz("Math", "beginner", 1)

    def test_missing_required_fields_are_rejected(self) -> None:
        payload = {
            "topic": "Math",
            "difficulty": "beginner",
            "questions": [
                {
                    "options": {"A": "3", "B": "4", "C": "5", "D": "6"},
                    "correct_answer": "B",
                }
            ],
        }
        with patch("backend.quiz.ask_ai", return_value=json.dumps(payload)):
            with self.assertRaisesRegex(ValueError, "non-empty question text"):
                generate_quiz("Math", "beginner", 1)

    def test_malformed_json_is_handled(self) -> None:
        with patch("backend.quiz.ask_ai", return_value="{not valid json"):
            with self.assertRaisesRegex(RuntimeError, "malformed quiz JSON"):
                generate_quiz("Math", "beginner", 1)

    def test_empty_topic_is_rejected(self) -> None:
        with patch("backend.quiz.ask_ai") as mocked_ask_ai:
            with self.assertRaisesRegex(ValueError, "Topic cannot be empty"):
                generate_quiz("", "beginner", 1)

        mocked_ask_ai.assert_not_called()

    def test_whitespace_only_topic_is_rejected(self) -> None:
        with patch("backend.quiz.ask_ai") as mocked_ask_ai:
            with self.assertRaisesRegex(ValueError, "Topic cannot be empty"):
                generate_quiz("   ", "beginner", 1)

        mocked_ask_ai.assert_not_called()

    def test_invalid_difficulty_is_rejected(self) -> None:
        with patch("backend.quiz.ask_ai") as mocked_ask_ai:
            with self.assertRaisesRegex(ValueError, "Allowed difficulties: beginner, intermediate, advanced"):
                generate_quiz("Math", "expert", 1)

        mocked_ask_ai.assert_not_called()

    def test_difficulty_normalization_works(self) -> None:
        payload = {
            "topic": "Math",
            "difficulty": "intermediate",
            "questions": [
                {
                    "question": "What is 2+2?",
                    "options": {"A": "3", "B": "4", "C": "5", "D": "6"},
                    "correct_answer": "B",
                }
            ],
        }
        with patch("backend.quiz.ask_ai", return_value=json.dumps(payload)) as mocked_ask_ai:
            generate_quiz("Math", "Intermediate", 1)

        prompt = mocked_ask_ai.call_args.args[0]
        self.assertIn("Difficulty level: intermediate", prompt)

    def test_zero_questions_is_rejected(self) -> None:
        with patch("backend.quiz.ask_ai") as mocked_ask_ai:
            with self.assertRaisesRegex(ValueError, "between 1 and 10"):
                generate_quiz("Math", "beginner", 0)

        mocked_ask_ai.assert_not_called()

    def test_negative_question_count_is_rejected(self) -> None:
        with patch("backend.quiz.ask_ai") as mocked_ask_ai:
            with self.assertRaisesRegex(ValueError, "between 1 and 10"):
                generate_quiz("Math", "beginner", -1)

        mocked_ask_ai.assert_not_called()

    def test_more_than_ten_questions_is_rejected(self) -> None:
        with patch("backend.quiz.ask_ai") as mocked_ask_ai:
            with self.assertRaisesRegex(ValueError, "between 1 and 10"):
                generate_quiz("Math", "beginner", 11)

        mocked_ask_ai.assert_not_called()

    def test_non_integer_question_count_is_rejected(self) -> None:
        with patch("backend.quiz.ask_ai") as mocked_ask_ai:
            with self.assertRaisesRegex(ValueError, "integer between 1 and 10"):
                generate_quiz("Math", "beginner", 2.5)

        mocked_ask_ai.assert_not_called()

    def test_boolean_question_count_is_rejected(self) -> None:
        with patch("backend.quiz.ask_ai") as mocked_ask_ai:
            with self.assertRaisesRegex(ValueError, "integer between 1 and 10"):
                generate_quiz("Math", "beginner", True)

        mocked_ask_ai.assert_not_called()

    def test_ai_api_failure_is_handled_correctly(self) -> None:
        with patch("backend.quiz.ask_ai", side_effect=RuntimeError("OpenAI request failed.")):
            with self.assertRaisesRegex(RuntimeError, "OpenAI request failed"):
                generate_quiz("Math", "beginner", 1)


if __name__ == "__main__":
    unittest.main()
