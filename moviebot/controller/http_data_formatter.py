"""This file contains methods to format data for HTTP requests."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Tuple

from dialoguekit.core import AnnotatedUtterance, Utterance
from moviebot.core.core_types import DialogueOptions

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
    intent: str = None
    attachments: List[Attachment] = field(default_factory=list)

    @classmethod
    def from_utterance(self, utterance: Utterance) -> Message:
        """Converts an utterance to a message.

        Args:
            utterance: An instance of Utterance.

        Returns:
            An instance of Message.
        """
        message = Message(utterance.text)
        if isinstance(utterance, AnnotatedUtterance):
            message.intent = str(utterance.intent)
            if utterance.metadata.get("options"):
                message.attachments.append(
                    get_buttons_attachment(utterance.metadata.get("options"))
                )
            if "**" in message.text and utterance.metadata.get(
                "recommended_item"
            ):
                # NLG adds ** in utterance text when a recommendation is made.
                message.text, movie_attachments = get_movie_message_data(
                    utterance.metadata.get("recommended_item")
                )
                message.attachments.append(movie_attachments)
        return message


@dataclass
class Button:
    title: str
    payload: str
    button_type: str = field(default="postback")


@dataclass
class Response:
    recipient: str
    message: Message


def get_buttons_attachment(user_options: DialogueOptions) -> Attachment:
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
    return Attachment(type="buttons", payload={"buttons": options})


def get_movie_message_data(info: Dict[str, Any]) -> Tuple[str, Attachment]:
    """Creates formatted message with movie information and movie image
    attachment.

    Args:
        info: Movie information.

    Returns:
        Formatted message with movie information and movie image attachment.
    """
    text = f"""Have you seen {info['title']} {info['imdb_rating']}
     {info['duration']} min"""
    attachment = Attachment(
        type="images", payload={"images": [info["cover_image"]]}
    )
    return text, attachment
