"""NLU (Natural Language Understander) is a main component of Dialogue Systems. NLU understands
the user requirements and intents for the system to generate an appropriate response.
"""

__author__ = "Javeria Habib"

from moviebot.database.database import DataBase
from moviebot.dialogue_manager.dialogue_act import DialogueAct
from moviebot.dialogue_manager.dialogue_state import DialogueState
from moviebot.intents.agent_intents import AgentIntents
from moviebot.intents.user_intents import UserIntents
from moviebot.nlu.user_intents_checker import UserIntentsChecker
from moviebot.ontology.ontology import Ontology
from moviebot.dialogue_manager.values import Values


class NLU:
    """NLU is a basic natural language understander to generate DActs for the Conversational Agent.
    Implementation of this NLU is designed to work for Slot-Filling applications. The purpose of
    this class is to provide a quick way of running Conversational Agents, sanity checks,
    and to aid debugging.
    """

    def __init__(self, config):
        """Loads the ontology and database, and preprocess
        the database so that we avoid some computations at runtime.
        Also create patterns to understand natural language

        :param config: Paths to ontology and database and tag words for slots in NLU
        :type self.database: DataBase
        :type self.ontology: Ontology
        """
        self.ontology = config['ontology']
        self.database = config['database']
        self.intents_checker = UserIntentsChecker(config)

    def generate_dact(self, raw_utterance, options, dialogue_state=None, dialogue_context=None):
        """Processes the utterance according to dialogue state and context and generate a user
        dialogue act for Agent to understand.

        :type dialogue_state: DialogueState
        :type last_agent_dact: DialogueAct
        :type options: dict
        :param utterance: a string containing user input
        :param options: a list of options provided to the user to choose from
        :param dialogue_state: the current dialogue state, if available
        :param dialogue_context: the current dialogue context, if available
        :return: a list of dialogue acts
        """
        # this is the top priority. The agent must check if user selected any option
        if options:
            for dact, value in options.items():
                if (isinstance(value, list) and value[0] == raw_utterance) or value == \
                        raw_utterance:
                    if dact.intent == UserIntents.CONTINUE_RECOMMENDATION:
                        dact.params = self.intents_checker.generate_params_continue_recommendation(
                            dialogue_state.item_in_focus)
                    return [dact]

        user_dacts = []  # Define a list of dialogue acts for this specific utterance
        utterance = self.intents_checker._lemmatize_value(
            raw_utterance)  # process the utterance for necessary
        self.dialogue_state = dialogue_state

        user_dacts.extend(self.intents_checker.check_bye_intent(utterance))
        if len(user_dacts) > 0:
            return user_dacts

        if not self.dialogue_state.last_agent_dacts:
            user_dacts.extend(self.intents_checker.check_reveal_voluntary_intent(utterance,
                                                                                 raw_utterance))
            if len(user_dacts) == 0:
                user_dacts.extend(self.intents_checker.check_hi_intent(utterance))
            if len(user_dacts) > 0:
                return user_dacts
            else:
                return None

        for last_agent_dact in self.dialogue_state.last_agent_dacts:
            if last_agent_dact.intent == AgentIntents.WELCOME:
                user_dacts.extend(self.intents_checker.check_reveal_voluntary_intent(utterance,
                                                                                     raw_utterance))
                if len(user_dacts) == 0:
                    user_dacts.extend(self.intents_checker.check_acknowledge_intent(utterance))
                if len(user_dacts) > 0:
                    return user_dacts
            elif last_agent_dact.intent == AgentIntents.ELICIT:
                user_dacts.extend(self.intents_checker.check_reveal_intent(utterance, raw_utterance,
                                                                           last_agent_dact))
                if len(user_dacts) == 0 or any([param.value in Values.__dict__.values() for dact
                                                in user_dacts for param in dact.params]):
                    user_dacts.extend(self.intents_checker.check_reveal_voluntary_intent(utterance,
                                                                                         raw_utterance))
                if len(user_dacts) > 0:
                    return user_dacts

        if dialogue_state.agent_made_offer:
            user_dacts.extend(self.intents_checker.check_reject_intent(utterance))
        if len(user_dacts) == 0:
            user_dacts.extend(self.intents_checker.check_inquire_intent(utterance))
        if len(user_dacts) == 0:
            user_dacts.extend(self.intents_checker.check_reveal_voluntary_intent(utterance,
                                                                                 raw_utterance))
        if len(user_dacts) == 0:
            deny_dact = self.intents_checker.check_deny_intent(utterance)
            if len(deny_dact) > 0:
                deny_dact[0].intent = UserIntents.INQUIRE
                user_dacts.extend(deny_dact)
        if len(user_dacts) > 0:
            return user_dacts

        if len(user_dacts) == 0:
            user_dacts.append(DialogueAct(UserIntents.UNK, []))
        return user_dacts
