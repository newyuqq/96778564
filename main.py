"""
Telegram Business Autoresponder Bot
------------------------------------
- Connects to a Telegram *Business* account (Settings -> Business -> Chatbots)
  and can auto-reply to incoming DMs using an AI backend.
- /aimode on|off toggles the autoresponder without disconnecting the bot.
- /setlang en|ua|ru switches the bot's own interface language.
- Ships with a tiny web server (keep_alive.py) so it can run on Render's
  free Web Service tier without going to sleep.

Fill in your token in config.py / .env (BOT_TOKEN), see README.md.
"""
import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    TypeHandler,
    ContextTypes,
)

import config
import storage
from translations import t, LANG_NAMES
from ai_client import generate_reply
from keep_alive import start_keep_alive

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
log = logging.getLogger("bizbot")


# ------------------------------------------------------------------ helpers
def is_admin(user_id: int) -> bool:
    # If no ADMIN_IDS were configured, fall back to "anyone can configure"
    # (fine for a single-owner personal bot, but set ADMIN_IDS in production).
    if not config.ADMIN_IDS:
        return True
    return user_id in config.ADMIN_IDS


def on_off(lang: str, enabled: bool) -> str:
    return {"en": "ON", "ua": "УВІМК", "ru": "ВКЛ"}[lang] if enabled else \
           {"en": "OFF", "ua": "ВИМК", "ru": "ВЫКЛ"}[lang]


# ------------------------------------------------------------------ commands
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = storage.get_lang()
    name = update.effective_user.first_name or update.effective_user.username or "there"
    await update.message.reply_text(t(lang, "welcome_new", name=name))


