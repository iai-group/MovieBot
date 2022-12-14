"""Types of conversational agents are available here."""

__author__ = "Javeria Habib"

import logging
import os

from moviebot.core.shared.utterance.utterance import AgentUtterance
from moviebot.database.database import DataBase
from moviebot.dialogue_manager.dialogue_manager import DialogueManager
from moviebot.nlg.nlg import NLG
from moviebot.nlu.nlu import NLU
from moviebot.ontology.ontology import Ontology
from moviebot.recorder.dialogue_recorder import DialogueRecorder
from moviebot.recorder.recorder_bot import RecorderBot

logger = logging.getLogger(__name__)


def _get_ontology(ontology_path):
    """Checks if the ontology exists and get the file

    Args:
        ontology_path: the path to the file

    Returns:
        the ontology class instance

    """
    if os.path.isfile(ontology_path):
        return Ontology(ontology_path)
    else:
        raise FileNotFoundError(
            "Ontology file {} not found.".format(ontology_path)
        )


def _get_db(db_path):
    """Checks if the database file exists and get the file

    Args:
        db_path: the path to the file

    Returns:
        the database class instance

    """
    if os.path.isfile(db_path):
        return DataBase(db_path)
    else:
        raise FileNotFoundError("Database file {} not found.".format(db_path))


