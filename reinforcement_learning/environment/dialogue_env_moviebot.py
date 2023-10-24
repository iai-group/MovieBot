"""Gymnasium environment to train a dialogue manager for MovieBot using
reinforcement learning.

The environment comprise a user simulator, MovieBot agent for which we want to
train a dialogue policy."""

import json
import logging
import os
from pprint import pprint
from typing import Any, Dict, List, Optional, Tuple

import confuse
import gymnasium as gym
import numpy as np
import torch

from dialoguekit.connector.dialogue_connector import (
    _DIALOGUE_EXPORT_PATH,
    DialogueConnector,
)
from dialoguekit.core.annotated_utterance import AnnotatedUtterance
from dialoguekit.core.dialogue import Dialogue
from dialoguekit.participant.participant import DialogueParticipant
from moviebot.core.utterance.utterance import UserUtterance
from moviebot.dialogue_manager.dialogue_act import DialogueAct
from moviebot.dialogue_manager.dialogue_policy.neural_dialogue_policy import (
    NeuralDialoguePolicy,
)
from reinforcement_learning.agent.rl_agent import MovieBotAgentRL
from reinforcement_learning.utils import build_agenda_based_simulator
from usersimcrs.simulator.user_simulator import UserSimulator


class DialogueEnvMovieBot(gym.Env):
    def __init__(
        self,
        user_simulator_config: confuse.Configuration,
        agent_config: Dict[str, Any],
        agent_possible_actions: List[DialogueAct],
        input_size: int,
        turn_penalty: float = 0.0,
        b_use_intents: bool = False,
    ) -> None:
        """Initializes the environment.

        Args:
            user_simulator: User simulator.
            agent: MovieBot agent.
            agent_possible_actions: List of possible actions for the agent.
            input_size: Size of the input vector for the dialogue policy.
            turn_penalty: Penalty for each turn in the dialogue. Defaults to
              0.0.
            b_user_intents: Whether to use user intents. Defaults to False.
        """
        super(DialogueEnvMovieBot, self).__init__()

        self.user_simulator: UserSimulator = build_agenda_based_simulator(
            user_simulator_config
        )
        self.agent = MovieBotAgentRL(agent_config)
        self.agent_possible_actions = agent_possible_actions

        self.turn_penalty = turn_penalty
        self.b_use_intents = b_use_intents
        self.input_size = input_size

        # Action space
        self.action_space = gym.spaces.Discrete(
            len(self.agent_possible_actions)
        )

        # Observation space
        self.observation_space = gym.spaces.Box(
            low=-np.inf,
            high=np.inf,
            shape=(self.input_size,),
            dtype=np.float32,
        )

        DialogueConnector(self.agent, self.user_simulator, None)

    def render(self) -> None:
        """Renders the environment."""
        state = self.agent.dialogue_manager.dialogue_state_tracker.get_state()
        print("Dialogue state:")
        pprint(state.to_dict())

    def reset(
        self, **kwargs: Optional[Dict[str, Any]]
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Resets the environment.

        Returns:
            The initial observation.
        """
        # 1. Initialize the agent and user simulator
        self.agent.initialize()
        self.user_simulator.initialize()

        # 2. Get initial dialogue state
        dialogue_state = (
            self.agent.dialogue_manager.dialogue_state_tracker.get_state()
        )
        user_intents = []
        agent_intents = []

        if self.b_use_intents:
            if dialogue_state.last_user_dacts:
                user_intents = [
                    da.intent for da in dialogue_state.last_user_dacts
                ]
            if dialogue_state.last_agent_dacts:
                agent_intents = [
                    da.intent for da in dialogue_state.last_agent_dacts
                ]
        # 3. Transform the dialogue state into a vector for dialogue policy
        observation = NeuralDialoguePolicy.build_input(
            dialogue_state,
            b_use_intents=self.b_use_intents,
            user_intents=user_intents,
            agent_intents=agent_intents,
        )
        observation = observation.numpy()

        # 4. Initialize the dialogue history
        self.dialogue_history = Dialogue(self.agent.id, self.user_simulator.id)

        return observation, {}

    def _check_terminal_state(self) -> bool:
        """Checks if the current state is a terminal state."""
        return self.agent.dialogue_manager.get_state().at_terminal_state

    def step(
        self, action: int
    ) -> Tuple[np.ndarray, float, bool, Dict[str, Any]]:
        """Performs a step in the environment.

        Args:
            action: The action to perform.

        Returns:
            A tuple containing the observation, reward, done flag and info
            dictionary.
        """
        reward = self.turn_penalty
        info = {}
        truncated = False
        user_intents = []
        agent_intents = []

        # 1. Check if the action can be performed, if not the episode is
        # truncated
        initial_agent_dacts = [self.agent_possible_actions[action]]
        try:
            agent_dacts = self.agent.dialogue_manager.get_filled_dialogue_acts(
                initial_agent_dacts
            )
            if self.b_use_intents:
                agent_intents = [da.intent for da in agent_dacts]
            recommended_movie = (
                self.agent.dialogue_manager.get_state().item_in_focus
            )

            agent_utterance, user_options = self.agent.generate_utterance(
                agent_dacts,
                user_fname=self.user_simulator.id,
                recommended_item=recommended_movie,
            )

            # 2. Perform the action in the environment (i.e., update state
            # tracker)
            dst = self.agent.dialogue_manager.dialogue_state_tracker
            dst.update_state_agent(agent_dacts)

            self.dialogue_history.add_utterance(agent_utterance)
        except Exception as e:
            logging.error(e, exc_info=True)
            truncated = True
            reward = -1000.0
            info.update(
                {
                    "reward": reward,
                    "message": "Exception",
                    "success": False,
                    "agent_dialogue_acts": initial_agent_dacts,
                }
            )
            self.dialogue_history.metadata["error"] = str(e)
            self._save_dialogue_history()
            return (
                torch.empty(1, self.input_size),
                reward,
                True,
                truncated,
                info,
            )

        done = self._check_terminal_state()

        if not done:
            # 3. Send the agent's response to the user simulator and get the
            # user's response
            logging.debug(f"Agent utterance: {agent_utterance.text}")
            try:
                user_utterance: AnnotatedUtterance = (
                    self.user_simulator.receive_utterance(agent_utterance)
                )
                logging.debug(f"User utterance: {user_utterance.text}")
                _user_utterance = UserUtterance.from_utterance(
                    user_utterance.get_utterance()
                )
                self.agent.dialogue_manager.get_state().user_utterance = (
                    _user_utterance
                )
                user_dacts = self.agent.get_user_dialogue_acts(
                    _user_utterance, user_options
                )

                user_utterance.participant = DialogueParticipant.USER
                if user_dacts is not None:
                    user_utterance.metadata.update(
                        {"NLU output": [str(da) for da in user_dacts]}
                    )
                self.dialogue_history.add_utterance(user_utterance)

                if self.b_use_intents:
                    user_intents = [da.intent for da in user_dacts]

                # 4. Update the dialogue state tracker
                dst = self.agent.dialogue_manager.dialogue_state_tracker
                dst.update_state_agent(user_dacts)

            except Exception as e:
                logging.error(e, exc_info=True)
                truncated = True
                reward = 0.0
                info.update(
                    {
                        "reward": reward,
                        "message": "Exception",
                        "success": False,
                    }
                )
                self.dialogue_history.metadata["error"] = str(e)
                self._save_dialogue_history()
                return (
                    torch.empty(1, self.input_size),
                    reward,
                    True,
                    truncated,
                    info,
                )

            # 5. Check if the episode is done
            done = self._check_terminal_state()

        # 6. Get the bonus reward
        if done:
            bonus_reward, success = self.get_bonus_reward()
            reward += bonus_reward
            info.update(
                {
                    "success": success,
                }
            )

            # 7. Save the dialogue history
            self._save_dialogue_history()

        # 8. Get the next state
        dialogue_state = (
            self.agent.dialogue_manager.dialogue_state_tracker.get_state()
        )
        observation = NeuralDialoguePolicy.build_input(
            dialogue_state,
            b_use_intents=self.b_use_intents,
            user_intents=user_intents,
            agent_intents=agent_intents,
        )
        observation = observation.numpy()

        # 9. Additional information
        info.update(
            {
                "reward": reward,
                "agent_dialogue_acts": agent_dacts,
            }
        )

        return observation, reward, done, truncated, info

    def get_bonus_reward(self) -> Tuple[float, bool]:
        """Returns the bonus reward and if the dialogue was successful.

        The reward is computed as follows:
        - If the user accepted one recommendation: +100
        - If the agent made an offer but the user didn't accept one: -50
        - If the agent didn't make a recommendation: -100
        """
        reward = 0.0
        success = self.accepted_recommendation()

        dialogue_state = (
            self.agent.dialogue_manager.dialogue_state_tracker.get_state()
        )

        if success:
            reward = 100.0
        elif dialogue_state.agent_made_offer:
            reward = -50.0
        else:
            reward = -100.0

        return reward, success

    def accepted_recommendation(self) -> bool:
        """Returns True if the user accepted one recommendation."""
        b_accept = False
        dialogue_state = (
            self.agent.dialogue_manager.dialogue_state_tracker.get_state()
        )
        for _, choices in dialogue_state.movies_recommended.items():
            if "accept" in choices:
                b_accept = True
                break
        return b_accept

    def _save_dialogue_history(self) -> None:
        """Saves the dialogue history.

        Code taken from DialogueKit's DialogueConnector."""
        if len(self.dialogue_history.utterances) == 0:
            return

        file_name = (
            f"{_DIALOGUE_EXPORT_PATH}/"
            f"{self.agent.id}_{self.user_simulator.id}.json"
        )
        json_file = []

        # Check directory and read if exists.
        if not os.path.exists(_DIALOGUE_EXPORT_PATH):
            os.makedirs(_DIALOGUE_EXPORT_PATH)
        if os.path.exists(file_name):
            with open(file_name, encoding="utf-8") as json_file_out:
                json_file = json.load(json_file_out)

        dialogue_as_dict = self.dialogue_history.to_dict()
        dialogue_as_dict["agent"] = self.agent.to_dict()
        dialogue_as_dict["user"] = self.user_simulator.to_dict()

        json_file.append(dialogue_as_dict)

        with open(file_name, "w", encoding="utf-8") as outfile:
            json.dump(json_file, outfile, indent=4)
