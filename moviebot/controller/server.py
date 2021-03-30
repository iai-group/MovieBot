from moviebot.controller.controller_messenger import ControllerMessenger
from flask import Flask, request
from os import environ
import yaml

app = Flask(__name__)
VERIFY_TOKEN = "bonobo"
controller = ControllerMessenger()

def run(config):
    controller.execute_agent(config)
    verify_token()
    app.run(host='0.0.0.0', port=environ.get("PORT", 5000))
    
def verify_token():
    path = 'config/bot_token.yaml'
    with open(path, 'r') as file:
        config = yaml.load(file, Loader=yaml.Loader)
        VERIFY_TOKEN = config['MESSENGER_VERIFY_TOKEN']
        print("---------------> ", config['MESSENGER_VERIFY_TOKEN'])

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
        event = output['entry'][0]['messaging'][0]
        user_id = event['sender']['id']
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

