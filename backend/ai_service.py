"""OpenAI helper for CampusMate AI."""

from __future__ import annotations

import os
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
    except openai.AuthenticationError:
        raise RuntimeError("OpenAI authentication failed. Check your API key.") from None
    except openai.RateLimitError:
        raise RuntimeError("OpenAI rate limit reached. Please try again later.") from None
    except openai.APITimeoutError:
        raise RuntimeError("OpenAI request timed out. Please try again.") from None
    except openai.APIConnectionError:
        raise RuntimeError("Could not connect to OpenAI. Check your internet connection.") from None
    except openai.APIStatusError as error:
        status = getattr(error, "status_code", None) or getattr(error, "status", None)
        raise RuntimeError(f"OpenAI request failed with status {status}.") from None
    except openai.APIError:
        raise RuntimeError("OpenAI request failed. Please try again.") from None


def main() -> None:
    """Temporary connection test for this ticket."""
    try:
        result = ask_ai("Reply with exactly: CampusMate API works")
        print(result)
    except Exception as exc:
        print(f"OpenAI test failed: {exc}")


if __name__ == "__main__":
    main()
