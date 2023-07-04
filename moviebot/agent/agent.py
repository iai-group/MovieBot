"""Types of conversational agents are available here."""
import logging
import os
from typing import Any, Dict, List, Union

from dialoguekit.core import AnnotatedUtterance, Intent
from dialoguekit.participant import Agent, DialogueParticipant

from moviebot.core.intents.agent_intents import AgentIntents
from moviebot.core.utterance.utterance import UserUtterance
from moviebot.database.database import DataBase
from moviebot.dialogue_manager.dialogue_act import DialogueAct
from moviebot.nlg.nlg import NLG
from moviebot.nlu.annotation.item_constraint import ItemConstraint
from moviebot.nlu.annotation.operator import Operator
from moviebot.nlu.nlu import NLU
from moviebot.ontology.ontology import Ontology
from moviebot.recommender.recommender_model import RecommenderModel
from moviebot.recommender.slot_based_recommender_model import (
    SlotBasedRecommenderModel,
)

logger = logging.getLogger(__name__)
DialogueOptions = Dict[DialogueAct, Union[str, List[str]]]


def _get_ontology(ontology_path: str) -> Ontology:
    """Checks if the ontology exists and get the file.

    Args:
        ontology_path: The path to the file.

    Returns:
        The ontology class instance.
    """
    if os.path.isfile(ontology_path):
        return Ontology(ontology_path)
    else:
        raise FileNotFoundError(f"Ontology file {ontology_path} not found.")


def _get_db(db_path: str) -> DataBase:
    """Checks if the database file exists and get the file.

    Args:
        db_path: The path to the file.

    Returns:
        The database class instance.
    """
    if os.path.isfile(db_path):
        return DataBase(db_path)
    else:
        raise FileNotFoundError(f"Database file {db_path} not found.")


