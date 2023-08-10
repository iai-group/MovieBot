"""Broker connecting MovieBot agent to the user."""
from collections import defaultdict
from typing import TYPE_CHECKING

from dialoguekit.connector import DialogueConnector
from dialoguekit.participant import User

from moviebot.agent.agent import MovieBotAgent

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

    def close(self) -> None:
        """Closes the conversation."""
        if self._save_dialogue_history:
            self._stringify_dialogue_acts()
            self._dump_dialogue_history()

    def _stringify_dialogue_acts(self) -> None:
        """Stringifies the dialogue acts before dump."""
        for utterance in self._dialogue_history.utterances:
            options = utterance.metadata.get("options", {})
            options_str = defaultdict(list)
            for da, opts in options.items():
                options_str[str(da)] = opts
            utterance.metadata["options"] = options_str
