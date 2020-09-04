"""The Dialogue Manager controls the action-selection and state-tracking part of the IAI MovieBot
agent. The agent can access the state, context and actions via the Dialogue Manager.
Dialogue manager also access the database and ontology to carry on the conversation.
"""

__author__ = "Javeria Habib"

from moviebot.dialogue_manager.dialogue_act import DialogueAct
from moviebot.dialogue_manager.dialogue_policy import DialoguePolicy
from moviebot.dialogue_manager.dialogue_state_tracker import DialogueStateTracker
from moviebot.dialogue_manager.item_constraint import ItemConstraint
from moviebot.dialogue_manager.operator import Operator
from moviebot.intents.agent_intents import AgentIntents


class DialogueManager:
    """The Dialogue Manager controls the action-selection and state-tracking part of the IAI MovieBot
    agent.
    The agent can access the state, context and actions via the Dialogue Manager.
    Dialogue manager also access the database and ontology to carry on the conversation.
    """

    def __init__(self, config, isBot, new_user):
        """Initialises the components of class DialogueStateTracking and ActionSelection

        :param config: The settings for components to be initialized
        :param isBot: if the conversation is via bot or not
        """
        self.ontology = config['ontology']
        self.database = config['database']
        self.isBot = isBot
        self.new_user = new_user
        self.dialogue_state_tracker = DialogueStateTracker(config, self.isBot)
        self.dialogue_policy = DialoguePolicy(self.ontology, self.isBot, self.new_user)

    def start_dialogue(self, new_user=False):
        """Starts the dialogue by generating a response from the agent

        :return: First agent response
        """
        self.dialogue_state_tracker.dialogue_state.initialize()
        self.dialogue_state_tracker.dialogue_context.initialize()
        agent_dact = DialogueAct(AgentIntents.WELCOME, [
            ItemConstraint('new_user', Operator.EQ, new_user), ItemConstraint('is_bot', Operator.EQ,
                                                                              self.isBot)])
        self.dialogue_state_tracker.update_state_agent([agent_dact])
        return [agent_dact]

    def receive_input(self, user_dacts):
        """Receives the input from the agent and updates state/context.

        :type user_dacts: list<DialogueAct>
        :param user_dacts: The user utterance in the form of Dialogue Acts
        """
        if user_dacts:
            self.dialogue_state_tracker.update_state_user(user_dacts)

    def generate_output(self, restart=False):
        """Selects the next action based on the Dialogue Policy and generates system response.
        Also accesses the database/ontology if required.

        :return: The system response in the form of Dialogue Acts"""
        # access the database if required according to the dialogue state and update the state
        if restart:
            self.dialogue_state_tracker.dialogue_state.initialize()
            self.dialogue_state_tracker.dialogue_context.initialize()
        dialogue_state = self.dialogue_state_tracker.dialogue_state
        if (dialogue_state.agent_can_lookup or dialogue_state.agent_req_filled) and not \
                dialogue_state.agent_made_offer:
            # accesses the database to fetch results if required
            database_result = self.database_lookup()
            self.dialogue_state_tracker.update_state_db(database_result,
                                                        self.database.backup_db_results)

        # next action based on updated state
        dialogue_state = self.dialogue_state_tracker.dialogue_state
        agent_dacts = self.dialogue_policy.next_action(dialogue_state, restart=restart)
        self.dialogue_state_tracker.update_state_agent(agent_dacts)

        return agent_dacts

    def database_lookup(self):
        """
        Performs a database query considering the current dialogue state (the current information
        needs)

        :return: The list of results matching user information needs
        """
        dialogue_state = self.dialogue_state_tracker.get_state()
        database_result = self.database.database_lookup(dialogue_state, self.ontology)
        return database_result

    def get_state(self):
        """Returns the dialogue state. This can be used by the NLG to generate an appropriate output

        :return: the current state of Dialogue"""
        return self.dialogue_state_tracker.dialogue_state

    def get_context(self):
        """Returns current context of the conversation

        :return: the current context of the conversation with a specific user"""
        return self.dialogue_state_tracker.dialogue_context
