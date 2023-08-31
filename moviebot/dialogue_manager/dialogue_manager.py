"""The dialogue manager controls the action-selection and state-tracking part
of the IAI MovieBot agent.

The agent can access the state, context and actions via the dialogue
manager. Dialogue manager also access the database and ontology to carry
on the conversation.
"""


from collections import defaultdict
from dataclasses import asdict
from typing import TYPE_CHECKING, Any, Dict, List

from dialoguekit.connector import DialogueConnector
from dialoguekit.core import AnnotatedUtterance
from dialoguekit.participant import User
from moviebot.core.utterance.utterance import UserUtterance
from moviebot.dialogue_manager.dialogue_act import DialogueAct
from moviebot.dialogue_manager.dialogue_policy import DialoguePolicy
from moviebot.dialogue_manager.dialogue_state import DialogueState
from moviebot.dialogue_manager.dialogue_state_tracker import (
    DialogueStateTracker,
)
from moviebot.recommender.recommender_model import RecommenderModel

if TYPE_CHECKING:
    from moviebot.agent.agent import MovieBotAgent
    from moviebot.controller.controller import Controller


class DialogueManager(DialogueConnector):
    def __init__(
        self,
        config: Dict[str, Any],
        isBot: bool,
        new_user: bool,
        agent: "MovieBotAgent",
        user: User,
        platform: "Controller",
        conversation_id: str = None,
        save_dialogue_history: bool = True,
    ) -> None:
        """Initializes the dialogue manager including the state tracker and
        dialogue policy.

        Args:
            config: The settings for components to be initialized.
            isBot: If the conversation is via bot or not.
            new_user: Whether the user is new or not.
            agent: The agent.
            user: The user.
            platform: The platform.
            conversation_id: The conversation ID. Defaults to None.
            save_dialogue_history: Whether to save the dialogue history or not.
              Defaults to True.
        """
        super().__init__(
            agent, user, platform, conversation_id, save_dialogue_history
        )
        self.isBot = isBot
        self.new_user = new_user
        self.dialogue_state_tracker = DialogueStateTracker(config, self.isBot)
        self.dialogue_policy = DialoguePolicy(self.isBot, self.new_user)
        self.recommender: RecommenderModel = config.get("recommender")

    def start(self) -> None:
        """Starts the dialogue."""
        self.dialogue_state_tracker.initialize()
        self._agent.welcome(self._user.id)

    def close(self) -> None:
        """Closes the conversation.

        If '_save_dialogue_history' is set to True it will export the
        dialogue history.
        """
        if self._save_dialogue_history:
            self._stringify_dialogue_acts()
            self._dump_dialogue_history()

    def register_agent_utterance(
        self, annotated_utterance: AnnotatedUtterance
    ) -> None:
        """Registers an annotated utterance from the agent.

        This method takes a AnnotatedUtterance but only a Utterance gets sent to
        the User. The AnnotatedUtterance gets used to store the conversation for
        future reference, and if the Agent wants to end the conversation with
        the _agent.stop_intent Intent, the DialogueConnector will end the
        conversation with the close() method.

        Note:
            If the Intent label is 'EXIT' the DialogueConnector will close. Thus
            it is only the agent that can close the DialogueConnector.

        Args:
            annotated_utterance: Agent utterance.
        """
        self._dialogue_history.add_utterance(annotated_utterance)
        self._platform.display_agent_utterance(
            self._user.id, annotated_utterance
        )
        if annotated_utterance.intent == self._agent.stop_intent:
            self.close()
        else:
            self._user.receive_utterance(annotated_utterance)

    def register_user_utterance(
        self, annotated_utterance: AnnotatedUtterance
    ) -> None:
        """Registers an annotated utterance from the user.

        In most cases the Agent should not know about the Users Intent and
        Annotation-s. But for some use cases this additional information may
        become useful, depending on the UI etc.
        Thus the complete AnnotatedUtterance will be sent to the Agent. It is
        the Agents responsibility to only use the information it is supposed
        to.

        Args:
            annotated_utterance: User utterance.
        """
        user_options = self._dialogue_history.utterances[-1].metadata.get(
            "options", {}
        )
        self._dialogue_history.add_utterance(annotated_utterance)
        self._platform.display_user_utterance(
            self._user.id, annotated_utterance
        )
        user_utterance = UserUtterance(
            **asdict(annotated_utterance.get_utterance())
        )
        self._agent.receive_utterance(user_utterance, user_options)

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
