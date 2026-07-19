"""
Configuration for the Telegram Business Autoresponder Bot.

All values are read from environment variables so nothing sensitive
lives in the source code (safe to push to GitHub / GitLab / etc).

For local testing you can create a `.env` file (see .env.example)
and it will be loaded automatically via python-dotenv.
"""
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


# --- Telegram ---------------------------------------------------------
BOT_TOKEN = os.getenv("BOT_TOKEN", "ТОКЕН БОТА СЮДА")

# Only these Telegram user IDs may use /settings, /aimode, /setlang etc.
# Comma-separated list of numeric Telegram user IDs, e.g. "111111,222222"
# Leave empty to allow the bot owner only (recommended: fill this in).
_admin_raw = os.getenv("ADMIN_IDS", "")
ADMIN_IDS = {int(x) for x in _admin_raw.split(",") if x.strip().isdigit()}

# --- AI backend (OpenAI-compatible endpoint) ---------------------------
# huihui.ai itself does not run a hosted API - it only publishes model
# weights ("abliterated" builds) that you run yourself via Ollama.
#
# Default setup here: Ollama running on YOUR PC, pulled model e.g.
#   ollama pull huihui_ai/qwen3-abliterated:4b-v2
# fronted by ollama_proxy.py (adds the API-key check Ollama itself lacks)
# and exposed to the internet via a tunnel (cloudflared / ngrok), since
# the Telegram bot runs on Render and needs to reach your PC over HTTPS.
# See README.md "Self-hosting with your own PC" for the full walkthrough.
#
#   AI_BASE_URL = https://your-tunnel-url.trycloudflare.com/v1
#   AI_API_KEY  = the PROXY_SECRET you set in ollama_proxy.py
#   AI_MODEL    = huihui_ai/qwen3-abliterated:4b-v2
#
# (If you ever want a paid managed option instead, Featherless.ai hosts
# these models directly with the same OpenAI-compatible shape - just
# swap AI_BASE_URL to https://api.featherless.ai/v1.)
AI_BASE_URL = os.getenv("AI_BASE_URL", "http://localhost:8000/v1")
AI_API_KEY = os.getenv("AI_API_KEY", "СЮДА_СВОЙ_СЕКРЕТНЫЙ_КЛЮЧ")
AI_MODEL = os.getenv("AI_MODEL", "huihui_ai/qwen3-abliterated:4b-v2")
AI_SYSTEM_PROMPT = os.getenv(
    "AI_SYSTEM_PROMPT",
    "You are a helpful, friendly assistant answering Telegram Business messages "
    "on behalf of the account owner. Keep replies concise and natural.",
)
AI_MAX_TOKENS = int(os.getenv("AI_MAX_TOKENS", "500"))
AI_TEMPERATURE = float(os.getenv("AI_TEMPERATURE", "0.7"))

# --- Storage -------------------------------------------------------------
DATA_FILE = os.getenv("DATA_FILE", "data/settings.json")

# --- Keep-alive web server (for Render free tier) -------------------------
PORT = int(os.getenv("PORT", "10000"))
# Render sets this automatically once the service is deployed as a Web Service
RENDER_EXTERNAL_URL = os.getenv("RENDER_EXTERNAL_URL", "")

# --- Away-message (first-contact template) --------------------------------
# Sent once per conversation (per AWAY_COOLDOWN_HOURS) instead of an AI
# reply, unless the sender's message starts with AWAY_TRIGGER_WORD - then
# it skips straight to an AI answer. Telegram's Bot API doesn't expose the
# owner's online/offline status, so this fires on "first message in a
# conversation" rather than true presence.
AWAY_TRIGGER_WORD = os.getenv("AWAY_TRIGGER_WORD", "Хеллоуу")
AWAY_COOLDOWN_HOURS = float(os.getenv("AWAY_COOLDOWN_HOURS", "6"))

# --- Default language ------------------------------------------------------
DEFAULT_LANG = os.getenv("DEFAULT_LANG", "en")
