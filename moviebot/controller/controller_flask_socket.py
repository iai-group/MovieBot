"""This file contains the Controller class which controls the flow of the
conversation while the user interacts with the agent using Flask Socket IO."""

import logging
from dataclasses import asdict
from typing import Any, Dict, Type

from flask import request, session
from flask_socketio import emit

from dialoguekit.core import Utterance
from dialoguekit.platforms.flask_socket_platform import (
    ChatNamespace as DKChatNamespace,
)
from dialoguekit.platforms.flask_socket_platform import FlaskSocketPlatform
from moviebot.agent.agent import MovieBotAgent
from moviebot.controller.controller import Controller
from moviebot.controller.http_data_formatter import Message, Response
from moviebot.database.db_users import UserDB

logger = logging.getLogger(__name__)


class ControllerFlaskSocket(Controller, FlaskSocketPlatform):
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

    def start(self, host: str = "127.0.0.1", port: str = "5000") -> None:
        """Starts the platform.

        Args:
            host: Hostname. Defaults to 127.0.0.1.
            port: Port. Defaults to 5000.
        """
        self.socketio.on_namespace(ChatNamespace("/", self))
        self.socketio.run(self.app, host=host, port=port)

    def display_agent_utterance(
        self, user_id: str, utterance: Utterance
    ) -> None:
        """Displays agent utterance to the client.

        Args:
            user_id: User ID.
            utterance: An instance of Utterance.
        """
        message = Message.from_utterance(utterance)
        self.socketio.send(
            asdict(Response(user_id, message)),
            room=user_id,
        )


class ChatNamespace(DKChatNamespace):
    def __init__(self, namespace: str, platform: ControllerFlaskSocket) -> None:
        """Represents a chat namespace.

        Args:
            namespace: Namespace.
            platform: An instance of ControllerFlaskSocket.
        """
        super().__init__(namespace, platform)
        self.user_db = UserDB()

    def _handle_authentication(
        self, is_registering: bool, data: Dict[str, Any]
    ) -> None:
        """Handles user authentication.

        Args:
            is_registering: Whether user is registering or logging in.
            data: Data received from client.
        """
        event_name = "authentication"

        username = data.get("username", "").strip()
        password = data.get("password", "").strip()

        # Check for empty fields
        if not username or not password:
            emit(
                event_name,
                {
                    "success": False,
                    "error": "Username and password cannot be empty",
                },
            )
            return

        if is_registering:
            authentication_success = self.user_db.register_user(
                username, password
            )
        else:
            authentication_success = self.user_db.verify_user(
                username, password
            )

        if authentication_success:
            self._platform._active_users[
                request.sid
            ] = self.user_db.get_user_id(username)
            emit(
                event_name,
                {"success": True},
            )
        else:
            emit(
                event_name,
                {
                    "success": False,
                    "error": "Username already taken"
                    if is_registering
                    else "Incorrect login credentials",
                },
            )

    def on_register(self, data: Dict[str, Any]) -> None:
        """Registers client.

        Args:
            data: Data received from client.
        """
        logger.info(f"Registration details received: {data}")
        self._handle_authentication(True, data)

    def on_login(self, data: Dict[str, Any]) -> None:
        """Logs in client.

        Args:
            data: Data received from client.
        """
        logger.info(f"Login received: {data}")
        self._handle_authentication(False, data)

    def on_start_conversation(self, data: Dict[str, Any]) -> None:
        """Starts conversation with client.
        Args:
            data: Data received from client.
        """
        logger.info(f"Conversation started: {data}")
        self._platform.connect(request.sid)
        session["conversation_started"] = True
