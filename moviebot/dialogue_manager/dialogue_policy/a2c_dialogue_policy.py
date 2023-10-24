"""Deep dialogue policy based on advantage actor-critic."""
from __future__ import annotations

from typing import Any, List, Optional, Tuple

import torch

from moviebot.dialogue_manager.dialogue_policy.neural_dialogue_policy import (
    NeuralDialoguePolicy,
)


class A2CDialoguePolicy(NeuralDialoguePolicy):
    def __init__(
        self,
        input_size: int,
        hidden_size: int,
        output_size: int,
        possible_actions: List[Any],
        num_timesteps: Optional[int] = None,
        n_envs: int = 1,
    ) -> None:
        """Initializes the policy.

        Args:
            input_size: The size of the input vector.
            hidden_size: The size of the hidden layer.
            output_size: The size of the output vector.
            possible_actions: The list of possible actions.
            num_timesteps: The number of timesteps. Defaults to None.
            n_envs: The number of environments. Defaults to 1.
        """
        super().__init__(input_size, hidden_size, output_size, possible_actions)

        self.n_envs = n_envs

        self.actor = torch.nn.Sequential(
            torch.nn.Linear(input_size, hidden_size),
            torch.nn.ReLU(),
            torch.nn.Linear(hidden_size, output_size),
        )

        self.critic = torch.nn.Sequential(
            torch.nn.Linear(input_size, hidden_size),
            torch.nn.ReLU(),
            torch.nn.Linear(hidden_size, 1),
        )

        self.actor_optimizer = torch.optim.Adam(
            self.actor.parameters(), lr=0.001
        )
        self.actor_lr_scheduler = None
        self.critic_optimizer = torch.optim.Adam(
            self.critic.parameters(), lr=0.005
        )
        self.critic_lr_scheduler = None

        if num_timesteps is not None:
            self.actor_lr_scheduler = torch.optim.lr_scheduler.LinearLR(
                self.actor_optimizer, total_iters=num_timesteps
            )
            self.critic_lr_scheduler = torch.optim.lr_scheduler.LinearLR(
                self.critic_optimizer, total_iters=num_timesteps
            )

    def forward(self, state: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """Forward pass.

        Args:
            state: A batched vector of dialogue states.

        Returns:
            The output of the actor and the critic.
        """
        state_values = self.critic(state)
        actions_log_probs = self.actor(state)
        return state_values, actions_log_probs

    def select_action(
        self, state: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        """Returns the selected action and its log probability.

        Args:
            state: Representation of dialogue state as a vector.

        Returns:
            The selected action id, its log probability, the state value, and
            the entropy.
        """
        state_value, actions_log_prob = self.forward(state)
        actions_distribution = torch.distributions.Categorical(
            logits=actions_log_prob
        )
        action = actions_distribution.sample()
        actions_log_prob = actions_distribution.log_prob(action)
        entropy = actions_distribution.entropy()
        return action, actions_log_prob, state_value, entropy

    def get_losses(
        self,
        rewards: torch.Tensor,
        action_log_probs: torch.Tensor,
        value_preds: torch.Tensor,
        entropy: torch.Tensor,
        mask: torch.Tensor,
        gamma: float = 0.99,
        lam: float = 0.95,
        entropy_coef: float = 0.01,
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """Computes the loss of a minibatch using the generalized advantage
        estimator.

        Args:
            rewards: The rewards.
            action_log_probs: The log probabilities of the actions.
            value_preds: The predicted values.
            entropy: The entropy.
            mask: The mask.
            gamma: The discount factor. Defaults to 0.99.
            lam: The GAE parameter (1 for Monte-Carlo sampling, 0 for normal
              TD-learning). Defaults to 0.95.
            entropy_coef: The entropy coefficient. Defaults to 0.01.

        Returns:
            The critic and actor losses for the minibatch.
        """
        T = len(rewards)
        advantages = torch.zeros(T, self.n_envs)

        # Compute advantages with GAE
        gae = 0.0
        for t in reversed(range(T - 1)):
            td_error = (
                rewards[t]
                + gamma * mask[t] * value_preds[t + 1]
                - value_preds[t]
            )
            gae = td_error + gamma * lam * mask[t] * gae
            advantages[t] = gae

        # Compute losses
        critic_loss = advantages.pow(2).mean()
        actor_loss = (
            -(advantages.detach() * action_log_probs).mean()
            - entropy_coef * entropy.mean()
        )
        return critic_loss, actor_loss

    def update_parameters(
        self, critic_loss: torch.Tensor, actor_loss: torch.Tensor
    ) -> None:
        """Updates the parameters of the policy.

        Args:
            critic_loss: The critic loss.
            actor_loss: The actor loss.
        """
        self.critic_optimizer.zero_grad()
        critic_loss.backward()
        self.critic_optimizer.step()
        if self.critic_lr_scheduler is not None:
            self.critic_lr_scheduler.step()

        self.actor_optimizer.zero_grad()
        actor_loss.backward()
        self.actor_optimizer.step()
        if self.actor_lr_scheduler is not None:
            self.actor_lr_scheduler.step()

    def save_policy(self, path: str) -> None:
        """Saves the policy.

        Args:
            path: The path to save the policy to.
        """
        state_dict = {
            "actor": self.actor.state_dict(),
            "critic": self.critic.state_dict(),
            "input_size": self.input_size,
            "hidden_size": self.hidden_size,
            "output_size": self.output_size,
            "possible_actions": self.possible_actions,
        }
        torch.save(state_dict, path)

    @classmethod
    def load_policy(cls, path: str) -> A2CDialoguePolicy:
        """Loads the policy.

        Args:
            path: The path to load the policy from.

        Returns:
            The loaded policy.
        """
        state_dict = torch.load(path)
        policy = cls(
            state_dict["input_size"],
            state_dict["hidden_size"],
            state_dict["output_size"],
            state_dict["possible_actions"],
        )
        policy.actor.load_state_dict(state_dict["actor"])
        policy.critic.load_state_dict(state_dict["critic"])
        return policy
