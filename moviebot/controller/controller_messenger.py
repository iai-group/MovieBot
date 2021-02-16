
from moviebot.agent.agent import Agent
from moviebot.controller.controller import Controller
from moviebot.utterance.utterance import UserUtterance
from flask import Flask, request
import requests
from os import environ
#import tokens
#import app
from moviebot.controller import messages, messages

class ControllerMessenger(Controller):

    def __init__(self):
        self.agent = {}
        self.user_options = {}
        self.recipient_id = ""
        self.payload = ""

        self.action_list = [
        {"payload": "ubutton", "action": self.url_button},
        {"payload": "pbutton", "action": self.postback_button},
        {"payload": "start", "action": self.get_started},
        {"payload": "m", "action": self.send_image}, #not working
        {"payload": "aa", "action": self.send_attachment}, #not working
        {"payload": "imdb", "action": self.send_template}
        ]

        #images.upload_images()
        self.start = {"get_started": {"payload": "start"}}

    def execute_agent(self, configuration):
        self.agent = Agent(configuration)
        self.agent.initialize()
        

    def send_template(self):
        template = messages.template
        template['recipient']['id'] = self.recipient_id
        return requests.post(messages.message, json=template).json()

    def send_message(self):
        # Agent testing
        text = messages.text
        #text['message']['text'] = self.payload
        user_options = {}
        agent_response, user_options = self.agent.start_dialogue()
        user_utterance = UserUtterance({'text': self.payload})
        agent_response, user_options = self.agent.continue_dialogue(
            user_utterance, user_options
        )
        print("agent_respnse: ", agent_response)
        print("user_options: ", user_options)
        text['recipient']['id'] = self.recipient_id
        text['message']['text'] = agent_response
        return requests.post(messages.message, json=text).json()

    def get_started(self):
        return requests.post(messages.get_started, json=self.start).json()

    def send_attachment(self):
        attachment = images.attachment
        attachment['recipient']['id'] = self.recipient_id
        print(images.images[0]['attachment_id'])
        attachment['message']['attachment']['payload']['attachment_id'] = images.images[0]['attachment_id']
        return requests.post(messages.images, json=attachment).json()

    def send_image(self):
        print("recipient_id: ", self.recipient_id)
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