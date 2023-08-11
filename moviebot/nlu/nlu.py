"""NLU (Natural Language Understander) is a main component of Dialogue Systems.

NLU understands the user requirements and intents for the system to
generate an appropriate response.
"""


from typing import Any, Dict, List, Union

from moviebot.core.intents.agent_intents import AgentIntents
from moviebot.core.intents.user_intents import UserIntents
from moviebot.core.utterance.utterance import UserUtterance
from moviebot.database.db_movies import DataBase
from moviebot.dialogue_manager.dialogue_act import DialogueAct
from moviebot.dialogue_manager.dialogue_state import DialogueState
from moviebot.nlu.annotation.values import Values
from moviebot.nlu.user_intents_checker import UserIntentsChecker
from moviebot.ontology.ontology import Ontology

DialogueOptions = Dict[DialogueAct, Union[str, List[str]]]


class NLU:
    def __init__(self, config):
        """NLU is a basic natural language understander to generate dialogue
        acts for the Conversational Agent.

        Implementation of this NLU is designed to work for Slot-Filling
        applications. The purpose of this class is to provide a quick way of
        running Conversational Agents, sanity checks, and to aid debugging.
        Loads the ontology and database, and preprocess the database so that
        we avoid some computations at runtime. Also create patterns to
        understand natural language.

        Args:
            config: Paths to ontology, database and tag words for slots in NLU.
        """
        self.ontology: Ontology = config["ontology"]
        self.database: DataBase = config["database"]
        self.intents_checker = UserIntentsChecker(config)

    def generate_dact(  # noqa: C901
        self,
        user_utterance: UserUtterance,
        options: DialogueOptions,
        dialogue_state: DialogueState = None,
    ):
        """Processes the utterance according to dialogue state and context and
        generate a user dialogue act for Agent to understand.

        Args:
            user_utterance: UserUtterance class containing user input.
            options: A list of options provided to the user to choose from.
            dialogue_state: The current dialogue state, if available. Defaults
              to None.

        Returns:
            A list of dialogue acts.
        """
        # this is the top priority. The agent must check if user selected
        # any option
        selected_option = self.get_selected_option(
            user_utterance, options, dialogue_state.item_in_focus
        )
        if selected_option:
            return selected_option

        # Define a list of dialogue acts for this specific utterance
        user_dacts = []

        # process the utterance for necessary
        # utterance = self.intents_checker._lemmatize_value(raw_utterance)
        self.dialogue_state = dialogue_state

        # check if user is ending the conversation
        user_dacts.extend(
            self.intents_checker.check_basic_intent(
                user_utterance, UserIntents.BYE
            )
        )
        if len(user_dacts) > 0:
            return user_dacts

        # check if it's the start of a conversation
        if not self.dialogue_state.last_agent_dacts:
            user_dacts.extend(
                self.intents_checker.check_reveal_voluntary_intent(
                    user_utterance
                )
            )
            if len(user_dacts) == 0:
                user_dacts.extend(
                    self.intents_checker.check_basic_intent(
                        user_utterance, UserIntents.HI
                    )
                )
            if len(user_dacts) > 0:
                return user_dacts
            else:
                return None

        for last_agent_dact in self.dialogue_state.last_agent_dacts:
            if last_agent_dact.intent == AgentIntents.WELCOME:
                user_dacts.extend(
                    self.intents_checker.check_reveal_voluntary_intent(
                        user_utterance
                    )
                )
                if len(user_dacts) == 0:
                    user_dacts.extend(
                        self.intents_checker.check_basic_intent(
                            user_utterance, UserIntents.ACKNOWLEDGE
                        )
                    )
                if len(user_dacts) > 0:
                    return user_dacts
            elif last_agent_dact.intent == AgentIntents.ELICIT:
                user_dacts.extend(
                    self.intents_checker.check_reveal_intent(
                        user_utterance, last_agent_dact
                    )
                )
                if len(user_dacts) == 0 or any(
                    [
                        param.value in Values.__dict__.values()
                        for dact in user_dacts
                        for param in dact.params
                    ]
                ):
                    user_dacts.extend(
                        self.intents_checker.check_reveal_voluntary_intent(
                            user_utterance
                        )
                    )
                if len(user_dacts) > 0:
                    return user_dacts

        if dialogue_state.agent_made_offer:
            user_dacts.extend(
                self.intents_checker.check_reject_intent(user_utterance)
            )
        if len(user_dacts) == 0:
            user_dacts.extend(
                self.intents_checker.check_inquire_intent(user_utterance)
            )
        if len(user_dacts) == 0:
            user_dacts.extend(
                self.intents_checker.check_reveal_voluntary_intent(
                    user_utterance
                )
            )
        if len(user_dacts) == 0:
            deny_dact = self.intents_checker.check_basic_intent(
                user_utterance, UserIntents.DENY
            )
            if len(deny_dact) > 0:
                deny_dact[0].intent = UserIntents.INQUIRE
                user_dacts.extend(deny_dact)
        if len(user_dacts) > 0:
            return user_dacts

        if len(user_dacts) == 0:
            user_dacts.append(DialogueAct(UserIntents.UNK, []))
        return user_dacts

    def get_selected_option(
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
                    dact.params = self.intents_checker.generate_params_continue_recommendation(  # noqa: E501
                        item_in_focus
                    )
                dacts.append(dact)
                break
        return dacts
