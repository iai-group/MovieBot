"""This file contains the flask server."""

from moviebot.controller.controller_messenger import ControllerMessenger
from moviebot.controller.controller_telegram import ControllerTelegram
from flask import Flask, request
from os import environ
import yaml
import telegram

app = Flask(__name__)
controller_messenger = ControllerMessenger()
controller_telegram = ControllerTelegram()

def bot_token():
    """Gets bot token from config file."""
    path = 'config/bot_token.yaml'
    with open(path, 'r') as file:
        config = yaml.load(file, Loader=yaml.Loader)
        BOT_TOKEN = config['BOT_TOKEN']
        return BOT_TOKEN

telegram_token = bot_token()
bot = telegram.Bot(token=telegram_token)

@app.route('/{}'.format(telegram_token), methods=['POST'])
def respond():
    """Receives to Telegram POST request"""
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    text = update.message.text.encode('utf-8').decode()

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
    return 'ok'

def set_webhook(webhook_url):
    webook = bot.setWebhook('{URL}{HOOK}'.format(URL=webhook_url, HOOK=telegram_token))
    if webook:
        return "webhook ok"
    else:
        return "webhook failed"

def run(config, webhook_url):
    """Runs execute_agent in ControllerMessenger and starts flask server.

    Args:
        config: agent settings
        
    """
    controller_telegram.execute_agent(config)
    controller_messenger.execute_agent(config)
    # Messenger verify token
    verify_token()
    set_webhook(webhook_url)
    app.run(host='0.0.0.0', port=environ.get("PORT", 5000))
    
def verify_token():
    """Gets verify token from config file."""
    path = 'config/bot_token.yaml'
    with open(path, 'r') as file:
        config = yaml.load(file, Loader=yaml.Loader)
        VERIFY_TOKEN = config['MESSENGER_VERIFY_TOKEN']
        return VERIFY_TOKEN

@app.route('/', methods=['GET', 'POST'])
def receive_message():
    """Receives messenger POST requests"""
    if request.method == 'GET':
        token_sent = request.args.get("hub.verify_token")
        return verify_fb_token(token_sent)
    else:  
        output = request.get_json()
        action(output)
        return "Message Processed"

def verify_fb_token(token_sent):
    if token_sent == verify_token():
        return request.args.get("hub.challenge")
    return 'Invalid verification token'

def action(output):
    """Gets user id and payload from output and runs get_message in the controller.

    Args: 
        output: output from request

    """
    event = output['entry'][0]['messaging'][0]
    user_id = event['sender']['id']
    controller_messenger.initialize(user_id)
    payload = get_message(output)
    print(payload)
    if payload is not None:
        if controller_messenger.run_method(user_id, payload):
            controller_messenger.send_message(user_id, payload)

def get_message(output):
    """Gets payload from output.
    Args:
        output: output from request

    Returns:
        string with payload

    """
    for event in output['entry']:
        for message in event['messaging']:
            if message.get('message'):
                if message['message'].get('quick_reply'):
                    return message['message']['quick_reply']['payload']
                if message['message'].get('text'): 
                    return message['message']['text']
            if message.get('postback'):
                return message['postback']['payload']

