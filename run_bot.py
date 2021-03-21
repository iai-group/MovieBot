from flask import Flask, request
#import requests
from os import environ

import run_bot
import os
import sys
import yaml

from moviebot.controller.controller_messenger import ControllerMessenger
from moviebot.controller.controller_telegram import ControllerTelegram
from moviebot.controller.controller_terminal import ControllerTerminal


def _validate_file(file_name, file_type):
    """Checks if the file is valid and is present

    Args:
      file_name: name/path of the file provided
      file_type: the type/extension of the file

    Returns:
      error and details

    """
    if isinstance(file_name, str):
        if os.path.isfile(file_name):
            details = file_name.split('.')
            if len(details) > 1:
                if details[-1] == file_type:
                    return 'NoError'
                else:
                    return 'ValueErrorType:{}'.format(details[-1])
            else:
                return 'ValueErrorType:{}'.format(details[-1])
        else:
            return 'FileNotFoundError'
    else:
        return 'ValueError'


def arg_parse(args=None):
    """Parses the arguments in the configuration file

    Args:
      args: configuration file for the dialogue (Default value = None)

    Returns:
      a dictionary containing the settings in the configuration file and a
      boolean variable identifying if the conversation is in Telegram.

    """
    argv = args if args else sys.argv
    cfg_parser = None

    if len(argv) < 3:
        print('WARNING: Configuration file is not provided.')
        config_file = r'config/moviebot_config.yaml'
        print(f'Default configuration file selected is \'{config_file}\'')
    else:
        config_file = argv[2]
    file_val = _validate_file(config_file, 'yaml')
    if file_val == 'NoError':
        with open(config_file, 'r') as file:
            cfg_parser = yaml.load(file, Loader=yaml.Loader)
    elif file_val == 'ValueError':
        raise ValueError('Unacceptable type of configuration file name')
    elif file_val == 'FileNotFoundError':
        raise FileNotFoundError(
            'Configuration file {} not found'.format(config_file))
    elif file_val.startswith('ValueErrorType'):
        file_type = file_val.split(':')[-1]
        raise ValueError(
            f'Unknown file type {file_type} for configuration file')

    if cfg_parser:
        print(f'Configuration file "{config_file}" is loaded.')
        return cfg_parser, cfg_parser['TELEGRAM'], cfg_parser['MESSENGER']
    else:
        raise ValueError(
            'The configuration file does not contain the correct format.')

def get_config():
    configuration, _, _ = arg_parse()
    return configuration

app = Flask(__name__)
VERIFY_TOKEN = 'bonobo'
CONTROLLER = ControllerMessenger()

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
        CONTROLLER.action(payload, recipient_id)
        return "Message Processed"


def get_message(output):
    for event in output['entry']:
        for message in event['messaging']:
            if message.get('message'):
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

def verify_fb_token(token_sent):
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Invalid verification token'


if __name__ == '__main__':
    # Usage: python run_bot.py -c <path_to_config.yaml>
    # Version: Python 3.6
    CONFIGURATION, BOT , MESSENGER = arg_parse()
    if BOT:
        CONTROLLER = ControllerTelegram()
    elif MESSENGER:
        CONTROLLER.execute_agent(CONFIGURATION)  
        app.run(host='0.0.0.0', port=environ.get("PORT", 5000))
    else:
        CONTROLLER = ControllerTerminal()
    CONTROLLER.execute_agent(CONFIGURATION)
    