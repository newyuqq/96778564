"""
Very small JSON-file storage layer.

Keeps per-admin settings (language, ai_mode, display name) and, for each
connected Telegram Business account, the business_connection_id so we
know which chats to auto-reply in.

Good enough for a single-owner bot. If you need multiple independent
business connections at real scale, swap this for SQLite/Postgres -
the get_settings/save() interface below is the only thing you'd change.
"""
import json
import os
import threading
import time
from config import DATA_FILE, DEFAULT_LANG

_lock = threading.Lock()

_DEFAULTS = {
    "lang": DEFAULT_LANG,
    "ai_mode": True,
    "display_name": "@username",
    "business_connections": {},  # business_connection_id -> {"user_id": int, "is_enabled": bool}
    "greeted_chats": {},  # "connectionId:chatId" -> unix timestamp of last away-message sent
}


def _ensure_file():
    os.makedirs(os.path.dirname(DATA_FILE) or ".", exist_ok=True)
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(_DEFAULTS, f, ensure_ascii=False, indent=2)


def load() -> dict:
    _ensure_file()
    with _lock:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    # backfill any missing keys (e.g. after upgrading the bot)
    changed = False
    for k, v in _DEFAULTS.items():
        if k not in data:
            data[k] = v
            changed = True
    if changed:
        save(data)
    return data


def save(data: dict) -> None:
    with _lock:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


def get_lang() -> str:
    return load().get("lang", DEFAULT_LANG)


def set_lang(lang: str) -> None:
    data = load()
    data["lang"] = lang
    save(data)


def get_ai_mode() -> bool:
    return load().get("ai_mode", True)


def set_ai_mode(enabled: bool) -> None:
    data = load()
    data["ai_mode"] = enabled
    save(data)


def get_display_name() -> str:
    return load().get("display_name", "@username")


def set_display_name(name: str) -> None:
    data = load()
    data["display_name"] = name
    save(data)


def was_recently_greeted(chat_key: str, cooldown_hours: float) -> bool:
    """chat_key should uniquely identify the conversation, e.g. f'{connection_id}:{chat_id}'."""
    data = load()
    ts = data.get("greeted_chats", {}).get(chat_key)
    if ts is None:
        return False
    return (time.time() - ts) < cooldown_hours * 3600


def mark_greeted(chat_key: str) -> None:
    data = load()
    data.setdefault("greeted_chats", {})[chat_key] = time.time()
    save(data)


def register_business_connection(connection_id: str, user_id: int, is_enabled: bool) -> None:
    data = load()
    data["business_connections"][connection_id] = {
        "user_id": user_id,
        "is_enabled": is_enabled,
    }
    save(data)


def remove_business_connection(connection_id: str) -> None:
    data = load()
    data["business_connections"].pop(connection_id, None)
    save(data)


def has_active_connection() -> bool:
    data = load()
    return any(c.get("is_enabled") for c in data["business_connections"].values())
