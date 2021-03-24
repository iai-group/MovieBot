
import json
import sqlite3
from moviebot.agent.agent import Agent
from moviebot.controller.controller import Controller
from moviebot.utterance.utterance import UserUtterance
from flask import Flask, request
import requests
from os import environ
import os
import yaml
#from imdb import IMDb
#import tokens
#import app
from moviebot.controller.messages import Messages
from moviebot.database.database import DataBase
from moviebot.nlu.annotation.slots import Slots
from moviebot.dialogue_manager.dialogue_state import DialogueState
import time
from datetime import datetime

class ControllerMessenger(Controller):

    def __init__(self):
        self.token = ""
        self.agent = {}
        self.record_data = {}
        self.user_messages = {}
        self.record_data_agent = {}
        self.user_options = {}
        self.agent_response = {}
        self.configuration = {}
        self.info = {}
        self.users = {}
        self.load_data = {}
        self.path = "conversation_history/"
        self.methods = [
            {"payload": "start", "action": self.privacy_policy},
            {"payload": "/help", "action": self.instructions},
            {"payload": "accept", "action": self.store_user},
            {"payload": "/restart", "action": self.restart},
            {"payload": "/exit", "action": self.exit}
        ]
        self.start = {"get_started": {"payload": "start"}}
        self.get_started()
        #self.greeting()
        
    def get_started(self):
        return requests.post('https://graph.facebook.com/v2.6/me/messenger_profile?access_token='+self.token, json=self.start).json()

    def store_user(self, user_id):
        self.users[user_id] = True
        self.start_agent(user_id)
        self.instructions(user_id, False)

    def load_bot_token(self, bot_token_path):
        """Loads the Token for the Telegram bot

        :return: the token of the Telegram Bot

        Args:
            bot_token_path:

        """
        if isinstance(bot_token_path, str):
            if os.path.isfile(bot_token_path):
                with open(bot_token_path, 'r') as file:
                    token_config = yaml.load(file, Loader=yaml.Loader)
                    if 'MESSENGER_TOKEN' in token_config:
                        return token_config['MESSENGER_TOKEN']
                    else:
                        raise ValueError(
                            f'The token for Messenger bot is not found in the file '
                            f'{bot_token_path}')
            else:
                raise FileNotFoundError(f'File {bot_token_path} not found')
        else:
            raise ValueError('Unacceptable type of Token file name')
    
    def movie_info(self, movie_id, user_id):
        for row in self.lookup().execute(f'SELECT * FROM movies_v2 WHERE ID="{movie_id}"'):
            self.info[user_id] = {
                "title": row[1],
                "rating": row[4],
                "duration": row[6],
                "summary": row[10],
                "image_url": row[9],
                "imdb_link": row[12]
            }

    def lookup(self):
        conn = sqlite3.connect(self.configuration['DATA']['db_path'])
        c = conn.cursor()
        return c

    def strip_tuple(self, element):
        for e in element:
            return e

    def execute_agent(self, configuration):
        self.configuration = configuration
        self.configuration['new_user'] = {}
        self.token = self.load_bot_token(self.configuration['BOT_TOKEN_PATH'])

    def restart(self, user_id):
        self.start_agent(user_id, True)
        
    def start_agent(self, user_id, restart=False):
        self.agent[user_id] = Agent(self.configuration)
        self.agent[user_id].initialize(user_id)
        self.agent_response[user_id], self.record_data_agent[user_id], self.user_options[user_id
        ] =  self.agent[user_id].start_dialogue()
        if restart:
            self.agent_response[user_id], self.record_data_agent[user_id], self.user_options[user_id
            ] = self.agent[user_id].start_dialogue(None, restart)
            self.user_messages[user_id].text(self.agent_response[user_id])


    def movie_template(self, user_id, buttons):
        title = self.info[user_id]['title'] + " " + str(self.info[user_id]['rating']) + \
            " " + str(self.info[user_id]['duration']) + " min"
        self.user_messages[user_id].template(
            buttons[0:3], self.info[user_id]['image_url'], self.info[user_id]['imdb_link'], \
                self.info[user_id]['summary'], title)

    def get_options(self, user_id):
        options = []
        for option in self.user_options[user_id].values():
            if type(option) == type("string"):
                options.append(option)
            else:
                for item in option:
                    options.append(item)
        print("OPTIONS: ", options)
        return options

    def get_movie_id(self, response):
        if "/tt" in response:
            start = response.find("/tt")
            movie_id = response[start+3:start+10]
            return movie_id

    def continue_dialogue(self, user_id, payload):
        user_utterance = UserUtterance({'text': payload})
        self.agent_response[user_id], self.record_data_agent[user_id], self.user_options[user_id
        ] = self.agent[user_id].continue_dialogue(
            user_utterance, self.user_options[user_id]
        )
        self.record(user_id, payload)
        movie_id = self.get_movie_id(self.agent_response[user_id])
        self.movie_info(movie_id, user_id)
        print("agent_response: ", self.agent_response[user_id])

    def record(self, user_id, payload):
        if self.agent[user_id].bot_recorder:
            self.record_data[user_id] = {
                'Timestamp': str(datetime.now()),
                'User_Input': payload
            }
            self.record_data[user_id].update(self.record_data_agent[user_id])
            self.agent[user_id].bot_recorder.record_user_data(
                user_id, self.record_data[user_id])

    def load_user_data(self, user_id):
        user_history_path = self.path + 'user_' + user_id + '.json'
        self.load_data[user_id] = {}
        if os.path.isfile(user_history_path):
            with open(user_history_path) as json_file:
                data = json.load(json_file)
                for conversation in data:
                    for movie in conversation["Context"]:
                        self.load_data[user_id][movie] = conversation["Context"][movie]

    def send_message(self, user_id, payload):
        self.continue_dialogue(user_id, payload)
        if self.user_options[user_id]:
            buttons = self.user_messages[user_id].create_buttons(self.get_options(user_id))
            if "**" in self.agent_response[user_id]:
                self.movie_template(user_id, buttons)
            else: 
                self.user_messages[user_id].buttons_template(buttons, self.agent_response[user_id])
        else: 
            self.user_messages[user_id].text(self.agent_response[user_id])

    def initialize(self, user_id):
        if user_id not in self.agent:
            self.user_messages[user_id] = Messages(user_id, self.token)
            self.start_agent(user_id)
        self.user_messages[user_id].mark_seen()
        self.user_messages[user_id].typing_on()

    def run_method(self, user_id, payload):
        for item in self.methods:
            if payload.lower() == item['payload']:
                func = item.get('action')
                return func(user_id)
        return True

    def exit(self, user_id):
        self.agent_response[user_id] = 'You are exiting. I hope you found a movie. Bye.'
        self.text(user_id, self.agent_response[user_id])
        del self.agent[user_id]

    def instructions(self, user_id, help=True):
        response =  "To start the conversation, issue \"/start\", say Hi/Hello, or simply " \
                "enter you preferences (\"I want a horror movie from the 90s\").\n\n" \
                "To restart the recommendation process, issue \"/restart\".\n\n" \
                "To end the conversation, issue \"/exit\" or say Bye/Goodbye.\n\n" \
                "To see these instructions again, issue: \"/help\"." 

        instructions = 'Hi there. I am IAI MovieBot, your movie recommending buddy. ' \
                       'I can recommend you movies based on your preferences.\n' \
                       'I will ask you a few questions and based on your answers, ' \
                       'I will try to find a movie for you.\n\n' 
        if help is False:
            response = instructions + response
        self.user_messages[user_id].text(response)

    def privacy_policy(self, user_id):
        policy = "Privacy policy... ."
        self.user_messages[user_id].text(policy)
        title = ["Accept", "Reject"]
        payload = ["accept", "reject"]
        self.user_messages[user_id].quickreply("Accept or Reject", title, payload)
         


