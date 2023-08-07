"""The flask server using socketIO to communicate with the client."""

import logging
from os import environ
from typing import Any, Dict

from flask import Flask, request, session
from flask_socketio import Namespace, SocketIO, emit, send

from moviebot.controller.controller_flask import ControllerFlask
from moviebot.database.db_users import UserDB

logger = logging.getLogger(__name__)

app = Flask(__name__)

socketio = SocketIO(app, cors_allowed_origins="*")
controller_flask: ControllerFlask = ControllerFlask()


class ChatNamespace(Namespace):
    def __init__(self, namespace: str) -> None:
        """Namespace for chat.

        Args:
            namespace: Namespace of chat.
        """
        super().__init__(namespace)
        self.user_db = UserDB()
        self.active_users = {}

    def _handle_authentication(
        self, is_registering: bool, data: Dict[str, Any]
    ) -> None:
        """Handles user authentication.

        Args:
            is_registering: Whether user is registering or logging in.
            data: Data received from client.
        """
        event_name = "register_response" if is_registering else "login_response"

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
            success = self.user_db.register_user(username, password)
        else:
            success = self.user_db.verify_user(username, password)

        if success:
            self.active_users[request.sid] = self.user_db.get_user_id(username)
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
                    else "Bad login credentials",
                },
            )

    def on_connect(self, data: Dict[str, Any]) -> None:
        """Connects client to server.

        Args:
            data: Data received from client.
        """
        self.active_users[request.sid] = request.sid
        logger.info("Client connected")

    def on_disconnect(self) -> None:
        """Disconnects client from server."""
        user_id = self.active_users.get(request.sid)
        if session.get("conversation_started"):
            controller_flask.exit(user_id)
        del self.active_users[request.sid]
        logger.info("Client disconnected")

    def on_start_conversation(self, data: Dict[str, Any]) -> None:
        """Starts conversation with client.

        Args:
            data: Data received from client.
        """
        logger.info(f"Conversation started: {data}")
        user_id = self.active_users.get(request.sid)
        controller_flask.initialize(user_id)
        session["conversation_started"] = True

        response = controller_flask.start_conversation(user_id)
        emit("message", response)

    def on_message(self, data: Dict[str, Any]) -> None:
        """Receives message from client and sends response.

        Args:
            data: Data received from client.
        """
        logger.info(f"Message received: {data}")
        user_id = self.active_users.get(request.sid)
        response = action(user_id, data["message"])
        if response:
            return send(response)
        send({"info": "Message Processed"})

    def on_feedback(self, data: Dict[str, Any]) -> None:
        """Receives feedback from client.

        Args:
            data: Data received from client.
        """
        logger.info(f"Feedback received: {data}")
        # user_id = self.active_users.get(request.sid)
        # TODO: Implement feedback logic
        # Issue: https://github.com/iai-group/MovieBot/issues/129
        send({"info": "Feedback received"})

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


def run(config: Dict[str, Any]) -> None:
    """Runs execute_agent in ControllerFlask and starts flask server.

    Args:
        config: Agent configuration.
    """
    controller_flask.execute_agent(config)
    socketio.on_namespace(ChatNamespace("/"))
    socketio.run(app, host="127.0.0.1", port=environ.get("PORT", 5000))


def action(user_id: str, message: Dict[str, Any]) -> Dict[str, Dict[str, str]]:
    """Passes message to ControllerFlask and returns response.

    Args:
        user_id: User id.
        message: Message to be processed.

    Returns:
        Response from ControllerFlask.
    """

    if message is not None:
        run_method_response = controller_flask.run_method(user_id, message)
        if run_method_response is True:
            return controller_flask.send_message(user_id, message)
        elif run_method_response:
            return run_method_response
