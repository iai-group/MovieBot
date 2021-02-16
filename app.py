from flask import Flask, request
#import requests
from os import environ
import tokens
from moviebot.controller.controller_messenger import ControllerMessenger
import run_bot

print("-----------------__TEST__----------------------------")
app = Flask(__name__)
VERIFY_TOKEN = tokens.VERIFY_TOKEN
controller = ControllerMessenger()
controller.execute_agent(run_bot.get_config())

@app.route('/', methods=['GET', 'POST'])
def receive_message():
    if request.method == 'GET':
        token_sent = request.args.get("hub.verify_token")
        return verify_fb_token(token_sent)

    else:
        output = request.get_json()
        print(output)
        recipient_id = get_id(output)
        payload = get_message(output)
        print(controller.action(payload, recipient_id))
        return "Message Processed"


def get_message(output):
    for event in output['entry']:
        messaging = event['messaging']
        for message in messaging:
            if message.get('message'):
                if message['message'].get('text'): 
                    m = message['message']['text']
                    return m
            if message.get('postback'):
                return message['postback']['payload']

def get_id(output):
    for event in output['entry']:
        messaging = event['messaging']
        for message in messaging:
            if message.get('message') or message.get('postback'):
                recipient_id = message['sender']['id']
                return recipient_id

def verify_fb_token(token_sent):
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Invalid verification token'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=environ.get("PORT", 5000))