"""Broker connecting MovieBot agent to the user."""
from collections import defaultdict
from dataclasses import asdict
from typing import TYPE_CHECKING

from dialoguekit.connector import DialogueConnector
from dialoguekit.core.annotated_utterance import AnnotatedUtterance
from dialoguekit.participant import User

from moviebot.agent.agent import MovieBotAgent
from moviebot.core.utterance.utterance import UserUtterance

if TYPE_CHECKING:
    from moviebot.controller.controller import Controller


class MovieBotDialogueConnector(DialogueConnector):
    def __init__(
        self,
        agent: MovieBotAgent,
        user: User,
        platform: "Controller",
        conversation_id: str = None,
        save_dialogue_history: bool = True,
    ) -> None:
        """Initializes a dialogue connector.

        Args:
            agent: MovieBot agent.
            user: User.
            platform: Controller.
            conversation_id: Conversation ID. Defaults to None.
            save_dialogue_history: Flag to save the dialogue or not. Defaults to
              True.
        """
        super().__init__(
            agent, user, platform, conversation_id, save_dialogue_history
        )

    def register_user_utterance(
        self, annotated_utterance: AnnotatedUtterance
    ) -> None:
        """Registers a user utterance.

        Args:
            annotated_utterance: Annotated utterance.
        """
        user_options = self._dialogue_history.utterances[-1].metadata.get(
            "options", {}
        )
        self._dialogue_history.add_utterance(annotated_utterance)
        self._platform.display_user_utterance(
            self._user.id, annotated_utterance
        )
        user_utterance = UserUtterance(
            **asdict(annotated_utterance.get_utterance())
        )
        self._agent.receive_utterance(user_utterance, user_options)

    def close(self) -> None:
        """Closes the conversation."""
        if self._save_dialogue_history:
            self._stringify_dialogue_acts()
            self._dump_dialogue_history()

    def _stringify_dialogue_acts(self) -> None:
        """Stringifies the dialogue acts."""
        for utterance in self._dialogue_history.utterances:
            options = utterance.metadata.get("options", {})
            options_str = defaultdict(list)
            for da, opts in options.items():
                options_str[str(da)] = opts
            utterance.metadata["options"] = options_str
