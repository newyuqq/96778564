"""
Thin wrapper around an OpenAI-compatible /chat/completions endpoint.

Works with any provider that speaks that protocol - point config.py's
AI_BASE_URL / AI_API_KEY / AI_MODEL at whichever one is actually serving
the model you want (see the long comment in config.py).
"""
import logging
import httpx
from config import AI_BASE_URL, AI_API_KEY, AI_MODEL, AI_SYSTEM_PROMPT, AI_MAX_TOKENS, AI_TEMPERATURE

log = logging.getLogger(__name__)

_client = httpx.AsyncClient(timeout=60.0)


async def generate_reply(user_message: str, history: list[dict] | None = None) -> str:
    """
    Send the conversation to the configured AI backend and return the
    assistant's reply text. Returns a safe fallback string on any error
    instead of raising, so a single failed API call never crashes the bot.
    """
    messages = [{"role": "system", "content": AI_SYSTEM_PROMPT}]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": user_message})

    payload = {
        "model": AI_MODEL,
        "messages": messages,
        "max_tokens": AI_MAX_TOKENS,
        "temperature": AI_TEMPERATURE,
    }
    headers = {
        "Authorization": f"Bearer {AI_API_KEY}",
        "Content-Type": "application/json",
    }

    url = f"{AI_BASE_URL.rstrip('/')}/chat/completions"
    try:
        resp = await _client.post(url, json=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()
    except Exception:
        log.exception("AI backend call failed")
        return "Sorry, I couldn't generate a reply right now — please try again in a moment."