class Agent:
    """The class Agent controls all the components of the basic architecture of
    IAI MovieBot. Initially the Conversational Agent is able to interact with
    human users via text."""

    def __init__(self, config=None):
        """Initializes the internal structure of the agent and other components.

        :type self.bot_recorder: RecorderBot
        :type self.dialogue_manager: DialogueManager

        Args:
            config: (Default value = None)

        """
        self.config = config

        # Parameters that need to be loaded using the configuration file
        self.record = False
        self.recorder = None
        self.ontology = None
        self.database = None
        self.slot_values_path = None
        self.nlu = None
        self.nlg = None
        self.isBot = False
        self.new_user = False  # a parameter for Bot
        self.bot_recorder = None

        # Dialogue component agent controls
        self.dialogue_manager = None

    def initialize(self, user_id=None):
        """Initializes the components and set their values as on the
        configuration.

        Args:
            user_id:  (Default value = None)

        """
        if (
            "CONVERSATION_LOGS" in self.config
            and self.config["CONVERSATION_LOGS"]["save"]
        ):
            self.record = True
            self.recorder = DialogueRecorder(
                self.config["CONVERSATION_LOGS"]["path"],
                self.config["CONVERSATION_LOGS"]["nlp"],
            )
        if "DATA" in self.config:
            if "ontology_path" in self.config["DATA"]:
                self.ontology = _get_ontology(
                    self.config["DATA"]["ontology_path"]
                )
            if "db_path" in self.config["DATA"]:
                self.database = _get_db(self.config["DATA"]["db_path"])
            if "slot_values_path" in self.config["DATA"]:
                self.slot_values_path = self.config["DATA"]["slot_values_path"]

        nlu_tag_words_slots_path = None
        if "NLU" in self.config and "tag_words_slots" in self.config["NLU"]:
            nlu_tag_words_slots_path = self.config["NLU"]["tag_words_slots"]
        else:
            raise EnvironmentError(
                "Conversational Agent: No tag words provided for slots in user utterance"
            )

        data_config = dict(
            ontology=self.ontology,
            database=self.database,
            slot_values_path=self.slot_values_path,
            tag_words_slots_path=nlu_tag_words_slots_path,
        )
        self.nlu = NLU(data_config)
        self.nlg = NLG(dict(ontology=self.ontology))
        data_config["slots"] = list(
            self.nlu.intents_checker.slot_values.keys()
        )

        if self.config.get("TELEGRAM", False):
            self.isBot = True
            # self.new_user = self.config['new_user'][user_id]

        if self.config.get("MESSENGER", True):
            self.isBot = True

        self.dialogue_manager = DialogueManager(
            data_config, self.isBot, self.new_user
        )

        if self.isBot:
            if (
                self.config["BOT_HISTORY"]
                and self.config["BOT_HISTORY"]["save"]
            ):
                if self.config["BOT_HISTORY"]["path"]:
                    self.bot_recorder = RecorderBot(
                        self.config["BOT_HISTORY"]["path"]
                    )
                else:
                    raise ValueError(
                        "Path to save conversation is not provided."
                    )

    def start_dialogue(self, user_fname=None, restart=False):
        """Starts the conversation


        Args:
            ser_fname:  (Default value = None)
            estart:  (Default value = False)

        Returns:
            agent response
        """
        if not restart:
            agent_dacts = self.dialogue_manager.start_dialogue(self.new_user)
        else:
            agent_dacts = self.dialogue_manager.generate_output(restart)
        agent_response, options = self.nlg.generate_output(
            agent_dacts, user_fname=user_fname
        )
        self.dialogue_manager.dialogue_state_tracker.dialogue_context.add_utterance(
            AgentUtterance({"text": agent_response})
        )
        if not self.isBot:
            logger.debug(
                str(
                    self.dialogue_manager.dialogue_state_tracker.dialogue_state
                )
            )
            logger.debug(
                str(
                    self.dialogue_manager.dialogue_state_tracker.dialogue_context
                )
            )
            return agent_response, options
        else:
            record_data = (
                self.dialogue_manager.dialogue_state_tracker.dialogue_state._dict()
            )
            record_data.update({"Agent_Output": agent_response})
            record_data.update(
                {
                    "Context": self.dialogue_manager.dialogue_state_tracker.dialogue_context.movies_recommended
                }
            )
            return agent_response, record_data, options

    def continue_dialogue(self, user_utterance, user_options, user_fname=None):
        """Performs the next dialogue according to user response and current
        state of dialogue.

        Args:
            user_utterance: The input received from the user
            user_options:
            user_fname:  (Default value = None)

        Returns:
            The agent response

        """
        self.dialogue_manager.dialogue_state_tracker.dialogue_state.user_utterance = (
            user_utterance
        )
        self.dialogue_manager.dialogue_state_tracker.dialogue_context.add_utterance(
            user_utterance
        )
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
        agent_response, options = self.nlg.generate_output(
            agent_dacts, dialogue_state=dialogue_state, user_fname=user_fname
        )
        self.dialogue_manager.dialogue_state_tracker.dialogue_context.add_utterance(
            AgentUtterance({"text": agent_response})
        )
        if not self.isBot:
            logger.debug(
                str(
                    self.dialogue_manager.dialogue_state_tracker.dialogue_state
                )
            )
            logger.debug(
                str(
                    self.dialogue_manager.dialogue_state_tracker.dialogue_context
                )
            )
            return agent_response, options
        else:
            record_data = {"User_Input": user_utterance.get_text()}
            record_data.update(
                self.dialogue_manager.dialogue_state_tracker.dialogue_state._dict()
            )
            record_data.update({"Agent_Output": agent_response})
            record_data.update(
                {
                    "Context": self.dialogue_manager.dialogue_state_tracker.dialogue_context.movies_recommended
                }
            )
            if options:
                _options = {str(x): y for x, y in options.items()}
                for key, val in _options.items():
                    if isinstance(val, list):
                        _options[key] = val[0]
                record_data.update({"Agent_Options": str(_options)})
            return agent_response, record_data, options

    def end_dialogue(self):
        """Ends the dialogue and save the experience if required"""
        # TODO: Save the experience

    def terminated_dialogue(self):
        """Checks if the dialogue is terminated by either user or the number of
        dialogues have reached a maximum limit

        Returns:
            True or False
        """
        return (
            self.dialogue_manager.dialogue_state_tracker.dialogue_state.at_terminal_state
        )
