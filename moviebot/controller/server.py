"""This file contains the flask server."""

import logging
from os import environ
from typing import Any, Dict

from flask import Flask, request
from flask_socketio import Namespace, SocketIO, emit, send

from moviebot.controller.controller_flask import ControllerFlask

logger = logging.getLogger()

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
controller_flask = ControllerFlask()


def run(config: Dict[str, Any]) -> None:
    """Runs execute_agent in ControllerFlask and starts flask server.

    Args:
        config: Agent configuration.
    """
    controller_flask.execute_agent(config)
    socketio.run(app, host="127.0.0.1", port=environ.get("PORT", 5000))


def action(user_id: str, message: Dict[str, Any]) -> Dict[str, Dict[str, str]]:
    """Gets user id and payload from output and runs get_message in the
    controller.

    Args:
        output: Output from request.

    Returns:
        Object with message to send to the server.
    """
    if message is not None:
        run_method_response = controller_flask.run_method(user_id, message)
        if run_method_response is True:
            return controller_flask.send_message(user_id, message)
        elif run_method_response:
            return run_method_response


class ChatNamespace(Namespace):
    def on_connect(self, data: Dict[str, Any]) -> None:
        controller_flask.initialize(request.sid)
        first_message = controller_flask.first_time_message(request.sid)
        logger.info("Client connected")
        emit("message", first_message)

    def on_disconnect(self) -> None:
        controller_flask.exit(request.sid)
        logger.info("Client disconnected")

    def on_message(self, data: dict) -> None:
        logger.info("Message received")
        response = action(request.sid, data["message"])
        if response:
            return send(response)
        send({"info": "Message Processed"})

    def on_feedback(self, data: dict) -> None:
        logger.info("Feedback received", data)
        send({"info": "Feedback received"})


socketio.on_namespace(ChatNamespace("/chat"))
