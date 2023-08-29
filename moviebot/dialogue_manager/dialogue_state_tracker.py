"""Dialogue state tracker updates the current dialogue state."""


import re
from collections import defaultdict
from copy import deepcopy
from typing import Any, Dict, List

from moviebot.core.intents.agent_intents import AgentIntents
from moviebot.core.intents.user_intents import UserIntents
from moviebot.dialogue_manager.dialogue_act import DialogueAct
from moviebot.dialogue_manager.dialogue_state import DialogueState
from moviebot.nlu.annotation.item_constraint import ItemConstraint
from moviebot.nlu.annotation.operator import Operator
from moviebot.nlu.annotation.slots import Slots
from moviebot.nlu.annotation.values import Values
from moviebot.ontology.ontology import Ontology


class DialogueStateTracker:
    def __init__(self, config: Dict[str, Any], isBot: bool) -> None:
        """Loads the database and ontology and creates an initial dialogue
        state.

        Args:
            config: The set of parameters to initialize the state tracker.
            isBot: If the conversation is via bot or not.
        """
        self.ontology: Ontology = config.get("ontology")
        self.slots: List[str] = config.get("slots", [])
        self.isBot = isBot
        self.dialogue_state = DialogueState(
            self.ontology, self.slots, self.isBot
        )

    def initialize(self) -> None:
        """Initializes the dialogue state tracker."""
        self.dialogue_state.initialize()

    def _update_information_need(self, user_dact: DialogueAct) -> None:
        """Updates the current information need.

        Args:
            user_dact: The user dialogue act.
        """
        # Back up of the information need before update it based on user dact.
        self.dialogue_state.frame_PIN = deepcopy(self.dialogue_state.frame_CIN)
        self.dialogue_state.agent_should_offer_similar = False
        self.dialogue_state.agent_made_offer = False

        # Update the information need based on user dact.
        if user_dact.intent == UserIntents.REVEAL:
            self._update_information_need_reveal(user_dact.params)
        elif user_dact.intent == UserIntents.REMOVE_PREFERENCE:
            # Remove mentioned slot value pairs from the information need.
            for param in user_dact.params:
                if param.slot in self.ontology.multiple_values_CIN:
                    self.dialogue_state.frame_CIN[param.slot].remove(
                        param.value
                    )
                else:
                    self.dialogue_state.frame_CIN[param.slot] = None

    def _update_information_need_reveal(
        self, params: List[ItemConstraint]
    ) -> None:
        """Updates the current information need based on reveal intent
        constraints.

        Args:
            params: The list of item constraints.
        """
        # Add mentioned slot value pairs to the information need.
        for param in params:
            if param.slot in self.dialogue_state.frame_CIN:
                if param.op == Operator.NE:
                    value = re.sub(
                        "(\.NOT\.|^)", ".NOT.", param.value, 1
                    ).strip()
                if param.slot in self.ontology.multiple_values_CIN:
                    self.dialogue_state.frame_CIN[param.slot].append(value)
                else:
                    self.dialogue_state.frame_CIN[param.slot] = value

        # Check if some slots are filled with the same value.
        self.dialogue_state.agent_must_clarify = False
        self.dialogue_state.dual_params = {}
        slot_values = defaultdict(list)

        for slot, value in self.dialogue_state.frame_CIN.items():
            if value:
                value_list = value if isinstance(value, list) else [value]
                for v in value_list:
                    slot_values[v].append(slot)

        dual_slot_values = {s: v for s, v in slot_values.items() if len(v) > 1}
        if dual_slot_values:
            self.dialogue_state.dual_params = dual_slot_values
            self.dialogue_state.agent_must_clarify = True

    def _update_state_recommended_movie(self, user_dact: DialogueAct) -> None:
        """Updates the decisions about the recommended movie.

        Args:
            user_dact: The user dialogue act.

        Raises:
            ValueError: If there is no item in focus.
        """
        if self.dialogue_state.item_in_focus is None:
            raise ValueError("No item in focus.")

        name = self.dialogue_state.item_in_focus[Slots.TITLE.value]

        # The recommended movie is accepted.
        if user_dact.intent == UserIntents.ACCEPT:
            self.dialogue_state.agent_made_offer = True
            self.dialogue_state.agent_should_make_offer = False
            self.dialogue_state.movies_recommended[name].append("accept")
        # The recommended movie is rejected.
        if user_dact.intent == UserIntents.REJECT:
            self.dialogue_state.agent_made_offer = False
            self.dialogue_state.agent_should_make_offer = True
            self.dialogue_state.agent_should_offer_similar = False
            self.dialogue_state.movies_recommended[name].append(
                user_dact.params[0].value
            )
        # The recommended movie is inquired.
        if user_dact.intent == UserIntents.INQUIRE:
            if "inquire" not in self.dialogue_state.movies_recommended[name]:
                self.dialogue_state.movies_recommended[name].append("inquire")
            try:
                [
                    self.dialogue_state.user_requestable.remove(s)
                    for s, v in user_dact.params
                ]
            except ValueError:
                pass

    def _update_state_pursuing_conversation(
        self, user_dact: DialogueAct
    ) -> None:
        """Updates the decisions about pursuing the conversation.

        Args:
            user_dact: The user dialogue act.
        """
        # The user wants to continue the recommendation.
        if user_dact.intent == UserIntents.CONTINUE_RECOMMENDATION:
            self.dialogue_state.agent_made_offer = False
            self.dialogue_state.agent_should_make_offer = True
            self.dialogue_state.agent_should_offer_similar = True

            self.dialogue_state.similar_movies = (
                {
                    self.dialogue_state.item_in_focus[Slots.TITLE.value]: eval(
                        user_dact.params[0].value
                    )
                }
                if self.dialogue_state.item_in_focus
                else {}
            )

        # The user wants to restart the conversation.
        if user_dact.intent == UserIntents.RESTART:
            self.initialize()

        # The user wants to end the conversation.
        if user_dact.intent == UserIntents.BYE:
            self.dialogue_state.at_terminal_state = True

    def _merge_constraints_per_intent(
        self, dacts: List[DialogueAct]
    ) -> List[DialogueAct]:
        """Merges the item constraints per intent.

        Args:
            dacts: The list of dialogue acts.

        Returns:
            The list of dialogue acts.
        """
        merged_dacts: List[DialogueAct] = []
        for dact in dacts:
            if dact.intent not in [d.intent for d in merged_dacts]:
                merged_dacts.append(dact)
            else:
                for merged_dact in merged_dacts:
                    if merged_dact.intent == dact.intent:
                        merged_dact.params.extend(dact.params)
        return merged_dacts

    def update_state_user(self, user_dacts: List[DialogueAct]) -> None:
        """Updates the current dialogue state and context based on user
        dialogue acts.

        Args:
            user_dacts: List of dialogue acts which is the output of NLU.
        """
        user_dacts = self._merge_constraints_per_intent(user_dacts)
        self.dialogue_state.last_user_dacts = user_dacts

        for user_dact in user_dacts:
            if user_dact.intent in [
                UserIntents.REMOVE_PREFERENCE,
                UserIntents.REVEAL,
            ]:
                self._update_information_need(user_dact)

            self._update_state_recommended_movie(user_dact)
            self._update_state_pursuing_conversation(user_dact)

        # Check if all agent requestable slots are filled.
        self.dialogue_state.agent_req_filled = all(
            [
                slot in self.dialogue_state.frame_CIN
                for slot in self.dialogue_state.agent_requestable
            ]
        )

        # Check is a recommendation can be made
        if self.dialogue_state.agent_req_filled:
            self.dialogue_state.agent_can_lookup = True
            for value in self.dialogue_state.frame_CIN.values():
                value = value if isinstance(value, list) else [value]
                for v in value:
                    if v in Values.__dict__.values():
                        self.dialogue_state.agent_can_lookup = False
                        break

    def update_state_agent(self, agent_dacts: List[DialogueAct]) -> None:
        """Updates the current dialogue state and context based on agent
        dialogue acts.

        Args:
            agent_dacts: List of dialogue acts which is the output of dialogue
              policy.
        """
        # re-filtering the dacts
        agent_dacts_copy = deepcopy(agent_dacts)
        agent_dacts = []
        for copy_dact in agent_dacts_copy:
            if copy_dact.intent not in [d.intent for d in agent_dacts]:
                agent_dacts.append(copy_dact)
            else:
                for agent_dact in agent_dacts:
                    if agent_dact.intent == copy_dact.intent:
                        agent_dact.params.extend(copy_dact.params)

        if agent_dacts[0].intent != AgentIntents.CANT_HELP:
            self.dialogue_state.last_agent_dacts = agent_dacts
            self.dialogue_state.prev_agent_dacts.append(agent_dacts)
        for agent_dact in agent_dacts:
            if agent_dact.intent == AgentIntents.RECOMMEND:
                self.dialogue_state.movies_recommended[
                    agent_dact.params[0].value
                ] = []
                self.dialogue_state.agent_made_partial_offer = False
                self.dialogue_state.agent_should_make_offer = False
                self.dialogue_state.agent_made_offer = True
                self.dialogue_state.user_requestable = deepcopy(
                    self.ontology.user_requestable
                )

    def update_state_db(
        self,
        database_result: List[Dict[str, Any]] = None,
        backup_results: List[Dict[str, Any]] = None,
    ) -> None:
        """Updates the state based on the results fetched from the database.

        Args:
            database_result: The database results based on user information
              needs. Defaults to None.
            backup_results: Previous results stored in the database. Defaults
              to None.
        """

        item_found = False
        self.dialogue_state.items_in_context = False
        if database_result:
            # get slots that have no value and can be a next elicit
            CIN_slots = [
                key
                for key in self.dialogue_state.frame_CIN.keys()
                if not self.dialogue_state.frame_CIN[key]
                and key != Slots.TITLE.value
            ]
            self.dialogue_state.database_result = database_result

            if len(database_result) > self.dialogue_state.max_db_result:
                if len(CIN_slots) > self.dialogue_state.slot_left_unasked:
                    self.dialogue_state.agent_made_partial_offer = True
                    self.dialogue_state.agent_offer_no_results = False
                    self.dialogue_state.agent_should_make_offer = False
                    self.dialogue_state.agent_made_offer = False
                    return

            # random.shuffle(database_result)
            for result in database_result:
                if (
                    result[Slots.TITLE.value]
                    not in self.dialogue_state.movies_recommended.keys()
                ):
                    item_found = True
                    self.dialogue_state.item_in_focus = deepcopy(result)
                    break
                else:
                    self.dialogue_state.items_in_context = True

        if (
            not item_found
            and self.dialogue_state.agent_should_offer_similar
            and backup_results
        ):
            self.dialogue_state.agent_should_offer_similar = False
            for result in backup_results:
                if (
                    result[Slots.TITLE.value]
                    not in self.dialogue_state.movies_recommended.keys()
                ):
                    item_found = True
                    self.dialogue_state.item_in_focus = deepcopy(result)
                    break
                else:
                    self.dialogue_state.items_in_context = True

        if item_found:
            self.dialogue_state.agent_made_partial_offer = False
            self.dialogue_state.agent_offer_no_results = False
            self.dialogue_state.agent_should_make_offer = True
            self.dialogue_state.agent_made_offer = False
        else:
            self.dialogue_state.agent_made_partial_offer = False
            self.dialogue_state.agent_offer_no_results = True
            self.dialogue_state.agent_should_make_offer = False
            self.dialogue_state.agent_made_offer = False

    def get_state(self) -> DialogueState:
        """Returns the current dialogue state.

        Returns:
            The current dialogue state.
        """
        return self.dialogue_state
