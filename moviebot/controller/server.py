"""This file contains the flask server."""

from os import environ

from flask import Flask, request

from moviebot.controller.controller_flask import ControllerFlask

app = Flask(__name__)
controller_flask = ControllerFlask()


def run(config):
    """Runs execute_agent in ControllerTelegram and starts flask server.

    Args:
        config: agent settings

    """
    controller_flask.execute_agent(config)
    app.run(host="0.0.0.0", port=environ.get("PORT", 5001))


@app.route("/", methods=["POST"])
def receive_message():
    """Receives POST requests send from client."""
    output = request.get_json()
    print(output)
    response = action(output)
    if response:
        return response
    return "Message Processed"


def action(output):
    """Gets user id and payload from output and runs get_message in the controller.

    Args:
        output: output from request

    """
    event = output["entry"][0]["messaging"][0]
    user_id = event["sender"]["id"]
    controller_flask.initialize(user_id)
    payload = get_message(output)
    print(payload)
    if payload is not None:
        run_method_response = controller_flask.run_method(user_id, payload)
        if run_method_response == True:
            return controller_flask.send_message(user_id, payload)
        elif run_method_response:
            return run_method_response


def get_message(output):
    """Gets payload from output.
    Args:
        output: output from request

    Returns:
        string with payload

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
