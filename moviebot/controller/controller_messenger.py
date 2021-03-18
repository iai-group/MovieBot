
import json
import sqlite3
from moviebot.agent.agent import Agent
from moviebot.controller.controller import Controller
from moviebot.utterance.utterance import UserUtterance
from flask import Flask, request
import requests
from os import environ
#from imdb import IMDb
#import tokens
#import app
from moviebot.controller import messages, messages
from moviebot.database.database import DataBase


class ControllerMessenger(Controller):

    def __init__(self):
        self.agent = {}
        self.user_options = {}
        self.recipient_id = ""
        self.payload = ""
        self.user_options = {}
        self.agent_response = ""
        self.movie_id = ""
        self.buttons = []
        self.configuration = ""
        self.info = {}
        self.template = {}
        self.action_list = [
        {"payload": "start", "action": self.send_reply}
        ]
        #images.upload_images()
        self.start = {"get_started": {"payload": "start"}}
        self.greeting()
        self.get_started()
        
    def get_started(self):
        return requests.post(messages.get_started, json=self.start).json()

    def greeting(self):
        greeting = messages.greeting
        return requests.post(messages.greet, json=greeting).json()

    def send_reply(self):
        text = messages.text
        text['recipient']['id'] = self.recipient_id
        text['message']['text'] = "test"
        return requests.post(messages.message, json=text).json()

    def persistent_menu(self):
        menu = messages.menu
        menu['psid'] = self.recipient_id
        return requests.post(messages.persistent_menu, json=menu).json()

    def get_info(self, movie_id):
        for row in self.lookup().execute(f'SELECT * FROM movies_v2 WHERE ID="{movie_id}"'):
            self.info['title'] = row[1]
            self.info['rating'] = row[4]
            self.info['duration'] = row[6]
            self.info['summary'] = row[10]
            self.info["image_url"] = row[9]
            self.info['imdb_link'] = row[12]

    def lookup(self):
        conn = sqlite3.connect(self.get_db())
        c = conn.cursor()
        return c

    def strip_tuple(self, element):
        for e in element:
            return e

    def get_db(self):
        db_path = self.configuration['DATA']['db_path']
        print("path: ", db_path)
        return db_path

    def execute_agent(self, configuration):
        self.configuration = configuration
        self.agent = Agent(configuration)
        self.agent.initialize()
        self.get_db()
        self.agent_response, self.user_options = self.agent.start_dialogue()

    def typing(self):
        typing = messages.typing_on(self.recipient_id)
        print("TYPING: ", typing)
        return requests.post(messages.button, json=typing).json()

    def mark_seen(self):
        mark = messages.mark_seen
        mark['recipient_id'] = self.recipient_id
        return requests.post(messages.button, json=mark).json()

    def send_template(self):
        template = messages.create_template(self.recipient_id, self.buttons[0:3],
            self.info['image_url'], self.info['imdb_link'], self.info['summary'], self.info['title'],
            self.info['rating'], self.info['duration'])
        return requests.post(messages.message, json=template).json()

    def create_buttons(self, options):
        buttons = []
        for option in options:
            print("type: ", type(option))
            if type(option) == type("string"):
                print("string option: ", option)
                buttons.append(self.create_button(option))
            else:
                for item in option:
                    print("item: ", item)
                    buttons.append(self.create_button(item))
        self.template = self.buttons_template(buttons)
        return buttons
        
    def create_button(self, payload):
        button = {"type": "postback", "title": payload, "payload": payload}
        return button

    def get_movie_id(self, response):
        if "/tt" in response:
            start = response.find("/tt")
            movie_id = response[start+3:start+10]
            return movie_id

    def send_message(self):
        user_utterance = UserUtterance({'text': self.payload})
        self.agent_response, self.user_options = self.agent.continue_dialogue(
            user_utterance, self.user_options
        )
        self.movie_id = self.get_movie_id(self.agent_response)
        self.get_info(self.movie_id)
        print("-----------------------------------------------------")
        print("agent_response: ", self.agent_response)
        print("USER OPTIONS: ", self.user_options.values())
        print("-----------------------------------------------------")
        if self.user_options:
            self.buttons = self.create_buttons(self.user_options.values())
            print("BUTTONS: ", self.buttons)
            #template = self.buttons_template(self.buttons)
            if "**" in self.agent_response:
                self.send_template()
            elif "Please choose" in self.agent_response:
                self.template['message']['attachment']['payload']['text'] = "Please choose"
                self.send_buttons(self.template)
                
            elif "Sorry" in self.agent_response:
                self.template['message']['attachment']['payload']['text'] = "Sorry"
                self.send_buttons(self.template)

            else: 
                text = messages.text
                text['recipient']['id'] = self.recipient_id
                text['message']['text'] = self.agent_response
                return requests.post(messages.message, json=text).json()
        else: 
            text = messages.text
            text['recipient']['id'] = self.recipient_id
            text['message']['text'] = self.agent_response
            return requests.post(messages.message, json=text).json()

    def send_buttons(self, buttons):
        return requests.post(messages.button, json=buttons).json()
    
    def buttons_template(self, buttons):
        template = {
            "recipient":{ "id": self.recipient_id},
            "message":{
            "attachment":{
                "type":"template",
                "payload":{
                "template_type":"button",
                "text":"",
                "buttons":buttons
                }
            }
            }
        }
        return template

    def get_started(self):
        return requests.post(messages.get_started, json=self.start).json()

    def action(self, payload, recipient_id):
        self.recipient_id = recipient_id
        self.typing()
        self.mark_seen()
        self.payload = payload
        #sender_action.sender_action(self.recipient_id)
        for item in self.action_list:
            if payload == item['payload']:
                func = item.get('action')
                return func()
        return self.send_message()

         # def send_quickreply(self):
        
    #     quickreply = messages.qreply(self.recipient_id)
    #     quick_replies = []
    #     for option in self.user_options.values():
    #         if type(option) == type("string"):
    #             quick_replies.append(messages.create_reply(option, option))
    #         else:
    #             for item in option:
    #                 quick_replies.append(messages.create_reply(item, item))
    #     quickreply['message']['quick_replies'] = quick_replies
    #     return requests.post(messages.quickreply, json=quickreply).json()