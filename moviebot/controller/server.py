"""This file contains the flask server."""

from os import environ

import telegram
import yaml
from flask import Flask, request

from moviebot.controller.controller_telegram import ControllerTelegram

app = Flask(__name__)
controller_telegram = ControllerTelegram()
URL = "https://636d944311f9.ngrok.io/"  # Webhook url


def bot_token():
    """Gets bot token from config file."""
    path = "config/bot_token.yaml"
    with open(path, "r") as file:
        config = yaml.load(file, Loader=yaml.Loader)
        BOT_TOKEN = config["BOT_TOKEN"]
        return BOT_TOKEN


telegram_token = bot_token()
bot = telegram.Bot(token=telegram_token)


@app.route("/{}".format(telegram_token), methods=["POST"])
def respond():
    """Receives to Telegram POST request."""
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    text = update.message.text.encode("utf-8").decode()

    if text == "/start":
        controller_telegram.start(update, True)
    elif text == "/restart":
        controller_telegram.start(update, True)
    elif text == "/help":
        controller_telegram.help(update, True)
    elif text == "/exit":
        controller_telegram.exit(update, True)
    else:
        controller_telegram.continue_conv(update, True)
    return "ok"


def set_webhook():
    s = bot.setWebhook("{URL}{HOOK}".format(URL=URL, HOOK=telegram_token))
    if s:
        return "webhook ok"
    else:
        return "webhook failed"


def run(config):
    """Runs execute_agent in ControllerTelegram and starts flask server.

    Args:
        config: agent settings
    """
    controller_telegram.execute_agent(config)
    set_webhook()
    app.run(host="0.0.0.0", port=environ.get("PORT", 5000))
