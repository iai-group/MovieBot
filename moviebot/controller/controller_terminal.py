"""This file contains the Controller class which controls the flow of the
conversation while the user interacts with the agent using python console.
"""

from typing import Any, Dict, Type

import questionary
from questionary.constants import INDICATOR_SELECTED

from dialoguekit.core import Utterance
from dialoguekit.participant import User
from dialoguekit.platforms import TerminalPlatform
from moviebot.agent.agent import MovieBotAgent
from moviebot.controller.controller import Controller
from moviebot.core.core_types import DialogueOptions


class ControllerTerminal(Controller, TerminalPlatform):
    """This is the main class that controls the other components of the
    IAI MovieBot. The controller executes the conversational agent."""

    def __init__(
        self,
        agent_class: Type[MovieBotAgent],
        agent_args: Dict[str, Any] = {},
        user_id: str = "terminal_user",
    ) -> None:
        """Represents a terminal platform. It handles a single user.

        Args:
            agent_class: The class of the agent. Defaults to MovieBotAgent.
            agent_args: The arguments to pass to the agent. Defaults to empty
              dict.
            user_id: User ID. Defaults to "terminal_user".
        """
        super().__init__(agent_class, agent_args)
        self._user_id = user_id

    def start(self) -> None:
        """Starts the platform."""
        self.connect(self._user_id)
        user: User = self._active_users[self._user_id]
        while True:
            if not user.ready_for_input:
                break
            user_options = user._dialogue_connector.dialogue_history.utterances[
                -1
            ].metadata.get("options", {})
            text = self.display_user_prompt(user_options)
            self.message(self._user_id, text)
        self.disconnect(self._user_id)

    def display_user_prompt(self, user_options: DialogueOptions) -> str:
        """Displays a user prompt.

        Args:
            user_options: The options to display to the user.

        Returns:
            The user's response.
        """
        user_prompt = "USER: "
        if not user_options:
            answer = questionary.text(
                user_prompt,
                qmark="",
            ).ask()
        else:
            options = [
                item if isinstance(item, str) else item[0]
                for item in user_options.values()
            ]
            formatted_options = f"\n  {INDICATOR_SELECTED}  ".join(options)
            answer = questionary.autocomplete(
                f" {INDICATOR_SELECTED}  "
                f"{formatted_options}\n {user_prompt}",
                qmark="",
                choices=options,
            ).ask()
        return answer

    def display_agent_utterance(
        self,
        user_id: str,
        utterance: Utterance,
        user_options: DialogueOptions = None,
    ) -> None:
        """Displays an agent utterance.

        Args:
            user_id: User ID.
            utterance: An instance of Utterance.
            user_options: The options to display to the user. Defaults to None.
        """
        agent_prompt = f"AGENT: {utterance.text}\n"
        questionary.print(f" {agent_prompt}", style="bold")

    def display_user_utterance(
        self, user_id: str, utterance: Utterance
    ) -> None:
        """Displays a user utterance.

        Args:
            user_id: User ID.
            utterance: An instance of Utterance.
        """
        pass
