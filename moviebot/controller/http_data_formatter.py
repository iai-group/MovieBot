"""This file contains methods to format data for HTTP requests."""

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


def _shorten(input: str) -> str:
    """Creates shorter versions of agent responses.

    Args:
        input: Agent response.

    Returns:
        Shorter version of input message.
    """
    return SHORT_ANSWER.get(input, input)


@dataclass
class Attachment:
    type: str
    payload: Dict[str, Any]


@dataclass
class Message:
    text: str
    intent: str
    attachments: List[Attachment] = field(default_factory=list)


@dataclass
class Button:
    title: str
    payload: str
    button_type: str = field(default="postback")


def create_buttons(user_options: DialogueOptions) -> List[Dict[str, Any]]:
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
                title=_shorten(item),
                payload=item,
                button_type="postback",
            )
            options.append(asdict(button))
    return options


def text_message(
    user_id: str, message: str, intent: str = "UNK"
) -> HTTP_OBJECT_MESSAGE:
    """Creates a message with a text response.

    Args:
        user_id: Id of the recipient.
        message: Message to send.
        intent: Intent of the message. Defaults to 'UNK'.

    Returns:
        Object to send to Flask server.
    """
    message = Message(text=message, intent=intent)
    text = {
        "recipient": {"id": user_id},
        "message": asdict(message),
    }
    return text


def attachment_message(
    user_id: str,
    message: str,
    attachments: List[Attachment],
    intent: str = "UNK",
) -> HTTP_OBJECT_MESSAGE:
    """Creates a message containing an attachment.

    Args:
        user_id: Id of the recipient.
        message: Message to send.
        attachments: Attachments to send.
        intent: Intent of the message.

    Returns:
        Object with message containing an attachment to send to Flask server.
    """
    message = Message(text=message, intent=intent, attachments=attachments)
    template = {
        "recipient": {"id": user_id},
        "message": asdict(message),
    }
    return template


def buttons_message(
    user_id: str, buttons: List[Dict[str, Any]], text: str, intent="UNK"
) -> HTTP_OBJECT_MESSAGE:
    """Creates a message along with a list of buttons.

    Args:
        user_id: Id of the recipient.
        buttons: List of buttons.
        text: Message to send.
        intent: Intent of the message.

    Returns:
        Object with message and buttons to send to Flask server.
    """
    attachment = Attachment(type="buttons", payload={"buttons": buttons})
    return attachment_message(
        user_id=user_id, message=text, attachments=[attachment], intent=intent
    )


def movie_message(
    user_id: str, info: Dict[str, Any], intent: str
) -> HTTP_OBJECT_MESSAGE:
    """Creates a message with movie information.

    Args:
        user_id: Id of the recipient.
        info: Movie information.
        intent: Intent of the message.

    Returns:
        Object with movie message to send to the server.
    """
    text = (
        f"Have you seen {info['title']} {info['rating']} {info['duration']} min"
    )
    attachment = Attachment(
        type="images", payload={"images": [info["image_url"]]}
    )

    return attachment_message(
        user_id=user_id, message=text, attachments=[attachment], intent=intent
    )
