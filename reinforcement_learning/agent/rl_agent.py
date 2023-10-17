"""MovieBot agent for reinforcement learning of dialogue policy."""
import logging
from typing import Any, Dict, List, Tuple

from dialoguekit.core import AnnotatedUtterance, Intent
from dialoguekit.participant import DialogueParticipant
from moviebot.agent.agent import MovieBotAgent
from moviebot.core.core_types import DialogueOptions
from moviebot.core.utterance.utterance import UserUtterance
from moviebot.dialogue_manager.dialogue_act import DialogueAct
from moviebot.nlu.neural_nlu import NeuralNLU
from reinforcement_learning.agent.rl_dialogue_manager import DialogueManagerRL

logger = logging.getLogger(__name__)


class MovieBotAgentRL(MovieBotAgent):
    def __init__(self, config: Dict[str, Any] = None) -> None:
        """Initializes a MovieBot agent for reinforcement learning.

        Args:
            config: Configuration. Defaults to None.
        """
        super().__init__(
            config=config,
        )

        self.dialogue_manager = DialogueManagerRL(
            self.data_config, self.isBot, self.new_user
        )

        if config.get("nlu_type", "") == "neural":
            self.nlu = NeuralNLU(None)

    def initialize(self) -> None:
        """Initializes the agent."""
        self.dialogue_manager.initialize()

    def generate_utterance(
        self,
        agent_dacts: List[DialogueAct],
        options: DialogueOptions = {},
        user_fname: str = None,
        recommended_item: Dict[str, Any] = None,
    ) -> Tuple[AnnotatedUtterance, DialogueOptions]:
        """Generates an utterance object based on agent dialogue acts.

        Args:
            agent_dacts: Agent dialogue acts.
            options: Dialogue options that are provided to the user along with
              the utterance.
            user_fname: User's first name. Defaults to None.
            recommended_item: Recommended item. Defaults to None.

        Returns:
            An annotated utterance and the associated options.
        """
        metadata = {"options": options}
        if recommended_item:
            metadata.update({"recommended_item": recommended_item})

        agent_response, options = self.nlg.generate_output(
            agent_dacts,
            self.dialogue_manager.get_state(),
            user_fname=user_fname,
        )
        agent_intent = Intent(
            ";".join([da.intent.value.label for da in agent_dacts])
        )

        if not self.isBot:
            logger.debug(
                str(self.dialogue_manager.dialogue_state_tracker.dialogue_state)
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

        return utterance, options

    def get_user_dialogue_acts(
        self,
        user_utterance: UserUtterance,
        utterance_options: DialogueOptions,
    ) -> List[DialogueAct]:
        """Generates dialogue acts associated to a given user utterance.

        Args:
            user_utterance: User utterance.
            utterance_options: Dialogue options that are provided to the user
              along with the utterance.

        Returns:
            List of dialogue acts.
        """
        return self.nlu.generate_dacts(
            user_utterance,
            utterance_options,
            self.dialogue_manager.get_state(),
        )

    def welcome(self, user_fname: str = None) -> None:
        """Sends a welcome message to the user.

        This method is not used for reinforcement learning.
        """
        pass

    def goodbye(self) -> None:
        """Sends a goodbye message to the user.

        This method is not used for reinforcement learning.
        """
        pass
