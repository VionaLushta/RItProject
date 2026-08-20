"""Reusable Summarize Text flow for CampusMate AI."""

from __future__ import annotations

from backend.ai_service import ask_ai
from backend.prompts import SUMMARY_STYLE_NORMALIZATIONS, SUMMARY_STYLES, build_summarization_prompt


def _normalize_style(style: str) -> str:
    if not isinstance(style, str) or not style.strip():
        raise ValueError(
            "Summary style cannot be empty. Choose one of: short, detailed, bullet_points, beginner_friendly."
        )

    candidate = " ".join(style.strip().lower().replace("-", " ").split())
    normalized_style = SUMMARY_STYLE_NORMALIZATIONS.get(candidate)
    if normalized_style is None:
        allowed = ", ".join(SUMMARY_STYLES)
        raise ValueError(f"Unsupported summary style '{style.strip()}'. Valid styles: {allowed}.")

    return normalized_style


def summarize_text(text: str, style: str) -> str:
    """Summarize supplied text using a style-specific study prompt."""
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Text cannot be empty. Please enter text to summarize.")

    normalized_style = _normalize_style(style)
    prompt = build_summarization_prompt(text, normalized_style)
    summary = ask_ai(prompt)

    if not summary.strip():
        raise RuntimeError("CampusMate AI returned an empty summary. Please try again.")

    return summary
