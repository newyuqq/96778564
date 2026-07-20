#!/usr/bin/env bash
# Sets up the bot on a fresh Ubuntu box: system deps, venv, Ollama, model pull.
# Run from inside the cloned repo directory: bash deploy/setup_ubuntu.sh
set -e

echo "== Installing system packages =="
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git curl

echo "== Creating Python virtualenv =="
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

if ! command -v ollama &> /dev/null; then
    echo "== Installing Ollama =="
    curl -fsSL https://ollama.com/install.sh | sh
else
    echo "== Ollama already installed, skipping =="
fi

echo "== Pulling the model (edit this if you want a different size) =="
ollama pull huihui_ai/qwen3-abliterated:4b-v2

if [ ! -f .env ]; then
    cp .env.example .env
    echo "== Created .env from .env.example - EDIT IT NOW before starting the bot =="
fi

echo
echo "Setup done. Next steps:"
echo "1. nano .env   -> fill in BOT_TOKEN, ADMIN_IDS, PROXY_SECRET (and AI_API_KEY = same value)"
echo "2. See README.md 'Running on Ubuntu with systemd' to install it as a service."
