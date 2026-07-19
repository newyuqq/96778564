"""Simple in-memory translation strings for /setlang en|ua|ru."""

TRANSLATIONS = {
    "en": {
        "welcome": "👋 Welcome back, {name}!",
        "welcome_new": "👋 Welcome, {name}! Use /cmds to see what I can do.",
        "cmds": (
            "📋 *Available commands:*\n\n"
            "👤 *General:*\n"
            "/start\n"
            "/cmds\n"
            "/settings\n"
            "/setlang en|ua|ru\n"
            "/setname <name>\n\n"
            "🤖 *AI:*\n"
            "/aimode on|off\n"
            "/status"
        ),
        "setlang_usage": "Usage: /setlang en|ua|ru",
        "setlang_ok": "✅ Language set: English 🇬🇧",
        "setlang_bad": "❌ Unknown language code. Use en, ua or ru.",
        "aimode_usage": "Usage: /aimode on|off",
        "aimode_on": "🤖 AI autoresponder: ✅ ON",
        "aimode_off": "🤖 AI autoresponder: ❌ OFF",
        "status": (
            "📊 *Status*\n"
            "Language: {lang}\n"
            "AI autoresponder: {ai}\n"
            "Business connection: {conn}"
        ),
        "settings_title": "⚙️ Settings",
        "settings_lang": "🌐 Language: {lang}",
        "settings_ai": "🤖 Autoresponder (AI): {ai}",
        "settings_name": "📛 Name: {name}",
        "settings_close": "❌ Close",
        "not_admin": "⛔ You're not allowed to manage this bot.",
        "no_connection": "This bot isn't connected to a Business account yet. "
                          "Connect it from Telegram Settings → Business → Chatbots.",
        "away_message": (
            "ℹ️ I'm not {name}. I'm their AI assistant.\n"
            "Hi! Please write what you want from {name} in one message "
            "(follow nohello.net).\n"
            "For a quick question, start your message with:\n"
            "{trigger} your question here\n"
            "©Personal AI (my bot)"
        ),
        "setname_usage": "Usage: /setname Your Display Name",
        "setname_ok": "✅ Display name set: {name}",
    },
    "ua": {
        "welcome": "👋 З поверненням, {name}!",
        "welcome_new": "👋 Вітаю, {name}! Введи /cmds, щоб побачити команди.",
        "cmds": (
            "📋 *Доступні команди:*\n\n"
            "👤 *Загальні:*\n"
            "/start\n"
            "/cmds\n"
            "/settings\n"
            "/setlang en|ua|ru\n"
            "/setname <ім'я>\n\n"
            "🤖 *AI:*\n"
            "/aimode on|off\n"
            "/status"
        ),
        "setlang_usage": "Використання: /setlang en|ua|ru",
        "setlang_ok": "✅ Мову встановлено: Українська 🇺🇦",
        "setlang_bad": "❌ Невідомий код мови. Використовуй en, ua або ru.",
        "aimode_usage": "Використання: /aimode on|off",
        "aimode_on": "🤖 AI автовідповідач: ✅ УВІМК",
        "aimode_off": "🤖 AI автовідповідач: ❌ ВИМК",
        "status": (
            "📊 *Статус*\n"
            "Мова: {lang}\n"
            "AI автовідповідач: {ai}\n"
            "Бізнес-підключення: {conn}"
        ),
        "settings_title": "⚙️ Налаштування",
        "settings_lang": "🌐 Мова: {lang}",
        "settings_ai": "🤖 Автовідповідач (AI): {ai}",
        "settings_name": "📛 Ім'я: {name}",
        "settings_close": "❌ Закрити",
        "not_admin": "⛔ Тобі не дозволено керувати цим ботом.",
        "no_connection": "Цей бот ще не підключений до бізнес-акаунту. "
                          "Підключи його в Налаштуваннях Telegram → Бізнес → Чат-боти.",
        "away_message": (
            "ℹ️ Я не {name}. Я їхній AI-асистент.\n"
            "Вітаю! Будь ласка, напишіть, що ви хочете від {name}, в одному "
            "повідомленні (дотримуйтесь nohello.net).\n"
            "Для швидкого питання почніть повідомлення з:\n"
            "{trigger} ваше питання тут\n"
            "©Особистий AI (мій бот)"
        ),
        "setname_usage": "Використання: /setname Твоє ім'я",
        "setname_ok": "✅ Ім'я встановлено: {name}",
    },
    "ru": {
        "welcome": "👋 С возвращением, {name}!",
        "welcome_new": "👋 Привет, {name}! Набери /cmds, чтобы увидеть команды.",
        "cmds": (
            "📋 *Доступные команды:*\n\n"
            "👤 *Общие:*\n"
            "/start\n"
            "/cmds\n"
            "/settings\n"
            "/setlang en|ua|ru\n"
            "/setname <имя>\n\n"
            "🤖 *AI:*\n"
            "/aimode on|off\n"
            "/status"
        ),
        "setlang_usage": "Использование: /setlang en|ua|ru",
        "setlang_ok": "✅ Язык установлен: Русский 🇷🇺",
        "setlang_bad": "❌ Неизвестный код языка. Используй en, ua или ru.",
        "aimode_usage": "Использование: /aimode on|off",
        "aimode_on": "🤖 Автоответчик (AI): ✅ ВКЛ",
        "aimode_off": "🤖 Автоответчик (AI): ❌ ВЫКЛ",
        "status": (
            "📊 *Статус*\n"
            "Язык: {lang}\n"
            "AI автоответчик: {ai}\n"
            "Бизнес-подключение: {conn}"
        ),
        "settings_title": "⚙️ Настройки",
        "settings_lang": "🌐 Язык: {lang}",
        "settings_ai": "🤖 Автоответ (AI): {ai}",
        "settings_name": "📛 Имя: {name}",
        "settings_close": "❌ Закрыть",
        "not_admin": "⛔ Тебе не разрешено управлять этим ботом.",
        "no_connection": "Этот бот ещё не подключен к бизнес-аккаунту. "
                          "Подключи его в Настройках Telegram → Бизнес → Чат-боты.",
        "away_message": (
            "ℹ️ Я не {name}. Я их AI ассистент.\n"
            "Привет! Пожалуйста, напишите что вы хотите от {name} в одном "
            "сообщении (следуйте nohello.net).\n"
            "Для быстрого вопроса начните сообщение с:\n"
            "{trigger} ваш вопрос здесь\n"
            "©АИ личный (мой бот)"
        ),
        "setname_usage": "Использование: /setname Твоё имя",
        "setname_ok": "✅ Имя установлено: {name}",
    },
}

LANG_NAMES = {"en": "English 🇬🇧", "ua": "Українська 🇺🇦", "ru": "Русский 🇷🇺"}


def t(lang: str, key: str, **kwargs) -> str:
    lang = lang if lang in TRANSLATIONS else "en"
    text = TRANSLATIONS[lang].get(key) or TRANSLATIONS["en"][key]
    return text.format(**kwargs) if kwargs else text
