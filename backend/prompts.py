"""Prompt templates for CampusMate AI features."""

from __future__ import annotations

EXPLANATION_LEVELS = ("beginner", "intermediate", "advanced")
SUMMARY_STYLES = ("short", "detailed", "bullet_points", "beginner_friendly")

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


EXPLANATION_PROMPT_TEMPLATE = """You are CampusMate AI, a helpful study assistant.
Your task is to explain the topic below at the selected difficulty level.
Topic: {topic}
Difficulty level: {level}

Explanation style for this level:
{style}

Output expectations:
- Help the student learn, not just memorize.
- Keep the explanation focused and well structured.
- Use the tone and vocabulary appropriate for the selected level.
- Include an example when requested by the level guidance.
- If a detail is uncertain or depends on context, say so clearly.
"""

EXPLANATION_LEVEL_STYLES = {
    "beginner": (
        "Use simple language, avoid unnecessary technical terms, define important terms, "
        "and include one simple example suitable for a first-time learner."
    ),
    "intermediate": (
        "Assume basic knowledge, use appropriate technical terminology, explain the concept "
        "in more depth, include one practical example, and mention key relationships or mechanisms where relevant."
    ),
    "advanced": (
        "Assume strong prior knowledge, use accurate technical terminology, discuss deeper mechanisms, "
        "trade-offs, and edge cases where relevant, and include a more technical example where appropriate."
    ),
}


def build_explanation_prompt(topic: str, level: str) -> str:
    """Build the prompt used for explaining a topic at a chosen difficulty."""
    normalized_level = level.strip().lower()
    style = EXPLANATION_LEVEL_STYLES[normalized_level]
    return EXPLANATION_PROMPT_TEMPLATE.format(
        topic=topic.strip(),
        level=normalized_level,
        style=style,
    )


SUMMARIZATION_PROMPT_TEMPLATE = """You are CampusMate AI, a helpful study assistant.
Your task is to summarize the supplied text for a student.
Selected summary style: {style}

Style-specific instructions:
{instructions}

Output expectations:
- Preserve the main ideas and important details from the original text.
- Do not invent information that does not appear in the supplied text.
- Keep the summary aligned with the selected style.
- Present the summary clearly and in a student-friendly way.

Original text:
{text}
"""

SUMMARIZATION_STYLE_INSTRUCTIONS = {
    "short": (
        "Produce a concise summary with only the most important ideas and avoid unnecessary detail."
    ),
    "detailed": (
        "Produce a more complete summary covering the main idea, important supporting points, "
        "and relevant details, while still being shorter than the original text."
    ),
    "bullet_points": (
        "Return the important information as clear, organized bullet points and avoid long paragraphs."
    ),
    "beginner_friendly": (
        "Rewrite the important ideas using simple language, short explanations, and minimal technical terminology. "
        "If an important technical term must remain, explain it briefly."
    ),
}

SUMMARY_STYLE_NORMALIZATIONS = {
    "short": "short",
    "detailed": "detailed",
    "bullet points": "bullet_points",
    "bullet_points": "bullet_points",
    "beginner friendly": "beginner_friendly",
    "beginner_friendly": "beginner_friendly",
}


def build_summarization_prompt(text: str, style: str) -> str:
    """Build the prompt used for summarizing text at a chosen style."""
    normalized_style = style.strip().lower()
    instructions = SUMMARIZATION_STYLE_INSTRUCTIONS[normalized_style]
    return SUMMARIZATION_PROMPT_TEMPLATE.format(
        text=text.strip(),
        style=normalized_style,
        instructions=instructions,
    )
