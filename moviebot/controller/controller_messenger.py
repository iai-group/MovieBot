"""This file contains the Controller class which controls the flow of the
conversation while the user interacts with the agent using Messenger."""

import json
import os
import sqlite3
from datetime import datetime

import requests
import yaml

from moviebot.agent.agent import Agent
from moviebot.controller.controller import Controller
from moviebot.controller.messenger import Messenger
from moviebot.core.utterance.utterance import UserUtterance


class ControllerMessenger(Controller):
    def __init__(self):
        """Initializes structs for Controller and sends the get started button
        to the facebook API.
        """
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
        self.path = ""
        self.methods = [
            {"payload": "/start", "action": self.privacy_policy},
            {"payload": "/help", "action": self.instructions},
            {"payload": "/accept", "action": self.store_user},
            {"payload": "/reject", "action": self.start_conversation},
            {"payload": "/restart", "action": self.restart},
            {"payload": "/exit", "action": self.exit},
            {"payload": "/delete", "action": self.delete_data},
            {"payload": "/test", "action": self.privacy_policy},
            {"payload": "/store", "action": self.store_user},
            {"payload": "/continue", "action": self.start_conversation},
        ]
        self.short_answers = {
            "I like this recommendation.": "I like this",
            "I have already watched it.": "Seen it",
            "Tell me more about it.": "Tell me more",
            "Recommend me something else please.": "Something else",
            "Tell me something about it.": "More information",
            "/restart": "Restart",
            "I would like a similar recommendation.": "Similar",
            "I want to restart for a new movie.": "Restart",
            "I would like to quit now.": "Quit",
        }
        self.start = {"get_started": {"payload": "/start"}}

    def get_started(self):
        """Displays 'Get Started' button at messenger weclome screen"""
        return requests.post(
            "https://graph.facebook.com/v10.0/me/messenger_profile?access_token="
            + self.token,
            json=self.start,
        ).json()

    def store_user(self, user_id):
        """True if user accepts licence agreement.
        Data for this user is stored in conversation history.

        Args:
            user_id:
        """
        self.users[user_id] = True
        self.store_data(user_id)
        # self.start_conversation(user_id)

    def start_conversation(self, user_id):
        """Start conversation with agent and send instructions to user.
        Args:
            user_id:
        """
        self.start_agent(user_id)
        self.instructions(user_id)

    def load_bot_token(self, bot_token_path):
        """Loads the Token for the Telegram bot

        :return: the token of the Telegram Bot

        Args:
            bot_token_path:

        """
        if isinstance(bot_token_path, str):
            if os.path.isfile(bot_token_path):
                with open(bot_token_path, "r") as file:
                    token_config = yaml.load(file, Loader=yaml.Loader)
                    if "MESSENGER_TOKEN" in token_config:
                        return token_config["MESSENGER_TOKEN"]
                    else:
                        raise ValueError(
                            "The token for Messenger bot is not found in the"
                            f" file {bot_token_path}"
                        )
            else:
                raise FileNotFoundError(f"File {bot_token_path} not found")
        else:
            raise ValueError("Unacceptable type of Token file name")

    def movie_info(self, movie_id, user_id):
        """Retrieve relevant movie info from database for selected user.
        Args:
            movie_id:
            user_id:
        """
        for row in self.lookup().execute(
            f'SELECT * FROM movies_v2 WHERE ID="{movie_id}"'
        ):
            self.info[user_id] = {
                "title": row[1],
                "rating": row[4],
                "duration": row[6],
                "summary": row[10],
                "image_url": row[9],
                "imdb_link": row[12],
            }

    def lookup(self):
        conn = sqlite3.connect(self.configuration["DATA"]["db_path"])
        c = conn.cursor()
        return c

    def execute_agent(self, configuration):
        """Gets access token and conversation_history path from config file.

        Sends get_started and greeting requests to the messenger API.

        Runs the conversational agent and executes the dialogue by calling
        the basic components of IAI MovieBot.

        Args:
            configuration: the settings for the agent

        """
        self.configuration = configuration
        self.configuration["new_user"] = {}
        self.token = self.load_bot_token(self.configuration["BOT_TOKEN_PATH"])
        if self.configuration["BOT_HISTORY"]["path"]:
            self.path = self.configuration["BOT_HISTORY"]["path"]
        self.get_started()
        self.greeting()

    def restart(self, user_id):
        """Restart agent for this user.

        Args:
            user_id:

        """
        self.start_agent(user_id, True)

    def start_agent(self, user_id, restart=False):
        """Start conversation with agent.

        Args:
            user_id:
            restart: True or False

        """
        self.agent[user_id] = Agent(self.configuration)
        self.agent[user_id].initialize(user_id)
        (
            self.agent_response[user_id],
            self.record_data_agent[user_id],
            self.user_options[user_id],
        ) = self.agent[user_id].start_dialogue()
        if restart:
            (
                self.agent_response[user_id],
                self.record_data_agent[user_id],
                self.user_options[user_id],
            ) = self.agent[user_id].start_dialogue(None, restart)
            self.user_messages[user_id].text(self.agent_response[user_id])

    def movie_template(self, user_id, buttons):
        """Sends template for recommended movie.

        Args:
            user_id:
            buttons: list of buttons

        """
        title = (
            self.info[user_id]["title"]
            + " "
            + str(self.info[user_id]["rating"])
            + " "
            + str(self.info[user_id]["duration"])
            + " min"
        )
        self.user_messages[user_id].template(
            buttons[0:3],
            self.info[user_id]["image_url"],
            self.info[user_id]["imdb_link"],
            self.info[user_id]["summary"],
            title,
        )

    def get_options(self, user_id):
        """Gets options from agent.

        Args:
            user_id:

        """
        options = []
        for option in self.user_options[user_id].values():
            for item in option:
                options.append(
                    {
                        "button_type": "postback",
                        "title": self.shorten(item),
                        "payload": item,
                    }
                )
        return options

    def shorten(self, input):
        """Creates shorter versions of agent responses.

        Args:
            input: agent options

        """
        for key, value in self.short_answers.items():
            if key == input:
                return value
        return input

    def get_movie_id(self, response):
        """Retrieves movie id from agent response string.

        Args:
            response: agent response

        """
        if "/tt" in response:
            start = response.find("/tt")
            movie_id = response[start + 3 : start + 10]
            return movie_id

    def continue_dialogue(self, user_id, payload):
        """Continues dialogue with the agent. Updates movie info.

        Args:
            user_id:
            payload: payload from user

        """
        user_utterance = UserUtterance({"text": payload})
        (
            self.agent_response[user_id],
            self.record_data_agent[user_id],
            self.user_options[user_id],
        ) = self.agent[user_id].continue_dialogue(
            user_utterance, self.user_options[user_id]
        )
        if self.users[user_id]:
            self.record(user_id, payload)
        movie_id = self.get_movie_id(self.agent_response[user_id])
        self.movie_info(movie_id, user_id)

    def record(self, user_id, payload):
        """Records user conversation if user has accepted privacy policy.

        Args:
            user_id:
            payload: user payload

        """
        if self.agent[user_id].bot_recorder:
            self.record_data[user_id] = {
                "Timestamp": str(datetime.now()),
                "User_Input": payload,
            }
            self.record_data[user_id].update(self.record_data_agent[user_id])
            self.agent[user_id].bot_recorder.record_user_data(
                user_id, self.record_data[user_id]
            )

    def load_user_data(self, user_id):
        """Gets movie choices (accept/reject) for a user from conversation
        history.

        Args:
            user_id:

        """
        user_history_path = self.path + "user_" + user_id + ".json"
        self.load_data[user_id] = {}
        if os.path.isfile(user_history_path):
            with open(user_history_path) as json_file:
                data = json.load(json_file)
                for conversation in data:
                    for movie in conversation["Context"]:
                        self.load_data[user_id][movie] = conversation[
                            "Context"
                        ][movie]

    def delete_data(self, user_id):
        """Delete stored conversation history for user.

        Args:
            user_id:

        """
        user_history_path = self.path + "user_" + user_id + ".json"
        if os.path.isfile(user_history_path):
            os.remove(user_history_path)
            self.users[user_id] = False
            self.user_messages[user_id].text("Conversation history deleted.")
        else:
            self.user_messages[user_id].text("No conversation history.")

    def send_message(self, user_id, payload):
        """Sends template, buttons or text based on current agent options.

        Args:
            user_id:
            payload: user_payload

        """
        self.continue_dialogue(user_id, payload)
        if self.user_options[user_id]:
            buttons = self.user_messages[user_id].create_buttons(
                self.get_options(user_id)
            )
            if "**" in self.agent_response[user_id]:
                self.movie_template(user_id, buttons)
            else:
                self.user_messages[user_id].buttons_template(
                    buttons, self.agent_response[user_id]
                )
        else:
            self.user_messages[user_id].text(self.agent_response[user_id])

    def initialize(self, user_id):
        """Initializes structs for a new user.

        Args:
            user_id:

        """
        if user_id not in self.agent:
            self.user_options[user_id] = {}
            self.users[user_id] = {}
            self.user_messages[user_id] = Messenger(user_id, self.token)
            self.start_agent(user_id)
        self.user_messages[user_id].mark_seen()
        self.user_messages[user_id].typing_on()

    def run_method(self, user_id, payload):
        """Runs methods for specific user inputs.

        Args:
            user_id:
            payload: user payload

        """
        for item in self.methods:
            if payload.lower() == item["payload"]:
                func = item.get("action")
                return func(user_id)
        return True

    def exit(self, user_id):
        """Ends conversation and deletes user id from agent.

        Args:
            user_id:

        """
        self.agent_response[
            user_id
        ] = "You are exiting. I hope you found a movie. Bye."
        self.user_messages[user_id].text(self.agent_response[user_id])
        del self.agent[user_id]

    def instructions(self, user_id):
        """Instructions when the conversation is started and when '/help' is
        issued.
        """

        response = (
            "To start the conversation say Hi/Hello, or simply "
            'enter you preferences ("I want a horror movie from the 90s").\n\n'
            'To restart the recommendation process, issue "/restart".\n\n'
            'To end the conversation, issue "/exit" or say Bye/Goodbye.\n\n'
            'To see these instructions again, issue: "/help".'
        )

        self.user_messages[user_id].text(response)

    def store_data(self, user_id):
        """Instructions for deleting stored conversation history.
        Args:
            user_id:

        """
        policy = (
            'Type "/delete" at any time to stop storing and delete conversation'
            " history.\n\nPress start to continue."
        )
        self.user_messages[user_id].text(policy)

    def privacy_policy(self, user_id):
        title = (
            "We may store some information to improve recommendations.\n"
            "You may delete stored data at any time.\n"
            "Read more in our privacy policy"
        )
        options = [
            {
                "button_type": "web_url",
                "title": "Privacy Policy",
                "url": (
                    "https://iai-group.github.io/moviebot/Privacy_policy.html"
                ),
            },
            {
                "button_type": "postback",
                "title": "Accept",
                "payload": "/store",
            },
            {
                "button_type": "postback",
                "title": "Start",
                "payload": "/continue",
            },
        ]
        self.user_messages[user_id].url_button(title, options)

    def greeting(self):
        """Posts greeting text on welcome screen."""
        greeting = {
            "greeting": [
                {
                    "locale": "default",
                    "text": (
                        "Hi there. I am IAI MovieBot, your movie recommending"
                        " buddy. I can recommend you movies based on your"
                        " preferences.\n I will ask you a few questions and"
                        " based on your answers, I will try to find a movie for"
                        " you.\n\n"
                    ),
                }
            ]
        }
        return requests.post(
            "https://graph.facebook.com/v10.0/me/messenger_profile?access_token="
            + self.token,
            json=greeting,
        ).json()
