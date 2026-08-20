"""Reusable Explain Topic flow for CampusMate AI."""

from __future__ import annotations

from backend.ai_service import ask_ai
from backend.prompts import EXPLANATION_LEVELS, build_explanation_prompt


def _normalize_level(level: str) -> str:
    if not isinstance(level, str) or not level.strip():
        raise ValueError(
            "Difficulty level cannot be empty. Choose one of: beginner, intermediate, advanced."
        )

    normalized_level = level.strip().lower()
    if normalized_level not in EXPLANATION_LEVELS:
        allowed = ", ".join(EXPLANATION_LEVELS)
        raise ValueError(f"Unsupported difficulty level '{level.strip()}'. Allowed levels: {allowed}.")

    return normalized_level


def explain_topic(topic: str, level: str) -> str:
    """Explain a topic using a difficulty-specific study prompt."""
    if not isinstance(topic, str) or not topic.strip():
        raise ValueError("Topic cannot be empty. Please enter a topic to explain.")

    normalized_level = _normalize_level(level)
    prompt = build_explanation_prompt(topic, normalized_level)
    explanation = ask_ai(prompt)

    if not explanation.strip():
        raise RuntimeError("CampusMate AI returned an empty explanation. Please try again.")

    return explanation
