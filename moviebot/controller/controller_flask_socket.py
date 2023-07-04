"""This file contains the Controller class which controls the flow of the
conversation while the user interacts with the agent using Flask Socket IO."""

from dataclasses import asdict
from typing import Any, Dict, Type

from dialoguekit.core import Utterance
from dialoguekit.platforms.flask_socket_platform import (
    FlaskSocketPlatform,
    Response,
)

import moviebot.controller.http_data_formatter as http_formatter
from moviebot.agent.agent import MovieBotAgent
from moviebot.controller.controller import Controller


class ControllerFlaskSocket(Controller, FlaskSocketPlatform):
    def __init__(
        self,
        agent_class: Type[MovieBotAgent],
        agent_args: Dict[str, Any] = {},
    ) -> None:
        """Initializes structs for Controller and sends the get started button
        to the client.

        Args:
            agent_class: The class of the agent.
            agent_args: The arguments to pass to the agent. Defaults to empty
              dict.
        """
        super().__init__(agent_class, agent_args)

    def display_agent_utterance(
        self, user_id: str, utterance: Utterance
    ) -> None:
        """Emits agent utterance to the client.

        Args:
            user_id: User ID.
            utterance: An instance of Utterance.
        """
        message = http_formatter.Message.from_utterance(utterance)
        self.socketio.send(
            asdict(Response(user_id, message)),
            room=user_id,
        )
