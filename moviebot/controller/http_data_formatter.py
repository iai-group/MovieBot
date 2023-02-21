"""This file contains a class to format data for HTTP requests."""

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List

from moviebot.agent.agent import DialogueOptions

HTTP_OBJECT_MESSAGE = Dict[str, Dict[str, str]]

SHORT_ANSWER = {
    "I like this recommendation.": "I like this",
    "I have already watched it.": "Seen it",
    "Tell me more about it.": "Tell me more",
    "Recommend me something else please.": "Something else",
    "Tell me something about it.": "More information",
    "/restart": "Restart",
    "I would like a similar recommendation.": "Similar",
    "I want to restart for a new movie.": "Restart",
    "I would like to quit now.": "Quit",
}


def shorten(input: str) -> str:
    """Creates shorter versions of agent responses.

    Args:
        input: Agent response.

    Returns:
        Shorter version of input message.
    """
    return SHORT_ANSWER.get(input, input)


@dataclass
class Message:
    text: str
    intent: str
    attachment: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Button:
    title: str
    payload: str
    button_type: str = field(default="postback")


class HTTPDataFormatter:
    def __init__(self, user_id: str) -> None:
        """Initializes object to format utterance for HTTP requests."""

        self.user_id = user_id
        self.buttons = {}

    def create_buttons(
        self, user_options: DialogueOptions
    ) -> List[Dict[str, Any]]:
        """Creates a list of buttons for each agent's option.

        Args:
            user_options: Agent's options

        Returns:
            List of buttons objects.
        """
        options = []
        for option in user_options.values():
            if isinstance(option, str):
                option = [option]
            for item in option:
                button = Button(
                    title=shorten(item),
                    payload=item,
                    button_type="postback",
                )
                options.append(asdict(button))
        return options

    def text_message(
        self, message: str, intent: str = "UNK"
    ) -> HTTP_OBJECT_MESSAGE:
        """Creates a message with a text response.

        Args:
            message: Message to send.
            intent: Intent of the message. Defaults to 'UNK'.

        Returns:
            Object to send to Flask server.
        """
        message = Message(text=message, intent=intent)
        text = {
            "recipient": {"id": self.user_id},
            "message": asdict(message),
        }
        return text

    def buttons_message(
        self, buttons: List[Dict[str, Any]], text: str, intent="UNK"
    ) -> HTTP_OBJECT_MESSAGE:
        """Creates a message along with a list of buttons.

        Args:
            buttons: List of buttons.
            text: Message to send.
            intent: Intent of the message.

        Returns:
            Object with message and buttons to send to Flask server.
        """
        attachment = {
            "type": "buttons",
            "payload": {
                "buttons": buttons,
            },
        }
        message = Message(text=text, intent=intent, attachment=attachment)
        template = {
            "recipient": {"id": self.user_id},
            "message": asdict(message),
        }
        return template

    def movie_message(
        self, info: Dict[str, Any], intent: str
    ) -> HTTP_OBJECT_MESSAGE:
        """Creates a message with movie information.

        Args:
            info: Movie information.
            intent: Intent of the message.

        Returns:
            Object with movie message to send to the server.
        """
        title = f"{info['title']} {info['rating']} {info['duration']} min"
        message = Message(text=f"Do you like: {title}", intent=intent)
        return asdict(message)
