"""Focused tests for the Summarize Text backend flow."""

from __future__ import annotations

import unittest
from unittest.mock import patch

from backend.summarization_service import summarize_text


class SummarizationServiceTests(unittest.TestCase):
    def test_short_style_works(self) -> None:
        with patch("backend.summarization_service.ask_ai", return_value="Short summary.") as mocked_ask_ai:
            result = summarize_text("A long text about biology.", "short")

        self.assertEqual(result, "Short summary.")
        prompt = mocked_ask_ai.call_args.args[0]
        self.assertIn("Selected summary style: short", prompt)
        self.assertIn("Produce a concise summary", prompt)

    def test_detailed_style_works(self) -> None:
        with patch("backend.summarization_service.ask_ai", return_value="Detailed summary.") as mocked_ask_ai:
            result = summarize_text("A long text about biology.", "detailed")

        self.assertEqual(result, "Detailed summary.")
        prompt = mocked_ask_ai.call_args.args[0]
        self.assertIn("Selected summary style: detailed", prompt)
        self.assertIn("main idea", prompt)

    def test_bullet_points_style_works(self) -> None:
        with patch("backend.summarization_service.ask_ai", return_value="- Point one\n- Point two") as mocked_ask_ai:
            result = summarize_text("A long text about biology.", "bullet_points")

        self.assertEqual(result, "- Point one\n- Point two")
        prompt = mocked_ask_ai.call_args.args[0]
        self.assertIn("Selected summary style: bullet_points", prompt)
        self.assertIn("bullet points", prompt)

    def test_beginner_friendly_style_works(self) -> None:
        with patch("backend.summarization_service.ask_ai", return_value="Simple summary.") as mocked_ask_ai:
            result = summarize_text("A long text about biology.", "beginner_friendly")

        self.assertEqual(result, "Simple summary.")
        prompt = mocked_ask_ai.call_args.args[0]
        self.assertIn("Selected summary style: beginner_friendly", prompt)
        self.assertIn("simple language", prompt)

    def test_original_text_is_included_in_the_prompt(self) -> None:
        with patch("backend.summarization_service.ask_ai", return_value="Summary.") as mocked_ask_ai:
            summarize_text("Photosynthesis happens in plants.", "short")

        prompt = mocked_ask_ai.call_args.args[0]
        self.assertIn("Original text:", prompt)
        self.assertIn("Photosynthesis happens in plants.", prompt)

    def test_each_style_has_meaningfully_different_prompt_instructions(self) -> None:
        prompts = {}

        def capture_prompt(prompt: str) -> str:
            prompts[capture_prompt.current_style] = prompt
            return "Summary."

        with patch("backend.summarization_service.ask_ai", side_effect=capture_prompt):
            for style in ("short", "detailed", "bullet_points", "beginner_friendly"):
                capture_prompt.current_style = style
                summarize_text("A long text about biology.", style)

        self.assertIn("Produce a concise summary", prompts["short"])
        self.assertIn("main idea", prompts["detailed"])
        self.assertIn("bullet points", prompts["bullet_points"])
        self.assertIn("simple language", prompts["beginner_friendly"])

    def test_empty_text_is_rejected(self) -> None:
        with patch("backend.summarization_service.ask_ai") as mocked_ask_ai:
            with self.assertRaisesRegex(ValueError, "Text cannot be empty"):
                summarize_text("", "short")

        mocked_ask_ai.assert_not_called()

    def test_whitespace_only_text_is_rejected(self) -> None:
        with patch("backend.summarization_service.ask_ai") as mocked_ask_ai:
            with self.assertRaisesRegex(ValueError, "Text cannot be empty"):
                summarize_text("   ", "short")

        mocked_ask_ai.assert_not_called()

    def test_empty_style_is_rejected(self) -> None:
        with patch("backend.summarization_service.ask_ai") as mocked_ask_ai:
            with self.assertRaisesRegex(ValueError, "Summary style cannot be empty"):
                summarize_text("A long text about biology.", "")

        mocked_ask_ai.assert_not_called()

    def test_unsupported_style_is_rejected(self) -> None:
        with patch("backend.summarization_service.ask_ai") as mocked_ask_ai:
            with self.assertRaisesRegex(ValueError, "Valid styles: short, detailed, bullet_points, beginner_friendly"):
                summarize_text("A long text about biology.", "expert")

        mocked_ask_ai.assert_not_called()

    def test_user_friendly_style_normalization_works(self) -> None:
        with patch("backend.summarization_service.ask_ai", return_value="Summary.") as mocked_ask_ai:
            result = summarize_text("A long text about biology.", "Bullet Points")

        self.assertEqual(result, "Summary.")
        prompt = mocked_ask_ai.call_args.args[0]
        self.assertIn("Selected summary style: bullet_points", prompt)

    def test_valid_ai_response_is_returned(self) -> None:
        with patch("backend.summarization_service.ask_ai", return_value="Final summary.") as mocked_ask_ai:
            result = summarize_text("A long text about biology.", "short")

        self.assertEqual(result, "Final summary.")
        mocked_ask_ai.assert_called_once()

    def test_ai_failure_is_handled_correctly(self) -> None:
        with patch("backend.summarization_service.ask_ai", side_effect=RuntimeError("OpenAI request failed.")):
            with self.assertRaisesRegex(RuntimeError, "OpenAI request failed"):
                summarize_text("A long text about biology.", "short")


if __name__ == "__main__":
    unittest.main()
