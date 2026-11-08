"""The one place the app calls Gemini. Every failure is turned into a ModelError so the template can take over."""

from __future__ import annotations

from collections.abc import Callable
from typing import Protocol

import httpx
from google import genai
from google.genai import errors, types

from api.core.settings import Settings
from api.services.brief_writer import ModelCall, ModelError

TEMPERATURE = 0.2
MAX_OUTPUT_TOKENS = 600
ATTEMPTS = 2
THINKING_LEVEL = types.ThinkingLevel.MINIMAL


class Models(Protocol):
    @property
    def generate_content(self) -> Callable[..., types.GenerateContentResponse]: ...


class ContentClient(Protocol):
    """The part of the SDK client the app uses. Tests pass a fake with the same shape."""

    @property
    def models(self) -> Models: ...


def create_client(settings: Settings) -> genai.Client | None:
    """None when no key is set, which means briefs use the template."""
    if not settings.gemini_api_key:
        return None
    options = types.HttpOptions(
        timeout=int(settings.brief_timeout_seconds * 1000),
        retry_options=types.HttpRetryOptions(attempts=ATTEMPTS),
    )
    return genai.Client(api_key=settings.gemini_api_key, http_options=options)


def gemini_call(client: ContentClient, model: str) -> ModelCall:
    # Thinking is kept minimal. With more, the model spent its whole budget thinking and the answer was cut off.
    config = types.GenerateContentConfig(
        temperature=TEMPERATURE,
        max_output_tokens=MAX_OUTPUT_TOKENS,
        thinking_config=types.ThinkingConfig(thinking_level=THINKING_LEVEL),
    )

    def call(prompt: str) -> str:
        try:
            response = client.models.generate_content(model=model, contents=prompt, config=config)
        except (errors.APIError, httpx.HTTPError) as error:
            raise ModelError(f"{type(error).__name__}: {error}") from error
        candidates = response.candidates or []
        finished = bool(candidates) and candidates[0].finish_reason == types.FinishReason.STOP
        if not response.text or not finished:
            raise ModelError("The model returned no text, or its answer was cut off.")
        return response.text

    return call
