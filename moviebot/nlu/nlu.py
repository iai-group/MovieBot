"""This file contains the code for the abstract NLU class of the MovieBot.
Other NLU classes should inherit from this class and implement the
`generate_dacts` method.
"""

from abc import ABC, abstractmethod
from copy import deepcopy
from typing import Any, Dict, List, Optional, Union

import wikipedia

from moviebot.core.core_types import DialogueOptions
from moviebot.core.intents import UserIntents
from moviebot.core.utterance import UserUtterance
from moviebot.dialogue_manager.dialogue_act import DialogueAct
from moviebot.dialogue_manager.dialogue_state import DialogueState
from moviebot.nlu.annotation.item_constraint import ItemConstraint
from moviebot.nlu.annotation.operator import Operator
from moviebot.nlu.annotation.slots import Slots
from moviebot.nlu.user_intents_checker import UserIntentsChecker


class NLU(ABC):
    def __init__(self, config: Dict[str, Any]) -> None:
        """The abstract NLU class.

        Args:
            config: Paths to domain, database and tag words for slots in NLU.
        """
        self.config = config
        if config:
            self.intents_checker = UserIntentsChecker(config)

    @abstractmethod
    def generate_dacts(
        self,
        user_utterance: UserUtterance,
        options: DialogueOptions,
        dialogue_state: DialogueState = None,
    ) -> List[DialogueAct]:
        """Processes the utterance according to dialogue state and
        generate user dialogue acts for Agent to understand.

        Args:
            user_utterance: UserUtterance class containing user input.
            options: A list of options provided to the user to choose from.
            dialogue_state: The current dialogue state, if available. Defaults
              to None.

        Raises:
            NotImplementedError: If the method is not implemented.
        Returns:
            A list of dialogue acts.
        """
        raise NotImplementedError

    def _get_selected_option(
        self,
        user_utterance: UserUtterance,
        options: DialogueOptions,
        item_in_focus: Union[Dict[str, Any], None],
    ) -> List[DialogueAct]:
        """Checks if user selected any of the suggested options.

        Args:
            user_utterance: User utterance.
            options: Options given to the user.
            item_in_focus: Item recommended to user on previous turn.

        Returns:
            A list with at most one item (i.e., the selected option).
        """
        raw_utterance = user_utterance.text
        dacts = []
        for dact, value in options.items():
            if (
                isinstance(value, list) and value[0] == raw_utterance
            ) or value == raw_utterance:
                if dact.intent == UserIntents.CONTINUE_RECOMMENDATION:
                    dact.params = self.generate_params_continue_recommendation(
                        item_in_focus
                    )
                dacts.append(dact)
                break
        return dacts

    def generate_params_continue_recommendation(
        self, item_in_focus: Dict[str, Any]
    ) -> Optional[ItemConstraint]:
        """Finds similar movies based on the title of item in focus.

        Args:
            item_in_focus: Item in conversation focus.

        Returns:
            Item constraint with titles of similar movies to the item in focus.
        """
        movie_title = item_in_focus[Slots.TITLE.value]
        for term in ["film", "movie"]:
            results = wikipedia.search(
                f"I need a {term} similar to {movie_title}", 20
            )
            results = [r.split("(")[0].strip() for r in results]
            for result in deepcopy(results):
                if (
                    result
                    not in self.intents_checker.slot_values[Slots.TITLE.value]
                ):
                    results.remove(result)
            if len(results) > 0:
                return [
                    ItemConstraint(Slots.TITLE.value, Operator.EQ, str(results))
                ]
