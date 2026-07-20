"""
Keeps the Render free-tier Web Service from spinning down.

Render's free Web Services sleep after ~15 minutes with no incoming HTTP
traffic. Two things fix that together:

1. This module runs a tiny Flask server on config.PORT and answers "/" and
   "/health" with 200 OK - this is REQUIRED anyway, because Render only
   treats a service as a healthy "Web Service" if something is listening
   on the assigned port.
2. A background thread pings that same URL every few minutes. That alone
   doesn't help while the dyno is fully asleep (it can't ping itself if
   it's not running) - the real fix is an external uptime pinger such as
   UptimeRobot (https://uptimerobot.com, free) hitting your Render URL
   every 5 minutes. The self-ping here just adds a second line of defense
   and gives you a live log line to confirm the service is up.
"""
import logging
import threading
import time

from flask import Flask
import requests

import config

log = logging.getLogger("keep_alive")
app = Flask(__name__)


@app.route("/")
def index():
    return "Bot is alive.", 200


@app.route("/health")
def health():
    return {"status": "ok"}, 200


def _run_flask():
    app.run(host="0.0.0.0", port=config.PORT)


def _self_ping_loop():
    if not config.RENDER_EXTERNAL_URL:
        log.info("RENDER_EXTERNAL_URL not set - skipping self-ping loop "
                  "(set up an external pinger like UptimeRobot instead).")
        return
    url = config.RENDER_EXTERNAL_URL.rstrip("/") + "/health"
    while True:
        time.sleep(600)  # every 10 minutes
        try:
            requests.get(url, timeout=10)
            log.info("Self-ping OK: %s", url)
        except Exception as e:
            log.warning("Self-ping failed: %s", e)


def start_keep_alive():
    threading.Thread(target=_run_flask, daemon=True).start()
    threading.Thread(target=_self_ping_loop, daemon=True).start()
    log.info("Keep-alive web server started on port %s", config.PORT)
