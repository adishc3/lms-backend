from __future__ import annotations
import httpx
from app.core.config import settings

SYSTEM_PROMPT = (
    "You are an LMS study assistant. Answer user questions only using the provided lesson context. "
    "If the answer is not contained in the lesson, say that the lesson does not provide enough information."
)


async def query_ai(prompt: str, context: str) -> str:
    if not settings.AI_ENABLED or not settings.AI_PROVIDER_URL:
        raise ValueError("AI is not configured. Set AI_ENABLED and AI_PROVIDER_URL.")

    payload = {
        "model": settings.AI_DEFAULT_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"{context}\n\nQuestion: {prompt}"},
        ],
        "temperature": settings.AI_TEMPERATURE,
    }
    headers = {"Content-Type": "application/json"}
    if settings.AI_API_KEY:
        headers["Authorization"] = f"Bearer {settings.AI_API_KEY}"

    async with httpx.AsyncClient(timeout=settings.AI_TIMEOUT_SECONDS) as client:
        response = await client.post(settings.AI_PROVIDER_URL, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()

    if "choices" in data and data["choices"]:
        message = data["choices"][0].get("message", {})
        return message.get("content", "").strip()

    if "answer" in data:
        return str(data["answer"]).strip()

    return str(data)


async def generate_quiz(context: str, question_count: int) -> str:
    prompt = (
        f"Create {question_count} multiple-choice quiz questions based on the lesson below. "
        "For each question, provide four answer options and mark the correct one. "
        "Return the quiz in a clear text format."
    )
    return await query_ai(prompt, context)
