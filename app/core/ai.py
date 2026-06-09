from __future__ import annotations
import httpx
from urllib.parse import urlencode, urlparse, urlunparse, parse_qs
from app.core.config import settings

SYSTEM_PROMPT = (
    "You are an LMS study assistant. Answer user questions only using the provided lesson context. "
    "If the answer is not contained in the lesson, say that the lesson does not provide enough information."
)


def _is_google_provider(url: str) -> bool:
    return "googleapis.com" in url or "generativelanguage" in url or "gemini" in url.lower()


def _append_api_key_to_url(url: str, api_key: str) -> str:
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    query["key"] = [api_key]
    new_query = urlencode(query, doseq=True)
    return urlunparse(parsed._replace(query=new_query))


def _google_endpoint_type(url: str) -> str:
    if ":generateContent" in url:
        return "content"
    if ":generateText" in url:
        return "text"
    if ":generateMessage" in url:
        return "message"
    return "content" if "flash" in url.lower() else ("text" if "text" in settings.AI_DEFAULT_MODEL.lower() else "message")


def _alternate_google_url(url: str) -> str:
    if ":generateContent" in url:
        return url.replace(":generateContent", ":generateText")
    if ":generateText" in url:
        return url.replace(":generateText", ":generateMessage")
    if ":generateMessage" in url:
        return url.replace(":generateMessage", ":generateContent")
    return url


def _extract_ai_text_response(data: dict) -> str:
    if "choices" in data and data["choices"]:
        message = data["choices"][0].get("message", {})
        return message.get("content", "").strip()

    if "candidates" in data and data["candidates"]:
        candidate_content = data["candidates"][0].get("content")
        if isinstance(candidate_content, dict):
            if "text" in candidate_content:
                return str(candidate_content["text"]).strip()
            return str(candidate_content.get("text", "")).strip()
        if isinstance(candidate_content, list):
            for item in candidate_content:
                if isinstance(item, dict) and item.get("type") == "text" and "text" in item:
                    return str(item["text"]).strip()

    if "response" in data and isinstance(data["response"], dict):
        response_content = data["response"].get("content")
        if isinstance(response_content, list):
            for item in response_content:
                if isinstance(item, dict) and item.get("type") == "text" and "text" in item:
                    return str(item["text"]).strip()
        if "text" in data["response"]:
            return str(data["response"]["text"]).strip()
        if "output_text" in data["response"]:
            return str(data["response"]["output_text"]).strip()

    if "answer" in data:
        return str(data["answer"]).strip()

    return str(data)


def _build_request_payload(prompt: str, context: str, url: str | None = None) -> dict:
    full_text = f"{context}\n\nQuestion: {prompt}"
    url = url or settings.AI_PROVIDER_URL
    if _is_google_provider(url):
        endpoint_type = _google_endpoint_type(url)
        if endpoint_type == "content":
            return {
                "contents": [
                    {"role": "user", "parts": [{"text": full_text}]}
                ],
                "generationConfig": {"temperature": settings.AI_TEMPERATURE},
            }
        elif endpoint_type == "text":
            return {
                "prompt": {"text": full_text},
                "generationConfig": {"temperature": settings.AI_TEMPERATURE},
            }
        else:  # message
            return {
                "temperature": settings.AI_TEMPERATURE,
                "messages": [
                    {
                        "author": "system",
                        "content": [{"type": "text", "text": SYSTEM_PROMPT}],
                    },
                    {
                        "author": "user",
                        "content": [{"type": "text", "text": full_text}],
                    },
                ],
            }

    return {
        "model": settings.AI_DEFAULT_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": full_text},
        ],
        "temperature": settings.AI_TEMPERATURE,
    }


async def query_ai(prompt: str, context: str) -> str:
    if not settings.AI_PROVIDER_URL:
        raise ValueError("AI is not configured. Set AI_PROVIDER_URL.")

    url = settings.AI_PROVIDER_URL
    payload = _build_request_payload(prompt, context, url)
    headers = {"Content-Type": "application/json"}

    if _is_google_provider(url) and settings.AI_API_KEY:
        url = _append_api_key_to_url(url, settings.AI_API_KEY)
    elif settings.AI_API_KEY:
        headers["Authorization"] = f"Bearer {settings.AI_API_KEY}"

    async with httpx.AsyncClient(timeout=settings.AI_TIMEOUT_SECONDS) as client:
        try:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            if _is_google_provider(url) and exc.response is not None and exc.response.status_code in {404, 501, 503}:
                alternate_url = _alternate_google_url(url)
                if alternate_url != url:
                    if _is_google_provider(alternate_url) and settings.AI_API_KEY:
                        alternate_url = _append_api_key_to_url(alternate_url, settings.AI_API_KEY)
                    alternate_payload = _build_request_payload(prompt, context, alternate_url)
                    try:
                        response = await client.post(alternate_url, json=alternate_payload, headers=headers)
                        response.raise_for_status()
                    except httpx.HTTPStatusError:
                        # If alternate also fails with 503, let it through for better error message
                        content = exc.response.text if exc.response is not None else str(exc)
                        raise ValueError(f"AI provider error {exc.response.status_code}: {content}")
                    try:
                        data = response.json()
                    except ValueError:
                        raise ValueError(f"AI provider returned a non-JSON response: {response.text}")
                    return _extract_ai_text_response(data)
            content = exc.response.text if exc.response is not None else str(exc)
            raise ValueError(f"AI provider error {exc.response.status_code}: {content}")
        except httpx.RequestError as exc:
            raise ValueError(f"AI request failed: {exc}")

        try:
            data = response.json()
        except ValueError:
            raise ValueError(f"AI provider returned a non-JSON response: {response.text}")

    return _extract_ai_text_response(data)


async def generate_quiz(context: str, question_count: int) -> str:
    prompt = (
        f"Create {question_count} multiple-choice quiz questions based on the lesson below. "
        "For each question, provide four answer options and mark the correct one. "
        "Return the quiz in a clear text format."
    )
    return await query_ai(prompt, context)
