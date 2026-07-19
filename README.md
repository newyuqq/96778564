# Telegram Business AI Autoresponder Bot

A Telegram bot that connects to a **Telegram Business** account (Settings →
Business → Chatbots) and can auto-reply to incoming DMs using an AI model,
with an on/off toggle, multi-language menu (EN / UA / RU), and a keep-alive
setup for Render's free tier.

## ⚠️ About "huihui.ai"

huihui.ai is **not an API host** — it's a research group that publishes
open ("abliterated"/uncensored) model *weights* on Hugging Face / Ollama.
There is no `https://huihui.ai/api` you can call. This project runs one of
those models **for free, on your own PC**, via Ollama — see below.

## Running everything on Ubuntu (no Render, no tunnel needed)

If your Ubuntu machine (PC or a server/VPS) can just stay on, this is the
simplest setup: the bot, the auth proxy, and Ollama all run on the same
box and talk to each other over `localhost` — no tunnel, no Render, no
"is my PC on" dependency for a separate cloud service.

### 1. Get the code onto the machine

```bash
# either clone from your own GitHub repo:
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git tg-business-ai-bot
cd tg-business-ai-bot
# or just copy the project folder over with scp/rsync/USB if you're not using git
```

### 2. Run the setup script

```bash
bash deploy/setup_ubuntu.sh
```

This installs Python/venv, your dependencies, installs Ollama, and pulls
`huihui_ai/qwen3-abliterated:4b-v2` (edit the script first if you want a
different model size). It also creates `.env` from `.env.example`.

### 3. Edit `.env`

```bash
nano .env
```

Fill in at least:
- `BOT_TOKEN` — from @BotFather
- `ADMIN_IDS` — your numeric Telegram id (from @userinfobot)
- `PROXY_SECRET` — any long random string
- `AI_API_KEY` — **the same value** as `PROXY_SECRET`

Since everything's local, you can leave `AI_BASE_URL=http://localhost:8000/v1`
as-is (already the default in `config.py`) — no tunnel URL needed.

### 4. Test it manually first

Open two terminals in the project folder (with `source venv/bin/activate` in each):

```bash
# terminal 1
python ollama_proxy.py

# terminal 2
python main.py
```

Message your bot on Telegram to confirm `/start`, `/status` etc. work, and
that a business-connected chat gets AI replies. Ctrl+C both once it's confirmed working.

### 5. Install as systemd services (so it survives reboots/logouts)

Edit `deploy/tgbot.service` and `deploy/ollama-proxy.service` first —
replace `YOUR_LINUX_USERNAME` and the paths with your actual username and
the folder you cloned into. Then:

```bash
sudo cp deploy/tgbot.service deploy/ollama-proxy.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now ollama-proxy.service
sudo systemctl enable --now tgbot.service
```

Check status / logs any time with:

```bash
systemctl status tgbot.service
journalctl -u tgbot.service -f
```

Ollama itself is already installed as a systemd service (`ollama.service`)
by its own installer, so it starts automatically too — you don't need a
unit file for it.

### Updating later

```bash
cd tg-business-ai-bot
git pull                      # if using git
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart tgbot.service ollama-proxy.service
```

## Self-hosting with your own PC, bot on Render (alternative)

