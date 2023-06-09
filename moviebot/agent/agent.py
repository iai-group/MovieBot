"""Types of conversational agents are available here."""
import logging
import os
from typing import Any, Dict, List, Tuple, Union

from moviebot.core.utterance.utterance import AgentUtterance, UserUtterance
from moviebot.database.database import DataBase
from moviebot.dialogue_manager.dialogue_act import DialogueAct
from moviebot.dialogue_manager.dialogue_manager import DialogueManager
from moviebot.nlg.nlg import NLG
from moviebot.nlu.nlu import NLU
from moviebot.ontology.ontology import Ontology
from moviebot.recommender.recommender_model import RecommenderModel
from moviebot.recommender.slot_based_recommender_model import (
    SlotBasedRecommenderModel,
)
from moviebot.recorder.dialogue_recorder import DialogueRecorder
from moviebot.recorder.recorder_bot import RecorderBot

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


class Agent:
    def __init__(self, config: Dict[str, Any] = None) -> None:
        """The class Agent controls all the components of the basic
        architecture of IAI MovieBot.

        Initially the Conversational Agent is able to interact with human
        users via text.

        Args:
            config: Configuration. Defaults to None.
        """
        self.config = config
        self.new_user = False

        self.record = self.config.get("CONVERSATION_LOGS", {}).get("save")
        self.recorder = (
            DialogueRecorder(
                self.config["CONVERSATION_LOGS"]["path"],
                self.config["CONVERSATION_LOGS"]["nlp"],
            )
            if self.record
            else None
        )
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

        data_config = dict(
            ontology=self.ontology,
            database=self.database,
            recommender=_recommender,
            slot_values_path=self.slot_values_path,
            tag_words_slots_path=nlu_tag_words_slots_path,
        )
        self.nlu = NLU(data_config)
        self.nlg = NLG(dict(ontology=self.ontology))
        data_config["slots"] = list(self.nlu.intents_checker.slot_values.keys())

        self.isBot = (
            self.config.get("TELEGRAM", False)
            or self.config.get("FLASK_REST", False)
            or self.config.get("FLASK_SOCKET", False)
        )

        self.dialogue_manager = DialogueManager(
            data_config, self.isBot, self.new_user
        )

        if self.isBot and self.config.get("BOT_HISTORY", {}).get("save"):
            path = self.config.get("BOT_HISTORY", {}).get("path")
            if path:
                self.bot_recorder = RecorderBot(path)
            else:
                raise ValueError("Path to save conversation is not provided.")

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

    def start_dialogue(
        self, user_fname: str = None, restart: bool = False
    ) -> Union[
        Tuple[str, str, DialogueOptions],
        Tuple[str, str, DialogueOptions, Dict[str, Any]],
    ]:
        """Starts the conversation.

        Args:
            user_fname: User's first name. Defaults to None.
            restart: Whether to restart the conversation or not. Defaults to
              False.

        Returns:
            Agent response, agent intents, dialogue options for quick reply,
            and data to be recorded if self.isBot is true.
        """
        if not restart:
            agent_dacts = self.dialogue_manager.start_dialogue(self.new_user)
        else:
            agent_dacts = self.dialogue_manager.generate_output(restart)
        agent_intents = ",".join([dact.intent.name for dact in agent_dacts])
        agent_response, options = self.nlg.generate_output(
            agent_dacts, user_fname=user_fname
        )
        self.dialogue_manager.get_context().add_utterance(
            AgentUtterance({"text": agent_response})
        )

        if self.record:
            self.recorder.record(
                user_fname, agent_response, agent_dacts, participant="AGENT"
            )

        if not self.isBot:
            logger.debug(
                str(self.dialogue_manager.dialogue_state_tracker.dialogue_state)
            )
            logger.debug(str(self.dialogue_manager.get_context()))
            return agent_response, agent_intents, options
        else:
            record_data = self.dialogue_manager.get_state().to_dict()
            context = self.dialogue_manager.get_context().movies_recommended
            record_data.update(
                {"Agent_Output": agent_response, "Context": context}
            )
            return agent_response, agent_intents, options, record_data

    def continue_dialogue(
        self,
        user_utterance: UserUtterance,
        user_options: DialogueOptions,
        user_fname: str = None,
    ) -> Union[
        Tuple[str, str, DialogueOptions],
        Tuple[str, str, DialogueOptions, Dict[str, Any]],
    ]:
        """Performs the next dialogue according to user response and current
        state of dialogue.

        Args:
            user_utterance: The input received from the user.
            user_options: Dialogue options that were provided to the user in
              previous turn.
            user_fname: User's first name. Defaults to None.

        Returns:
            Agent response, agent intents, dialogue options for quick reply,
              and data to be recorded if self.isBot is true.
        """
        self.dialogue_manager.get_state().user_utterance = user_utterance
        self.dialogue_manager.get_context().add_utterance(user_utterance)
        user_dacts = self.nlu.generate_dact(
            user_utterance,
            user_options,
            self.dialogue_manager.get_state(),
            self.dialogue_manager.get_context(),
        )
        self.dialogue_manager.receive_input(user_dacts)
        agent_dacts = self.dialogue_manager.generate_output()
        dialogue_state = (
            self.dialogue_manager.dialogue_state_tracker.dialogue_state
        )

        agent_intents = ",".join([dact.intent.name for dact in agent_dacts])
        agent_response, options = self.nlg.generate_output(
            agent_dacts, dialogue_state=dialogue_state, user_fname=user_fname
        )
        self.dialogue_manager.get_context().add_utterance(
            AgentUtterance({"text": agent_response})
        )

        if self.record:
            self.recorder.record(
                user_fname,
                user_utterance.get_text(),
                user_dacts,
                participant="USER",
            )
            self.recorder.record(
                user_fname,
                agent_response,
                agent_dacts,
                participant="AGENT",
            )

        if not self.isBot:
            logger.debug(
                str(self.dialogue_manager.dialogue_state_tracker.dialogue_state)
            )
            logger.debug(str(self.dialogue_manager.get_context()))
            return agent_response, agent_intents, options
        else:
            record_data = self.dialogue_manager.get_state().to_dict()
            context = self.dialogue_manager.get_context().movies_recommended
            record_data.update(
                {
                    "Agent_Output": agent_response,
                    "User_Input": user_utterance.get_text(),
                    "Context": context,
                }
            )

            if options:
                _options = {
                    str(key): val[0] if isinstance(val, list) else val
                    for key, val in options.items()
                }
                record_data.update({"Agent_Options": str(_options)})
            return agent_response, agent_intents, options, record_data

    def end_dialogue(self) -> None:
        """Ends the dialogue and save the experience if required."""
        if self.record:
            self.recorder.save()

    def terminated_dialogue(self) -> bool:
        """Checks if the dialogue is terminated by either user or the number of
        dialogues have reached a maximum limit.

        Returns:
            True if conversation is finished.
        """
        return self.dialogue_manager.get_state().at_terminal_state