async def cmd_cmds(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = storage.get_lang()
    await update.message.reply_text(t(lang, "cmds"), parse_mode=ParseMode.MARKDOWN)


async def cmd_setlang(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = storage.get_lang()
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(t(lang, "not_admin"))
        return
    if not context.args:
        await update.message.reply_text(t(lang, "setlang_usage"))
        return
    new_lang = context.args[0].lower()
    if new_lang not in ("en", "ua", "ru"):
        await update.message.reply_text(t(lang, "setlang_bad"))
        return
    storage.set_lang(new_lang)
    await update.message.reply_text(t(new_lang, "setlang_ok"))


async def cmd_setname(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = storage.get_lang()
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(t(lang, "not_admin"))
        return
    if not context.args:
        await update.message.reply_text(t(lang, "setname_usage"))
        return
    name = " ".join(context.args)
    storage.set_display_name(name)
    await update.message.reply_text(t(lang, "setname_ok", name=name))


async def cmd_aimode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = storage.get_lang()
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(t(lang, "not_admin"))
        return
    if not context.args or context.args[0].lower() not in ("on", "off"):
        await update.message.reply_text(t(lang, "aimode_usage"))
        return
    enabled = context.args[0].lower() == "on"
    storage.set_ai_mode(enabled)
    await update.message.reply_text(t(lang, "aimode_on" if enabled else "aimode_off"))


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = storage.get_lang()
    ai_enabled = storage.get_ai_mode()
    conn = "✅" if storage.has_active_connection() else "❌"
    await update.message.reply_text(
        t(lang, "status", lang=LANG_NAMES[lang], ai=on_off(lang, ai_enabled), conn=conn),
        parse_mode=ParseMode.MARKDOWN,
    )


def _settings_keyboard(lang: str) -> InlineKeyboardMarkup:
    ai_enabled = storage.get_ai_mode()
    name = storage.get_display_name()
    rows = [
        [InlineKeyboardButton(t(lang, "settings_lang", lang=LANG_NAMES[lang]), callback_data="cycle_lang")],
        [InlineKeyboardButton(
            t(lang, "settings_ai", ai=("🟢 " + on_off(lang, True)) if ai_enabled else ("🔴 " + on_off(lang, False))),
            callback_data="toggle_ai",
        )],
        [InlineKeyboardButton(t(lang, "settings_name", name=name), callback_data="noop")],
        [InlineKeyboardButton(t(lang, "settings_close"), callback_data="close")],
    ]
    return InlineKeyboardMarkup(rows)


async def cmd_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = storage.get_lang()
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(t(lang, "not_admin"))
        return
    await update.message.reply_text(t(lang, "settings_title"), reply_markup=_settings_keyboard(lang))


async def on_settings_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    lang = storage.get_lang()

    if not is_admin(query.from_user.id):
        await query.answer(t(lang, "not_admin"), show_alert=True)
        return

    if query.data == "close":
        await query.message.delete()
        await query.answer()
        return

    if query.data == "toggle_ai":
        storage.set_ai_mode(not storage.get_ai_mode())

    elif query.data == "cycle_lang":
        order = ["en", "ua", "ru"]
        lang = order[(order.index(lang) + 1) % len(order)]
        storage.set_lang(lang)

    await query.edit_message_text(t(lang, "settings_title"), reply_markup=_settings_keyboard(lang))
    await query.answer()


# ------------------------------------------------------------- business flow
async def route_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Catches the Business-related update types PTB doesn't expose via
    normal MessageHandler filters and dispatches them by hand."""
    if update.business_connection:
        await on_business_connection(update, context)
    elif update.business_message:
        await on_business_message(update, context)
    # edited/deleted business messages are ignored for now


async def on_business_connection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bc = update.business_connection
    if bc.is_enabled:
        storage.register_business_connection(bc.id, bc.user.id, True)
        log.info("Business connection established: %s (user %s)", bc.id, bc.user.id)
    else:
        storage.remove_business_connection(bc.id)
        log.info("Business connection disabled: %s", bc.id)


async def on_business_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.business_message
    if not msg or not msg.text:
        return

    # Don't reply to the business owner's own messages sent from the linked account.
    data = storage.load()
    conn_info = data["business_connections"].get(msg.business_connection_id)
    if conn_info and msg.from_user and msg.from_user.id == conn_info.get("user_id"):
        return

    if not storage.get_ai_mode():
        return  # autoresponder turned off

    lang = storage.get_lang()
    name = storage.get_display_name()
    trigger = config.AWAY_TRIGGER_WORD
    text = msg.text.strip()
    chat_key = f"{msg.business_connection_id}:{msg.chat_id}"

    has_trigger = text.lower().startswith(trigger.lower())
    question = text[len(trigger):].strip(" :,-—") if has_trigger else text

    # First message in a conversation (and no quick-question trigger used):
    # send the canned away-message instead of an AI reply, and wait for a
    # real follow-up. Bot API has no presence info, so "first message in
    # this conversation" stands in for "owner not available right now".
    if not has_trigger and not storage.was_recently_greeted(chat_key, config.AWAY_COOLDOWN_HOURS):
        storage.mark_greeted(chat_key)
        away_text = t(lang, "away_message", name=name, trigger=trigger)
        await context.bot.send_message(
            chat_id=msg.chat_id,
            text=away_text,
            business_connection_id=msg.business_connection_id,
            reply_to_message_id=msg.message_id,
            disable_web_page_preview=True,
        )
        return

    reply_text = await generate_reply(question)
    storage.mark_greeted(chat_key)  # refresh cooldown so the away-message doesn't repeat mid-conversation

    await context.bot.send_message(
        chat_id=msg.chat_id,
        text=reply_text,
        business_connection_id=msg.business_connection_id,
        reply_to_message_id=msg.message_id,
    )


# ----------------------------------------------------------------------- main
def build_application() -> Application:
    application = Application.builder().token(config.BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", cmd_start))
    application.add_handler(CommandHandler("cmds", cmd_cmds))
    application.add_handler(CommandHandler("settings", cmd_settings))
    application.add_handler(CommandHandler("setlang", cmd_setlang))
    application.add_handler(CommandHandler("setname", cmd_setname))
    application.add_handler(CommandHandler("aimode", cmd_aimode))
    application.add_handler(CommandHandler("status", cmd_status))
    application.add_handler(CallbackQueryHandler(on_settings_button))

    # Handles business_connection / business_message updates (group=1 so it
    # never interferes with the CommandHandlers registered above in group 0).
    application.add_handler(TypeHandler(Update, route_update), group=1)

    return application


def main():
    if config.BOT_TOKEN in ("", "ТОКЕН БОТА СЮДА"):
        raise SystemExit(
            "BOT_TOKEN is not set. Put it in a .env file or the BOT_TOKEN "
            "environment variable (see .env.example)."
        )

    start_keep_alive()  # tiny Flask server, keeps Render free tier awake

    application = build_application()
    log.info("Bot starting (polling)...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
