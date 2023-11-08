"""The dialogue manager controls the action-selection and state-tracking part
of the IAI MovieBot agent.

The agent can access the state, context and actions via the dialogue
manager. Dialogue manager also access the database and domain to carry
on the conversation.
"""


from typing import Any, Dict, List

from moviebot.core.intents.agent_intents import AgentIntents
from moviebot.dialogue_manager.dialogue_act import DialogueAct
from moviebot.dialogue_manager.dialogue_policy.rb_dialogue_policy import (
    RuleBasedDialoguePolicy,
)
from moviebot.dialogue_manager.dialogue_state import DialogueState
from moviebot.dialogue_manager.dialogue_state_tracker import (
    DialogueStateTracker,
)
from moviebot.nlu.annotation.item_constraint import ItemConstraint
from moviebot.nlu.annotation.operator import Operator
from moviebot.recommender.recommender_model import RecommenderModel


class DialogueManager:
    def __init__(
        self, config: Dict[str, Any], isBot: bool, new_user: bool
    ) -> None:
        """Initializes the dialogue manager including the state tracker and
        dialogue policy.

        Args:
            config: The settings for components to be initialized.
            isBot: If the conversation is via bot or not.
            new_user: Whether the user is new or not.
        """
        self.isBot = isBot
        self.new_user = new_user
        self.dialogue_state_tracker = DialogueStateTracker(config, self.isBot)
        self.dialogue_policy = RuleBasedDialoguePolicy(
            self.isBot, self.new_user
        )
        self.recommender: RecommenderModel = config.get("recommender")

    def start_dialogue(self, new_user: bool = False) -> List[DialogueAct]:
        """Starts the dialogue by generating a response from the agent.

        Args:
            new_user: Whether the user is new or not. Defaults to False.

        Returns:
            A list with the first agent response.
        """
        self.dialogue_state_tracker.initialize()
        agent_dact = DialogueAct(
            AgentIntents.WELCOME,
            [
                ItemConstraint("new_user", Operator.EQ, new_user),
                ItemConstraint("is_bot", Operator.EQ, self.isBot),
            ],
        )
        self.dialogue_state_tracker.update_state_agent([agent_dact])
        return [agent_dact]

    def receive_input(self, user_dacts: List[DialogueAct]) -> None:
        """Receives the input from the agent and updates state/context.

        Args:
            user_dacts: The user utterance in the form of dialogue acts.
        """
        if user_dacts:
            self.dialogue_state_tracker.update_state_user(user_dacts)

    def generate_output(self, restart: bool = False) -> List[DialogueAct]:
        """Selects the next action based on the dialogue policy and generates
        system response.

        Also accesses the recommender system if required.

        Args:
            restart: Whether to restart the dialogue or not. Defaults to False.

        Returns:
            The system response in the form of dialogue acts list.
        """
        # access the database if required according to the dialogue state
        # and update the state
        if restart:
            self.dialogue_state_tracker.initialize()
        dialogue_state = self.dialogue_state_tracker.get_state()
        if (
            dialogue_state.agent_can_lookup or dialogue_state.agent_req_filled
        ) and not dialogue_state.agent_made_offer:
            # accesses the database to fetch results if required
            recommended_movies = self.recommender.recommend_items(
                dialogue_state
            )
            self.dialogue_state_tracker.update_state_db(
                recommended_movies,
                self.recommender.get_previous_recommend_items(),
            )

        # next action based on updated state
        dialogue_state = self.dialogue_state_tracker.get_state()
        agent_dacts = self.dialogue_policy.next_action(
            dialogue_state, restart=restart
        )
        self.dialogue_state_tracker.update_state_agent(agent_dacts)

        return agent_dacts

    def get_state(self) -> DialogueState:
        """Returns the dialogue state.

        This can be used by the NLG to generate an appropriate output.

        Returns:
            The current state of dialogue.
        """
        return self.dialogue_state_tracker.dialogue_state
