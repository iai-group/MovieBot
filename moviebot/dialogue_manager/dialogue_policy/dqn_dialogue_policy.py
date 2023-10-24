"""Deep dialogue policy based on Q network."""

from __future__ import annotations

from typing import Any, List, Tuple

import torch

from moviebot.dialogue_manager.dialogue_policy.neural_dialogue_policy import (
    NeuralDialoguePolicy,
)


class DQNDialoguePolicy(NeuralDialoguePolicy):
    def __init__(
        self,
        input_size: int,
        hidden_size: int,
        output_size: int,
        possible_actions: List[Any],
    ) -> None:
        """Initializes the policy.

        Args:
            input_size: The size of the input vector.
            hidden_size: The size of the hidden layer.
            output_size: The size of the output vector.
            possible_actions: The list of possible actions.
        """
        super().__init__(input_size, hidden_size, output_size, possible_actions)

        self.model = torch.nn.Sequential(
            torch.nn.Linear(input_size, hidden_size),
            torch.nn.ReLU(),
            torch.nn.Linear(hidden_size, hidden_size),
            torch.nn.ReLU(),
            torch.nn.Linear(hidden_size, output_size),
        )

    def forward(self, state: torch.Tensor) -> torch.Tensor:
        """Forward pass of the policy.

        Args:
            state: State or batch of states.

        Returns:
            Next action(s) probabilities.
        """
        return self.model(state)

    def select_action(self, state: torch.Tensor) -> Tuple[int, Any]:
        """Selects an action based on the current state.

        Args:
            state: The current state.

        Returns:
            The id of selected action and the action.
        """
        with torch.no_grad():
            action = self.model(state).max(1)[1].view(1, 1)

        return action.item(), self.possible_actions[action.item()]

    def save_policy(self, path: str) -> None:
        """Saves the policy to a file.

        Args:
            path: The path to save the policy to.
        """
        state_dict = {
            "input_size": self.input_size,
            "hidden_size": self.hidden_size,
            "output_size": self.output_size,
            "possible_actions": self.possible_actions,
            "model_state_dict": self.model.state_dict(),
        }
        torch.save(state_dict, path)

    @classmethod
    def load_policy(cls, path: str) -> DQNDialoguePolicy:
        """Loads the policy from a file.

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
        policy.load_state_dict(state_dict["model_state_dict"])
        return policy
