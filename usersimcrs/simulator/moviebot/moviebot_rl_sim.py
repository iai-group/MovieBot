"""User simulator to interact with MovieBot agent during reinforcement
learning."""

import logging
import random
from typing import Any, Dict, List, Tuple

from nltk.stem import WordNetLemmatizer

from dialoguekit.core.annotated_utterance import AnnotatedUtterance
from dialoguekit.core.annotation import Annotation
from dialoguekit.core.domain import Domain
from dialoguekit.core.intent import Intent
from dialoguekit.core.utterance import Utterance
from dialoguekit.nlg import ConditionalNLG
from dialoguekit.nlu.nlu import NLU
from usersimcrs.domain.simulation_domain import SimulationDomain
from usersimcrs.items.item_collection import ItemCollection
from usersimcrs.items.ratings import Ratings
from usersimcrs.simulator.agenda_based.interaction_model import (
    InteractionModel,
)
from usersimcrs.simulator.user_simulator import UserSimulator
from usersimcrs.user_modeling.simple_preference_model import PreferenceModel

_LEMMATIZER = WordNetLemmatizer()


class UserSimulatorMovieBot(UserSimulator):
    def __init__(
        self,
        id: str,
        preference_model: PreferenceModel,
        interaction_model: InteractionModel,
        nlu: NLU,
        nlg: ConditionalNLG,
        domain: SimulationDomain,
        item_collection: ItemCollection,
        ratings: Ratings,
    ) -> None:
        """Initializes the user simulator.

        Args:
            id: User simulator id.
            preference_model: Preference model.
            interaction_model: Interaction model.
            nlu: Natural language understanding model.
            nlg: Natural language generation model.
            domain: Domain.
            item_collection: Item collection.
            ratings: Ratings.
        """
        super().__init__(id=id)
        self._preference_model = preference_model
        self._interaction_model = interaction_model
        self._nlu = nlu
        self._nlg = nlg
        self._domain = domain
        self._item_collection = item_collection
        self._ratings = ratings
        self.initialize_goal()

    def _get_information_need(self) -> Dict[str, str]:
        """Gets the information need for the goal.

        Returns:
            Information need as a dictionary of slot value pairs.
        """
        information_need = dict()
        nb_slots = random.randint(
            1, len(self._domain.get_slot_names_elicitation())
        )
        for _ in range(nb_slots):
            slot = random.choice(self._domain.get_slot_names_elicitation())
            slot_value, _ = self._preference_model.get_slot_preference(slot)
            information_need[slot] = slot_value
        return information_need

    def initialize_goal(self) -> Dict[str, Any]:
        """Initializes user goal.

        The ultimate goal is to find an item. The user goal contains the
        preference for the item to accept and a probability of accepting the
        item.
        For example: the user wants a comedy movie and always accept the
        recommendation.

        Returns:
            User goal.
        """
        self._goal = dict()
        self._goal["acceptance_probability"] = random.random()
        # Define slot value pairs for the goal.
        self._goal["information_need"] = self._get_information_need()
        logging.info(f"User goal: {self._goal}")

    def update_goal(self, annotation: Annotation) -> None:
        """Updates user goal.

        Args:
            annotation: Annotation.
        """
        if annotation.slot in self._goal.get("information_need", {}).keys():
            del self._goal["information_need"][annotation.slot]

    def initialize(self) -> None:
        """Initializes the user simulator if the dialogue starts again."""
        self.initialize_goal()
        self._interaction_model.initialize_agenda()

    def _generate_response(self, agent_utterance: Utterance) -> Utterance:
        """Generates response to the agent's utterance.

        Args:
            agent_utterance: Agent utterance.

        Return:
            User utterance.
        """
        return self.generate_response(agent_utterance)

    def _get_preference_intent(self, preference: float) -> Intent:
        """Gets the intent associated to a preference value.

        Args:
            preference: Preference value.

        Return:
            Preference intent.
        """
        if preference > self._preference_model.PREFERENCE_THRESHOLD:
            return self._interaction_model.INTENT_LIKE  # type: ignore[attr-defined] # noqa

        if preference < -self._preference_model.PREFERENCE_THRESHOLD:
            return self._interaction_model.INTENT_DISLIKE  # type: ignore[attr-defined] # noqa

        return self._interaction_model.INTENT_NEUTRAL  # type: ignore[attr-defined] # noqa

    def _generate_elicit_response_intent_and_annotations(
        self, slot: str = None, value: str = None
    ) -> Tuple[Intent, List[Annotation]]:
        """Generates response intent and annotations for the elicited slot value
        pair.

        Args:
            slot: Elicited slot.
            value: Elicited value.

        Return:
            Response intent and annotations.
        """
        elicited_slot = (
            slot
            if slot
            else random.choice(self._domain.get_slot_names_elicitation())
        )
        # During training of the slot annotator, a slot's name and value can be
        # the almost the same, e.g., (GENRE, genres). In that case, value does
        # not represent an entity.
        elicited_value = (
            None
            if value
            and _LEMMATIZER.lemmatize(value).lower()
            == _LEMMATIZER.lemmatize(elicited_slot).lower()
            else value
        )

        # Agent is asking about a particular slot-value pair, e.g.,
        # "Do you like action movies?"
        if elicited_value:
            preference = (
                1
                if elicited_value
                in self._goal.get("information_need", {}).values()
                else self._preference_model.get_slot_value_preference(
                    elicited_slot, elicited_value
                )
            )
            return self._get_preference_intent(preference), [
                Annotation(slot=elicited_slot, value=elicited_value)
            ]
        else:
            # Agent is asking about value preferences on a given slot, e.g.,
            # "What movie genre would you prefer?"
            if elicited_slot in self._goal.get("information_need", {}).keys():
                response_value = self._goal.get("information_need", {}).get(
                    elicited_slot
                )
                preference = 1
            else:
                (
                    response_value,
                    preference,
                ) = self._preference_model.get_slot_preference(elicited_slot)

            if response_value:
                response_intent = self._interaction_model.INTENT_DISCLOSE  # type: ignore[attr-defined] # noqa
                response_slot_values = [
                    Annotation(slot=elicited_slot, value=response_value)
                ]
                return response_intent, response_slot_values

        response_intent = self._interaction_model.INTENT_DONT_KNOW  # type: ignore[attr-defined] # noqa
        return response_intent, None

    def _generate_item_preference_response_intent(self, item_id: str) -> Intent:
        """Generates response preference intent for a given item id.

        Args:
            item_id: Item id.

        Returns:
            Preference intent.
        """
        acceptance_probability = self._goal.get("acceptance_probability", 1)

        if item_id is None:
            # The recommended item was not found in the item collection.
            return random.choices(
                [
                    self._interaction_model.INTENT_LIKE,
                    self._interaction_model.INTENT_DISLIKE,
                ],
                [acceptance_probability, 1 - acceptance_probability],
                k=1,
            )[0]

        logging.debug(f"Item id: {item_id}")

        # Check if the user has already consumed the item.
        if self._preference_model.is_item_consumed(item_id):
            # Currently, the user only responds by saying that they
            # already consumed the item. If there is a follow-up
            # question by the agent whether they've liked it, that
            # should end up in the other branch of the fork.
            return self._interaction_model.INTENT_ITEM_CONSUMED  # type: ignore[attr-defined] # noqa

        # Check if recommendation matches to the user's goal.
        information_need = self._goal.get("information_need", {})
        recommended_item = self._item_collection.get_item(item_id)
        if all(
            [
                value == recommended_item.get_property(slot)
                for slot, value in information_need.items()
            ]
        ):
            # Get a response based on the recommendation. Currently, the
            # user responds immediately with a like/dislike, but it
            # could ask questions about the item before deciding (this
            # should be based on the agenda).
            preference = self._preference_model.get_item_preference(item_id)
        else:
            # The recommended item does not match the user's goal.
            preference = self._preference_model.PREFERENCE_THRESHOLD - 0.01

        # Alter preference based on the goal's acceptance probability.
        if preference > self._preference_model.PREFERENCE_THRESHOLD:
            preference = random.choices(
                [
                    self._preference_model.PREFERENCE_THRESHOLD + 0.01,
                    self._preference_model.PREFERENCE_THRESHOLD - 0.01,
                ],
                [acceptance_probability, 1 - acceptance_probability],
                k=1,
            )[0]

        response_intent = self._get_preference_intent(preference)
        return response_intent

    def _generate_inquire_annotations(self) -> List[Annotation]:
        """Generates response annotations for the inquired slot value.

        Returns:
            Response  annotations.
        """
        response_slot = None
        response_slot = random.choice(self._domain.get_slot_names_inquiry())
        return [Annotation(slot=response_slot, value="")]

    def _retrieve_last_slot_value_pair(self) -> Annotation:
        """Retrieves the last slot value pair from simulator's previous
        utterances.

        If not slot value pair is found, select a random one.

        Returns:
            Slot value pair.
        """
        dialogue_history = self._dialogue_connector.dialogue_history
        for utterance in reversed(dialogue_history.utterances):
            if (
                isinstance(utterance, AnnotatedUtterance)
                and utterance.participant == self._user_type
            ):
                annotations = utterance.get_annotations()
                for annotation in reversed(annotations):
                    if (
                        annotation.slot
                        in self._domain.get_slot_names_elicitation()
                    ):
                        return annotation

        # No slot value pair found, select a random one.
        slot = random.choice(
            self._preference_model._domain.get_slot_names_elicitation()
        )
        value = random.choice(
            list(self._item_collection.get_possible_property_values(slot))
        )
        return Annotation(slot=slot, value=value)

    def generate_response(
        self, agent_utterance: Utterance
    ) -> AnnotatedUtterance:
        """Generates response to the agent's utterance.

        Args:
            agent_utterance: Agent utterance.

        Return:
            User utterance.
        """
        # Run agent utterance through NLU.
        agent_annotations = self._nlu.annotate_slot_values(agent_utterance)
        agent_intent = self._nlu.classify_intent(agent_utterance)

        # Test for the agent's stopping intent. Note that this would normally
        # handled by the dialogue connector. However, since intent annotations
        # for the agent's utterance are not available when the response is
        # received by the dialogue connector, an extra check is needed here.
        if (
            agent_intent.label.lower()
            == self._dialogue_connector._agent.stop_intent.label.lower()
        ):
            response_intent = self._interaction_model.INTENT_STOP  # type: ignore[attr-defined] # noqa
            response = self._nlg.generate_utterance_text(response_intent)
            response.participant = self._user_type
            return response

        # Response generation (intent and slot-values).
        response_intent = None
        response_slot_values = None

        self._interaction_model.update_agenda(agent_intent)
        response_intent = self._interaction_model.current_intent

        # Agent wants to elicit preferences.
        if (
            self._interaction_model.is_agent_intent_elicit(agent_intent)
            or self._interaction_model.INTENT_DISCLOSE == response_intent
        ):
            # Extract the first slot, value pair from agent response on
            # which preferences are elicited. For now, we just focus on a
            # single slot.
            slot, value = (
                (agent_annotations[0].slot, agent_annotations[0].value)
                if agent_annotations
                else (None, None)
            )

            (
                response_intent,
                response_slot_values,
            ) = self._generate_elicit_response_intent_and_annotations(
                slot, value
            )

        # Agent is recommending items.
        elif self._interaction_model.is_agent_intent_set_retrieval(
            agent_intent
        ):
            possible_items = (
                self._item_collection.get_items_by_properties(agent_annotations)
                if agent_annotations
                else []
            )
            # The first identified item is considered the recommended item.
            item_id = possible_items[0].id if possible_items else None
            response_intent = self._generate_item_preference_response_intent(
                item_id
            )
            response_slot_values = None

        # Agent cannot find recommendations.
        elif agent_intent == Intent("NO_RESULTS"):
            logging.debug(
                "Agent cannot find recommendations. Update response intent."
            )
            response_intent = random.choice(
                [Intent("RESTART"), Intent("REMOVE_PREFERENCE")]
            )
            self._interaction_model._current_intent = response_intent

        # Simulator is asking for information.
        elif self._interaction_model.is_user_intent_inquire(response_intent):
            response_slot_values = self._generate_inquire_annotations()

        # User is revising their preferences.
        if self._interaction_model.is_user_intent_remove_preference(
            response_intent
        ):
            # Remove the last slot pair value from the current information need.
            response_slot_values = [self._retrieve_last_slot_value_pair()]
            self.update_goal(response_slot_values[0])

        # Generating natural language response through NLG.
        response = self._nlg.generate_utterance_text(
            response_intent, response_slot_values
        )
        response.participant = self._user_type

        return response

    def receive_utterance(self, utterance: Utterance) -> Utterance:
        """Gets called every time there is a new agent utterance.

        Args:
            utterance: Agent utterance.

        Returns:
            User utterance.
        """
        return self._generate_response(utterance)
