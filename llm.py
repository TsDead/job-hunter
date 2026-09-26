"""Провайдеро-независимый LLM-клиент. По умолчанию — бесплатный Groq (OpenAI-совместимый API).
Сменить провайдера/модель = одна переменная LLM_MODEL в .env."""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

GROQ_KEY = os.getenv("GROQ_API_KEY", "").strip()
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = os.getenv("LLM_MODEL", "openai/gpt-oss-20b").strip()


def available() -> bool:
    return bool(GROQ_KEY)


def chat(messages, max_tokens=700, temperature=0.0):
    """Вернуть (текст_ответа, usage). Бросает исключение при сетевой/HTTP-ошибке."""
    if not GROQ_KEY:
        raise RuntimeError("нет GROQ_API_KEY в .env")
    payload = {
        "model": MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    # gpt-oss — «думающие» модели: без низкого reasoning_effort они тратят весь лимит на размышления
    if "gpt-oss" in MODEL:
        payload["reasoning_effort"] = "low"

    r = requests.post(
        GROQ_URL,
        headers={"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"},
        json=payload, timeout=45,
    )
    r.raise_for_status()
    data = r.json()
    content = data["choices"][0]["message"].get("content", "") or ""
    return content.strip(), data.get("usage", {})
