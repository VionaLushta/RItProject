"""Focused tests for the Explain Topic backend flow."""

from __future__ import annotations

import unittest
from unittest.mock import patch

from backend.explanation_service import explain_topic


class ExplainTopicTests(unittest.TestCase):
    def test_beginner_topic_generates_beginner_prompt(self) -> None:
        with patch("backend.explanation_service.ask_ai", return_value="Beginner explanation.") as mocked_ask_ai:
            result = explain_topic("Photosynthesis", "beginner")

        self.assertEqual(result, "Beginner explanation.")
        prompt = mocked_ask_ai.call_args.args[0]
        self.assertIn("Difficulty level: beginner", prompt)
        self.assertIn("Use simple language", prompt)

    def test_intermediate_topic_generates_intermediate_prompt(self) -> None:
        with patch("backend.explanation_service.ask_ai", return_value="Intermediate explanation.") as mocked_ask_ai:
            result = explain_topic("Photosynthesis", "intermediate")

        self.assertEqual(result, "Intermediate explanation.")
        prompt = mocked_ask_ai.call_args.args[0]
        self.assertIn("Difficulty level: intermediate", prompt)
        self.assertIn("Assume basic knowledge", prompt)

    def test_advanced_topic_generates_advanced_prompt(self) -> None:
        with patch("backend.explanation_service.ask_ai", return_value="Advanced explanation.") as mocked_ask_ai:
            result = explain_topic("Photosynthesis", "advanced")

        self.assertEqual(result, "Advanced explanation.")
        prompt = mocked_ask_ai.call_args.args[0]
        self.assertIn("Difficulty level: advanced", prompt)
        self.assertIn("Assume strong prior knowledge", prompt)

    def test_topic_is_included_in_prompt(self) -> None:
        with patch("backend.explanation_service.ask_ai", return_value="Explanation.") as mocked_ask_ai:
            explain_topic("Cellular respiration", "beginner")

        prompt = mocked_ask_ai.call_args.args[0]
        self.assertIn("Topic: Cellular respiration", prompt)

    def test_empty_topic_is_rejected(self) -> None:
        with patch("backend.explanation_service.ask_ai") as mocked_ask_ai:
            with self.assertRaisesRegex(ValueError, "Topic cannot be empty"):
                explain_topic("", "beginner")

        mocked_ask_ai.assert_not_called()

    def test_whitespace_only_topic_is_rejected(self) -> None:
        with patch("backend.explanation_service.ask_ai") as mocked_ask_ai:
            with self.assertRaisesRegex(ValueError, "Topic cannot be empty"):
                explain_topic("   ", "beginner")

        mocked_ask_ai.assert_not_called()

    def test_invalid_difficulty_is_rejected(self) -> None:
        with patch("backend.explanation_service.ask_ai") as mocked_ask_ai:
            with self.assertRaisesRegex(ValueError, "Allowed levels: beginner, intermediate, advanced"):
                explain_topic("Photosynthesis", "expert")

        mocked_ask_ai.assert_not_called()

    def test_difficulty_normalization_works(self) -> None:
        with patch("backend.explanation_service.ask_ai", return_value="Beginner explanation.") as mocked_ask_ai:
            explain_topic("Photosynthesis", "Beginner")

        prompt = mocked_ask_ai.call_args.args[0]
        self.assertIn("Difficulty level: beginner", prompt)

    def test_ai_failure_is_handled_correctly(self) -> None:
        with patch("backend.explanation_service.ask_ai", side_effect=RuntimeError("OpenAI request failed.")):
            with self.assertRaisesRegex(RuntimeError, "OpenAI request failed"):
                explain_topic("Photosynthesis", "beginner")

    def test_valid_ai_response_is_returned_to_caller(self) -> None:
        with patch("backend.explanation_service.ask_ai", return_value="This is the explanation.") as mocked_ask_ai:
            result = explain_topic("Photosynthesis", "beginner")

        self.assertEqual(result, "This is the explanation.")
        mocked_ask_ai.assert_called_once()


if __name__ == "__main__":
    unittest.main()
