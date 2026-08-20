"""Prompt templates for CampusMate AI features."""

from __future__ import annotations

QUESTION_ANSWER_PROMPT_TEMPLATE = """You are CampusMate AI, a helpful study assistant.
Answer the student's question clearly and in understandable language.
Focus on helping the student learn.
If the information is uncertain or depends on context, say so instead of pretending it is definitely correct.
Encourage verification of important information when appropriate.

Student question:
{question}
"""


def build_question_answer_prompt(question: str) -> str:
    """Build the prompt used for answering a student's question."""
    return QUESTION_ANSWER_PROMPT_TEMPLATE.format(question=question.strip())
