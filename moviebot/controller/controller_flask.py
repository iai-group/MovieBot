"""This file contains the Controller class which controls the flow of the
conversation while the user interacts with the agent using Flask."""

from datetime import datetime
from typing import Any, Callable, Dict, Union

import moviebot.controller.http_data_formatter as http_formatter
from moviebot.agent.agent import Agent, DialogueOptions
from moviebot.controller.controller import Controller
from moviebot.core.utterance.utterance import UserUtterance


class ControllerFlask(Controller):
    def __init__(self) -> None:
        """Initializes structs for Controller and sends the get started button
        to the client."""
        self.token = ""
        self.agent: Dict[str, Agent] = {}
        self.record_data: Dict[str, Dict[str, Any]] = {}
        self.record_data_agent: Dict[str, Dict[str, Any]] = {}
        self.user_options: Dict[str, DialogueOptions] = {}
        self.agent_response: Dict[str, str] = {}
        self.configuration: Dict[str, Any] = {}
        self.info: Dict[str, Any] = {}
        self.users: Dict[str, bool] = {}
        self.load_data: Dict[str, Any] = {}
        self.path = ""
        self.methods = [
            {"payload": "/start", "action": self.start_conversation},
            {"payload": "/help", "action": self.instructions},
            {"payload": "/accept", "action": self.accept_license},
            {"payload": "/reject", "action": self.reject_license},
            {"payload": "/restart", "action": self.restart},
            {"payload": "/exit", "action": self.exit},
            {"payload": "/delete", "action": self.delete_data},
            {"payload": "/policy", "action": self.privacy_policy},
            {"payload": "/store", "action": self.accept_license},
        ]
        self.agent_intent = ""

    def initialize(self, user_id: str) -> None:
        """Initializes structs for a new user.

        Args:
            user_id: User id.
        """
        if user_id not in self.agent:
            self.user_options[user_id] = {}
            # By defaults the user accepts license agreement.
            self.users[user_id] = True
            self.agent[user_id] = self.initialize_agent()

    def start_conversation(
        self, user_id: str, restart=False
    ) -> http_formatter.HTTP_OBJECT_MESSAGE:
        """Starts conversation with agent and sends instructions to user.

        Args:
            user_id: User id.
            restart: Whether or not to restart the agent.

        Returns:
            Object with start message to send to the server.
        """
        (
            self.agent_response[user_id],
            self.user_options[user_id],
            self.record_data_agent[user_id],
        ) = self.agent[user_id].start_dialogue(user_id, restart)
        msg = self.greetings()
        if restart:
            msg = self.agent_response[user_id]
        else:
            instructions = self.instructions(user_id)
            msg = "\n\n".join(
                [
                    msg,
                    "INSTRUCTIONS",
                    instructions["message"]["text"],
                ]
            )

        return http_formatter.text_message(
            user_id=user_id,
            message=msg,
            intent=self.agent_intent,
        )

    def movie_info(self, movie_id: str, user_id: str) -> None:
        """Retrieves relevant movie info from database for selected user.

        Args:
            movie_id: Movie id.
            user_id: User id.
        """
        for row in self.get_cursor().execute(
            f'SELECT * FROM movies_v2 WHERE ID="{movie_id}"'
        ):
            self.info[user_id] = {
                "title": row[1],
                "rating": row[4],
                "duration": row[6],
                "summary": row[10],
                "image_url": row[9],
                "imdb_link": row[12],
            }

    def execute_agent(self, configuration: Dict[str, Any]) -> None:
        """Runs the conversational agent and executes the dialogue by calling
        the basic components of IAI MovieBot.

        Args:
            configuration: Configuration for the agent.
        """
        self.configuration = configuration
        self.configuration["new_user"] = {}
        if self.configuration["BOT_HISTORY"]["path"]:
            self.path = self.configuration["BOT_HISTORY"]["path"]

    def restart(self, user_id: str) -> Callable:
        """Restarts agent for this user."""
        return self.start_conversation(user_id, True)

    def get_movie_id(self, response: str) -> str:
        """Retrieves movie id from agent response string.

        Args:
            response: Agent response.

        Returns:
            Movie id.
        """
        if "/tt" in response:
            start = response.find("/tt")
            movie_id = response[start + 3 : start + 10]
            return movie_id

    def continue_dialogue(self, user_id: str, payload: str) -> None:
        """Continues dialogue with the agent. Updates movie info.

        Args:
            user_id: User id.
            payload: User payload.
        """
        user_utterance = UserUtterance({"text": payload})
        (
            self.agent_response[user_id],
            self.user_options[user_id],
            self.record_data_agent[user_id],
        ) = self.agent[user_id].continue_dialogue(
            user_utterance, self.user_options[user_id]
        )
        if self.users.get(user_id, True):
            self.record(user_id, payload)
        movie_id = self.get_movie_id(self.agent_response[user_id])
        self.movie_info(movie_id, user_id)

    def accept_license(self, user_id: str, b_accept: bool = True) -> Callable:
        """User accepts license agreement. Data for this user is stored
        in conversation history.

        Args:
            user_id: User id.
            b_accept: Whether or not the user accepts the license agreement.
              Defaults to True.
        """
        self.users[user_id] = b_accept
        return self.storage_instructions(user_id, b_accept)

    def reject_license(self, user_id: str) -> Callable:
        """User rejects license agreement. Data for this user is not stored
        in conversation history.

        Args:
            user_id: User id.
        """
        return self.accept_license(user_id=user_id, b_accept=False)

    def record(self, user_id: str, payload: str) -> None:
        """Records user conversation if user has accepted privacy policy.

        Args:
            user_id: User id.
            payload: User payload.
        """
        if self.agent[user_id].bot_recorder:
            self.record_data[user_id] = {
                "Timestamp": str(datetime.now()),
                "User_Input": payload,
            }
            self.record_data[user_id].update(self.record_data_agent[user_id])
            self.agent[user_id].bot_recorder.record_user_data(
                user_id, self.record_data[user_id]
            )

    def delete_data(self, user_id: str) -> http_formatter.HTTP_OBJECT_MESSAGE:
        """Deletes stored conversation history for user.

        Args:
            user_id: User id.
        """
        deleted = self.delete_history(self.path, user_id)
        if deleted:
            self.users[user_id] = False
            return http_formatter.text_message(
                user_id=user_id,
                message="Conversation history deleted.",
                intent=self.agent_intent,
            )

        return http_formatter.text_message(
            user_id=user_id,
            message="No conversation history.",
            intent=self.agent_intent,
        )

    def send_message(
        self, user_id: str, payload: str
    ) -> http_formatter.HTTP_OBJECT_MESSAGE:
        """Sends template, buttons or text based on current agent options.

        Args:
            user_id: User id.
            payload: User payload.

        Returns:
            Object with message to send to the server.
        """
        self.continue_dialogue(user_id, payload)
        if self.user_options[user_id]:
            if "**" in self.agent_response[user_id]:
                return http_formatter.movie_message(
                    info=self.info[user_id], intent=self.agent_intent
                )
            else:
                buttons = http_formatter.create_buttons(
                    self.user_options[user_id]
                )
                return http_formatter.buttons_message(
                    user_id=user_id,
                    buttons=buttons,
                    text=self.agent_response[user_id],
                    intent=self.agent_intent,
                )
        else:
            return http_formatter.text_message(
                user_id=user_id,
                message=self.agent_response[user_id],
                intent=self.agent_intent,
            )

    def run_method(self, user_id: str, payload: str) -> Union[bool, Callable]:
        """Runs methods for specific user inputs.

        Args:
            user_id: User id.
            payload: User payload.

        Returns:
            Output of the payload action if possible.
        """
        for item in self.methods:
            if payload.lower() == item["payload"]:
                func = item.get("action")
                return func(user_id)
        return True

    def exit(self, user_id: str) -> http_formatter.HTTP_OBJECT_MESSAGE:
        """Ends conversation and deletes user id from agent.

        Args:
            user_id: User id.
        """
        self.agent_response[
            user_id
        ] = "You are exiting. I hope you found a movie. Bye."
        self.agent[user_id].end_dialogue()
        del self.agent[user_id]
        return http_formatter.text_message(
            user_id=user_id,
            message=self.agent_response[user_id],
            intent=self.agent_intent,
        )

    def instructions(self, user_id: str) -> http_formatter.HTTP_OBJECT_MESSAGE:
        """Creates utterance with usage instructions.

        The instructions are sent when the conversation starts and when '/help'
        is received.

        Args:
            user_id: User id.

        Returns:
            Object with instructions message to send to the server.
        """
        response = (
            "To start the conversation say Hi or Hello, or simply "
            'enter you preferences ("I want a horror movie from the 90s").\n\n'
            'To restart the recommendation process, issue "/restart".\n\n'
            'To end the conversation, issue "/exit" or say Bye/Goodbye.\n\n'
            'To see these instructions again, issue: "/help".'
        )

        return http_formatter.text_message(
            user_id=user_id, message=response, intent="REVEAL.DISCLOSE"
        )

    def storage_instructions(
        self, user_id: str, b_accept: bool
    ) -> http_formatter.HTTP_OBJECT_MESSAGE:
        """Instructions for deleting stored conversation history.

        Args:
            user_id: User id.
            b_accept: Whether or not the user accepts the license agreement.

        Returns:
            Object with storage information to send to the server.
        """
        policy = (
            'Type "/delete" at any time to stop storing and delete conversation'
            ' history.\n\nType "/start" to continue.'
        )
        if not b_accept:
            policy = (
                "Your conversation history will not be saved.\n\n"
                'Type "/start" to continue.'
            )
        return http_formatter.text_message(
            user_id=user_id, message=policy, intent="REVEAL.DISCLOSE"
        )

    def privacy_policy(
        self, user_id: str
    ) -> http_formatter.HTTP_OBJECT_MESSAGE:
        """Creates utterance with policy.

        Args:
            user_id: User id. Defaults to None.

        Returns:
            Object with privacy message to send to the server.
        """
        policy = (
            "We may store some information to improve recommendations.\n"
            "You may delete stored data at any time.\n"
            "Read more in our privacy policy\n"
            "Privacy Policy: https://iai-group.github.io/moviebot/Privacy_policy.html\n"  # noqa
            'To accept the privacy policy write "/store"\n'
            'To continue without accepting write "/reject"'
        )
        return http_formatter.text_message(
            user_id=user_id, message=policy, intent=self.agent_intent
        )

    def greetings(self) -> str:
        """Returns a greeting message."""
        return (
            "Hi there. I am IAI MovieBot, your movie recommending buddy. I"
            " can recommend you movies based on your preferences.\nI will ask"
            " you a few questions and based on your answers, I will try to"
            " find a movie for you.\n\n"
        )
