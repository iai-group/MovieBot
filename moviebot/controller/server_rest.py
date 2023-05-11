"""This file contains the flask server."""

import json
from dataclasses import dataclass, field
from os import environ
from typing import Any, Dict

from dataclasses_json import dataclass_json
from flask import Flask, request

from moviebot.controller.controller_flask import ControllerFlask

app = Flask(__name__)
controller_flask = ControllerFlask()


@dataclass_json
@dataclass
class Message:
    text: str = field(default=None)
    quick_reply: Dict[str, str] = field(default=None)
    postback: Dict[str, str] = field(default=None)


def run(config: Dict[str, Any]) -> None:
    """Runs execute_agent in ControllerFlask and starts flask server.

    Args:
        config: Agent configuration.
    """
    controller_flask.execute_agent(config)
    app.run(host="0.0.0.0", port=environ.get("PORT", 5001))


@app.route("/", methods=["GET", "POST"])
def receive_message() -> None:
    """Receives POST requests send from client."""
    if request.method == "GET":
        return "MovieBot is alive", 200
    else:
        output = request.get_json()
        print(output)
        response = action(output)
        if response:
            return response
        return {"info": "Message Processed"}


def action(output: Dict[str, Any]) -> Dict[str, Dict[str, str]]:
    """Gets user id and payload from output and runs get_message in the
    controller.

    The data should be sent with the following template:
    {
        "message": {
            "text": "TEXT_SENT",
            "quick_reply": {"payload": "QR_PAYLOAD"},
            "postback": {"payload": "PB_PAYLOAD"},
        },
        "sender": {"id": "SENDER_ID"},
    }

    Args:
        output: Output from request.

    Returns:
        Object with message to send to the server.
    """
    user_id = output["sender"]["id"]
    controller_flask.initialize(user_id)
    payload = get_message(output)
    print(payload)
    if payload is not None:
        run_method_response = controller_flask.run_method(user_id, payload)
        if run_method_response is True:
            return controller_flask.send_message(user_id, payload)
        elif run_method_response:
            return run_method_response


def get_message(output: Dict[str, Any]) -> str:
    """Gets payload from output.

    Args:
        output: Output from request.

    Returns:
        String with payload.
    """
    message = Message.from_json(json.dumps(output.get("message")))
    if message.quick_reply:
        return message.quick_reply["payload"]
    elif message.text:
        return message.text
    elif message.postback:
        return message.postback["payload"]
