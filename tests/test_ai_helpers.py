from app.core import ai
from app.core.config import settings


def test_build_request_payload_for_google_provider():
    settings.AI_PROVIDER_URL = "https://generativelanguage.googleapis.com/v1beta2/models/gemini-text-1:generateMessage"
    settings.AI_DEFAULT_MODEL = "gemini-text-1"
    settings.AI_TEMPERATURE = 0.5

    payload = ai._build_request_payload("Explain this concept", "Lesson content")

    assert "model" not in payload
    assert payload["temperature"] == 0.5
    assert "messages" in payload
    assert payload["messages"][0]["author"] == "system"
    assert payload["messages"][1]["author"] == "user"
    assert payload["messages"][1]["content"][0]["text"] == "Lesson content\n\nQuestion: Explain this concept"


def test_extract_ai_text_response_from_candidates():
    data = {"candidates": [{"content": [{"type": "text", "text": "This is the answer."}]}]}
    assert ai._extract_ai_text_response(data) == "This is the answer."


def test_append_api_key_to_url():
    url = "https://generativelanguage.googleapis.com/v1beta2/models/gemini-text-1:generateMessage"
    result = ai._append_api_key_to_url(url, "abc123")
    assert "key=abc123" in result


def test_alternate_google_url():
    assert ai._alternate_google_url("https://generativelanguage.googleapis.com/v1beta2/models/gemini-text-1:generateMessage") == "https://generativelanguage.googleapis.com/v1beta2/models/gemini-text-1:generateText"
    assert ai._alternate_google_url("https://generativelanguage.googleapis.com/v1beta2/models/gemini-text-1:generateText") == "https://generativelanguage.googleapis.com/v1beta2/models/gemini-text-1:generateMessage"


def test_build_request_payload_for_google_text_provider():
    settings.AI_PROVIDER_URL = "https://generativelanguage.googleapis.com/v1beta2/models/gemini-text-1:generateText"
    settings.AI_DEFAULT_MODEL = "gemini-text-1"
    settings.AI_TEMPERATURE = 0.5

    payload = ai._build_request_payload("Explain this concept", "Lesson content", settings.AI_PROVIDER_URL)

    assert "model" not in payload
    assert payload["temperature"] == 0.5
    assert payload["prompt"] == {"text": "Lesson content\n\nQuestion: Explain this concept"}
