"""
Tiny auth proxy for a local Ollama server.

Ollama's OpenAI-compatible endpoint (http://localhost:11434/v1) doesn't
check any API key - anyone who finds the URL can use it for free. Since
you're about to expose your PC to the internet (via a tunnel) so Render
can reach it, this proxy sits in front of Ollama and only forwards
requests that include the correct Bearer token.

Run this INSTEAD of pointing your tunnel straight at 11434:

    python ollama_proxy.py

Then point your tunnel (cloudflared / ngrok) at this proxy's port
(default 8000), not at Ollama's port (11434) directly.

Set a strong random PROXY_SECRET below or via env var - this is the value
you'll put in AI_API_KEY in Render.
"""
import os
from flask import Flask, request, Response
import requests

PROXY_PORT = int(os.getenv("PROXY_PORT", "8000"))
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
PROXY_SECRET = os.getenv("PROXY_SECRET", "СЮДА_СВОЙ_СЕКРЕТНЫЙ_КЛЮЧ")

app = Flask(__name__)


@app.route("/v1/<path:subpath>", methods=["POST", "GET"])
def proxy(subpath):
    auth = request.headers.get("Authorization", "")
    if auth != f"Bearer {PROXY_SECRET}":
        return {"error": "unauthorized"}, 401

    upstream_url = f"{OLLAMA_URL}/v1/{subpath}"
    resp = requests.request(
        method=request.method,
        url=upstream_url,
        json=request.get_json(silent=True),
        timeout=120,
    )
    return Response(resp.content, status=resp.status_code, content_type=resp.headers.get("Content-Type"))


@app.route("/health")
def health():
    return {"status": "ok"}, 200


if __name__ == "__main__":
    if PROXY_SECRET == "СЮДА_СВОЙ_СЕКРЕТНЫЙ_КЛЮЧ":
        print("⚠️  Set a real PROXY_SECRET (env var) before exposing this publicly!")
    print(f"Auth proxy listening on :{PROXY_PORT}, forwarding to {OLLAMA_URL}")
    app.run(host="0.0.0.0", port=PROXY_PORT)
