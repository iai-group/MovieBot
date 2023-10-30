"""Class to perform training of dialogue policy."""

import logging
from abc import abstractmethod
from typing import Union

import confuse
import gymnasium as gym

import wandb
from moviebot.domain.movie_domain import MovieDomain
from reinforcement_learning.environment.dialogue_env_moviebot import (
    DialogueEnvMovieBot,
)
from reinforcement_learning.environment.dialogue_env_moviebot_no_nlu import (
    DialogueEnvMovieBotNoNLU,
)
from reinforcement_learning.utils import define_possible_actions, get_config


class Trainer:
    def __init__(self, config: confuse.Configuration) -> None:
        """Initializes the trainer.

        Args:
            config: Training configuration.
        """
        self.config = config

        # Initialize wandb
        wandb.init(project="MovieBot-Policy-Training")
        wandb.config.update(self.config.get())

        # Get user simulator and agent configuration
        self.usersim_config = get_config(
            self.config["usersim_config"].get(), name="UserSimulator"
        )
        self.agent_config = get_config(
            self.config["agent_config"].get(), name="MovieBot"
        ).get()
        domain_path = self.agent_config.get("DATA", {}).get("domain_path")
        self.agent_domain = MovieDomain(domain_path) if domain_path else None
        self.agent_possible_actions = define_possible_actions(self.agent_domain)

        self.initialize_policy()
        self.policy_path = self.config["model"]["model_path"].get()

    def create_environment(
        self, b_vectorized: bool
    ) -> Union[DialogueEnvMovieBotNoNLU, DialogueEnvMovieBot]:
        """Creates the environment for training.

        Args:
            b_vectorized: Whether or not to vectorize the environment.

        Returns:
            Environment.
        """
        env_args = {
            "input_size": self.config["model"]["policy_input_size"].get(),
            "user_simulator_config": self.usersim_config,
            "agent_config": self.agent_config,
            "agent_possible_actions": self.agent_possible_actions,
            "turn_penalty": self.config["turn_penalty"].get(),
            "b_use_intents": self.config["use_intents"].get(),
        }
        env_name = (
            "DialogueEnvMovieBotNoNLU-v0"
            if self.config["no_nlu"].get()
            else "DialogueEnvMovieBot-v0"
        )
        logging.info(f"Environment: {env_name}")

        if b_vectorized:
            return gym.make_vec(
                id=env_name, vectorization_mode="sync", **env_args
            )

        return gym.make(id=env_name, **env_args)

    @abstractmethod
    def initialize_policy(self) -> None:
        """Initializes the policy.

        This method should initialize self.policy that represents the policy
        trained. Note that additional attributes can be added to the class
        if needed.

        Returns:
            Policy.

        Raises:
            NotImplementedError: If not implemented in subclass.
        """
        raise NotImplementedError

    @abstractmethod
    def train_policy(self) -> None:
        """Trains the policy.

        Raises:
            NotImplementedError: If not implemented in subclass.
        """
        raise NotImplementedError

    def save_model(self) -> None:
        """Saves the model."""
        self.policy.save_policy(self.policy_path)
        model = wandb.Artifact("policy", type="model")
        model.add_file(self.policy_path)
        wandb.log_artifact(model)
