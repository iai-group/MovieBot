"""The flask server using socketIO to communicate with the client."""

import logging
from os import environ
from typing import Any, Dict

from flask import Flask, request
from flask_socketio import Namespace, SocketIO, emit, send

from moviebot.controller.controller_flask import ControllerFlask

logger = logging.getLogger(__name__)

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
controller_flask = ControllerFlask()


class ChatNamespace(Namespace):
    def on_connect(self, data: Dict[str, Any]) -> None:
        """Connects client to server.

        Args:
            data: Data received from client.
        """
        controller_flask.initialize(request.sid)
        first_message = controller_flask.first_time_message(request.sid)
        logger.info("Client connected")
        emit("message", first_message)

    def on_disconnect(self) -> None:
        """Disconnects client from server."""
        controller_flask.exit(request.sid)
        logger.info("Client disconnected")

    def on_message(self, data: dict) -> None:
        """Receives message from client and sends response.

        Args:
            data: Data received from client.
        """
        logger.info(f"Message received: {data}")
        response = action(request.sid, data["message"])
        if response:
            return send(response)
        send({"info": "Message Processed"})

    def on_feedback(self, data: dict) -> None:
        """Receives feedback from client.

        Args:
            data: Data received from client.
        """
        logger.info(f"Feedback received: {data}")
        send({"info": "Feedback received"})


def run(config: Dict[str, Any]) -> None:
    """Runs execute_agent in ControllerFlask and starts flask server.

    Args:
        config: Agent configuration.
    """
    controller_flask.execute_agent(config)
    socketio.run(app, host="127.0.0.1", port=environ.get("PORT", 5000))
    socketio.on_namespace(ChatNamespace("/chat"))


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