class MovieBotAgent(Agent):
    def __init__(self, config: Dict[str, Any] = None) -> None:
        """MovieBotAgent controls all the components of the basic architecture
        of IAI MovieBot.

        Initially the Conversational Agent is able to interact with human
        users via text.

        Args:
            config: Configuration. Defaults to None.
        """
        super().__init__(
            id="IAIMovieBot",
            agent_type=DialogueParticipant.AGENT,
            stop_intent=AgentIntents.BYE.value,
        )

        self.config = config
        self.new_user = False

        ontology_path = self.config.get("DATA", {}).get("ontology_path")
        self.ontology = _get_ontology(ontology_path) if ontology_path else None
        db_path = self.config.get("DATA", {}).get("db_path")
        self.database = _get_db(db_path) if db_path else None
        self.slot_values_path = self.config.get("DATA", {}).get(
            "slot_values_path"
        )

        nlu_tag_words_slots_path = self.config.get("NLU", {}).get(
            "tag_words_slots"
        )
        if not nlu_tag_words_slots_path:
            raise EnvironmentError(
                "Conversational Agent: No tag words provided for slots in user"
                " utterance"
            )

        _recommender = self._get_recommender(
            self.config.get("RECOMMENDER", "slot_based")
        )

        self.data_config = dict(
            ontology=self.ontology,
            database=self.database,
            recommender=_recommender,
            slot_values_path=self.slot_values_path,
            tag_words_slots_path=nlu_tag_words_slots_path,
        )
        self.nlu = NLU(self.data_config)
        self.nlg = NLG(dict(ontology=self.ontology))
        self.data_config["slots"] = list(
            self.nlu.intents_checker.slot_values.keys()
        )

        self.isBot = (
            self.config.get("TELEGRAM", False)
            or self.config.get("FLASK_REST", False)
            or self.config.get("FLASK_SOCKET", False)
        )

    def _get_recommender(self, recommender_type: str) -> RecommenderModel:
        """Creates a recommender model of given type.

        Recommender types supported: slot_based.

        Args:
            recommender_type: Recommender type.

        Returns:
            A recommender model.

        Raises:
            ValueError: If the recommender type is not supported.
        """
        if recommender_type == "slot_based":
            return SlotBasedRecommenderModel(self.database, self.ontology)

        raise ValueError(f"{recommender_type} is not supported.")

    def _generate_utterance(
        self,
        agent_response: str,
        agent_intent: Intent,
        options: DialogueOptions,
        recommend_item: Dict[str, Any] = None,
    ):
        """Generates an utterance object based on response and options.

        Args:
            agent_response: Agent response.
            agent_intent: Intent of the agent.
            options: Options for the user.

        Returns:
            An annotated utterance.
        """
        metadata = {"options": options}
        if recommend_item:
            metadata.update({"recommended_item": recommend_item})

        if not self.isBot:
            logger.debug(
                str(
                    self._dialogue_connector.dialogue_state_tracker.dialogue_state  # noqa
                )
            )

            utterance = AnnotatedUtterance(
                intent=agent_intent,
                text=agent_response,
                participant=DialogueParticipant.AGENT,
                annotations=[],
                metadata=metadata,
            )
        else:
            record_data = self._dialogue_connector.get_state().to_dict()
            metadata.update({"record_data": record_data})
            utterance = AnnotatedUtterance(
                intent=agent_intent,
                text=agent_response,
                participant=DialogueParticipant.AGENT,
                annotations=[],
                metadata=metadata,
            )

        return utterance

    def welcome(self, user_fname: str = None) -> None:
        """Sends a welcome message to the user.

        Args:
            user_fname: User's first name. Defaults to None.
        """
        agent_dacts = [
            DialogueAct(
                AgentIntents.WELCOME,
                [
                    ItemConstraint("new_user", Operator.EQ, self.new_user),
                    ItemConstraint("is_bot", Operator.EQ, self.isBot),
                ],
            )
        ]
        self._dialogue_connector.dialogue_state_tracker.update_state_agent(
            agent_dacts
        )
        agent_response, options = self.nlg.generate_output(
            agent_dacts, user_fname=user_fname
        )

        utterance = self._generate_utterance(
            agent_response, AgentIntents.WELCOME.value, options
        )

        self._dialogue_connector.register_agent_utterance(utterance)

    def goodbye(self) -> None:
        """Sends a goodbye message to the user."""
        agent_dacts = [DialogueAct(AgentIntents.BYE, [])]
        self._dialogue_connector.dialogue_state_tracker.update_state_agent(
            agent_dacts
        )
        agent_response, options = self.nlg.generate_output(agent_dacts)
        utterance = self._generate_utterance(
            agent_response, AgentIntents.BYE.value, options
        )
        self._dialogue_connector.register_agent_utterance(utterance)

    def receive_utterance(
        self,
        user_utterance: UserUtterance,
        user_options: DialogueOptions = {},
    ) -> None:
        """Receives an utterance from the user and sends a response.

        Args:
            utterance: User utterance.
            Dialogue options that were provided to the user in
              previous turn.
        """
        self._dialogue_connector.get_state().user_utterance = user_utterance

        user_dacts = self.nlu.generate_dact(
            user_utterance,
            user_options,
            self._dialogue_connector.get_state(),
        )
        self._dialogue_connector.receive_input(user_dacts)

        agent_dacts = self._dialogue_connector.generate_output()
        dialogue_state = (
            self._dialogue_connector.dialogue_state_tracker.dialogue_state
        )
        agent_response, options = self.nlg.generate_output(
            agent_dacts,
            dialogue_state=dialogue_state,
            user_fname=self._dialogue_connector._user.id,
        )

        agent_intents = Intent(
            ";".join([da.intent.value.label for da in agent_dacts])
        )
        if AgentIntents.RECOMMEND in [da.intent for da in agent_dacts]:
            utterance = self._generate_utterance(
                agent_response,
                agent_intents,
                options,
                self._dialogue_connector.get_state().item_in_focus,
            )
        else:
            utterance = self._generate_utterance(
                agent_response, agent_intents, options
            )
        self._dialogue_connector.register_agent_utterance(utterance)

    def end_dialogue(self) -> None:
        """Ends the dialogue and save the experience if required."""
        # TODO: Save the experience
        pass

    def terminated_dialogue(self) -> bool:
        """Checks if the dialogue is terminated by either user or the number of
        dialogues have reached a maximum limit.

        Returns:
            True if conversation is finished.
        """
        return self._dialogue_connector.get_state().at_terminal_state
