"""This file contains the flask server."""

from os import environ
from typing import Any, Dict

from flask import Flask, request
from flask_socketio import Namespace, SocketIO, send

from moviebot.controller.controller_flask import ControllerFlask

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
    controller_flask.initialize(user_id)
    if message is not None:
        run_method_response = controller_flask.run_method(user_id, message)
        if run_method_response is True:
            return controller_flask.send_message(user_id, message)
        elif run_method_response:
            return run_method_response


class ChatNamespace(Namespace):
    def on_connect(self):
        print("Client connected")

    def on_disconnect(self):
        print("Client disconnected")

    def on_message(self, data: dict) -> None:
        print(data)
        response = action(request.sid, data["message"])
        if response:
            return send(response)
        return send({"info": "Message Processed"})

    def on_feedback(self, data: dict) -> None:
        print("Feedback received", data)
        return send({"info": "Feedback received"})


socketio.on_namespace(ChatNamespace("/chat"))
