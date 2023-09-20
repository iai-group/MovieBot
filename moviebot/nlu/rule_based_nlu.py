"""NLU (Natural Language Understander) is a main component of Dialogue Systems.

NLU understands the user requirements and intents for the system to
generate an appropriate response.
"""


from typing import Any, Dict, List, Union

from moviebot.core.core_types import DialogueOptions
from moviebot.core.intents.agent_intents import AgentIntents
from moviebot.core.intents.user_intents import UserIntents
from moviebot.core.utterance.utterance import UserUtterance
from moviebot.dialogue_manager.dialogue_act import DialogueAct
from moviebot.dialogue_manager.dialogue_state import DialogueState
from moviebot.nlu.annotation.values import Values
from moviebot.nlu.nlu import NLU


class RuleBasedNLU(NLU):
    def __init__(self, config: Dict[str, Any]) -> None:
        """RuleBasedNLU is a basic natural language understander to generate
        dialogue acts for the Conversational Agent.

        Implementation of this NLU is designed to work for Slot-Filling
        applications. The purpose of this class is to provide a quick way of
        running Conversational Agents, sanity checks, and to aid debugging.
        Loads the domain and database, and preprocess the database so that
        we avoid some computations at runtime. Also create patterns to
        understand natural language.

        Args:
            config: Paths to domain, database and tag words for slots in NLU.
        """
        super().__init__(config)

    def _process_first_turn(
        self, user_utterance: UserUtterance
    ) -> List[DialogueAct]:
        """Generates dialogue acts for the first turn of the conversation.

        The system checks if the user provided any voluntary preferences or
        if the user is just saying hi.

        Args:
            user_utterance: User utterance.

        Returns:
            A list of dialogue acts.
        """
        return (
            self.intents_checker.check_reveal_voluntary_intent(user_utterance)
            or self.intents_checker.check_basic_intent(
                user_utterance, UserIntents.HI
            )
            or [DialogueAct(UserIntents.UNK, [])]
        )

    def _process_last_agent_dacts(
        self, user_utterance: UserUtterance, last_agent_dacts: List[DialogueAct]
    ) -> List[DialogueAct]:
        """Processes response to agent dialogue acts from previous turn.


        Args:
            user_utterance: User utterance.
            last_agent_dacts: Last agent dialogue acts.

        Returns:
            A list of dialogue acts. Returns an empty list if user haven't
            provided any voluntary preferences or preferences after elicitation.
        """
        for last_agent_dact in last_agent_dacts:
            if last_agent_dact.intent == AgentIntents.WELCOME:
                user_dacts = self._follow_up_welcome(user_utterance)
                if user_dacts:
                    return user_dacts
            elif last_agent_dact.intent == AgentIntents.ELICIT:
                user_dacts = self._follow_up_elicit(
                    user_utterance, last_agent_dact
                )
                if user_dacts:
                    return user_dacts
        return []

    def _process_recommendation_feedback(
        self, user_utterance: UserUtterance
    ) -> List[DialogueAct]:
        """Processes recommendation feedback from the user.

        The function checks if the user is rejecting the recommendation,
        inquiring about the recommendation, or providing voluntary preferences.

        Args:
            user_utterance: User utterance.

        Returns:
            A list of dialogue acts.
        """
        feedback_intents = [
            self.intents_checker.check_reject_intent,
            self.intents_checker.check_inquire_intent,
            self.intents_checker.check_reveal_voluntary_intent,
            self._convert_deny_to_inquire,
        ]

        for check_intent in feedback_intents:
            user_dacts = check_intent(user_utterance)
            if user_dacts:
                return user_dacts
        return []

    def _follow_up_welcome(
        self, user_utterance: UserUtterance
    ) -> List[DialogueAct]:
        """Follow up on welcome intent.

        Args:
            user_utterance: User utterance.

        Returns:
            A list of dialogue acts.
        """
        return self.intents_checker.check_reveal_voluntary_intent(
            user_utterance
        ) or self.intents_checker.check_basic_intent(
            user_utterance, UserIntents.ACKNOWLEDGE
        )

    def _follow_up_elicit(
        self, user_utterance: UserUtterance, last_agent_dact: DialogueAct
    ) -> List[DialogueAct]:
        """Follow up on elicit intent.

        Args:
            user_utterance: User utterance.
            last_agent_dact: Last agent dialogue act.

        Returns:
            A list of dialogue acts.
        """
        user_dacts = self.intents_checker.check_reveal_intent(
            user_utterance, last_agent_dact
        )
        elicitation_is_irrelevant = any(
            [
                param.value in Values.__dict__.values()
                for dact in user_dacts
                for param in dact.params
            ]
        )
        if not user_dacts or elicitation_is_irrelevant:
            user_dacts.extend(
                self.intents_checker.check_reveal_voluntary_intent(
                    user_utterance
                )
            )
        return user_dacts

    def _convert_deny_to_inquire(
        self, user_utterance: UserUtterance
    ) -> List[DialogueAct]:
        """Converts deny intent to inquire intent.

        Args:
            user_utterance: User utterance.

        Returns:
            A list of dialogue acts.
        """
        # TODO: It is unclear the purpose of this function. It should be
        # removed or refactored.
        # https://github.com/iai-group/MovieBot/issues/199
        deny_dact = self.intents_checker.check_basic_intent(
            user_utterance, UserIntents.DENY
        )
        if deny_dact:
            deny_dact[0].intent = UserIntents.INQUIRE
        return deny_dact

    def generate_dacts(
        self,
        user_utterance: UserUtterance,
        options: DialogueOptions,
        dialogue_state: DialogueState,
    ) -> List[DialogueAct]:
        """Processes the utterance according to dialogue state and
        generates a user dialogue act for Agent to understand.

        Args:
            user_utterance: UserUtterance class containing user input.
            options: A list of options provided to the user to choose from.
            dialogue_state: The current dialogue state, if available. Defaults
              to None.

        Returns:
            A list of dialogue acts.
        """
        # This is the top priority. The agent must check if user selected
        # any option.
        selected_option = self.get_selected_option(
            user_utterance, options, dialogue_state.item_in_focus
        )
        if selected_option:
            return selected_option

        # Check if user is ending the conversation.
        bye_dacts = self.intents_checker.check_basic_intent(
            user_utterance, UserIntents.BYE
        )
        if bye_dacts:
            return bye_dacts

        # Check if it's the start of a conversation.
        if not dialogue_state.last_agent_dacts:
            return self._process_first_turn(user_utterance)

        # Start eliciting or follow up on elicitation.
        user_dacts = self._process_last_agent_dacts(
            user_utterance, dialogue_state.last_agent_dacts
        )
        if user_dacts:
            return user_dacts

        # Handle feedback after recommendation.
        if dialogue_state.agent_made_offer:
            user_dacts = self._process_recommendation_feedback(user_utterance)
            if user_dacts:
                return user_dacts

        return [DialogueAct(UserIntents.UNK, [])]

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
