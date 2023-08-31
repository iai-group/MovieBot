"""Types of conversational agents are available here."""
import logging
import os
from typing import Any, Dict

from dialoguekit.core import AnnotatedUtterance, Intent, Utterance
from dialoguekit.participant import Agent, DialogueParticipant
from moviebot.core.core_types import DialogueOptions
from moviebot.core.intents.agent_intents import AgentIntents
from moviebot.database.db_movies import DataBase
from moviebot.dialogue_manager.dialogue_manager import DialogueManager
from moviebot.domain.movie_domain import MovieDomain
from moviebot.nlg.nlg import NLG
from moviebot.nlu.rule_based_nlu import RuleBasedNLU as NLU
from moviebot.recommender.recommender_model import RecommenderModel
from moviebot.recommender.slot_based_recommender_model import (
    SlotBasedRecommenderModel,
)

logger = logging.getLogger(__name__)


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

        domain_path = self.config.get("DATA", {}).get("domain_path")
        self.domain = MovieDomain(domain_path) if domain_path else None
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
            domain=self.domain,
            database=self.database,
            recommender=_recommender,
            slot_values_path=self.slot_values_path,
            tag_words_slots_path=nlu_tag_words_slots_path,
        )
        self.nlu = NLU(self.data_config)
        self.nlg = NLG(dict(domain=self.domain))
        self.data_config["slots"] = list(
            self.nlu.intents_checker.slot_values.keys()
        )

        self.isBot = (
            self.config.get("TELEGRAM", False)
            or self.config.get("FLASK_REST", False)
            or self.config.get("FLASK_SOCKET", False)
        )

        self.dialogue_manager = DialogueManager(
            self.data_config, self.isBot, self.new_user
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
            return SlotBasedRecommenderModel(self.database, self.domain)

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
            recommend_item: Recommended item. Defaults to None.

        Returns:
            An annotated utterance.
        """
        metadata = {"options": options}
        if recommend_item:
            metadata.update({"recommended_item": recommend_item})

        if not self.isBot:
            logger.debug(
                str(self.dialogue_manager.dialogue_state_tracker.dialogue_state)
            )

            utterance = AnnotatedUtterance(
                intent=agent_intent,
                text=agent_response,
                participant=DialogueParticipant.AGENT,
                annotations=[],
                metadata=metadata,
            )
        else:
            record_data = self.dialogue_manager.get_state().to_dict()
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
        agent_dacts = self.dialogue_manager.start_dialogue(self.new_user)
        self.dialogue_manager.dialogue_state_tracker.update_state_agent(
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
        """Sends a goodbye message to the user.

        This method is not used, bye intent is generated by the dialogue policy.
        """
        pass

    def receive_utterance(
        self,
        user_utterance: Utterance,
        user_options: DialogueOptions = {},
    ) -> None:
        """Receives an utterance from the user and sends a response.

        Args:
            utterance: User utterance.
            Dialogue options that were provided to the user in
              previous turn.
        """
        self.dialogue_manager.get_state().user_utterance = user_utterance
        user_dacts = self.nlu.generate_dacts(
            user_utterance, user_options, self.dialogue_manager.get_state()
        )
        self.dialogue_manager.receive_input(user_dacts)

        agent_dacts = self.dialogue_manager.generate_output()
        dialogue_state = (
            self.dialogue_manager.dialogue_state_tracker.dialogue_state
        )
        agent_response, options = self.nlg.generate_output(
            agent_dacts,
            dialogue_state=dialogue_state,
            user_fname=self._dialogue_connector._user.id,
        )

        agent_intents = Intent(
            ";".join([da.intent.value.label for da in agent_dacts])
        )
        recommend_flag = AgentIntents.RECOMMEND in [
            da.intent for da in agent_dacts
        ]
        utterance = self._generate_utterance(
            agent_response,
            agent_intents,
            options,
            self.dialogue_manager.get_state().item_in_focus
            if recommend_flag
            else None,
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
        return self.dialogue_manager.get_state().at_terminal_state
