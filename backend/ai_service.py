"""OpenAI helper for CampusMate AI."""

from __future__ import annotations

import os
from collections.abc import Iterator
from pathlib import Path

import openai
from dotenv import load_dotenv
from openai import OpenAI

MODEL_NAME = "gpt-4o-mini"
ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")


def _get_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is missing. Add it to your .env file.")
    return OpenAI(api_key=api_key)


def _translate_openai_error(error: Exception) -> RuntimeError:
    if isinstance(error, openai.AuthenticationError):
        return RuntimeError("OpenAI authentication failed. Check your API key.")
    if isinstance(error, openai.RateLimitError):
        return RuntimeError("OpenAI rate limit reached. Please try again later.")
    if isinstance(error, openai.APITimeoutError):
        return RuntimeError("OpenAI request timed out. Please try again.")
    if isinstance(error, openai.APIConnectionError):
        return RuntimeError("Could not connect to OpenAI. Check your internet connection.")
    if isinstance(error, openai.APIStatusError):
        status = getattr(error, "status_code", None) or getattr(error, "status", None)
        return RuntimeError(f"OpenAI request failed with status {status}.")
    if isinstance(error, openai.APIError):
        return RuntimeError("OpenAI request failed. Please try again.")
    return RuntimeError("CampusMate couldn't complete this request. Please try again.")


def ask_ai(prompt: str) -> str:
    """Send a prompt to OpenAI and return the text response."""
    if not prompt or not prompt.strip():
        raise ValueError("Prompt cannot be empty.")

    client = _get_client()

    try:
        response = client.responses.create(
            model=MODEL_NAME,
            input=prompt.strip(),
        )
        return (response.output_text or "").strip()
    except Exception as error:  # noqa: BLE001
        raise _translate_openai_error(error) from None


def stream_ai(prompt: str) -> Iterator[str]:
    """Stream a prompt to OpenAI and yield answer chunks."""
    if not prompt or not prompt.strip():
        raise ValueError("Prompt cannot be empty.")

    client = _get_client()

    try:
        with client.responses.stream(
            model=MODEL_NAME,
            input=prompt.strip(),
        ) as stream:
            for event in stream:
                if event.type == "response.output_text.delta" and event.delta:
                    yield event.delta
            final_response = stream.get_final_response()
            if not (final_response.output_text or "").strip():
                raise RuntimeError("CampusMate AI returned an empty answer. Please try again.")
    except RuntimeError:
        raise
    except Exception as error:  # noqa: BLE001
        raise _translate_openai_error(error) from None


def main() -> None:
    """Temporary connection test for this ticket."""
    try:
        result = ask_ai("Reply with exactly: CampusMate API works")
        print(result)
    except Exception as exc:
        print(f"OpenAI test failed: {exc}")


if __name__ == "__main__":
    main()
