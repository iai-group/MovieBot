"""This file contains the Controller class which controls the flow of the
conversation while the user interacts with the agent using Messenger."""

import json
import os
import sqlite3
from datetime import datetime
from typing import Any, Callable, Dict, Union

from moviebot.agent.agent import Agent
from moviebot.controller.controller import Controller
from moviebot.controller.http_data_formatter import (
    HTTP_OBJECT_MESSAGE,
    HTTPDataFormatter,
)
from moviebot.core.utterance.utterance import UserUtterance


class ControllerFlask(Controller):
    def __init__(self) -> None:
        """Initializes structs for Controller and sends the get started button
        to the client."""
        self.token = ""
        self.agent: Dict[str, Agent] = {}
        self.record_data = {}
        self.user_messages: Dict[str, HTTPDataFormatter] = {}
        self.record_data_agent = {}
        self.user_options = {}
        self.agent_response = {}
        self.configuration = {}
        self.info = {}
        self.users = {}
        self.load_data = {}
        self.path = ""
        self.methods = [
            {"payload": "/start", "action": self.first_time_message},
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
        self.agent_intent = ""

    def lookup(self) -> sqlite3.Cursor:
        """Returns SQL cursor."""
        conn = sqlite3.connect(self.configuration["DATA"]["db_path"])
        c = conn.cursor()
        return c

    def initialize(self, user_id: str) -> None:
        """Initializes structs for a new user.

        Args:
            user_id: User id.
        """
        if user_id not in self.agent:
            self.user_options[user_id] = {}
            self.users[user_id] = {}
            self.user_messages[user_id] = HTTPDataFormatter(user_id)
            self.start_agent(user_id)

    def start_conversation(self, user_id: str) -> HTTP_OBJECT_MESSAGE:
        """Starts conversation with agent and sends instructions to user.

        Args:
            user_id: User id.

        Returns:
            Object with start message to send to the server.
        """
        start_text = self.start_agent(user_id)
        instructions_text = self.instructions(user_id)
        start_text["message"]["text"] = "\n\n".join(
            [
                start_text["message"]["text"],
                instructions_text["message"]["text"],
            ]
        )
        return start_text

    def movie_info(self, movie_id: str, user_id: str) -> None:
        """Retrieves relevant movie info from database for selected user.

        Args:
            movie_id: Movie id.
            user_id: User id.
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

    def execute_agent(self, configuration: Dict[str, Any]) -> None:
        """Configures the controller.

        Args:
            configuration: Configuration for the agent.
        """
        self.configuration = configuration
        self.configuration["new_user"] = {}
        if self.configuration["BOT_HISTORY"]["path"]:
            self.path = self.configuration["BOT_HISTORY"]["path"]

    def restart(self, user_id: str) -> Callable:
        """Restarts agent for this user."""
        return self.start_agent(user_id, True)

    def start_agent(self, user_id: str, restart=False) -> HTTP_OBJECT_MESSAGE:
        """Starts conversation with agent.

        Args:
            user_id: User id.
            restart: Whether or not to restart the agent.

        Returns:
            Object with start message to send to the server.
        """
        self.agent[user_id] = Agent(self.configuration)

        (
            self.agent_response[user_id],
            self.record_data_agent[user_id],
            self.user_options[user_id],
        ) = self.agent[user_id].start_dialogue()
        if restart:
            (
                self.agent_response[user_id],
                self.user_options[user_id],
                self.record_data_agent[user_id],
            ) = self.agent[user_id].start_dialogue(None, restart)
            return self.user_messages[user_id].text(
                self.agent_response[user_id], intent=self.agent_intent
            )
        else:
            return {"message": {"text": "", "intent": self.agent_intent}}

    def get_movie_id(self, response: str) -> str:
        """Retrieves movie id from agent response string.

        Args:
            response: Agent response.

        Returns:
            Movie id.
        """
        if "/tt" in response:
            start = response.find("/tt")
            movie_id = response[start + 3 : start + 10]
            return movie_id

    def continue_dialogue(self, user_id: str, payload: str) -> None:
        """Continues dialogue with the agent. Updates movie info.

        Args:
            user_id: User id.
            payload: User payload.
        """
        user_utterance = UserUtterance({"text": payload})
        (
            self.agent_response[user_id],
            self.user_options[user_id],
            self.record_data_agent[user_id],
        ) = self.agent[user_id].continue_dialogue(
            user_utterance, self.user_options[user_id]
        )
        if self.users[user_id]:
            self.record(user_id, payload)
        movie_id = self.get_movie_id(self.agent_response[user_id])
        self.movie_info(movie_id, user_id)

    def store_user(self, user_id: str) -> Callable:
        """True if user accepts license agreement. Data for this user is stored
        in conversation history.

        Args:
            user_id: User id.
        """
        self.users[user_id] = True
        return self.store_data(user_id)

    def record(self, user_id: str, payload: str) -> None:
        """Records user conversation if user has accepted privacy policy.

        Args:
            user_id: User id.
            payload: User payload.
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

    def load_user_data(self, user_id: str) -> None:
        """Gets movie choices (accept/reject) for a user from conversation
        history.

        Args:
            user_id: User id.
        """
        user_history_path = f"{self.path}user_{user_id}.json"
        self.load_data[user_id] = {}
        if os.path.isfile(user_history_path):
            with open(user_history_path) as json_file:
                data = json.load(json_file)
                for conversation in data:
                    for movie in conversation["Context"]:
                        self.load_data[user_id][movie] = conversation[
                            "Context"
                        ][movie]

    def delete_data(self, user_id: str) -> None:
        """Deletes stored conversation history for user.

        Args:
            user_id: User id.
        """
        user_history_path = f"{self.path}user_{user_id}.json"
        if os.path.isfile(user_history_path):
            os.remove(user_history_path)
            self.users[user_id] = False
            self.user_messages[user_id].text(
                "Conversation history deleted.", intent=self.agent_intent
            )
        else:
            self.user_messages[user_id].text(
                "No conversation history.", intent=self.agent_intent
            )

    def send_message(self, user_id: str, payload: str) -> HTTP_OBJECT_MESSAGE:
        """Sends template, buttons or text based on current agent options.

        Args:
            user_id: User id.
            payload: User payload.

        Returns:
            Object with message to send to the server.
        """
        self.continue_dialogue(user_id, payload)
        if self.user_options[user_id]:
            if "**" in self.agent_response[user_id]:
                return self.user_messages[user_id].movie_template(
                    self.info[user_id], self.agent_intent
                )
            else:
                buttons = self.user_messages[user_id].create_buttons(
                    self.user_options[user_id]
                )
                return self.user_messages[user_id].buttons_template(
                    buttons,
                    self.agent_response[user_id],
                    intent=self.agent_intent,
                )
        else:
            return self.user_messages[user_id].text(
                self.agent_response[user_id], intent=self.agent_intent
            )

    def run_method(self, user_id: str, payload: str) -> Union[bool, Callable]:
        """Runs methods for specific user inputs.

        Args:
            user_id: User id.
            payload: User payload.

        Returns:
            Output of the payload action if possible.
        """
        for item in self.methods:
            if payload.lower() == item["payload"]:
                func = item.get("action")
                return func(user_id)
        return True

    def exit(self, user_id: str) -> None:
        """Ends conversation and deletes user id from agent.

        Args:
            user_id: User id.
        """
        self.agent_response[
            user_id
        ] = "You are exiting. I hope you found a movie. Bye."
        self.user_messages[user_id].text(
            self.agent_response[user_id], intent=self.agent_intent
        )
        del self.agent[user_id]

    def instructions(self, user_id: str) -> HTTP_OBJECT_MESSAGE:
        """Creates utterance with usage instructions.

        The instructions are sent when the conversation starts and when '/help'
        is received.

        Args:
            user_id: User id.

        Returns:
            Object with instructions message to send to the server.
        """
        response = (
            "To start the conversation say Hi or Hello, or simply "
            'enter you preferences ("I want a horror movie from the 90s").\n\n'
            'To restart the recommendation process, issue "/restart".\n\n'
            'To end the conversation, issue "/exit" or say Bye/Goodbye.\n\n'
            'To see these instructions again, issue: "/help".'
        )

        return self.user_messages[user_id].text(
            response, intent="REVEAL.DISCLOSE"
        )

    def store_data(self, user_id: str) -> HTTP_OBJECT_MESSAGE:
        """Instructions for deleting stored conversation history.

        Args:
            user_id: User id.

        Returns:
            Object with instructions message to send to the server.
        """
        policy = (
            'Type "/delete" at any time to stop storing and delete conversation'
            " history.\n\nPress start to continue."
        )
        return self.user_messages[user_id].text(
            policy, intent="REVEAL.DISCLOSE"
        )

    def first_time_message(self, user_id: str) -> HTTP_OBJECT_MESSAGE:
        """Creates utterance with greetings message.

        Args:
            user_id: User id.

        Returns:
            Object with greetings message to send to the server.
        """
        self.start_agent(user_id)
        greet = self.greeting()

        return self.user_messages[user_id].text(
            greet["message"]["text"], intent="REVEAL.DISCLOSE"
        )

    def privacy_policy(self, user_id: str = None) -> HTTP_OBJECT_MESSAGE:
        """Creates utterance with policy.

        Args:
            user_id: User id. Defaults to None.

        Returns:
            Object with privacy message to send to the server.
        """
        title = (
            "We may store some information to improve recommendations.\n"
            "You may delete stored data at any time.\n"
            "Read more in our privacy policy\n"
            "Privacy Policy: https://iai-group.github.io/moviebot/Privacy_policy.html\n"  # noqa
            'To accept the privacy policy write "/store"\n'
            'To continue without accepting write "/continue"'
        )
        message = {"message": {"text": title, "intent": self.agent_intent}}
        return message

    def greeting(self) -> HTTP_OBJECT_MESSAGE:
        """Creates greeting message.

        Returns:
            Object with greetings message to send to the server.
        """
        return {
            "message": {
                "locale": "default",
                "text": "Hi there. I am IAI MovieBot, your movie recommending"
                " buddy. I can recommend you movies based on your preferences."
                "\nI will ask you a few questions and based on your answers, "
                "I will try to find a movie for you.\n\n",
                "intent": self.agent_intent,
            }
        }
