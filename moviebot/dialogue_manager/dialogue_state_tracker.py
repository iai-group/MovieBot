"""Dialogue State Tracker updates the current dialogue state."""

__author__ = "Javeria Habib"

from copy import deepcopy

from moviebot.dialogue_manager.dialogue_context import DialogueContext
from moviebot.dialogue_manager.dialogue_state import DialogueState
from moviebot.nlu.annotation.item_constraint import ItemConstraint
from moviebot.nlu.annotation.operator import Operator
from moviebot.nlu.annotation.slots import Slots
from moviebot.nlu.annotation.values import Values
from moviebot.core.shared.intents.agent_intents import AgentIntents
from moviebot.core.shared.intents.user_intents import UserIntents


class DialogueStateTracker:
    """Dialogue State Tracker updates the current dialogue state."""

    def __init__(self, config, isBot):
        """Loads the database and ontology and creates an initial dialogue state.

        Args:
            config: the set of parameters to initialize the state tracker
            isBot: if the conversation is via bot or not 
        
        """
        self.ontology = config['ontology']
        self.database = config['database']
        self.slots = config['slots']
        self.isBot = isBot
        self.dialogue_state = DialogueState(self.ontology, self.slots,
                                            self.isBot)
        self.dialogue_context = DialogueContext()

    def initialize(self, config):
        """Loads the database results and initialize the dialogue state and context.
        This function also initializes the state if dialogue needs to run from scratch.

        Args:
            config: the database and ontology to load for further use

        """

    def _add_year_CIN(self, param):
        """

        Args:
            param: 

        """
        if param.value in Values.__dict__.values():
            return param.value
        value = str(param.op) + " " + param.value
        if value not in Values.__dict__.values():
            value = value.strip()
        time_value = self.dialogue_state.frame_CIN[param.slot]
        if time_value and (
                (time_value.startswith('>') and value.startswith('<')) or \
                (time_value.startswith('<') and value.startswith('>'))):
            if time_value.startswith('>'):
                value = f'between {time_value.split()[-1]} and ' \
                        f'{value.split()[-1]}'
            else:
                value = f' between {value.split()[-1]} and' \
                        f' {time_value.split()[-1]}'
            self.dialogue_state.frame_CIN[param.slot] = value
        else:
            if value.startswith('='):
                value = value.replace('=', '').strip()
            self.dialogue_state.frame_CIN[param.slot] = value

    def update_state_user(self, user_dacts):
        """Updates the current dialogue state and context based on user DActs

        Args:
            user_dacts: dialogue acts) which is the output of NLU.

        """
        # re-filtering the dacts
        user_dacts_copy = deepcopy(user_dacts)
        user_dacts = []
        for copy_dact in user_dacts_copy:
            if copy_dact.intent not in [d.intent for d in user_dacts]:
                user_dacts.append(copy_dact)
            else:
                for user_dact in user_dacts:
                    if user_dact.intent == copy_dact.intent:
                        user_dact.params.extend(copy_dact.params)

        self.dialogue_state.last_user_dacts = user_dacts
        for user_dact in user_dacts:
            # makes a back-up of current info needs if user wants to refine those
            if user_dact.intent in [
                    UserIntents.REMOVE_PREFERENCE, UserIntents.REVEAL
            ]:
                self.dialogue_state.frame_PIN = deepcopy(
                    self.dialogue_state.frame_CIN)
                self.dialogue_state.agent_should_offer_similar = False

            # user liked the movie
            if user_dact.intent == UserIntents.ACCEPT:
                name = self.dialogue_state.item_in_focus[Slots.TITLE.value]
                if name in self.dialogue_context.movies_recommended:
                    self.dialogue_context.movies_recommended[name].append(
                        'accept')

            # change agent state to should make offer
            if user_dact.intent == UserIntents.REJECT:
                self.dialogue_state.agent_made_offer = False
                self.dialogue_state.agent_should_make_offer = True
                name = self.dialogue_state.item_in_focus[Slots.TITLE.value]
                if name in self.dialogue_context.movies_recommended:
                    self.dialogue_context.movies_recommended[name].append(
                        user_dact.params[0].value)
                else:
                    self.dialogue_context.movies_recommended[name] = [
                        user_dact.params[0].value
                    ]
                if self.dialogue_state.agent_should_offer_similar:
                    # Todo
                    pass

            # removed the information needs if mentioned by the user
            if user_dact.intent == UserIntents.REMOVE_PREFERENCE:
                for param in user_dact.params:
                    if param.slot in self.ontology.multiple_values_CIN:
                        self.dialogue_state.frame_CIN[param.slot].remove(
                            param.value)
                    else:
                        self.dialogue_state.frame_CIN[param.slot] = None

            if user_dact.intent == UserIntents.REVEAL:
                # fills in the current information needs
                for param in user_dact.params:
                    if param.slot in self.dialogue_state.frame_CIN:
                        if param.slot in self.ontology.multiple_values_CIN:
                            if param.op == Operator.NE:
                                if param.value in self.dialogue_state.frame_CIN[
                                        param.slot]:
                                    self.dialogue_state.frame_CIN[
                                        param.slot].remove(param.value)
                                else:
                                    param.value = f'.NOT.{param.value}'
                                    if param.value not in self.dialogue_state.frame_CIN[
                                            param.slot]:
                                        self.dialogue_state.frame_CIN[
                                            param.slot].append(param.value)
                            else:
                                if f'.NOT.{param.value}' in self.dialogue_state.frame_CIN[
                                        param.slot]:
                                    self.dialogue_state.frame_CIN[
                                        param.slot].remove(
                                            f'.NOT.{param.value}')
                                if param.value not in self.dialogue_state.frame_CIN[
                                        param.slot]:
                                    self.dialogue_state.frame_CIN[
                                        param.slot].append(param.value)
                        # elif param.slot == Slots.YEAR.value:
                        #     self._add_year_CIN(param)
                        else:
                            if param.op == Operator.NE:
                                if self.dialogue_state.frame_CIN[
                                        param.slot] == param.value:
                                    self.dialogue_state.frame_CIN[
                                        param.slot] = None
                                else:
                                    param.value = f'.NOT.{param.value}'
                                    self.dialogue_state.frame_CIN[
                                        param.slot] = param.value
                            else:
                                self.dialogue_state.frame_CIN[
                                    param.slot] = param.value

                # checks if two parameters have the same value:
                self.dialogue_state.agent_must_clarify = False
                self.dialogue_state.dual_params = {}
                param_values = {}
                for param, value in self.dialogue_state.frame_CIN.items():
                    if value and isinstance(value, list):
                        for v in value:
                            if v in param_values:
                                param_values[v].append(param)
                            else:
                                param_values[v] = [param]
                    elif value:
                        if value in param_values:
                            param_values[value].append(param)
                        else:
                            param_values[value] = [param]
                if any([len(v) > 1 for v in param_values.values()]):
                    self.dialogue_state.dual_params = {
                        x: y for x, y in param_values.items() if len(y) > 1
                    }
                    self.dialogue_state.agent_must_clarify = True

            if user_dact.intent in [UserIntents.REVEAL, UserIntents.REMOVE_PREFERENCE] and \
                    self.dialogue_state.agent_made_offer:
                self.dialogue_state.agent_made_offer = False

            # remove from user requestables when user asks for anything
            if user_dact.intent == UserIntents.INQUIRE:
                if not self.dialogue_state.item_in_focus[Slots.TITLE.value]:
                    print(self.dialogue_state)  # debuggig here
                name = self.dialogue_state.item_in_focus[Slots.TITLE.value]
                if name in self.dialogue_context.movies_recommended:
                    if 'inquire' not in self.dialogue_context.movies_recommended[
                            name]:
                        self.dialogue_context.movies_recommended[name].append(
                            'inquire')
                else:
                    self.dialogue_context.movies_recommended[name] = ['inquire']
                for param in user_dact.params:
                    if param.slot in self.dialogue_state.user_requestable:
                        self.dialogue_state.user_requestable.remove(param.slot)

            # when user acknowledges the previous intent
            # TODO: if any approval required, add here

            if user_dact.intent == UserIntents.CONTINUE_RECOMMENDATION:
                self.dialogue_state.agent_made_offer = False
                self.dialogue_state.agent_should_make_offer = True
                self.dialogue_state.agent_should_offer_similar = True
                self.dialogue_state.similar_movies = {
                    self.dialogue_state.item_in_focus[Slots.TITLE.value]:
                        eval(user_dact.params[0].value)
                }

            if user_dact.intent == UserIntents.RESTART:
                self.dialogue_state.initialize()
                self.dialogue_context.initialize()

            if user_dact.intent == UserIntents.BYE:
                self.dialogue_state.at_terminal_state = True

        # checks if all CIN slots are filled, database is accessed to get a recommendation
        if not self.dialogue_state.agent_req_filled:
            self.dialogue_state.agent_req_filled = True
            for slot in self.dialogue_state.agent_requestable:
                if not self.dialogue_state.frame_CIN[slot]:
                    self.dialogue_state.agent_req_filled = False
                    break

        # check if the agent can make any offer without asking any further question
        if not self.dialogue_state.agent_can_lookup:
            for value in self.dialogue_state.frame_CIN.values():
                if isinstance(value, list):
                    for val in value:
                        if val not in Values.__dict__.values():
                            self.dialogue_state.agent_can_lookup = True
                            break
                if self.dialogue_state.agent_can_lookup:
                    break
                elif value and value not in Values.__dict__.values():
                    self.dialogue_state.agent_can_lookup = True
                    break

    def update_state_agent(self, agent_dacts):
        """Updates the current dialogue state and context based on agent DActs

        Args:
            agent_dacts: dialogue acts) which is the output of dialogue policy.

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
                self.dialogue_context.movies_recommended[
                    agent_dact.params[0].value] = []
                self.dialogue_state.agent_made_partial_offer = False
                self.dialogue_state.agent_should_make_offer = False
                self.dialogue_state.agent_made_offer = True
                self.dialogue_state.user_requestable = deepcopy(
                    self.ontology.user_requestable)

    def update_state_db(self, database_result=None, backup_results=None):
        """Updates the state based on  the results fetched from the database

        Args:
            database_result: the database results based on user information needs (Default value = None)
            remove_title_from_CIN: flag indicating that agent removed the name from CIN as
                there were no result
            backup_results:  (Default value = None)

        """

        item_found = False
        self.dialogue_state.items_in_context = False
        if database_result:
            # get slots that have no value and can be a next elicit
            CIN_slots = [
                key for key in self.dialogue_state.frame_CIN.keys()
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
                if result[
                        Slots.TITLE.
                        value] not in self.dialogue_context.movies_recommended.keys(
                        ):
                    item_found = True
                    self.dialogue_state.item_in_focus = deepcopy(result)
                    break
                else:
                    self.dialogue_state.items_in_context = True

        if not item_found and self.dialogue_state.agent_should_offer_similar and backup_results:
            self.dialogue_state.agent_should_offer_similar = False
            for result in backup_results:
                if result[
                        Slots.TITLE.
                        value] not in self.dialogue_context.movies_recommended.keys(
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

    def get_state(self):
        """Returns the current dialogue state.
        
        Returns:
            the current dialogue state

        """
        return self.dialogue_state

    def get_context(self):
        """Returns the history for a specific user

        Returns:
            the current user context
            
        """
        # return self.dialogue_context
