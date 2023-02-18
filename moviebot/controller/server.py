"""This file contains the flask server."""

from os import environ
from typing import Any, Dict

from flask import Flask, request

from moviebot.controller.controller_flask import ControllerFlask

app = Flask(__name__)
controller_flask = ControllerFlask()


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
        return "Message Processed"


def action(output: Dict[str, Any]) -> Dict[str, Dict[str, str]]:
    """Gets user id and payload from output and runs get_message in the
    controller.

    Args:
        output: Output from request.

    Returns:
        Object with message to send to the server.
    """
    event = output["entry"][0]["messaging"][0]
    user_id = event["sender"]["id"]
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
    for event in output["entry"]:
        for message in event["messaging"]:
            if message.get("message"):
                if message["message"].get("quick_reply"):
                    return message["message"]["quick_reply"]["payload"]
                if message["message"].get("text"):
                    return message["message"]["text"]
            if message.get("postback"):
                return message["postback"]["payload"]
