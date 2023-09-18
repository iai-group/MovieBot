"""This file contains the Controller class which controls the flow of the
conversation while the user interacts with the agent using Flask REST."""

import logging
from dataclasses import asdict
from typing import Any, Dict, Type

from flask import Flask, request

from dialoguekit.core import Utterance
from moviebot.agent.agent import MovieBotAgent
from moviebot.controller.controller import Controller
from moviebot.controller.http_data_formatter import Message, Response


class ControllerFlaskRest(Controller):
    def __init__(
        self,
        agent_class: Type[MovieBotAgent],
        agent_args: Dict[str, Any] = {},
    ) -> None:
        """Initializes structs for Controller and sends the get_started button
        to the client.

        Args:
            agent_class: The class of the agent.
            agent_args: The arguments to pass to the agent. Defaults to empty
              dict.
        """
        super().__init__(agent_class, agent_args)
        self.app = Flask(__name__)
        self.app.add_url_rule(
            "/",
            "receive_message",
            self.receive_message,
            methods=["GET", "POST"],
        )
        self._last_agent_responses = dict()

    def start(self, host: str = "127.0.0.1", port: str = "5001") -> None:
        """Starts the platform.

        Args:
            host: Hostname. Defaults to 127.0.0.1.
            port: Port. Defaults to 5001.
        """
        self._host = host
        self._port = port
        self.app.run(host=host, port=port)

    def receive_message(self) -> None:
        """Receives POST requests send from client."""
        if request.method == "GET":
            return "MovieBot is alive", 200
        else:
            output = request.get_json()
            logging.info(output)
            sender_id = output.get("sender", {}).get("id", "ClientREST")
            if sender_id not in self._active_users.keys():
                self.connect(sender_id)
            self.message(sender_id, output.get("message", {}).get("text", ""))

            agent_response = self._last_agent_responses.pop(sender_id)
            return agent_response

    def display_agent_utterance(
        self, user_id: str, utterance: Utterance
    ) -> None:
        """Stores the agent's reply to the given user.

        Args:
            user_id: User ID.
            utterance: An instance of Utterance.
        """
        self._last_agent_responses[user_id] = asdict(
            Response(user_id, Message.from_utterance(utterance))
        )

    def display_user_utterance(
        self, user_id: str, utterance: Utterance
    ) -> None:
        """Overrides the method in Platform to avoid raising an error.

        This method is not used in ControllerFlaskRest.

        Args:
            user_id: User ID.
            utterance: An instance of Utterance.
        """
        pass
