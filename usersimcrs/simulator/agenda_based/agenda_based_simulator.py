"""Agenda-based user simulator from [Zhang and Balog, KDD'20]."""

import logging
import random
from typing import List, Tuple

from nltk.stem import WordNetLemmatizer

from dialoguekit.core.annotated_utterance import AnnotatedUtterance
from dialoguekit.core.annotation import Annotation
from dialoguekit.core.domain import Domain
from dialoguekit.core.intent import Intent
from dialoguekit.core.utterance import Utterance
from dialoguekit.nlg import ConditionalNLG
from dialoguekit.nlu.nlu import NLU
from usersimcrs.items.item_collection import ItemCollection
from usersimcrs.items.ratings import Ratings
from usersimcrs.simulator.agenda_based.interaction_model import (
    InteractionModel,
)
from usersimcrs.simulator.user_simulator import UserSimulator
from usersimcrs.user_modeling.simple_preference_model import PreferenceModel

_LEMMATIZER = WordNetLemmatizer()


class AgendaBasedSimulator(UserSimulator):
    def __init__(
        self,
        id: str,
        preference_model: PreferenceModel,
        interaction_model: InteractionModel,
        nlu: NLU,
        nlg: ConditionalNLG,
        domain: Domain,
        item_collection: ItemCollection,
        ratings: Ratings,
    ) -> None:
        """Initializes the agenda-based simulated user.

        Args:
            preference_model: Preference model.
            interaction_model: Interaction model.
            nlu: NLU module performing intent classification and entity linking.
            nlg: NLG module generating textual responses.
            domain: Domain.
            item_collection: Item collection.
            ratings: Historical ratings.
        """
        super().__init__(id=id)
        self._preference_model = preference_model
        self._interaction_model = interaction_model
        self._interaction_model.initialize_agenda()
        self._nlu = nlu
        self._nlg = nlg
        self._domain = domain
        self._item_collection = item_collection
        self._ratings = ratings

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
            else random.choice(
                self._preference_model._domain.get_slot_names_elicitation()
            )
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
        logging.debug(f"Elicited slot: {elicited_slot}")
        logging.debug(f"Elicited value: {elicited_value}")

        # Agent is asking about a particular slot-value pair, e.g.,
        # "Do you like action movies?"
        if elicited_value:
            preference = self._preference_model.get_slot_value_preference(
                elicited_slot, elicited_value
            )
            return self._get_preference_intent(preference), [
                Annotation(slot=elicited_slot, value=elicited_value)
            ]
        else:
            # Agent is asking about value preferences on a given slot, e.g.,
            # "What movie genre would you prefer?"
            (
                response_value,
                preference,
            ) = self._preference_model.get_slot_preference(elicited_slot)

            logging.debug(f"Response value: {response_value}")
            logging.debug(f"Preference: {preference}")

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
        if item_id is None:
            # The recommended item was not found in the item collection.
            # return self._interaction_model.INTENT_DONT_KNOW  # type: ignore[attr-defined] # noqa
            return random.choice([self._interaction_model.INTENT_LIKE, self._interaction_model.INTENT_DISLIKE])  # type: ignore[attr-defined] # noqa

        logging.debug(f"Item id: {item_id}")

        # Check if the user has already consumed the item.
        if self._preference_model.is_item_consumed(item_id):
            # Currently, the user only responds by saying that they
            # already consumed the item. If there is a follow-up
            # question by the agent whether they've liked it, that
            # should end up in the other branch of the fork.
            return self._interaction_model.INTENT_ITEM_CONSUMED  # type: ignore[attr-defined] # noqa

        # Get a response based on the recommendation. Currently, the
        # user responds immediately with a like/dislike, but it
        # could ask questions about the item before deciding (this
        # should be based on the agenda).
        preference = self._preference_model.get_item_preference(item_id)
        if preference > self._preference_model.PREFERENCE_THRESHOLD:
            response_intent = self._interaction_model.INTENT_LIKE  # type: ignore[attr-defined] # noqa
        elif preference < -self._preference_model.PREFERENCE_THRESHOLD:
            response_intent = self._interaction_model.INTENT_DISLIKE  # type: ignore[attr-defined] # noqa
        else:
            response_intent = self._interaction_model.INTENT_NEUTRAL  # type: ignore[attr-defined] # noqa

        return response_intent

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

    def _generate_inquire_annotations(self) -> List[Annotation]:
        """Generates response annotations for the inquired slot value.

        Returns:
            Response  annotations.
        """
        response_slot = None
        response_slot = random.choice(self._domain.get_slot_names_inquiry())
        return [Annotation(slot=response_slot, value="")]

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

        logging.debug(f"Agent intent: {agent_intent}")
        logging.debug(f"Agent annotations: {agent_annotations}")

        # Test for the agent's stopping intent. Note that this would normally
        # handled by the dialogue connector. However, since intent annotations
        # for the agent's utterance are not available when the response is
        # received by the dialogue connector, an extra check is needed here.
        if (
            agent_intent.label.lower()
            == self._dialogue_connector._agent.stop_intent.label.lower()
        ):
            # self._dialogue_connector.close()
            # quit()
            response_intent = self._interaction_model.INTENT_STOP  # type: ignore[attr-defined] # noqa
            response_slot_values = None
            response = self._nlg.generate_utterance_text(
                response_intent, response_slot_values
            )
            response._participant = self._user_type
            return response

        # Response generation (intent and slot-values).
        response_intent = None
        response_slot_values = None

        self._interaction_model.update_agenda(agent_intent)
        response_intent = self._interaction_model.current_intent

        # Agent wants to elicit preferences.
        if self._interaction_model.is_agent_intent_elicit(agent_intent):
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

        # Simulator is asking for information.
        elif self._interaction_model.is_user_intent_inquire(response_intent):
            response_slot_values = self._generate_inquire_annotations()

        # User is revising their preferences.
        if self._interaction_model.is_user_intent_remove_preference(
            response_intent
        ):
            # Remove the last slot pair value from the current information need.
            response_slot_values = [self._retrieve_last_slot_value_pair()]

        # Generating natural language response through NLG.
        logging.debug(f"Response intent: {response_intent}")
        logging.debug(f"Response slot values: {response_slot_values}")
        response = self._nlg.generate_utterance_text(
            response_intent, response_slot_values
        )
        response._participant = self._user_type

        return response
