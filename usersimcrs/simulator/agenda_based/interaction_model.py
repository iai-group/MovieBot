"""Interaction model."""

import functools
import logging
import os
import random
from collections import defaultdict
from typing import Any, DefaultDict, List, Tuple

import yaml

from dialoguekit.core.annotated_utterance import AnnotatedUtterance
from dialoguekit.core.dialogue import Dialogue
from dialoguekit.core.intent import Intent

IntentDistribution = DefaultDict[Intent, DefaultDict[Intent, Any]]
logger = logging.getLogger(__name__)


class InteractionModel:
    """Represents an interaction model."""

    # This set contains the name of the required intents that need to be
    # defined in the configuration file under the field required_intents.
    REQUIRED_INTENTS = {
        "INTENT_START",
        "INTENT_STOP",
        "INTENT_ITEM_CONSUMED",
        "INTENT_LIKE",
        "INTENT_DISLIKE",
        "INTENT_NEUTRAL",
        "INTENT_DISCLOSE",
        "INTENT_DONT_KNOW",
    }

    def __init__(
        self, config_file: str, annotated_conversations: List[Dialogue]
    ) -> None:
        """Initializes the interaction model.

        Args:
            config_file: Path to configuration file.
            annotated_conversations: List of annotated conversations.
        """
        # Load interaction model.
        if not os.path.isfile(config_file):
            raise FileNotFoundError(f"Config file not found: {config_file}")

        with open(config_file) as yaml_file:
            self._config = yaml.load(yaml_file, Loader=yaml.FullLoader)

        self._initialize_required_intents()

        self._initialize_preference_intent_config()
        (
            self._user_intent_distribution,
            self._intent_distribution,
        ) = self.intent_distribution(annotated_conversations)

        # Initialize agenda.
        self._agenda = self.initialize_agenda()

        # Keep track of the current user intent.
        self._current_intent = self._agenda.pop()

    def _initialize_required_intents(self) -> None:
        """Initializes required intents.

        Raises:
            RuntimeError: if some required intents are not defined.
        """
        required_intents = self._config.get("required_intents", {})
        if not self.REQUIRED_INTENTS.issubset(required_intents.keys()):
            raise RuntimeError(
                f'The interaction model {self._config.get("name")} needs to '
                "define the following intents under required_intents: "
                f"{self.REQUIRED_INTENTS}"
            )

        for k, v in required_intents.items():
            setattr(self, k, Intent(v))

    def intent_distribution(
        self, annotated_conversations: List[Dialogue]
    ) -> Tuple[IntentDistribution, IntentDistribution]:
        """Distills user intent distributions based on conversations.

        Arg:
            annotated_conversations: List of annotated conversations.

        Returns:
            Intent distributions:
                {user of agent intent: {next_user_intent: occurrence}}

        Raises:
            TypeError: if some utterances are not an instance of
              AnnotatedUtterance.
        """
        # Check if all the utterances are annotated utterances.
        if not all(
            isinstance(utterance, AnnotatedUtterance)
            for dialogue in annotated_conversations
            for utterance in dialogue.utterances
        ):
            raise TypeError(
                "Some utterances are not an instance of 'AnnotatedUtterance'."
            )

        user_intent_dist: DefaultDict[
            Intent, DefaultDict[Intent, Any]
        ] = defaultdict(functools.partial(defaultdict, int))
        intent_dist: DefaultDict[
            Intent, DefaultDict[Intent, Any]
        ] = defaultdict(functools.partial(defaultdict, int))
        for annotated_conversation in annotated_conversations:
            # Extracts conjoint user intent pairs from conversations.
            # Note: dialoguekit reader does not cast participant to
            # DialogueParticipant.
            user_agenda = [
                u.intent
                for u in annotated_conversation.utterances
                if u.participant != "AGENT"
            ]
            for i, user_intent in enumerate(user_agenda):
                next_user_intent = (
                    user_agenda[i + 1]
                    if i < len(user_agenda) - 1
                    else self.INTENT_STOP  # type: ignore[attr-defined]
                )
                user_intent_dist[user_intent][next_user_intent] += 1

            # Extracts conjoint agent intent and user intent pairs
            # from conversations.
            for j, utterance in enumerate(annotated_conversation.utterances):
                # Only consider agent intent as keys
                if utterance.participant != "AGENT":
                    continue
                intent = utterance.intent
                # TODO: consider the case when the next intent is not
                # user intent.
                next_user_intent = (
                    annotated_conversation.utterances[j + 1].intent
                    if j < len(annotated_conversation.utterances) - 1
                    else self.INTENT_START  # type: ignore[attr-defined]
                )
                intent_dist[intent][next_user_intent] += 1
        return user_intent_dist, intent_dist

    def initialize_agenda(self) -> List[Intent]:
        """Initializes user agenda."""
        current_intent = self.INTENT_START  # type: ignore[attr-defined]
        agenda = self._create_agenda(current_intent)
        return agenda

    def _create_agenda(self, current_intent: Intent) -> List[Intent]:
        """Creates an agenda based on the current user intent.

        Args:
            current_intent: Current user intent.

        Returns:
            Agenda.
        """
        agenda = list()
        agenda.append(current_intent)
        next_intent = self.next_intent(
            current_intent, self._user_intent_distribution
        )
        while next_intent != self.INTENT_STOP:  # type: ignore[attr-defined]
            current_intent = next_intent
            agenda.append(current_intent)
            next_intent = self.next_intent(
                current_intent, self._user_intent_distribution
            )
        agenda.reverse()
        self._agenda = agenda
        return agenda

    def _initialize_preference_intent_config(self):
        sub_to_main_intent = dict()
        self._config["user_preference_intents"] = dict()
        for intent_label, properties in self._config["user_intents"].items():
            if "preference_contingent" in properties:
                if (
                    not self._get_main_intent_from_sub_intent_label(
                        intent_label
                    )
                    in self._config["user_preference_intents"]
                ):
                    self._config["user_preference_intents"][
                        self._get_main_intent_from_sub_intent_label(
                            intent_label
                        )
                    ] = {}
                self._config["user_preference_intents"][
                    self._get_main_intent_from_sub_intent_label(intent_label)
                ][properties["preference_contingent"]] = intent_label
                sub_to_main_intent[
                    intent_label
                ] = self._get_main_intent_from_sub_intent_label(intent_label)
        self._config["user_preference_intents_reverse"] = sub_to_main_intent

    @staticmethod
    def _get_main_intent_from_sub_intent_label(sub_intent: str) -> str:
        return sub_intent.split(".")[0]

    @property
    def agenda(self):
        return self._agenda

    @property
    def current_intent(self) -> Intent:
        return self._current_intent

    def is_agent_intent_elicit(self, agent_intent: Intent) -> bool:
        """Checks if the given agent intent is elicitation.

        Args:
            agent_intent: Agent's intent.

        Returns:
            True if it is an elicitation intent.
        """
        return agent_intent.label in self._config["agent_elicit_intents"]

    def is_agent_intent_set_retrieval(self, agent_intent: Intent) -> bool:
        """Checks if the given agent intent is set retrieval.

        Args:
            agent_intent: Agent's intent.

        Returns:
            True if it is a set retrieval intent.
        """
        return agent_intent.label in self._config["agent_set_retrieval"]

    def is_user_intent_remove_preference(self, user_intent: Intent) -> bool:
        """Checks if the given user intent is remove preference.

        Args:
            user_intent: User's intent.

        Returns:
            True if it is a remove preference intent.
        """
        return (
            self._config.get("user_intents", {})
            .get(user_intent.label, {})
            .get("remove_user_preference", False)
        )

    def is_user_intent_inquire(self, user_intent: Intent) -> bool:
        """Checks if the given user intent is inquiring information.

        Args:
            user_intent: User's intent.
        """
        return (
            self._config.get("user_intents", {})
            .get(user_intent.label, {})
            .get("inquiry", False)
        )

    def next_intent(
        self, intent: Intent, intent_dist: IntentDistribution
    ) -> Intent:
        """Predicts the next user intent.

        Given current_intent, we determine the next intent
            (either next_intent1 or next_intent2) by probabilities.

        Args:
            Intent: current intent.
            Intent_dist: intent distributions.

        Returns:
            Next user intent based on probability distribution.
        """
        # Get the distribution of next intent for the current user intent.
        intent_map = intent_dist.get(intent)
        assert isinstance(intent_map, dict)

        # Randomly generates a probability from 0~1.
        p_random = random.uniform(0, 1)

        # Get the sum of the next intent occurrences.
        next_intent_occurrences_sum = sum(intent_map.values())

        # Get normalized next intent distribution occurrences and next intent
        # list.
        d, next_intents = [], []
        for next_intent, next_intent_occurrence in intent_map.items():
            d.append(next_intent_occurrence / next_intent_occurrences_sum)
            next_intents.append(next_intent)
        return self._sample_random_intent(p_random, d, next_intents)

    @staticmethod
    def _sample_random_intent(
        p: float, d: List[float], items: List[Intent]
    ) -> Intent:
        """Determines the next item based on a randomly generated probability.

        Args:
            p: a randomly generated uniform probability.
            d: list of probabilities of items.
            items: items to be sampled from.

        Return:
            The sampled item.
        """
        p_start = 0.0
        for i, p_item in enumerate(d):
            p_start += p_item
            if p < p_start:
                return items[i]
        return items[-1]

    def update_agenda(self, agent_intent: Intent) -> None:
        """Updates the agenda and determines the next user intent based on agent
        intent.

        If agent replies with an expected intent in response to the last user
        intent (based on the expected_responses mapping in the config file),
        then
            pops up the next user intent from the agenda;
            update the current intent;
        Otherwise:
            pushes a new intent (select a replacement intent);
            updates the current intent.

        Args:
            Agent_intent: Agent's intent.
        """
        expected_agent_intents = (
            self._config["user_intents"]
            .get(self._current_intent.label)
            .get("expected_agent_intents")
        ) or []

        logger.debug(f"Agent intent: {agent_intent}\n")

        if not self._agenda:
            self._current_intent = self.INTENT_STOP  # type: ignore[attr-defined] # noqa
            return

        # If agent replies with an expected intent, then pop the next intent
        # from the agenda.
        if agent_intent.label in expected_agent_intents:
            self._current_intent = self._agenda.pop()
        else:  # Find a replacement based on last agent intent
            self._current_intent = self.next_intent(
                agent_intent, self._intent_distribution
            )
            # Create a new agenda based on the new current intent.
            self._agenda = self._create_agenda(self._current_intent)