The Telegram bot itself runs on Render (24/7, small, doesn't need power).
The AI model runs on your PC, which Render reaches over the internet
through a tunnel. Four pieces:

```
Telegram  →  Render (bot, main.py)  →  tunnel (internet)  →  your PC:
                                                               ollama_proxy.py (checks API key)
                                                               → Ollama (the actual model)
```

### Step 1 — Install Ollama and pull a model

Download Ollama from https://ollama.com, then in a terminal:

```bash
ollama pull huihui_ai/qwen3-abliterated:4b-v2
```

Pick a size that fits your hardware — 4B runs fine on CPU/laptop-class
machines; if you've got a decent GPU you can go bigger (`8b`, `14b`, etc. —
check the tags on https://ollama.com/huihui_ai for what's available).
Larger = smarter but slower and needs more RAM/VRAM.

### Step 2 — Run the auth proxy in front of Ollama

Ollama's API has **no password** — anyone with the URL can use it for
free once it's exposed to the internet. `ollama_proxy.py` (included)
adds a required API-key check in front of it.

```bash
pip install flask requests
set PROXY_SECRET=pick-a-long-random-string      # Windows (cmd)
# export PROXY_SECRET=pick-a-long-random-string  # macOS/Linux
python ollama_proxy.py
```

Leave this running. It listens on `:8000` and forwards authorized
requests to Ollama on `:11434`.

### Step 3 — Expose it to the internet with a tunnel

Easiest free option — **Cloudflare Tunnel** (no account required for a
quick tunnel):

```bash
# https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/
cloudflared tunnel --url http://localhost:8000
```

It prints a public URL like `https://random-words.trycloudflare.com`.
That's your `AI_BASE_URL` (with `/v1` appended). Keep this window open too.

Note: a *quick* tunnel's URL changes every time you restart it — you'd
need to update `AI_BASE_URL` on Render each time. For a stable URL, use
`ngrok` with a free static domain (`ngrok http 8000 --domain=your-name.ngrok-free.app`,
one static domain is free per account) or set up a named Cloudflare Tunnel
if you own a domain.

### Step 4 — Point Render at your PC

In Render's Environment tab, set:
- `AI_BASE_URL` = `https://your-tunnel-url/v1`
- `AI_API_KEY` = the same `PROXY_SECRET` you used in Step 2
- `AI_MODEL` = `huihui_ai/qwen3-abliterated:4b-v2` (or whatever you pulled)

**Important:** your PC, `ollama_proxy.py`, and the tunnel all need to stay
running for the bot to get AI replies — if you turn off your PC, the
Telegram commands (`/start`, `/settings` etc.) still work fine, but
autoresponder replies will fail until it's back online.

### If you'd rather not depend on your PC being on

A paid managed alternative exists — **Featherless.ai** hosts these same
huihui-ai models directly with an OpenAI-compatible API (~$10/mo, no
proxy/tunnel needed): just set `AI_BASE_URL=https://api.featherless.ai/v1`
and `AI_MODEL=huihui-ai/Qwen2.5-72B-Instruct-abliterated`.

The bot's AI client (`ai_client.py`) just talks to whatever OpenAI-compatible
`base_url` you configure — nothing else needs to change either way.

## Features

- `/start`, `/cmds` — basic bot info
- `/settings` — inline-button menu (language, AI toggle, connected name)
- `/setlang en|ua|ru` — switch bot language
- `/setname <name>` — sets the display name used in the away-message (e.g. `@username`)
- `/aimode on|off` — toggle the AI autoresponder without disconnecting
- `/status` — quick health check
- Auto-replies to messages sent to your connected Business account, using
  any OpenAI-compatible AI backend
- **Away-message on first contact**: the first message in a new conversation
  gets a canned "I'm an AI assistant, please ask your full question" template
  instead of an AI reply (see below), unless the sender opens with the quick-question
  trigger word — then it answers right away
- Small Flask keep-alive server so Render's free Web Service doesn't sleep

## How auto-replies work

Telegram's Bot API doesn't expose your online/offline status, so there's no
way to detect "reply only while I'm away" directly. Instead, the bot uses
"first message in a conversation" as the trigger:

1. Someone messages your Business account for the first time (or it's been
   more than `AWAY_COOLDOWN_HOURS` since their last message) → they get the
   away-message template (edit the wording in `translations.py`, key
   `away_message`; the name and trigger word are filled in automatically):

   > ℹ️ I'm not {name}. I'm their AI assistant.
   > Hi! Please write what you want from {name} in one message (follow nohello.net).
   > For a quick question, start your message with:
   > {trigger} your question here
   > ©Personal AI (my bot)

2. If they start their message with the trigger word (`AWAY_TRIGGER_WORD` in
   `.env`, default `Хеллоуу`), the bot skips the template and answers with
   the AI immediately.
3. Any message after the first one in that conversation gets a normal AI
   reply (no trigger word needed) until `AWAY_COOLDOWN_HOURS` passes with no
   activity, at which point the away-message shows again.

Set `/setname` to your actual `@username` so it shows correctly in the template.

## 1. Local setup

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# edit .env: put in BOT_TOKEN, ADMIN_IDS, AI_API_KEY, etc.
python main.py
```

Get a bot token from **@BotFather** on Telegram (`/newbot`).
Get your numeric Telegram user id from **@userinfobot**.

## 2. Connect it to your Business account

In the Telegram app: **Settings → Business → Chatbots** → select your bot →
grant it access to reply to messages. Once connected, the bot will start
receiving `business_message` updates for your business chats.

## 3. Push to GitHub

```bash
git init
git add .
git commit -m "Telegram business AI autoresponder bot"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

`.env` and `data/` are already in `.gitignore` — your token and settings
never get committed. **Never put your real token in `config.py` or commit
a `.env` file.**

## 4. Deploy on Render

1. New → **Web Service** → connect your GitHub repo.
2. Render will read `render.yaml` automatically (Blueprint), or set manually:
   - Build command: `pip install -r requirements.txt`
   - Start command: `python main.py`
3. In the **Environment** tab, set the real values for:
   - `BOT_TOKEN`
   - `ADMIN_IDS`
   - `AI_API_KEY`
   - (optionally override `AI_BASE_URL` / `AI_MODEL`)
4. Deploy. Render assigns a public URL and sets `RENDER_EXTERNAL_URL`
   automatically — the bot uses that for its self-ping.

### Keeping it awake (free tier)

Render free Web Services sleep after ~15 min of no HTTP traffic. This repo
already listens on `/health` and self-pings every 10 minutes, but for a
Telegram bot on **polling** mode, the *only* reliable fix on the free tier
is an external uptime pinger:

1. Go to [UptimeRobot](https://uptimerobot.com) (free account).
2. Add a new **HTTP(s)** monitor pointing at `https://YOUR-APP.onrender.com/health`.
3. Set the check interval to 5 minutes.

That keeps the dyno continuously warm so polling never stalls. (If you'd
rather avoid this entirely, upgrade to a paid Render instance, which never
sleeps — or switch the bot to webhooks, which is a bigger change.)

## File overview

| File | Purpose |
|---|---|
| `main.py` | Bot entrypoint, commands, business message routing |
| `config.py` | Reads all settings from environment variables |
| `translations.py` | EN / UA / RU strings |
| `storage.py` | JSON-file settings storage (language, AI toggle, connections) |
| `ai_client.py` | Calls your configured OpenAI-compatible AI backend |
| `ollama_proxy.py` | Runs on YOUR PC in front of Ollama, adds the API-key check Ollama lacks |
| `keep_alive.py` | Flask health server + self-ping thread |
| `render.yaml` | Render Blueprint config |
| `.env.example` | Template for local environment variables |
| `deploy/setup_ubuntu.sh` | One-shot Ubuntu setup script (deps, venv, Ollama, model pull) |
| `deploy/tgbot.service` | systemd unit to run the bot as an always-on service |
| `deploy/ollama-proxy.service` | systemd unit to run `ollama_proxy.py` as an always-on service |
