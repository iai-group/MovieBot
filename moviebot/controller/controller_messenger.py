
import json
from moviebot.agent.agent import Agent
from moviebot.controller.controller import Controller
from moviebot.utterance.utterance import UserUtterance
from flask import Flask, request
import requests
from os import environ
from imdb import IMDb
#import tokens
#import app
from moviebot.controller import messages, messages

class ControllerMessenger(Controller):

    def __init__(self):
        self.ia = IMDb()
        self.agent = {}
        self.user_options = {}
        self.recipient_id = ""
        self.payload = ""
        self.user_options = {}
        self.agent_response = ""
        self.movie = ""
        
        self.buttons = []
        self.action_list = [
        {"payload": "ubutton", "action": self.url_button},
        {"payload": "quickreply", "action": self.send_quickreply}
        ]

        #images.upload_images()
        self.start = {"get_started": {"payload": "start"}}

    def execute_agent(self, configuration):
        self.agent = Agent(configuration)
        self.agent.initialize()
        self.agent_response, self.user_options = self.agent.start_dialogue()

    def send_quickreply(self):
        quickreply = messages.qreply(self.recipient_id)
        quick_replies = []
        for option in self.user_options.values():
            if type(option) == type("string"):
                quick_replies.append(messages.create_reply(option, option))
            else:
                for item in option:
                    quick_replies.append(messages.create_reply(item, item))
        quickreply['message']['quick_replies'] = quick_replies
        return requests.post(messages.quickreply, json=quickreply).json()

    def send_template(self):
        url = self.find_link(self.agent_response)
        movie_id = self.get_movie_id(self.agent_response)
        self.movie = self.ia.get_movie(movie_id)
        
        template = messages.create_template(self.recipient_id, self.buttons[0:3],
            self.movie['cover url'], url, self.movie['plot outline'], self.movie['original title'],
            self.movie['rating'])
        
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
        return buttons
        
    def create_button(self, payload):
        button = messages.template_button("postback", payload, payload)
        return button
        
    def find_link(self, response):
        if "https" in response:
            start = response.find("https")
            url = response[int(start):int(response.find(")"))]
            return url

    def get_movie_id(self, response):
        if "/tt" in response:
            start = response.find("/tt")
            movie_id = response[start+3:start+10]
            return movie_id

    def send_buttons(self, start, end):
        buttons = messages.buttons_template(self.recipient_id, self.buttons[start:end])
        return requests.post(messages.button, json=buttons).json()

    def send_message(self):
        # Agent testing
        # if True:
        user_utterance = UserUtterance({'text': self.payload})
        self.agent_response, self.user_options = self.agent.continue_dialogue(
            user_utterance, self.user_options
        )
        print("-----------------------------------------------------")
        print(self.payload)
        print("agent_response: ", self.agent_response)
        self.find_link(self.agent_response)
            
        if self.user_options:
            print("options: ", list(self.user_options.values()))
            self.buttons = self.create_buttons(self.user_options.values())
            print("buttons: ", self.buttons)
            if "**" in self.agent_response:
                self.send_template()
                self.send_buttons(3, 5)
            else:
                self.send_buttons(0, 3)
                self.send_quickreply()
            # text = messages.text
            # text['recipient']['id'] = self.recipient_id
            # text['message']['text'] = self.agent_response
            # return requests.post(messages.message, json=text).json()
            
        else: 
            text = messages.text
            text['recipient']['id'] = self.recipient_id
            text['message']['text'] = self.agent_response
            return requests.post(messages.message, json=text).json()

    def get_started(self):
        return requests.post(messages.get_started, json=self.start).json()

    def send_attachment(self):
        attachment = images.attachment
        attachment['recipient']['id'] = self.recipient_id
        attachment['message']['attachment']['payload']['attachment_id'] = images.images[0]['attachment_id']
        return requests.post(messages.images, json=attachment).json()

    def send_image(self):
        image = messages.image
        image['recipient']['id'] = self.recipient_id
        return requests.post(messages.images, json=image).json()

    def url_button(self):
        response = messages.url_button(self.recipient_id, "hello", "https://wikipedia.com", "Title")
        return requests.post(messages.button, json=response).json()

    def postback_button(self):
        response = messages.postback_button(self.recipient_id, "Get payload", "payload string", "Title")
        return requests.post(messages.button, json=response).json()

    def action(self, payload, recipient_id):
        self.recipient_id = recipient_id
        self.payload = payload
        #sender_action.sender_action(self.recipient_id)
        for item in self.action_list:
            if payload == item['payload']:
                func = item.get('action')
                return func()
        return self.send_message()