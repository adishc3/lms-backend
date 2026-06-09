from __future__ import annotations
import httpx
import asyncio
import logging
from urllib.parse import urlencode, urlparse, urlunparse, parse_qs
from app.core.config import settings

logger = logging.getLogger(__name__)

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


def _extract_text_from_parts(parts) -> str:
    if not isinstance(parts, list):
        return ""

    extracted = []
    for item in parts:
        if isinstance(item, str):
            extracted.append(item.strip())
        elif isinstance(item, dict):
            if "text" in item and isinstance(item["text"], str):
                extracted.append(item["text"].strip())
            elif "type" in item and item["type"] == "text" and "text" in item:
                extracted.append(str(item["text"]).strip())
            elif "parts" in item:
                extracted.append(_extract_text_from_parts(item["parts"]))
            elif "content" in item:
                extracted.append(_extract_text_from_parts(item["content"]))
    return "\n".join(part for part in extracted if part)


def _extract_ai_text_response(data: dict) -> str:
    if "choices" in data and data["choices"]:
        message = data["choices"][0].get("message", {})
        if isinstance(message, dict):
            if "content" in message and isinstance(message["content"], str):
                return message["content"].strip()
            if "content" in message:
                return _extract_text_from_parts(message["content"]) or ""

    if "candidates" in data and data["candidates"]:
        candidate_content = data["candidates"][0].get("content")
        if isinstance(candidate_content, dict):
            if "text" in candidate_content and isinstance(candidate_content["text"], str):
                return candidate_content["text"].strip()
            if "parts" in candidate_content:
                return _extract_text_from_parts(candidate_content["parts"])
            if "content" in candidate_content:
                return _extract_text_from_parts(candidate_content["content"])
        if isinstance(candidate_content, list):
            return _extract_text_from_parts(candidate_content)

    if "response" in data and isinstance(data["response"], dict):
        response_content = data["response"].get("content")
        if isinstance(response_content, list):
            result = _extract_text_from_parts(response_content)
            if result:
                return result
        if "text" in data["response"] and isinstance(data["response"]["text"], str):
            return data["response"]["text"].strip()
        if "output_text" in data["response"] and isinstance(data["response"]["output_text"], str):
            return data["response"]["output_text"].strip()

    if "answer" in data and isinstance(data["answer"], str):
        return data["answer"].strip()

    return ""


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
    headers = {"Content-Type": "application/json"}

    if _is_google_provider(url) and settings.AI_API_KEY:
        url = _append_api_key_to_url(url, settings.AI_API_KEY)
    elif settings.AI_API_KEY:
        headers["Authorization"] = f"Bearer {settings.AI_API_KEY}"

    # Retry logic with exponential backoff
    max_retries = 5
    for attempt in range(max_retries):
        try:
            payload = _build_request_payload(prompt, context, url)
            async with httpx.AsyncClient(timeout=settings.AI_TIMEOUT_SECONDS) as client:
                response = await client.post(url, json=payload, headers=headers)
                
                # Check if successful
                if response.status_code == 200:
                    data = response.json()
                    logger.debug("AI raw response: %s", data)
                    result = _extract_ai_text_response(data)
                    if result:
                        return result
                    logger.error("AI provider returned an empty response after parsing: %s", data)
                    raise ValueError(f"AI provider returned an empty response: {data}")

                if response.status_code == 429:
                    try:
                        error_data = response.json()
                        error_msg = error_data.get("error", {}).get("message", response.text)
                    except ValueError:
                        error_msg = response.text
                    logger.error(f"AI provider rate limit error {response.status_code}: {error_msg}")
                    raise ValueError(f"AI provider rate limit exceeded: {error_msg}")
                
                # Handle 503 with retry
                if response.status_code == 503 and attempt < max_retries - 1:
                    delay = (2 ** attempt) * 0.5  # 0.5s, 1s, 2s, 4s, 8s
                    await asyncio.sleep(delay)
                    continue
                
                # Try alternate endpoint for certain errors
                if response.status_code in {404, 501, 503} and _is_google_provider(url):
                    alternate_url = _alternate_google_url(url)
                    if alternate_url != url and attempt < max_retries - 1:
                        url = alternate_url
                        if _is_google_provider(alternate_url) and settings.AI_API_KEY:
                            url = _append_api_key_to_url(alternate_url, settings.AI_API_KEY)
                        delay = (2 ** attempt) * 0.5
                        await asyncio.sleep(delay)
                        continue
                
                # If we get here, the request failed
                content = response.text
                logger.error(f"AI provider error {response.status_code}: {content}")
                raise ValueError(f"AI provider error {response.status_code}: {content}")
                
        except httpx.RequestError as exc:
            logger.error(f"AI request failed (attempt {attempt + 1}/{max_retries}): {exc}")
            if attempt < max_retries - 1:
                delay = (2 ** attempt) * 0.5
                await asyncio.sleep(delay)
                continue
            raise ValueError(f"AI request failed: {exc}")
    
    # If we exhausted retries
    raise ValueError("AI provider unavailable after multiple attempts. Please try again later.")


async def generate_quiz(context: str, question_count: int) -> str:
    prompt = (
        f"Create {question_count} multiple-choice quiz questions based on the lesson below. "
        "For each question, provide four answer options and mark the correct one. "
        "Return the quiz in a clear text format."
    )
    return await query_ai(prompt, context)
