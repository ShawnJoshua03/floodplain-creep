import httpx
import pytest
from google.genai import errors, types

from api.core.settings import load_settings
from api.services.brief_writer import ModelError
from api.services.gemini_client import create_client, gemini_call


def answer(text: str | None, reason: types.FinishReason) -> types.GenerateContentResponse:
    parts = [types.Part(text=text)] if text else []
    candidate = types.Candidate(content=types.Content(parts=parts), finish_reason=reason)
    return types.GenerateContentResponse(candidates=[candidate])


class FakeModels:
    def __init__(self, outcome: types.GenerateContentResponse | Exception) -> None:
        self.outcome = outcome
        self.model = ""
        self.contents = ""
        self.config: types.GenerateContentConfig | None = None

    def generate_content(
        self, *, model: str, contents: str, config: types.GenerateContentConfig
    ) -> types.GenerateContentResponse:
        self.model, self.contents, self.config = model, contents, config
        if isinstance(self.outcome, Exception):
            raise self.outcome
        return self.outcome


class FakeClient:
    def __init__(self, outcome: types.GenerateContentResponse | Exception) -> None:
        self.models = FakeModels(outcome)


def test_a_finished_answer_is_returned_and_thinking_is_minimal() -> None:
    client = FakeClient(answer("Badda had 14,902 buildings.", types.FinishReason.STOP))
    assert gemini_call(client, "a-model")("prompt") == "Badda had 14,902 buildings."
    assert client.models.model == "a-model"
    assert client.models.contents == "prompt"
    config = client.models.config
    assert config is not None and config.thinking_config is not None
    assert config.thinking_config.thinking_level == types.ThinkingLevel.MINIMAL


def test_an_answer_cut_off_by_the_token_limit_is_an_error() -> None:
    client = FakeClient(answer("Badda had 14,9", types.FinishReason.MAX_TOKENS))
    with pytest.raises(ModelError, match="cut off"):
        gemini_call(client, "m")("prompt")


def test_an_empty_answer_is_an_error() -> None:
    with pytest.raises(ModelError):
        gemini_call(FakeClient(answer(None, types.FinishReason.STOP)), "m")("prompt")


@pytest.mark.parametrize(
    "failure",
    [errors.ServerError(504, {"error": {"message": "late"}}), httpx.ConnectTimeout("slow")],
)
def test_service_and_network_failures_become_model_errors(failure: Exception) -> None:
    with pytest.raises(ModelError):
        gemini_call(FakeClient(failure), "m")("prompt")


def test_no_key_means_no_client(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    assert create_client(load_settings("postgresql://x")) is None


def test_a_key_makes_a_client_without_calling_the_network(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GEMINI_API_KEY", "test-key-not-real")
    assert create_client(load_settings("postgresql://x")) is not None
