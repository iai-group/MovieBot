from moviebot.controller.controller_messenger import ControllerMessenger
from flask import Flask, request
from os import environ

app = Flask(__name__)
VERIFY_TOKEN = 'bonobo'
controller = ControllerMessenger()

def run(config):
    controller.execute_agent(config)
    app.run(host='0.0.0.0', port=environ.get("PORT", 5000))

@app.route('/', methods=['GET', 'POST'])
def receive_message():
    if request.method == 'GET':
        token_sent = request.args.get("hub.verify_token")
        return verify_fb_token(token_sent)
    else:  
        output = request.get_json()
        print(output)
        action(output)
        return "Message Processed"

def verify_fb_token(token_sent):
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Invalid verification token'

def action(output):
        user_id = get_id(output)
        controller.initialize(user_id)
        payload = get_message(output)
        print(payload)
        if payload is not None:
            if controller.run_method(user_id, payload):
                controller.send_message(user_id, payload)

def get_message(output):
    for event in output['entry']:
        for message in event['messaging']:
            if message.get('message'):
                if message['message'].get('quick_reply'):
                    return message['message']['quick_reply']['payload']
                if message['message'].get('text'): 
                    return message['message']['text']
            if message.get('postback'):
                return message['postback']['payload']

def get_id(output):
    for event in output['entry']:
        messaging = event['messaging']
        for message in event['messaging']:
            if message.get('message') or message.get('postback'):
                recipient_id = message['sender']['id']
                return recipient_id